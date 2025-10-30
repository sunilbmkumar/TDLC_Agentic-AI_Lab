"""
Unit tests for Validation Agent.
Tests SKU validation, price deviation checks, quantity validation, and validation result generation.
"""

import unittest
import os
import sys
import csv
import json
import tempfile
from unittest.mock import patch, mock_open

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from agents.validation.agent import ValidationAgent


class TestValidationAgent(BaseAgentTest):
    """Unit tests for Validation Agent functionality"""
    
    def setUp(self):
        """Setup test environment for Validation Agent tests"""
        super().setUp()
        self.agent = ValidationAgent()
        
    def create_test_orders_file(self, orders_data):
        """Helper method to create test orders CSV file"""
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writeheader()
            writer.writerows(orders_data)
        return orders_file
        
    def create_test_sku_file(self, sku_data):
        """Helper method to create test master SKU CSV file"""
        sku_file = os.path.join(self.test_data_dir, 'master_sku.csv')
        with open(sku_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['SKU', 'Description', 'Reference_Price', 'Category'])
            writer.writeheader()
            writer.writerows(sku_data)
        return sku_file
        
    def test_read_customer_orders_success(self):
        """Test successful reading of customer orders"""
        orders_data = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': '10', 'Price': '25.50'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc', 'SKU': 'SKU002', 'Quantity': '5', 'Price': '15.75'}
        ]
        orders_file = self.create_test_orders_file(orders_data)
        
        orders = self.agent.read_customer_orders(orders_file)
        
        # Verify orders were read correctly
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0]['PO_Number'], 'PO001')
        self.assertEqual(orders[0]['Quantity'], 10)  # Should be converted to int
        self.assertEqual(orders[0]['Price'], 25.50)  # Should be converted to float
        
    def test_read_customer_orders_file_not_found(self):
        """Test handling of missing customer orders file"""
        orders = self.agent.read_customer_orders("nonexistent_file.csv")
        
        self.assertEqual(orders, [])
        self.assertEqual(len(self.agent.customer_orders), 0)
        
    def test_read_customer_orders_invalid_format(self):
        """Test handling of invalid CSV format"""
        # Create invalid CSV file
        invalid_file = os.path.join(self.test_data_dir, 'invalid_orders.csv')
        with open(invalid_file, 'w') as f:
            f.write("Invalid CSV content\n")
            f.write("Not,Proper,Format\n")
            
        orders = self.agent.read_customer_orders(invalid_file)
        
        # Should handle error gracefully
        self.assertEqual(orders, [])
        
    def test_read_master_skus_success(self):
        """Test successful reading of master SKU data"""
        sku_data = [
            {'SKU': 'SKU001', 'Description': 'Widget A', 'Reference_Price': '25.00', 'Category': 'Electronics'},
            {'SKU': 'SKU002', 'Description': 'Widget B', 'Reference_Price': '15.00', 'Category': 'Hardware'}
        ]
        sku_file = self.create_test_sku_file(sku_data)
        
        skus = self.agent.read_master_skus(sku_file)
        
        # Verify SKUs were read correctly
        self.assertEqual(len(skus), 2)
        self.assertIn('SKU001', skus)
        self.assertIn('SKU002', skus)
        self.assertEqual(skus['SKU001']['Reference_Price'], 25.00)  # Should be converted to float
        
    def test_read_master_skus_file_not_found(self):
        """Test handling of missing master SKU file"""
        skus = self.agent.read_master_skus("nonexistent_file.csv")
        
        self.assertEqual(skus, {})
        self.assertEqual(len(self.agent.master_skus), 0)
        
    def test_validate_sku_existence_valid(self):
        """Test SKU existence validation for valid SKUs"""
        # Setup master SKU data
        self.agent.master_skus = {
            'SKU001': {'Description': 'Widget A', 'Reference_Price': 25.00},
            'SKU002': {'Description': 'Widget B', 'Reference_Price': 15.00}
        }
        
        # Test valid SKU
        is_valid, message = self.agent.validate_sku_existence('SKU001')
        
        self.assertTrue(is_valid)
        self.assertIn('SKU001 found in master data', message)
        
    def test_validate_sku_existence_invalid(self):
        """Test SKU existence validation for invalid SKUs"""
        # Setup master SKU data
        self.agent.master_skus = {
            'SKU001': {'Description': 'Widget A', 'Reference_Price': 25.00}
        }
        
        # Test invalid SKU
        is_valid, message = self.agent.validate_sku_existence('INVALID_SKU')
        
        self.assertFalse(is_valid)
        self.assertIn('INVALID_SKU not found in master data', message)
        
    def test_check_price_deviation_within_threshold(self):
        """Test price deviation check within acceptable threshold"""
        order_price = 25.50
        reference_price = 25.00
        threshold = 0.10  # 10%
        
        exceeds_threshold, deviation_percent = self.agent.check_price_deviation(
            order_price, reference_price, threshold
        )
        
        self.assertFalse(exceeds_threshold)
        self.assertAlmostEqual(deviation_percent, 2.0, places=1)  # 2% deviation
        
    def test_check_price_deviation_exceeds_threshold(self):
        """Test price deviation check exceeding threshold"""
        order_price = 30.00
        reference_price = 25.00
        threshold = 0.10  # 10%
        
        exceeds_threshold, deviation_percent = self.agent.check_price_deviation(
            order_price, reference_price, threshold
        )
        
        self.assertTrue(exceeds_threshold)
        self.assertAlmostEqual(deviation_percent, 20.0, places=1)  # 20% deviation
        
    def test_check_price_deviation_exact_match(self):
        """Test price deviation check with exact price match"""
        order_price = 25.00
        reference_price = 25.00
        threshold = 0.10
        
        exceeds_threshold, deviation_percent = self.agent.check_price_deviation(
            order_price, reference_price, threshold
        )
        
        self.assertFalse(exceeds_threshold)
        self.assertEqual(deviation_percent, 0.0)
        
    def test_check_price_deviation_lower_price(self):
        """Test price deviation check with lower order price"""
        order_price = 20.00
        reference_price = 25.00
        threshold = 0.10  # 10%
        
        exceeds_threshold, deviation_percent = self.agent.check_price_deviation(
            order_price, reference_price, threshold
        )
        
        self.assertTrue(exceeds_threshold)
        self.assertAlmostEqual(deviation_percent, 20.0, places=1)  # 20% deviation
        
    def test_validate_price_deviation_within_threshold(self):
        """Test price deviation validation within threshold"""
        order_price = 25.50
        reference_price = 25.00
        sku = 'SKU001'
        threshold = 0.10
        
        is_valid, message = self.agent.validate_price_deviation(
            order_price, reference_price, sku, threshold
        )
        
        self.assertTrue(is_valid)
        self.assertIn('within acceptable range', message)
        self.assertIn('SKU001', message)
        
    def test_validate_price_deviation_exceeds_threshold(self):
        """Test price deviation validation exceeding threshold"""
        order_price = 30.00
        reference_price = 25.00
        sku = 'SKU001'
        threshold = 0.10
        
        is_valid, message = self.agent.validate_price_deviation(
            order_price, reference_price, sku, threshold
        )
        
        self.assertFalse(is_valid)
        self.assertIn('exceeds 10.0% threshold', message)
        self.assertIn('SKU001', message)
        
    def test_determine_validation_status_valid_order(self):
        """Test validation status determination for valid order"""
        # Setup test data
        self.agent.master_skus = {
            'SKU001': {'Reference_Price': 25.00}
        }
        
        order = {
            'PO_Number': 'PO001',
            'SKU': 'SKU001',
            'Price': 25.50  # Within 10% threshold
        }
        
        result = self.agent.determine_validation_status(order)
        
        # Verify validation result
        self.assertEqual(result['PO_Number'], 'PO001')
        self.assertEqual(result['SKU'], 'SKU001')
        self.assertEqual(result['Status'], 'Valid')
        self.assertIsInstance(result['Reasons'], list)
        self.assertGreater(len(result['Reasons']), 0)
        self.assertEqual(result['Details']['order_price'], 25.50)
        self.assertEqual(result['Details']['reference_price'], 25.00)
        
    def test_determine_validation_status_invalid_sku(self):
        """Test validation status determination for invalid SKU"""
        # Setup test data with limited SKUs
        self.agent.master_skus = {
            'SKU001': {'Reference_Price': 25.00}
        }
        
        order = {
            'PO_Number': 'PO002',
            'SKU': 'INVALID_SKU',
            'Price': 25.50
        }
        
        result = self.agent.determine_validation_status(order)
        
        # Verify validation result
        self.assertEqual(result['Status'], 'Exception')
        self.assertIn('INVALID_SKU not found in master data', result['Reasons'][0])
        self.assertIsNone(result['Details']['reference_price'])
        
    def test_determine_validation_status_price_deviation(self):
        """Test validation status determination for price deviation"""
        # Setup test data
        self.agent.master_skus = {
            'SKU001': {'Reference_Price': 25.00}
        }
        
        order = {
            'PO_Number': 'PO003',
            'SKU': 'SKU001',
            'Price': 35.00  # 40% deviation, exceeds 10% threshold
        }
        
        result = self.agent.determine_validation_status(order)
        
        # Verify validation result
        self.assertEqual(result['Status'], 'Exception')
        self.assertIn('exceeds 10.0% threshold', result['Reasons'][0])
        self.assertEqual(result['Details']['reference_price'], 25.00)
        self.assertAlmostEqual(result['Details']['price_deviation'], 40.0, places=1)
        
    def test_run_validation_engine_mixed_results(self):
        """Test complete validation engine with mixed valid/invalid orders"""
        # Setup test data files
        orders_data = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': '10', 'Price': '25.50'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc', 'SKU': 'INVALID_SKU', 'Quantity': '5', 'Price': '15.75'},
            {'PO_Number': 'PO003', 'Customer_Name': 'Gamma LLC', 'SKU': 'SKU001', 'Quantity': '8', 'Price': '35.00'}
        ]
        orders_file = self.create_test_orders_file(orders_data)
        
        sku_data = [
            {'SKU': 'SKU001', 'Description': 'Widget A', 'Reference_Price': '25.00', 'Category': 'Electronics'}
        ]
        sku_file = self.create_test_sku_file(sku_data)
        
        # Mock file paths
        with patch.object(self.agent, 'read_customer_orders') as mock_read_orders, \
             patch.object(self.agent, 'read_master_skus') as mock_read_skus:
            
            mock_read_orders.return_value = [
                {'PO_Number': 'PO001', 'SKU': 'SKU001', 'Price': 25.50},
                {'PO_Number': 'PO002', 'SKU': 'INVALID_SKU', 'Price': 15.75},
                {'PO_Number': 'PO003', 'SKU': 'SKU001', 'Price': 35.00}
            ]
            mock_read_skus.return_value = {'SKU001': {'Reference_Price': 25.00}}
            
            results = self.agent.run_validation_engine()
            
        # Verify results
        self.assertEqual(len(results), 3)
        
        # Check individual results
        valid_results = [r for r in results if r['Status'] == 'Valid']
        exception_results = [r for r in results if r['Status'] == 'Exception']
        
        self.assertEqual(len(valid_results), 1)  # PO001 should be valid
        self.assertEqual(len(exception_results), 2)  # PO002 and PO003 should be exceptions
        
    def test_generate_simple_json_output(self):
        """Test generation of simple JSON output format"""
        # Setup validation results
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'}
        ]
        
        simple_output = self.agent.generate_simple_json_output()
        
        # Verify output format
        self.assertEqual(len(simple_output), 3)
        for result in simple_output:
            self.assertIn('PO_Number', result)
            self.assertIn('Status', result)
            self.assertIn(result['Status'], ['Valid', 'Exception'])
            
    def test_generate_detailed_json_output(self):
        """Test generation of detailed JSON output format"""
        # Setup validation results
        test_results = [
            {
                'PO_Number': 'PO001',
                'Status': 'Valid',
                'Reasons': ['Price within acceptable range'],
                'Details': {'order_price': 25.50, 'reference_price': 25.00}
            }
        ]
        self.agent.validation_results = test_results
        
        detailed_output = self.agent.generate_detailed_json_output()
        
        # Verify output is the same as validation_results
        self.assertEqual(detailed_output, test_results)
        
    def test_save_validation_results(self):
        """Test saving validation results to JSON files"""
        # Setup validation results
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'}
        ]
        
        simple_file, detailed_file = self.agent.save_validation_results(self.test_output_dir)
        
        # Verify files were created
        self.assert_file_exists(simple_file)
        self.assert_file_exists(detailed_file)
        
        # Verify file contents
        with open(simple_file, 'r') as f:
            simple_data = json.load(f)
        with open(detailed_file, 'r') as f:
            detailed_data = json.load(f)
            
        self.assertEqual(len(simple_data), 2)
        self.assertEqual(len(detailed_data), 2)
        self.assertEqual(simple_data[0]['PO_Number'], 'PO001')
        
    def test_generate_validation_explanations(self):
        """Test generation of validation explanations"""
        # Setup validation results
        self.agent.validation_results = [
            {
                'PO_Number': 'PO001',
                'SKU': 'SKU001',
                'Status': 'Valid',
                'Reasons': ['Price deviation of 2.0% is within acceptable range for SKU001'],
                'Details': {'reference_price': 25.00, 'price_deviation': 2.0}
            },
            {
                'PO_Number': 'PO002',
                'SKU': 'INVALID_SKU',
                'Status': 'Exception',
                'Reasons': ['SKU INVALID_SKU not found in master data'],
                'Details': {'reference_price': None}
            },
            {
                'PO_Number': 'PO003',
                'SKU': 'SKU001',
                'Status': 'Exception',
                'Reasons': ['Price deviation of 40.0% exceeds 10% threshold for SKU001'],
                'Details': {'reference_price': 25.00, 'price_deviation': 40.0}
            }
        ]
        
        explanations = self.agent.generate_validation_explanations()
        
        # Verify explanations
        self.assertEqual(len(explanations), 3)
        self.assertIn('PO001 passed validation', explanations[0])
        self.assertIn('PO002 failed validation', explanations[1])
        self.assertIn('PO003 failed validation', explanations[2])
        
    def test_get_validation_summary(self):
        """Test generation of validation summary"""
        # Setup validation results
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'}
        ]
        
        summary = self.agent.get_validation_summary()
        
        # Verify summary structure
        self.assertIn('total_orders', summary)
        self.assertIn('valid_orders', summary)
        self.assertIn('exception_orders', summary)
        self.assertIn('explanations', summary)
        self.assertIn('detailed_results', summary)
        
        # Verify summary values
        self.assertEqual(summary['total_orders'], 3)
        self.assertEqual(summary['valid_orders'], 2)
        self.assertEqual(summary['exception_orders'], 1)
        
    def test_display_validation_reasoning(self):
        """Test display of validation reasoning output"""
        # Setup validation results
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'}
        ]
        
        # Capture output
        with patch('builtins.print') as mock_print:
            self.agent.display_validation_reasoning()
            
        # Verify print was called with validation content
        self.assertTrue(mock_print.called)
        
        # Check that validation reasoning was displayed
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        output_content = '\n'.join(print_calls)
        
        self.assertIn('VALIDATION AGENT REASONING', output_content)
        self.assertIn('Processing', output_content)
        self.assertIn('VALIDATION SUMMARY', output_content)
        
    def test_cross_reference_skus(self):
        """Test cross-referencing SKUs between orders and master data"""
        # Setup test data
        self.agent.customer_orders = [
            {'SKU': 'SKU001', 'PO_Number': 'PO001'},
            {'SKU': 'SKU002', 'PO_Number': 'PO002'},
            {'SKU': 'INVALID_SKU', 'PO_Number': 'PO003'}
        ]
        
        self.agent.master_skus = {
            'SKU001': {'Reference_Price': 25.00},
            'SKU002': {'Reference_Price': 15.00}
        }
        
        cross_referenced = self.agent.cross_reference_skus()
        
        # Verify cross-reference results
        self.assertEqual(len(cross_referenced), 3)
        
        # Check first order (should have master data)
        order1, master1 = cross_referenced[0]
        self.assertEqual(order1['SKU'], 'SKU001')
        self.assertIsNotNone(master1)
        self.assertEqual(master1['Reference_Price'], 25.00)
        
        # Check third order (should not have master data)
        order3, master3 = cross_referenced[2]
        self.assertEqual(order3['SKU'], 'INVALID_SKU')
        self.assertIsNone(master3)
        
    def test_validate_orders_complete_workflow(self):
        """Test complete validation workflow"""
        # Setup test data files
        orders_data = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': '10', 'Price': '25.50'}
        ]
        orders_file = self.create_test_orders_file(orders_data)
        
        sku_data = [
            {'SKU': 'SKU001', 'Description': 'Widget A', 'Reference_Price': '25.00', 'Category': 'Electronics'}
        ]
        sku_file = self.create_test_sku_file(sku_data)
        
        # Mock file paths and capture output
        with patch.object(self.agent, 'read_customer_orders') as mock_read_orders, \
             patch.object(self.agent, 'read_master_skus') as mock_read_skus, \
             patch.object(self.agent, 'save_validation_results') as mock_save, \
             patch('builtins.print') as mock_print:
            
            mock_read_orders.return_value = [{'PO_Number': 'PO001', 'SKU': 'SKU001', 'Price': 25.50}]
            mock_read_skus.return_value = {'SKU001': {'Reference_Price': 25.00}}
            mock_save.return_value = ('simple.json', 'detailed.json')
            
            results = self.agent.validate_orders()
            
        # Verify workflow completed
        self.assertIsInstance(results, list)
        self.assertTrue(mock_read_orders.called)
        self.assertTrue(mock_read_skus.called)
        self.assertTrue(mock_save.called)
        self.assertTrue(mock_print.called)


if __name__ == '__main__':
    unittest.main()