"""
Example unit test to verify test infrastructure functionality.
This test demonstrates the base test classes and data generation capabilities.
"""

import unittest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from test_suite.utilities.test_data_generator import TestDataGenerator


class TestInfrastructureExample(BaseAgentTest):
    """Example test class demonstrating infrastructure functionality"""
    
    def test_valid_data_generation(self):
        """Test that valid test data can be generated"""
        test_data = self.create_test_data('valid')
        
        # Verify test data structure
        self.assertIn('scenario', test_data)
        self.assertEqual(test_data['scenario'], 'valid')
        self.assertIn('orders_file', test_data)
        self.assertIn('sku_file', test_data)
        
        # Verify files were created
        self.assert_file_exists(test_data['orders_file'])
        self.assert_file_exists(test_data['sku_file'])
        self.assert_file_not_empty(test_data['orders_file'])
        self.assert_file_not_empty(test_data['sku_file'])
        
    def test_invalid_data_generation(self):
        """Test that invalid test data can be generated"""
        test_data = self.create_test_data('invalid')
        
        # Verify test data structure
        self.assertEqual(test_data['scenario'], 'invalid')
        self.assertIn('expected_errors', test_data)
        self.assertGreater(test_data['expected_errors'], 0)
        
        # Verify files were created
        self.assert_file_exists(test_data['orders_file'])
        self.assert_file_exists(test_data['sku_file'])
        
    def test_mixed_data_generation(self):
        """Test that mixed valid/invalid test data can be generated"""
        test_data = self.create_test_data('mixed')
        
        # Verify test data structure
        self.assertEqual(test_data['scenario'], 'mixed')
        self.assertIn('expected_valid', test_data)
        self.assertIn('expected_invalid', test_data)
        self.assertGreater(test_data['expected_valid'], 0)
        self.assertGreater(test_data['expected_invalid'], 0)
        
    def test_empty_data_generation(self):
        """Test that empty test data can be generated"""
        test_data = self.create_test_data('empty')
        
        # Verify test data structure
        self.assertEqual(test_data['scenario'], 'empty')
        self.assertEqual(test_data['order_count'], 0)
        self.assertEqual(test_data['sku_count'], 0)
        
        # Files should still exist but be empty (headers only)
        self.assert_file_exists(test_data['orders_file'])
        self.assert_file_exists(test_data['sku_file'])
        
    def test_data_generator_scenarios(self):
        """Test TestDataGenerator scenario creation"""
        generator = TestDataGenerator(self.test_data_dir)
        
        # Test normal flow scenario
        normal_dataset = generator.create_scenario_dataset('normal_flow')
        self.assertIn('orders', normal_dataset)
        self.assertIn('master_sku', normal_dataset)
        self.assertIn('scenario_info', normal_dataset)
        
        scenario_info = normal_dataset['scenario_info']
        self.assertEqual(scenario_info['name'], 'normal_flow')
        self.assertGreater(scenario_info['expected_valid_orders'], 0)
        self.assertEqual(scenario_info['expected_invalid_orders'], 0)
        
    def test_agent_output_validation(self):
        """Test agent output validation methods"""
        # Test valid outputs
        valid_result = {'status': 'success', 'data': {'orders': 5}}
        self.assertTrue(self.validate_agent_output(valid_result))
        
        # Test invalid outputs
        self.assertFalse(self.validate_agent_output(None))
        
        # Test list/dict outputs
        self.assertTrue(self.validate_agent_output([1, 2, 3]))
        self.assertTrue(self.validate_agent_output({'key': 'value'}))
        self.assertTrue(self.validate_agent_output([]))  # Empty is valid
        
    def test_test_environment_isolation(self):
        """Test that test environment is properly isolated"""
        # Verify temporary directories exist
        self.assertTrue(os.path.exists(self.test_temp_dir))
        self.assertTrue(os.path.exists(self.test_data_dir))
        self.assertTrue(os.path.exists(self.test_output_dir))
        self.assertTrue(os.path.exists(self.test_config_dir))
        
        # Verify logger is setup
        self.assertIsNotNone(self.test_logger)
        
        # Verify shared data is initialized
        self.assertIsInstance(self.shared_data, dict)
        self.assertEqual(len(self.shared_data), 0)


class TestDataGeneratorUnit(unittest.TestCase):
    """Unit tests for TestDataGenerator class"""
    
    def setUp(self):
        """Setup test environment"""
        import tempfile
        self.test_dir = tempfile.mkdtemp(prefix='data_gen_test_')
        self.generator = TestDataGenerator(self.test_dir)
        
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def test_generate_valid_orders(self):
        """Test valid order generation"""
        orders = self.generator.generate_valid_orders(5)
        
        self.assertEqual(len(orders), 5)
        
        for order in orders:
            self.assertIn('PO_Number', order)
            self.assertIn('Customer_Name', order)
            self.assertIn('SKU', order)
            self.assertIn('Quantity', order)
            self.assertIn('Price', order)
            
            # Validate data types and ranges
            self.assertIsInstance(order['Quantity'], int)
            self.assertGreater(order['Quantity'], 0)
            self.assertIsInstance(order['Price'], float)
            self.assertGreater(order['Price'], 0)
            
    def test_generate_invalid_orders(self):
        """Test invalid order generation"""
        error_types = ['invalid_sku', 'negative_quantity', 'missing_customer']
        orders = self.generator.generate_invalid_orders(error_types)
        
        self.assertEqual(len(orders), 3)
        
        # Check that each order has the expected error
        self.assertEqual(orders[0]['SKU'], 'INVALID_SKU')
        self.assertLess(orders[1]['Quantity'], 0)
        self.assertEqual(orders[2]['Customer_Name'], '')
        
    def test_generate_master_sku_data(self):
        """Test master SKU data generation"""
        skus = ['SKU001', 'SKU002', 'SKU003']
        sku_data = self.generator.generate_master_sku_data(skus)
        
        self.assertEqual(len(sku_data), 3)
        
        for i, sku_record in enumerate(sku_data):
            self.assertEqual(sku_record['sku'], skus[i])
            self.assertIn('description', sku_record)
            self.assertIn('standard_price', sku_record)
            self.assertIn('category', sku_record)
            self.assertIsInstance(sku_record['standard_price'], float)
            self.assertGreater(sku_record['standard_price'], 0)
            
    def test_scenario_dataset_creation(self):
        """Test scenario dataset creation"""
        scenarios = ['normal_flow', 'exception_flow', 'mixed_scenario', 'empty_dataset']
        
        for scenario in scenarios:
            dataset = self.generator.create_scenario_dataset(scenario)
            
            self.assertIn('orders', dataset)
            self.assertIn('master_sku', dataset)
            self.assertIn('scenario_info', dataset)
            
            scenario_info = dataset['scenario_info']
            self.assertEqual(scenario_info['name'], scenario)
            self.assertIn('description', scenario_info)
            
    def test_save_dataset_to_files(self):
        """Test saving dataset to CSV files"""
        dataset = self.generator.create_scenario_dataset('normal_flow')
        file_paths = self.generator.save_dataset_to_files(dataset, self.test_dir)
        
        # Verify files were created
        self.assertIn('orders_file', file_paths)
        self.assertIn('sku_file', file_paths)
        self.assertIn('info_file', file_paths)
        
        for file_path in file_paths.values():
            self.assertTrue(os.path.exists(file_path))
            
        # Verify JSON info file
        import json
        with open(file_paths['info_file'], 'r') as f:
            info = json.load(f)
            self.assertEqual(info['name'], 'normal_flow')


if __name__ == '__main__':
    unittest.main()