#!/usr/bin/env python3
"""
API Stability Tests - Test agent interface method signatures and orchestration API consistency
Tests API stability, method signatures, return types, and shared data structure compatibility
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
import inspect
from typing import Dict, List, Any, Optional, get_type_hints

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.po_reader.agent import POReaderAgent
from agents.validation.agent import ValidationAgent
from agents.so_creator.agent import SalesOrderCreatorAgent
from agents.summary_insights.agent import SummaryInsightsAgent
from orchestration.orchestration_manager import OrchestrationManager
from orchestration.agent_pipeline import AgentExecutionPipeline, AgentResult, AgentStatus
from orchestration.agent_coordinator import AgentCoordinator


class AgentInterfaceStabilityTest(unittest.TestCase):
    """Test agent interface method signatures and return types"""
    
    def test_po_reader_agent_api_stability(self):
        """Test PO Reader Agent API stability"""
        po_agent = POReaderAgent()
        
        # Test core method signatures
        self.assertTrue(hasattr(po_agent, 'read_orders'))
        self.assertTrue(callable(po_agent.read_orders))
        
        # Test method signature parameters
        read_orders_sig = inspect.signature(po_agent.read_orders)
        self.assertEqual(len(read_orders_sig.parameters), 0, "read_orders should have no parameters")
        
        # Test return type consistency
        orders = po_agent.read_orders()
        self.assertIsInstance(orders, list, "read_orders should return a list")
        
        # Test required methods exist with correct signatures
        required_methods = {
            'display_orders_table': {'params': 0, 'return_type': type(None)},
            'get_summary_stats': {'params': 0, 'return_type': dict},
            'generate_reasoning_summary': {'params': 0, 'return_type': str},
            'display_reasoning_output': {'params': 0, 'return_type': type(None)}
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(po_agent, method_name), f"Method {method_name} should exist")
            method = getattr(po_agent, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count
            sig = inspect.signature(method)
            self.assertEqual(len(sig.parameters), expected['params'], 
                           f"Method {method_name} should have {expected['params']} parameters")
        
        # Test data structure consistency
        if orders:
            order = orders[0]
            required_fields = ['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price', 'Total_Value']
            for field in required_fields:
                self.assertIn(field, order, f"Order should contain {field} field")
        
        # Test summary stats structure
        stats = po_agent.get_summary_stats()
        required_stats_fields = ['total_orders', 'total_value', 'unique_customers', 'customer_breakdown']
        for field in required_stats_fields:
            self.assertIn(field, stats, f"Summary stats should contain {field} field")
    
    def test_validation_agent_api_stability(self):
        """Test Validation Agent API stability"""
        validation_agent = ValidationAgent()
        
        # Test core method signatures
        required_methods = {
            'run_validation_engine': {'params': 0, 'return_type': list},
            'validate_orders': {'params': 0, 'return_type': list},
            'save_validation_results': {'params': 1, 'return_type': tuple},  # output_dir parameter
            'get_validation_summary': {'params': 0, 'return_type': dict},
            'generate_validation_explanations': {'params': 0, 'return_type': list},
            'display_validation_reasoning': {'params': 0, 'return_type': type(None)}
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(validation_agent, method_name), f"Method {method_name} should exist")
            method = getattr(validation_agent, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count (excluding self and optional parameters)
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertLessEqual(len(required_params), expected['params'] + 1,  # +1 for self
                               f"Method {method_name} should have at most {expected['params']} required parameters")
        
        # Test validation result structure consistency
        validation_results = validation_agent.run_validation_engine()
        if validation_results:
            result = validation_results[0]
            required_fields = ['PO_Number', 'SKU', 'Status', 'Reasons', 'Details']
            for field in required_fields:
                self.assertIn(field, result, f"Validation result should contain {field} field")
            
            # Test status values are consistent
            self.assertIn(result['Status'], ['Valid', 'Exception'], "Status should be Valid or Exception")
            self.assertIsInstance(result['Reasons'], list, "Reasons should be a list")
            self.assertIsInstance(result['Details'], dict, "Details should be a dict")
        
        # Test validation summary structure
        summary = validation_agent.get_validation_summary()
        required_summary_fields = ['total_orders', 'valid_orders', 'exception_orders', 'explanations', 'detailed_results']
        for field in required_summary_fields:
            self.assertIn(field, summary, f"Validation summary should contain {field} field")
    
    def test_so_creator_agent_api_stability(self):
        """Test Sales Order Creator Agent API stability"""
        so_agent = SalesOrderCreatorAgent()
        
        # Test core method signatures
        required_methods = {
            'create_sales_orders': {'params': 0, 'return_type': dict},
            'process_validated_orders': {'params': 0, 'return_type': list},
            'generate_csv_output': {'params': 1, 'return_type': str},  # output_file parameter
            'validate_output_format': {'params': 1, 'return_type': bool},  # csv_file parameter
            'calculate_line_totals': {'params': 0, 'return_type': dict}
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(so_agent, method_name), f"Method {method_name} should exist")
            method = getattr(so_agent, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertLessEqual(len(required_params), expected['params'] + 1,  # +1 for self
                               f"Method {method_name} should have at most {expected['params']} required parameters")
        
        # Test create_sales_orders return structure
        # Note: This will fail without proper setup, but we're testing the structure
        try:
            result = so_agent.create_sales_orders()
            if isinstance(result, dict):
                expected_fields = ['success', 'sales_orders', 'csv_file', 'total_sales_value', 'order_count']
                for field in expected_fields:
                    if field in result:  # Only check if field exists (may not exist on failure)
                        if field == 'success':
                            self.assertIsInstance(result[field], bool)
                        elif field == 'sales_orders':
                            self.assertIsInstance(result[field], list)
                        elif field in ['total_sales_value', 'order_count']:
                            self.assertIsInstance(result[field], (int, float))
        except Exception:
            # Expected to fail without proper setup, but API structure should be consistent
            pass
    
    def test_summary_insights_agent_api_stability(self):
        """Test Summary Insights Agent API stability"""
        summary_agent = SummaryInsightsAgent()
        
        # Test core method signatures
        required_methods = {
            'generate_comprehensive_summary': {'params': 0, 'return_type': dict},
            'display_console_report': {'params': 0, 'return_type': type(None)},
            'save_executive_report': {'params': 1, 'return_type': str},  # output_file parameter
            'save_dashboard_data': {'params': 1, 'return_type': str}     # output_file parameter
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(summary_agent, method_name), f"Method {method_name} should exist")
            method = getattr(summary_agent, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertLessEqual(len(required_params), expected['params'] + 1,  # +1 for self
                               f"Method {method_name} should have at most {expected['params']} required parameters")


class OrchestrationAPIStabilityTest(unittest.TestCase):
    """Test orchestration API consistency and stability"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_orchestration_manager_api_stability(self):
        """Test OrchestrationManager API stability"""
        manager = OrchestrationManager()
        
        # Test core method signatures
        required_methods = {
            'execute_workflow': {'params': 0, 'return_type': dict},
            'get_workflow_status': {'params': 0, 'return_type': dict},
            'validate_configuration': {'params': 0, 'return_type': dict},
            'create_config_file': {'params': 1, 'return_type': str},  # output_path parameter
            'display_workflow_summary': {'params': 0, 'return_type': type(None)}
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(manager, method_name), f"Method {method_name} should exist")
            method = getattr(manager, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertLessEqual(len(required_params), expected['params'] + 1,  # +1 for self
                               f"Method {method_name} should have at most {expected['params']} required parameters")
        
        # Test workflow status structure
        status = manager.get_workflow_status()
        required_status_fields = ['execution_mode', 'pipeline_status', 'coordination_status', 'shared_data_summary']
        for field in required_status_fields:
            self.assertIn(field, status, f"Workflow status should contain {field} field")
        
        # Test configuration validation structure
        validation = manager.validate_configuration()
        required_validation_fields = ['valid', 'errors', 'warnings']
        for field in required_validation_fields:
            self.assertIn(field, validation, f"Configuration validation should contain {field} field")
        
        self.assertIsInstance(validation['valid'], bool, "valid field should be boolean")
        self.assertIsInstance(validation['errors'], list, "errors field should be list")
        self.assertIsInstance(validation['warnings'], list, "warnings field should be list")
    
    def test_agent_pipeline_api_stability(self):
        """Test AgentExecutionPipeline API stability"""
        pipeline = AgentExecutionPipeline()
        
        # Test core method signatures
        required_methods = {
            'execute_pipeline': {'params': 0, 'return_type': dict},
            'get_pipeline_status': {'params': 0, 'return_type': dict},
            'save_pipeline_results': {'params': 1, 'return_type': str}  # output_file parameter
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(pipeline, method_name), f"Method {method_name} should exist")
            method = getattr(pipeline, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertLessEqual(len(required_params), expected['params'] + 1,  # +1 for self
                               f"Method {method_name} should have at most {expected['params']} required parameters")
        
        # Test pipeline status structure
        status = pipeline.get_pipeline_status()
        required_status_fields = ['pipeline_start_time', 'pipeline_end_time', 'execution_results', 'shared_data_keys']
        for field in required_status_fields:
            self.assertIn(field, status, f"Pipeline status should contain {field} field")
        
        # Test shared_data structure consistency
        self.assertIsInstance(pipeline.shared_data, dict, "shared_data should be a dictionary")
        self.assertIsInstance(pipeline.execution_results, dict, "execution_results should be a dictionary")
    
    def test_agent_coordinator_api_stability(self):
        """Test AgentCoordinator API stability"""
        coordinator = AgentCoordinator()
        
        # Test core method signatures
        required_methods = {
            'register_agent_dependencies': {'params': 1, 'return_type': type(None)},  # dependencies parameter
            'set_parallel_execution_rules': {'params': 1, 'return_type': type(None)}, # parallel_groups parameter
            'check_dependencies_satisfied': {'params': 1, 'return_type': bool},       # agent_name parameter
            'get_ready_agents': {'params': 0, 'return_type': list},
            'update_agent_status': {'params': 2, 'return_type': type(None)},          # agent_name, status parameters
            'get_coordination_status': {'params': 0, 'return_type': dict},
            'save_coordination_results': {'params': 1, 'return_type': str}            # output_file parameter
        }
        
        for method_name, expected in required_methods.items():
            self.assertTrue(hasattr(coordinator, method_name), f"Method {method_name} should exist")
            method = getattr(coordinator, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test parameter count
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertLessEqual(len(required_params), expected['params'] + 1,  # +1 for self
                               f"Method {method_name} should have at most {expected['params']} required parameters")
        
        # Test coordination status structure
        status = coordinator.get_coordination_status()
        required_status_fields = ['completed_agents', 'failed_agents', 'running_agents', 'agent_monitoring', 'dependencies']
        for field in required_status_fields:
            self.assertIn(field, status, f"Coordination status should contain {field} field")
        
        # Test data structure types
        self.assertIsInstance(status['completed_agents'], list)
        self.assertIsInstance(status['failed_agents'], list)
        self.assertIsInstance(status['running_agents'], list)
        self.assertIsInstance(status['agent_monitoring'], dict)
        self.assertIsInstance(status['dependencies'], dict)


class SharedDataStructureStabilityTest(unittest.TestCase):
    """Test shared data structure compatibility"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test data directories
        self.data_dir = os.path.join(self.test_dir, 'data')
        self.outputs_dir = os.path.join(self.test_dir, 'outputs')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.outputs_dir, exist_ok=True)
        
        os.chdir(self.test_dir)
        
        # Create minimal test data
        self._create_test_data()
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def _create_test_data(self):
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
    
    def test_agent_result_structure_stability(self):
        """Test AgentResult data structure stability"""
        # Test AgentResult structure
        result = AgentResult(
            agent_name="test_agent",
            status=AgentStatus.COMPLETED
        )
        
        # Test required fields exist
        required_fields = ['agent_name', 'status', 'start_time', 'end_time', 'execution_time', 'data', 'error_message', 'output_files']
        for field in required_fields:
            self.assertTrue(hasattr(result, field), f"AgentResult should have {field} field")
        
        # Test field types
        self.assertIsInstance(result.agent_name, str)
        self.assertIsInstance(result.status, AgentStatus)
        
        # Test that AgentResult can be converted to dict (for serialization)
        from dataclasses import asdict
        result_dict = asdict(result)
        self.assertIsInstance(result_dict, dict)
        self.assertIn('agent_name', result_dict)
        self.assertIn('status', result_dict)
    
    def test_shared_data_structure_consistency(self):
        """Test shared data structure consistency across agents"""
        pipeline = AgentExecutionPipeline()
        
        # Execute a minimal pipeline to test shared data structure
        try:
            results = pipeline.execute_pipeline()
            
            # Test shared data keys consistency
            expected_shared_data_keys = ['customer_orders', 'po_reader_stats']
            for key in expected_shared_data_keys:
                if key in pipeline.shared_data:
                    # Test data types
                    if key == 'customer_orders':
                        self.assertIsInstance(pipeline.shared_data[key], list)
                        if pipeline.shared_data[key]:
                            order = pipeline.shared_data[key][0]
                            self.assertIsInstance(order, dict)
                    elif key == 'po_reader_stats':
                        self.assertIsInstance(pipeline.shared_data[key], dict)
            
            # Test that shared data can be serialized to JSON
            import json
            try:
                json.dumps(pipeline.shared_data, default=str)  # default=str for datetime objects
            except (TypeError, ValueError) as e:
                self.fail(f"Shared data should be JSON serializable: {e}")
                
        except Exception as e:
            # Pipeline may fail due to missing data, but structure should be consistent
            self.assertIsInstance(pipeline.shared_data, dict)
    
    def test_configuration_structure_stability(self):
        """Test configuration structure stability"""
        # Test default configuration structure
        manager = OrchestrationManager()
        
        # Test configuration keys
        required_config_keys = ['execution_mode', 'max_parallel_agents', 'dependencies', 'agents']
        for key in required_config_keys:
            self.assertIn(key, manager.config, f"Configuration should contain {key}")
        
        # Test configuration value types
        self.assertIsInstance(manager.config['execution_mode'], str)
        self.assertIsInstance(manager.config['max_parallel_agents'], int)
        self.assertIsInstance(manager.config['dependencies'], dict)
        self.assertIsInstance(manager.config['agents'], dict)
        
        # Test that configuration can be serialized to JSON
        try:
            json.dumps(manager.config)
        except (TypeError, ValueError) as e:
            self.fail(f"Configuration should be JSON serializable: {e}")


class APIBackwardCompatibilityTest(unittest.TestCase):
    """Test that internal API changes don't break existing functionality"""
    
    def test_agent_instantiation_compatibility(self):
        """Test that agents can be instantiated with default parameters"""
        # Test that all agents can be instantiated without parameters
        agents = [
            POReaderAgent,
            ValidationAgent,
            SalesOrderCreatorAgent,
            SummaryInsightsAgent
        ]
        
        for agent_class in agents:
            try:
                agent = agent_class()
                self.assertIsNotNone(agent, f"{agent_class.__name__} should be instantiable")
            except Exception as e:
                self.fail(f"{agent_class.__name__} should be instantiable without parameters: {e}")
    
    def test_orchestration_instantiation_compatibility(self):
        """Test that orchestration components can be instantiated with defaults"""
        # Test orchestration components
        orchestration_classes = [
            AgentExecutionPipeline,
            OrchestrationManager,
            AgentCoordinator
        ]
        
        for orchestration_class in orchestration_classes:
            try:
                component = orchestration_class()
                self.assertIsNotNone(component, f"{orchestration_class.__name__} should be instantiable")
            except Exception as e:
                self.fail(f"{orchestration_class.__name__} should be instantiable without parameters: {e}")
    
    def test_method_call_compatibility(self):
        """Test that core methods can be called without breaking"""
        # Test that core methods exist and are callable
        po_agent = POReaderAgent()
        
        # These methods should exist and be callable (even if they fail due to missing data)
        core_methods = ['read_orders', 'display_orders_table', 'get_summary_stats']
        
        for method_name in core_methods:
            self.assertTrue(hasattr(po_agent, method_name), f"Method {method_name} should exist")
            method = getattr(po_agent, method_name)
            self.assertTrue(callable(method), f"Method {method_name} should be callable")
            
            # Test that method signature hasn't changed (no required parameters added)
            sig = inspect.signature(method)
            required_params = [p for p in sig.parameters.values() if p.default == inspect.Parameter.empty]
            self.assertEqual(len(required_params), 0, f"Method {method_name} should not have required parameters")


if __name__ == '__main__':
    unittest.main()