"""
Unit tests for PO Reader Agent.
Tests CSV file reading, data parsing, error handling, and shared data population.
"""

import unittest
import os
import sys
import csv
import tempfile
import shutil
from unittest.mock import patch, mock_open

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from agents.po_reader.agent import POReaderAgent


class TestPOReaderAgent(BaseAgentTest):
    """Unit tests for PO Reader Agent functionality"""
    
    def setUp(self):
        """Setup test environment for PO Reader Agent tests"""
        super().setUp()
        self.agent = POReaderAgent()
        
    def test_read_valid_orders_success(self):
        """Test reading valid CSV file with proper order data"""
        # Create valid test data
        test_data = self.create_test_data('valid')
        
        # Initialize agent with test data path
        agent = POReaderAgent(data_path=test_data['orders_file'])
        
        # Read orders
        orders = agent.read_orders()
        
        # Verify orders were read successfully
        self.assertIsInstance(orders, list)
        self.assertGreater(len(orders), 0)
        
        # Verify order structure
        for order in orders:
            self.assertIn('PO_Number', order)
            self.assertIn('Customer_Name', order)
            self.assertIn('SKU', order)
            self.assertIn('Quantity', order)
            self.assertIn('Price', order)
            self.assertIn('Total_Value', order)
            
            # Verify data types
            self.assertIsInstance(order['Quantity'], int)
            self.assertIsInstance(order['Price'], float)
            self.assertIsInstance(order['Total_Value'], float)
            
            # Verify positive values
            self.assertGreater(order['Quantity'], 0)
            self.assertGreaterEqual(order['Price'], 0)
            self.assertGreaterEqual(order['Total_Value'], 0)
            
    def test_read_orders_file_not_found(self):
        """Test handling of missing CSV file"""
        agent = POReaderAgent(data_path="nonexistent_file.csv")
        
        orders = agent.read_orders()
        
        # Should return empty list when file not found
        self.assertEqual(orders, [])
        self.assertEqual(len(agent.orders), 0)
        
    def test_read_orders_missing_headers(self):
        """Test handling of CSV file with missing required headers"""
        # Create CSV with missing headers
        csv_file = os.path.join(self.test_data_dir, 'missing_headers.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU'])  # Missing Quantity, Price
            writer.writerow(['PO001', 'Test Corp', 'SKU001'])
            
        agent = POReaderAgent(data_path=csv_file)
        orders = agent.read_orders()
        
        # Should return empty list due to missing headers
        self.assertEqual(orders, [])
        
    def test_read_orders_malformed_data(self):
        """Test handling of CSV file with malformed data rows"""
        # Create CSV with malformed data
        csv_file = os.path.join(self.test_data_dir, 'malformed_data.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writerow(['PO001', 'Valid Corp', 'SKU001', '10', '25.50'])  # Valid
            writer.writerow(['PO002', 'Invalid Corp', 'SKU002', 'invalid_qty', '15.75'])  # Invalid quantity
            writer.writerow(['PO003', 'Another Corp', 'SKU003', '5', 'invalid_price'])  # Invalid price
            writer.writerow(['PO004', '', 'SKU004', '8', '12.25'])  # Empty customer name
            
        agent = POReaderAgent(data_path=csv_file)
        orders = agent.read_orders()
        
        # Should only return valid orders, skip malformed ones
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]['PO_Number'], 'PO001')
        
    def test_validate_and_parse_order_valid(self):
        """Test validation and parsing of valid order data"""
        agent = POReaderAgent()
        
        valid_row = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': '10',
            'Price': '25.50'
        }
        
        parsed_order = agent._validate_and_parse_order(valid_row, 2)
        
        # Verify parsed structure
        self.assertEqual(parsed_order['PO_Number'], 'PO001')
        self.assertEqual(parsed_order['Customer_Name'], 'Test Corp')
        self.assertEqual(parsed_order['SKU'], 'SKU001')
        self.assertEqual(parsed_order['Quantity'], 10)
        self.assertEqual(parsed_order['Price'], 25.50)
        self.assertEqual(parsed_order['Total_Value'], 255.0)
        
    def test_validate_and_parse_order_empty_fields(self):
        """Test validation of order with empty required fields"""
        agent = POReaderAgent()
        
        # Test empty PO number
        empty_po_row = {
            'PO_Number': '',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': '10',
            'Price': '25.50'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(empty_po_row, 2)
        self.assertIn("Empty required field 'PO_Number'", str(context.exception))
        
        # Test empty customer name
        empty_customer_row = {
            'PO_Number': 'PO001',
            'Customer_Name': '',
            'SKU': 'SKU001',
            'Quantity': '10',
            'Price': '25.50'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(empty_customer_row, 2)
        self.assertIn("Empty required field 'Customer_Name'", str(context.exception))
        
    def test_validate_and_parse_order_invalid_quantity(self):
        """Test validation of order with invalid quantity values"""
        agent = POReaderAgent()
        
        # Test negative quantity
        negative_qty_row = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': '-5',
            'Price': '25.50'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(negative_qty_row, 2)
        self.assertIn("Invalid quantity: -5", str(context.exception))
        
        # Test zero quantity
        zero_qty_row = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': '0',
            'Price': '25.50'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(zero_qty_row, 2)
        self.assertIn("Invalid quantity: 0", str(context.exception))
        
    def test_validate_and_parse_order_invalid_price(self):
        """Test validation of order with invalid price values"""
        agent = POReaderAgent()
        
        # Test negative price
        negative_price_row = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': '10',
            'Price': '-25.50'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(negative_price_row, 2)
        self.assertIn("Invalid price: -25.5", str(context.exception))
        
    def test_validate_and_parse_order_invalid_data_format(self):
        """Test validation of order with invalid data format"""
        agent = POReaderAgent()
        
        # Test non-numeric quantity
        invalid_qty_row = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': 'ten',
            'Price': '25.50'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(invalid_qty_row, 2)
        self.assertIn("invalid literal", str(context.exception))
        
        # Test non-numeric price
        invalid_price_row = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Test Corp',
            'SKU': 'SKU001',
            'Quantity': '10',
            'Price': 'twenty-five'
        }
        
        with self.assertRaises(ValueError) as context:
            agent._validate_and_parse_order(invalid_price_row, 2)
        self.assertIn("could not convert string to float", str(context.exception))
        
    def test_display_orders_table_with_data(self):
        """Test display of orders table with valid data"""
        # Create valid test data
        test_data = self.create_test_data('valid')
        agent = POReaderAgent(data_path=test_data['orders_file'])
        agent.read_orders()
        
        # Capture output
        with patch('builtins.print') as mock_print:
            agent.display_orders_table()
            
        # Verify print was called (table was displayed)
        self.assertTrue(mock_print.called)
        
        # Check that table headers and data were printed
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        table_content = '\n'.join(print_calls)
        
        self.assertIn('CUSTOMER ORDERS', table_content)
        self.assertIn('PO Number', table_content)
        self.assertIn('Customer', table_content)
        self.assertIn('Total Orders:', table_content)
        
    def test_display_orders_table_no_data(self):
        """Test display of orders table with no data"""
        agent = POReaderAgent()
        
        # Capture output
        with patch('builtins.print') as mock_print:
            agent.display_orders_table()
            
        # Verify appropriate message was printed
        mock_print.assert_called_with("No customer orders to display.")
        
    def test_get_summary_stats(self):
        """Test generation of summary statistics"""
        # Create valid test data
        test_data = self.create_test_data('valid')
        agent = POReaderAgent(data_path=test_data['orders_file'])
        agent.read_orders()
        
        stats = agent.get_summary_stats()
        
        # Verify stats structure
        self.assertIn('total_orders', stats)
        self.assertIn('total_value', stats)
        self.assertIn('unique_customers', stats)
        self.assertIn('customer_breakdown', stats)
        
        # Verify stats values
        self.assertGreater(stats['total_orders'], 0)
        self.assertGreater(stats['total_value'], 0)
        self.assertGreater(stats['unique_customers'], 0)
        self.assertIsInstance(stats['customer_breakdown'], dict)
        
    def test_get_summary_stats_no_data(self):
        """Test summary statistics with no data"""
        agent = POReaderAgent()
        
        stats = agent.get_summary_stats()
        
        # Verify empty stats
        self.assertEqual(stats['total_orders'], 0)
        self.assertEqual(stats['total_value'], 0.0)
        self.assertEqual(stats['unique_customers'], 0)
        self.assertEqual(stats['customer_breakdown'], {})
        
    def test_generate_reasoning_summary(self):
        """Test generation of reasoning summary output"""
        # Create valid test data
        test_data = self.create_test_data('valid')
        agent = POReaderAgent(data_path=test_data['orders_file'])
        agent.read_orders()
        
        summary = agent.generate_reasoning_summary()
        
        # Verify summary content
        self.assertIsInstance(summary, str)
        self.assertIn('REASONING OUTPUT - PO READER AGENT', summary)
        self.assertIn('SUMMARY:', summary)
        self.assertIn('DETAILED BREAKDOWN:', summary)
        self.assertIn('ORDER DETAILS:', summary)
        self.assertIn('NEXT STEPS:', summary)
        
    def test_generate_reasoning_summary_no_data(self):
        """Test reasoning summary with no data"""
        agent = POReaderAgent()
        
        summary = agent.generate_reasoning_summary()
        
        self.assertEqual(summary, "No customer orders detected for processing.")
        
    def test_process_natural_language_query_show_orders(self):
        """Test natural language query processing for showing orders"""
        # Create valid test data
        test_data = self.create_test_data('valid')
        agent = POReaderAgent(data_path=test_data['orders_file'])
        agent.read_orders()
        
        # Test show orders query
        response = agent.process_natural_language_query("Show me all customer orders pending validation")
        
        self.assertIsInstance(response, str)
        self.assertIn("Found", response)
        self.assertIn("customer orders pending validation", response)
        self.assertIn("Total pending order value:", response)
        
    def test_process_natural_language_query_count(self):
        """Test natural language query processing for count queries"""
        # Create valid test data
        test_data = self.create_test_data('valid')
        agent = POReaderAgent(data_path=test_data['orders_file'])
        agent.read_orders()
        
        # Test count query
        response = agent.process_natural_language_query("Total orders")
        
        self.assertIsInstance(response, str)
        self.assertIn("Order Summary:", response)
        self.assertIn("orders", response)
        self.assertIn("total value", response)
        self.assertIn("unique customers", response)
        
    def test_process_natural_language_query_help(self):
        """Test natural language query processing for help"""
        agent = POReaderAgent()
        
        response = agent.process_natural_language_query("help")
        
        self.assertIsInstance(response, str)
        self.assertIn("Available queries:", response)
        self.assertIn("Show me all customer orders", response)
        
    def test_process_natural_language_query_unknown(self):
        """Test natural language query processing for unknown queries"""
        agent = POReaderAgent()
        
        response = agent.process_natural_language_query("unknown query")
        
        self.assertIsInstance(response, str)
        self.assertIn("I don't understand the query", response)
        self.assertIn("Try 'help'", response)
        
    def test_file_permission_error_handling(self):
        """Test handling of file permission errors"""
        # Create a file and make it unreadable (if possible on the system)
        csv_file = os.path.join(self.test_data_dir, 'permission_test.csv')
        with open(csv_file, 'w') as f:
            f.write("PO_Number,Customer_Name,SKU,Quantity,Price\n")
            f.write("PO001,Test Corp,SKU001,10,25.50\n")
            
        # Try to make file unreadable (may not work on all systems)
        try:
            os.chmod(csv_file, 0o000)
            
            agent = POReaderAgent(data_path=csv_file)
            orders = agent.read_orders()
            
            # Should handle permission error gracefully
            self.assertEqual(orders, [])
            
        except (OSError, PermissionError):
            # Skip test if we can't modify permissions
            self.skipTest("Cannot modify file permissions on this system")
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(csv_file, 0o644)
            except (OSError, PermissionError):
                pass
                
    def test_corrupted_csv_file_handling(self):
        """Test handling of corrupted CSV files"""
        # Create corrupted CSV file
        csv_file = os.path.join(self.test_data_dir, 'corrupted.csv')
        with open(csv_file, 'wb') as f:
            f.write(b'PO_Number,Customer_Name,SKU,Quantity,Price\n')
            f.write(b'PO001,Test Corp,SKU001,10,25.50\n')
            f.write(b'\x00\x01\x02\x03\x04')  # Binary garbage
            
        agent = POReaderAgent(data_path=csv_file)
        orders = agent.read_orders()
        
        # Should handle corruption gracefully and return what it can parse
        self.assertIsInstance(orders, list)
        # May return empty list or partial data depending on corruption handling
        
    def test_large_csv_file_handling(self):
        """Test handling of large CSV files"""
        # Create a larger CSV file for performance testing
        csv_file = os.path.join(self.test_data_dir, 'large_orders.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            
            # Generate 100 orders
            for i in range(100):
                writer.writerow([
                    f'PO{str(i+1).zfill(3)}',
                    f'Customer_{i+1}',
                    f'SKU{str((i % 10) + 1).zfill(3)}',
                    str((i % 20) + 1),
                    str(round((i + 1) * 1.5, 2))
                ])
                
        agent = POReaderAgent(data_path=csv_file)
        orders = agent.read_orders()
        
        # Verify all orders were processed
        self.assertEqual(len(orders), 100)
        
        # Verify first and last orders
        self.assertEqual(orders[0]['PO_Number'], 'PO001')
        self.assertEqual(orders[-1]['PO_Number'], 'PO100')


if __name__ == '__main__':
    unittest.main()