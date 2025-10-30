#!/usr/bin/env python3
"""
Baseline Functionality Tests - Regression testing for core workflow functionality
Tests core workflow functionality as regression baseline to detect breaking changes
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.po_reader.agent import POReaderAgent
from agents.validation.agent import ValidationAgent
from agents.so_creator.agent import SalesOrderCreatorAgent
from agents.summary_insights.agent import SummaryInsightsAgent
from orchestration.orchestration_manager import OrchestrationManager
from orchestration.agent_pipeline import AgentExecutionPipeline, AgentStatus


class BaselineWorkflowTest(unittest.TestCase):
    """Test core workflow functionality as regression baseline"""
    
    def setUp(self):
        """Setup test environment with temporary directories and baseline data"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test data directories
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.outputs_dir = os.path.join(self.test_dir, 'outputs')
        self.config_dir = os.path.join(self.test_dir, 'config')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Change to test directory
        os.chdir(self.test_dir)
        
        # Create baseline test data
        self._create_baseline_test_data()
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def _create_baseline_test_data(self):
        """Create baseline test data for regression testing"""
        # Create customer orders CSV
        customer_orders_data = [
            "PO_Number,Customer_Name,SKU,Quantity,Price",
            "PO1001,ACME Corp,SKU001,10,25.50",
            "PO1002,Zenith Ltd,SKU002,5,15.75",
            "PO1003,Innova Inc,SKU001,8,26.00",
            "PO1004,ACME Corp,SKU999,3,100.00"  # Invalid SKU for testing
        ]
        
        with open(os.path.join(self.data_dir, 'customer_orders.csv'), 'w') as f:
            f.write('\n'.join(customer_orders_data))
        
        # Create master SKU CSV
        master_sku_data = [
            "SKU,Product_Name,Reference_Price",
            "SKU001,Widget A,25.00",
            "SKU002,Widget B,15.00",
            "SKU003,Widget C,30.00"
        ]
        
        with open(os.path.join(self.data_dir, 'master_sku.csv'), 'w') as f:
            f.write('\n'.join(master_sku_data))
    
    def test_po_reader_baseline_functionality(self):
        """Test PO Reader Agent baseline functionality"""
        po_agent = POReaderAgent(data_path=os.path.join(self.data_dir, 'customer_orders.csv'))
        
        # Test order reading
        orders = po_agent.read_orders()
        
        # Baseline assertions
        self.assertEqual(len(orders), 4, "Should read 4 orders from baseline data")
        self.assertIn('PO_Number', orders[0], "Orders should contain PO_Number field")
        self.assertIn('Customer_Name', orders[0], "Orders should contain Customer_Name field")
        self.assertIn('SKU', orders[0], "Orders should contain SKU field")
        self.assertIn('Quantity', orders[0], "Orders should contain Quantity field")
        self.assertIn('Price', orders[0], "Orders should contain Price field")
        self.assertIn('Total_Value', orders[0], "Orders should contain calculated Total_Value field")
        
        # Test specific baseline values
        first_order = orders[0]
        self.assertEqual(first_order['PO_Number'], 'PO1001')
        self.assertEqual(first_order['Customer_Name'], 'ACME Corp')
        self.assertEqual(first_order['SKU'], 'SKU001')
        self.assertEqual(first_order['Quantity'], 10)
        self.assertEqual(first_order['Price'], 25.50)
        self.assertEqual(first_order['Total_Value'], 255.0)
        
        # Test summary statistics
        stats = po_agent.get_summary_stats()
        self.assertEqual(stats['total_orders'], 4)
        self.assertEqual(stats['unique_customers'], 3)
        self.assertAlmostEqual(stats['total_value'], 486.25, places=2)
    
    def test_validation_agent_baseline_functionality(self):
        """Test Validation Agent baseline functionality"""
        validation_agent = ValidationAgent()
        
        # Test validation process
        validation_results = validation_agent.run_validation_engine()
        
        # Baseline assertions
        self.assertEqual(len(validation_results), 4, "Should validate 4 orders")
        
        # Check validation structure
        for result in validation_results:
            self.assertIn('PO_Number', result)
            self.assertIn('SKU', result)
            self.assertIn('Status', result)
            self.assertIn('Reasons', result)
            self.assertIn('Details', result)
            self.assertIn(result['Status'], ['Valid', 'Exception'])
        
        # Test specific baseline validation results
        po1001_result = next(r for r in validation_results if r['PO_Number'] == 'PO1001')
        self.assertEqual(po1001_result['Status'], 'Valid')
        self.assertIsNotNone(po1001_result['Details']['reference_price'])
        
        po1004_result = next(r for r in validation_results if r['PO_Number'] == 'PO1004')
        self.assertEqual(po1004_result['Status'], 'Exception')
        self.assertTrue(any('not found in master data' in reason for reason in po1004_result['Reasons']))
        
        # Test validation summary
        summary = validation_agent.get_validation_summary()
        self.assertEqual(summary['total_orders'], 4)
        self.assertEqual(summary['valid_orders'], 3)
        self.assertEqual(summary['exception_orders'], 1)
    
    def test_so_creator_baseline_functionality(self):
        """Test Sales Order Creator Agent baseline functionality"""
        # First run validation to create required input files
        validation_agent = ValidationAgent()
        validation_agent.run_validation_engine()
        validation_agent.save_validation_results(self.outputs_dir)
        
        # Test SO creation
        so_agent = SalesOrderCreatorAgent()
        result = so_agent.create_sales_orders()
        
        # Baseline assertions
        self.assertTrue(result['success'], "SO creation should succeed")
        self.assertEqual(result['order_count'], 3, "Should create 3 sales orders from valid POs")
        self.assertGreater(result['total_sales_value'], 0, "Should have positive total sales value")
        
        # Test sales order structure
        sales_orders = result['sales_orders']
        self.assertEqual(len(sales_orders), 3)
        
        for so in sales_orders:
            self.assertIn('SO_Number', so)
            self.assertIn('PO_Number', so)
            self.assertIn('Customer', so)
            self.assertIn('Material', so)
            self.assertIn('Quantity', so)
            self.assertIn('Price', so)
            self.assertIn('Total', so)
            self.assertIn('Created_Date', so)
            self.assertTrue(so['SO_Number'].startswith('SO'))
        
        # Test CSV output exists and is valid
        self.assertIsNotNone(result['csv_file'])
        self.assertTrue(os.path.exists(result['csv_file']))
    
    def test_agent_pipeline_baseline_functionality(self):
        """Test Agent Pipeline baseline functionality"""
        pipeline = AgentExecutionPipeline()
        
        # Execute pipeline
        results = pipeline.execute_pipeline()
        
        # Baseline assertions
        self.assertGreaterEqual(len(results), 4, "Should execute at least 4 agents")
        
        # Check that critical agents completed successfully
        critical_agents = ['po_reader', 'validation']
        for agent_name in critical_agents:
            self.assertIn(agent_name, results, f"Critical agent {agent_name} should be executed")
            self.assertEqual(results[agent_name].status, AgentStatus.COMPLETED, 
                           f"Critical agent {agent_name} should complete successfully")
        
        # Check shared data flow
        self.assertIn('customer_orders', pipeline.shared_data)
        self.assertIn('validation_results', pipeline.shared_data)
        self.assertEqual(len(pipeline.shared_data['customer_orders']), 4)
        self.assertEqual(len(pipeline.shared_data['validation_results']), 4)
        
        # Test pipeline status
        status = pipeline.get_pipeline_status()
        self.assertIsNotNone(status['pipeline_start_time'])
        self.assertIsNotNone(status['pipeline_end_time'])
        self.assertIn('execution_results', status)
    
    def test_orchestration_manager_baseline_functionality(self):
        """Test Orchestration Manager baseline functionality"""
        # Create minimal config for testing
        config_data = {
            "execution_mode": "sequential",
            "max_parallel_agents": 2,
            "dependencies": {
                "po_reader": [],
                "validation": ["po_reader"],
                "so_creator": ["validation"]
            }
        }
        
        config_path = os.path.join(self.config_dir, 'orchestration_config.json')
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Test orchestration manager
        manager = OrchestrationManager(config_path=config_path)
        
        # Test configuration validation
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'], "Configuration should be valid")
        
        # Test workflow status
        status = manager.get_workflow_status()
        self.assertIn('execution_mode', status)
        self.assertEqual(status['execution_mode'], 'sequential')
        
        # Test workflow execution
        results = manager.execute_workflow()
        self.assertGreaterEqual(len(results), 3, "Should execute at least 3 agents")


class BaselineOutputFormatTest(unittest.TestCase):
    """Test output format consistency and backward compatibility"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test directories
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.outputs_dir = os.path.join(self.test_dir, 'outputs')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
        
        os.chdir(self.test_dir)
        
        # Create minimal test data
        self._create_minimal_test_data()
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def _create_minimal_test_data(self):
        """Create minimal test data"""
        customer_orders = [
            "PO_Number,Customer_Name,SKU,Quantity,Price",
            "PO1001,Test Corp,SKU001,5,10.00"
        ]
        
        with open(os.path.join(self.data_dir, 'customer_orders.csv'), 'w') as f:
            f.write('\n'.join(customer_orders))
        
        master_skus = [
            "SKU,Product_Name,Reference_Price",
            "SKU001,Test Widget,10.00"
        ]
        
        with open(os.path.join(self.data_dir, 'master_sku.csv'), 'w') as f:
            f.write('\n'.join(master_skus))
    
    def test_validation_output_format_consistency(self):
        """Test validation output format remains consistent"""
        validation_agent = ValidationAgent()
        validation_agent.run_validation_engine()
        simple_file, detailed_file = validation_agent.save_validation_results(self.outputs_dir)
        
        # Test simple format structure
        with open(simple_file, 'r') as f:
            simple_data = json.load(f)
        
        self.assertIsInstance(simple_data, list)
        for item in simple_data:
            self.assertIn('PO_Number', item)
            self.assertIn('Status', item)
            self.assertIn(item['Status'], ['Valid', 'Exception'])
        
        # Test detailed format structure
        with open(detailed_file, 'r') as f:
            detailed_data = json.load(f)
        
        self.assertIsInstance(detailed_data, list)
        for item in detailed_data:
            self.assertIn('PO_Number', item)
            self.assertIn('SKU', item)
            self.assertIn('Status', item)
            self.assertIn('Reasons', item)
            self.assertIn('Details', item)
            self.assertIsInstance(item['Reasons'], list)
            self.assertIsInstance(item['Details'], dict)
    
    def test_sales_order_csv_format_consistency(self):
        """Test sales order CSV format remains consistent"""
        # Setup validation results first
        validation_agent = ValidationAgent()
        validation_agent.run_validation_engine()
        validation_agent.save_validation_results(self.outputs_dir)
        
        # Create sales orders
        so_agent = SalesOrderCreatorAgent()
        result = so_agent.create_sales_orders()
        
        # Test CSV format
        csv_file = result['csv_file']
        self.assertTrue(os.path.exists(csv_file))
        
        with open(csv_file, 'r') as f:
            lines = f.readlines()
        
        # Test header format
        header = lines[0].strip().split(',')
        expected_headers = ['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total']
        self.assertEqual(header, expected_headers)
        
        # Test data format
        if len(lines) > 1:
            data_line = lines[1].strip().split(',')
            self.assertEqual(len(data_line), len(expected_headers))
            self.assertTrue(data_line[0].startswith('SO'))  # SO_Number format
    
    def test_agent_result_structure_consistency(self):
        """Test agent result structure remains consistent"""
        pipeline = AgentExecutionPipeline()
        results = pipeline.execute_pipeline()
        
        # Test result structure for each agent
        for agent_name, result in results.items():
            self.assertHasAttr(result, 'agent_name')
            self.assertHasAttr(result, 'status')
            self.assertHasAttr(result, 'start_time')
            self.assertHasAttr(result, 'end_time')
            self.assertHasAttr(result, 'execution_time')
            self.assertHasAttr(result, 'data')
            self.assertHasAttr(result, 'error_message')
            self.assertHasAttr(result, 'output_files')
            
            self.assertEqual(result.agent_name, agent_name)
            self.assertIsInstance(result.status, AgentStatus)


class BaselineAgentInterfaceTest(unittest.TestCase):
    """Test agent interface stability and contract compliance"""
    
    def test_po_reader_interface_compliance(self):
        """Test PO Reader Agent interface compliance"""
        po_agent = POReaderAgent()
        
        # Test required methods exist
        self.assertTrue(hasattr(po_agent, 'read_orders'))
        self.assertTrue(hasattr(po_agent, 'display_orders_table'))
        self.assertTrue(hasattr(po_agent, 'get_summary_stats'))
        self.assertTrue(hasattr(po_agent, 'generate_reasoning_summary'))
        
        # Test method signatures (callable)
        self.assertTrue(callable(po_agent.read_orders))
        self.assertTrue(callable(po_agent.display_orders_table))
        self.assertTrue(callable(po_agent.get_summary_stats))
        self.assertTrue(callable(po_agent.generate_reasoning_summary))
    
    def test_validation_agent_interface_compliance(self):
        """Test Validation Agent interface compliance"""
        validation_agent = ValidationAgent()
        
        # Test required methods exist
        self.assertTrue(hasattr(validation_agent, 'run_validation_engine'))
        self.assertTrue(hasattr(validation_agent, 'save_validation_results'))
        self.assertTrue(hasattr(validation_agent, 'get_validation_summary'))
        self.assertTrue(hasattr(validation_agent, 'validate_orders'))
        
        # Test method signatures
        self.assertTrue(callable(validation_agent.run_validation_engine))
        self.assertTrue(callable(validation_agent.save_validation_results))
        self.assertTrue(callable(validation_agent.get_validation_summary))
        self.assertTrue(callable(validation_agent.validate_orders))
    
    def test_so_creator_interface_compliance(self):
        """Test Sales Order Creator Agent interface compliance"""
        so_agent = SalesOrderCreatorAgent()
        
        # Test required methods exist
        self.assertTrue(hasattr(so_agent, 'create_sales_orders'))
        self.assertTrue(hasattr(so_agent, 'process_validated_orders'))
        self.assertTrue(hasattr(so_agent, 'generate_csv_output'))
        self.assertTrue(hasattr(so_agent, 'validate_output_format'))
        
        # Test method signatures
        self.assertTrue(callable(so_agent.create_sales_orders))
        self.assertTrue(callable(so_agent.process_validated_orders))
        self.assertTrue(callable(so_agent.generate_csv_output))
        self.assertTrue(callable(so_agent.validate_output_format))
    
    def test_orchestration_interface_compliance(self):
        """Test orchestration components interface compliance"""
        # Test AgentExecutionPipeline
        pipeline = AgentExecutionPipeline()
        
        self.assertTrue(hasattr(pipeline, 'execute_pipeline'))
        self.assertTrue(hasattr(pipeline, 'get_pipeline_status'))
        self.assertTrue(hasattr(pipeline, 'save_pipeline_results'))
        
        # Test OrchestrationManager
        manager = OrchestrationManager()
        
        self.assertTrue(hasattr(manager, 'execute_workflow'))
        self.assertTrue(hasattr(manager, 'get_workflow_status'))
        self.assertTrue(hasattr(manager, 'validate_configuration'))


if __name__ == '__main__':
    unittest.main()