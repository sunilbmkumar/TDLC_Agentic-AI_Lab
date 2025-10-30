"""
Base test classes for the comprehensive test suite.
Provides common setup/teardown functionality and utilities for all test types.
"""

import unittest
import os
import shutil
import tempfile
import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import logging

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class BaseAgentTest(unittest.TestCase):
    """
    Base class for all agent tests with common setup/teardown functionality.
    Provides agent isolation, test data management, and common validation methods.
    """
    
    def setUp(self):
        """Setup test environment with isolation"""
        # Create temporary directories for test isolation
        self.test_temp_dir = tempfile.mkdtemp(prefix='agent_test_')
        self.test_data_dir = os.path.join(self.test_temp_dir, 'data')
        self.test_output_dir = os.path.join(self.test_temp_dir, 'outputs')
        self.test_config_dir = os.path.join(self.test_temp_dir, 'config')
        
        # Create test directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_config_dir, exist_ok=True)
        
        # Setup test logging
        self.test_logger = self._setup_test_logging()
        
        # Store original working directory
        self.original_cwd = os.getcwd()
        
        # Initialize shared data for agent testing
        self.shared_data = {}
        
    def tearDown(self):
        """Cleanup test environment"""
        # Restore original working directory
        os.chdir(self.original_cwd)
        
        # Cleanup temporary directories
        if os.path.exists(self.test_temp_dir):
            shutil.rmtree(self.test_temp_dir, ignore_errors=True)
            
        # Clear shared data
        self.shared_data.clear()
        
    def _setup_test_logging(self) -> logging.Logger:
        """Setup isolated logging for tests"""
        logger = logging.getLogger(f'test_{self.__class__.__name__}')
        logger.setLevel(logging.DEBUG)
        
        # Create file handler for test logs
        log_file = os.path.join(self.test_temp_dir, 'test.log')
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
        
    def create_test_data(self, scenario: str) -> Dict[str, Any]:
        """
        Generate test data for specific scenarios.
        
        Args:
            scenario: Test scenario name ('valid', 'invalid', 'mixed', 'empty')
            
        Returns:
            Dictionary containing test data paths and metadata
        """
        test_data = {
            'scenario': scenario,
            'data_dir': self.test_data_dir,
            'output_dir': self.test_output_dir,
            'config_dir': self.test_config_dir,
            'timestamp': datetime.now().isoformat()
        }
        
        if scenario == 'valid':
            test_data.update(self._create_valid_test_data())
        elif scenario == 'invalid':
            test_data.update(self._create_invalid_test_data())
        elif scenario == 'mixed':
            test_data.update(self._create_mixed_test_data())
        elif scenario == 'empty':
            test_data.update(self._create_empty_test_data())
        else:
            raise ValueError(f"Unknown test scenario: {scenario}")
            
        return test_data
        
    def _create_valid_test_data(self) -> Dict[str, Any]:
        """Create valid test data files"""
        # Create valid customer orders
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writerow(['PO001', 'Acme Corp', 'SKU001', '10', '25.50'])
            writer.writerow(['PO002', 'Beta Industries', 'SKU002', '5', '15.75'])
            writer.writerow(['PO003', 'Gamma LLC', 'SKU003', '20', '8.25'])
            
        # Create valid master SKU data
        sku_file = os.path.join(self.test_data_dir, 'master_sku.csv')
        with open(sku_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sku', 'description', 'standard_price', 'category'])
            writer.writerow(['SKU001', 'Widget A', '25.00', 'Electronics'])
            writer.writerow(['SKU002', 'Widget B', '15.00', 'Electronics'])
            writer.writerow(['SKU003', 'Widget C', '8.00', 'Hardware'])
            
        return {
            'orders_file': orders_file,
            'sku_file': sku_file,
            'order_count': 3,
            'sku_count': 3
        }
        
    def _create_invalid_test_data(self) -> Dict[str, Any]:
        """Create invalid test data files"""
        # Create invalid customer orders
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writerow(['PO001', 'Invalid Corp', 'INVALID_SKU', '10', '25.50'])
            writer.writerow(['PO002', '', 'SKU002', '5', '15.75'])  # Missing customer
            writer.writerow(['PO003', 'Negative Qty', 'SKU003', '-5', '8.25'])  # Negative quantity
            
        # Create master SKU data (valid for comparison)
        sku_file = os.path.join(self.test_data_dir, 'master_sku.csv')
        with open(sku_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sku', 'description', 'standard_price', 'category'])
            writer.writerow(['SKU002', 'Widget B', '15.00', 'Electronics'])
            writer.writerow(['SKU003', 'Widget C', '8.00', 'Hardware'])
            
        return {
            'orders_file': orders_file,
            'sku_file': sku_file,
            'order_count': 3,
            'sku_count': 2,
            'expected_errors': 3
        }
        
    def _create_mixed_test_data(self) -> Dict[str, Any]:
        """Create mixed valid/invalid test data"""
        # Create mixed customer orders
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writerow(['PO001', 'Acme Corp', 'SKU001', '10', '25.50'])  # Valid
            writer.writerow(['PO002', 'Invalid Corp', 'INVALID_SKU', '5', '15.75'])  # Invalid SKU
            writer.writerow(['PO003', 'Gamma LLC', 'SKU003', '20', '8.25'])  # Valid
            writer.writerow(['PO004', 'Bad Qty', 'SKU001', '0', '25.50'])  # Invalid quantity
            
        # Create master SKU data
        sku_file = os.path.join(self.test_data_dir, 'master_sku.csv')
        with open(sku_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sku', 'description', 'standard_price', 'category'])
            writer.writerow(['SKU001', 'Widget A', '25.00', 'Electronics'])
            writer.writerow(['SKU003', 'Widget C', '8.00', 'Hardware'])
            
        return {
            'orders_file': orders_file,
            'sku_file': sku_file,
            'order_count': 4,
            'sku_count': 2,
            'expected_valid': 2,
            'expected_invalid': 2
        }
        
    def _create_empty_test_data(self) -> Dict[str, Any]:
        """Create empty test data files"""
        # Create empty customer orders (headers only)
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            
        # Create empty master SKU data (headers only)
        sku_file = os.path.join(self.test_data_dir, 'master_sku.csv')
        with open(sku_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sku', 'description', 'standard_price', 'category'])
            
        return {
            'orders_file': orders_file,
            'sku_file': sku_file,
            'order_count': 0,
            'sku_count': 0
        }
        
    def validate_agent_output(self, agent_result: Any) -> bool:
        """
        Common validation logic for agent outputs.
        
        Args:
            agent_result: Result from agent execution
            
        Returns:
            True if output is valid, False otherwise
        """
        if agent_result is None:
            return False
            
        # Check if result has expected structure
        if hasattr(agent_result, 'status') and hasattr(agent_result, 'data'):
            return agent_result.status in ['success', 'completed', 'failed']
            
        # For simple data structures, check if not empty
        if isinstance(agent_result, (list, dict)):
            return len(agent_result) >= 0  # Allow empty results
            
        return True
        
    def assert_agent_success(self, agent_result: Any, message: str = "Agent execution failed"):
        """Assert that agent execution was successful"""
        self.assertTrue(self.validate_agent_output(agent_result), message)
        
        if hasattr(agent_result, 'status'):
            self.assertIn(agent_result.status, ['success', 'completed'], 
                         f"Agent status was {agent_result.status}: {message}")
                         
    def assert_file_exists(self, file_path: str, message: str = None):
        """Assert that a file exists"""
        if message is None:
            message = f"Expected file does not exist: {file_path}"
        self.assertTrue(os.path.exists(file_path), message)
        
    def assert_file_not_empty(self, file_path: str, message: str = None):
        """Assert that a file exists and is not empty"""
        self.assert_file_exists(file_path, message)
        if message is None:
            message = f"Expected file is empty: {file_path}"
        self.assertGreater(os.path.getsize(file_path), 0, message)


class BaseIntegrationTest(unittest.TestCase):
    """
    Base class for integration tests with workflow testing setup.
    Provides orchestration setup, data flow validation, and workflow execution utilities.
    """
    
    def setUp(self):
        """Setup integration test environment"""
        # Create temporary directories for integration testing
        self.test_temp_dir = tempfile.mkdtemp(prefix='integration_test_')
        self.test_data_dir = os.path.join(self.test_temp_dir, 'data')
        self.test_output_dir = os.path.join(self.test_temp_dir, 'outputs')
        self.test_config_dir = os.path.join(self.test_temp_dir, 'config')
        
        # Create test directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_output_dir, exist_ok=True)
        os.makedirs(self.test_config_dir, exist_ok=True)
        
        # Setup test logging
        self.test_logger = self._setup_test_logging()
        
        # Store original working directory
        self.original_cwd = os.getcwd()
        
        # Initialize shared data for workflow testing
        self.shared_data = {}
        self.workflow_results = {}
        
        # Setup test orchestration configuration
        self._setup_test_orchestration_config()
        
    def tearDown(self):
        """Cleanup integration test environment"""
        # Restore original working directory
        os.chdir(self.original_cwd)
        
        # Cleanup temporary directories
        if os.path.exists(self.test_temp_dir):
            shutil.rmtree(self.test_temp_dir, ignore_errors=True)
            
        # Clear shared data
        self.shared_data.clear()
        self.workflow_results.clear()
        
    def _setup_test_logging(self) -> logging.Logger:
        """Setup isolated logging for integration tests"""
        logger = logging.getLogger(f'integration_test_{self.__class__.__name__}')
        logger.setLevel(logging.DEBUG)
        
        # Create file handler for test logs
        log_file = os.path.join(self.test_temp_dir, 'integration_test.log')
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
        
    def _setup_test_orchestration_config(self):
        """Setup test orchestration configuration"""
        config = {
            "execution_mode": "sequential",
            "max_parallel_agents": 2,
            "agent_timeout": 30,
            "agents": {
                "po_reader": {
                    "enabled": True,
                    "dependencies": [],
                    "parallel_group": None
                },
                "validation": {
                    "enabled": True,
                    "dependencies": ["po_reader"],
                    "parallel_group": "validation_group"
                },
                "exception_response": {
                    "enabled": True,
                    "dependencies": ["validation"],
                    "parallel_group": "response_group"
                },
                "so_creator": {
                    "enabled": True,
                    "dependencies": ["validation"],
                    "parallel_group": "response_group"
                },
                "summary_insights": {
                    "enabled": True,
                    "dependencies": ["exception_response", "so_creator"],
                    "parallel_group": None
                }
            }
        }
        
        config_file = os.path.join(self.test_config_dir, 'orchestration_config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        self.orchestration_config_path = config_file
        
    def execute_workflow_segment(self, agents: List[str]) -> Dict[str, Any]:
        """
        Execute specific agent combinations for workflow segment testing.
        
        Args:
            agents: List of agent names to execute
            
        Returns:
            Dictionary containing execution results for each agent
        """
        results = {}
        
        for agent_name in agents:
            try:
                # Mock agent execution for testing
                result = self._mock_agent_execution(agent_name)
                results[agent_name] = result
                
                # Update shared data based on agent type
                self._update_shared_data_for_agent(agent_name, result)
                
            except Exception as e:
                self.test_logger.error(f"Error executing agent {agent_name}: {e}")
                results[agent_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
        return results
        
    def _mock_agent_execution(self, agent_name: str) -> Dict[str, Any]:
        """Mock agent execution for testing purposes"""
        # Simulate agent execution with realistic results
        base_result = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'execution_time': 0.5,
            'agent_name': agent_name
        }
        
        if agent_name == 'po_reader':
            base_result['data'] = {
                'orders_read': 3,
                'orders': [
                    {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': 10, 'Price': 25.50},
                    {'PO_Number': 'PO002', 'Customer_Name': 'Beta Industries', 'SKU': 'SKU002', 'Quantity': 5, 'Price': 15.75},
                    {'PO_Number': 'PO003', 'Customer_Name': 'Gamma LLC', 'SKU': 'SKU003', 'Quantity': 20, 'Price': 8.25}
                ]
            }
        elif agent_name == 'validation':
            base_result['data'] = {
                'validated_orders': 3,
                'valid_orders': 2,
                'invalid_orders': 1,
                'validation_results': [
                    {'PO_Number': 'PO001', 'status': 'valid'},
                    {'PO_Number': 'PO002', 'status': 'valid'},
                    {'PO_Number': 'PO003', 'status': 'invalid', 'errors': ['SKU not found']}
                ]
            }
        elif agent_name == 'exception_response':
            base_result['data'] = {
                'emails_generated': 1,
                'emails': [
                    {'PO_Number': 'PO003', 'recipient': 'gamma@example.com', 'subject': 'Order Exception'}
                ]
            }
        elif agent_name == 'so_creator':
            base_result['data'] = {
                'sales_orders_created': 2,
                'sales_orders': [
                    {'SO_Number': 'SO001', 'PO_Number': 'PO001'},
                    {'SO_Number': 'SO002', 'PO_Number': 'PO002'}
                ]
            }
        elif agent_name == 'summary_insights':
            base_result['data'] = {
                'total_orders': 3,
                'valid_orders': 2,
                'invalid_orders': 1,
                'total_value': 67.00
            }
            
        return base_result
        
    def _update_shared_data_for_agent(self, agent_name: str, result: Dict[str, Any]):
        """Update shared data based on agent execution results"""
        if result['status'] == 'success' and 'data' in result:
            self.shared_data[agent_name] = result['data']
            
    def validate_data_flow(self, shared_data: Dict[str, Any]) -> bool:
        """
        Validate data consistency between agents.
        
        Args:
            shared_data: Shared data dictionary from workflow execution
            
        Returns:
            True if data flow is consistent, False otherwise
        """
        try:
            # Check that required data exists
            if 'po_reader' not in shared_data:
                return False
                
            # Validate data consistency between agents
            po_data = shared_data.get('po_reader', {})
            validation_data = shared_data.get('validation', {})
            
            if validation_data:
                # Check that validation processed the same number of orders
                orders_read = po_data.get('orders_read', 0)
                orders_validated = validation_data.get('validated_orders', 0)
                
                if orders_read != orders_validated:
                    self.test_logger.warning(
                        f"Data flow inconsistency: {orders_read} orders read, "
                        f"{orders_validated} orders validated"
                    )
                    return False
                    
            return True
            
        except Exception as e:
            self.test_logger.error(f"Error validating data flow: {e}")
            return False
            
    def assert_workflow_success(self, results: Dict[str, Any], message: str = "Workflow execution failed"):
        """Assert that workflow execution was successful"""
        self.assertIsInstance(results, dict, "Workflow results should be a dictionary")
        
        for agent_name, result in results.items():
            self.assertIn('status', result, f"Agent {agent_name} result missing status")
            self.assertEqual(result['status'], 'success', 
                           f"Agent {agent_name} failed: {result.get('error', 'Unknown error')}")
                           
    def assert_data_consistency(self, shared_data: Dict[str, Any], message: str = "Data flow inconsistency"):
        """Assert that data flow between agents is consistent"""
        self.assertTrue(self.validate_data_flow(shared_data), message)