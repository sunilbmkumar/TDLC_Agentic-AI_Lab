"""
Unit tests for SO Creator Agent.
Tests sales order generation, data transformation, output file creation, and error handling.
"""

import unittest
import os
import sys
import csv
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from agents.so_creator.agent import SalesOrderCreatorAgent


class TestSalesOrderCreatorAgent(BaseAgentTest):
    """Unit tests for Sales Order Creator Agent functionality"""
    
    def setUp(self):
        """Setup test environment for SO Creator Agent tests"""
        super().setUp()
        self.agent = SalesOrderCreatorAgent()
        
    def create_test_validation_results(self, results_data):
        """Helper method to create test validation results JSON file"""
        results_file = os.path.join(self.test_output_dir, 'validation_results_simple.json')
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        return results_file
        
    def create_test_customer_orders(self, orders_data):
        """Helper method to create test customer orders CSV file"""
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writeheader()
            writer.writerows(orders_data)
        return orders_file
        
    def test_read_validation_results_success(self):
        """Test successful reading of validation results"""
        test_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'}
        ]
        
        results_file = self.create_test_validation_results(test_results)
        
        validation_results = self.agent.read_validation_results(results_file)
        
        # Verify results were read correctly
        self.assertEqual(len(validation_results), 3)
        self.assertEqual(validation_results[0]['PO_Number'], 'PO001')
        self.assertEqual(validation_results[0]['Status'], 'Valid')
        
    def test_read_validation_results_file_not_found(self):
        """Test handling of missing validation results file"""
        validation_results = self.agent.read_validation_results("nonexistent_file.json")
        
        self.assertEqual(validation_results, [])
        
    def test_read_validation_results_invalid_json(self):
        """Test handling of invalid JSON in validation results file"""
        # Create invalid JSON file
        invalid_file = os.path.join(self.test_output_dir, 'invalid.json')
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json content")
            
        validation_results = self.agent.read_validation_results(invalid_file)
        
        self.assertEqual(validation_results, [])
        
    def test_read_customer_orders_success(self):
        """Test successful reading of customer orders"""
        orders_data = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': '10', 'Price': '25.50'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc', 'SKU': 'SKU002', 'Quantity': '5', 'Price': '15.75'}
        ]
        
        orders_file = self.create_test_customer_orders(orders_data)
        
        customer_orders = self.agent.read_customer_orders(orders_file)
        
        # Verify orders were read correctly
        self.assertEqual(len(customer_orders), 2)
        self.assertEqual(customer_orders[0]['PO_Number'], 'PO001')
        self.assertEqual(customer_orders[0]['Quantity'], 10)  # Should be converted to int
        self.assertEqual(customer_orders[0]['Price'], 25.50)  # Should be converted to float
        self.assertEqual(self.agent.customer_orders, customer_orders)
        
    def test_read_customer_orders_file_not_found(self):
        """Test handling of missing customer orders file"""
        customer_orders = self.agent.read_customer_orders("nonexistent_file.csv")
        
        self.assertEqual(customer_orders, [])
        self.assertEqual(len(self.agent.customer_orders), 0)
        
    def test_filter_valid_orders(self):
        """Test filtering validation results for valid orders only"""
        validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'},
            {'PO_Number': 'PO004', 'Status': 'Exception'}
        ]
        
        valid_po_numbers = self.agent.filter_valid_orders(validation_results)
        
        # Verify only valid PO numbers are returned
        self.assertEqual(len(valid_po_numbers), 2)
        self.assertIn('PO001', valid_po_numbers)
        self.assertIn('PO003', valid_po_numbers)
        self.assertNotIn('PO002', valid_po_numbers)
        self.assertNotIn('PO004', valid_po_numbers)
        
    def test_get_validated_order_data(self):
        """Test getting order data for validated PO numbers"""
        # Setup customer orders
        self.agent.customer_orders = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': 10, 'Price': 25.50},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc', 'SKU': 'SKU002', 'Quantity': 5, 'Price': 15.75},
            {'PO_Number': 'PO003', 'Customer_Name': 'Gamma LLC', 'SKU': 'SKU003', 'Quantity': 8, 'Price': 12.25}
        ]
        
        valid_po_numbers = ['PO001', 'PO003']
        
        validated_orders = self.agent.get_validated_order_data(valid_po_numbers)
        
        # Verify only validated orders are returned
        self.assertEqual(len(validated_orders), 2)
        self.assertEqual(validated_orders[0]['PO_Number'], 'PO001')
        self.assertEqual(validated_orders[1]['PO_Number'], 'PO003')
        self.assertEqual(self.agent.validated_orders, validated_orders)
        
    def test_generate_so_number(self):
        """Test SO number generation"""
        # Test sequential SO number generation
        so1 = self.agent.generate_so_number('PO001')
        so2 = self.agent.generate_so_number('PO002')
        so3 = self.agent.generate_so_number('PO003')
        
        # Verify SO numbers are sequential
        self.assertEqual(so1, 'SO2001')
        self.assertEqual(so2, 'SO2002')
        self.assertEqual(so3, 'SO2003')
        
        # Verify counter is incremented
        self.assertEqual(self.agent.so_counter, 2004)
        
    def test_transform_po_to_so(self):
        """Test transformation of PO data to sales order format"""
        po_data = {
            'PO_Number': 'PO001',
            'Customer_Name': 'Acme Corp',
            'SKU': 'SKU001',
            'Quantity': 10,
            'Price': 25.50
        }
        
        # Mock datetime for consistent testing
        with patch('agents.so_creator.agent.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '2024-01-01 12:00:00'
            
            sales_order = self.agent.transform_po_to_so(po_data)
            
        # Verify sales order structure
        self.assertIn('SO_Number', sales_order)
        self.assertIn('PO_Number', sales_order)
        self.assertIn('Customer', sales_order)
        self.assertIn('Material', sales_order)
        self.assertIn('Quantity', sales_order)
        self.assertIn('Price', sales_order)
        self.assertIn('Total', sales_order)
        self.assertIn('Created_Date', sales_order)
        
        # Verify sales order content
        self.assertEqual(sales_order['SO_Number'], 'SO2001')
        self.assertEqual(sales_order['PO_Number'], 'PO001')
        self.assertEqual(sales_order['Customer'], 'Acme Corp')
        self.assertEqual(sales_order['Material'], 'SKU001')  # SKU mapped to Material
        self.assertEqual(sales_order['Quantity'], 10)
        self.assertEqual(sales_order['Price'], 25.50)
        self.assertEqual(sales_order['Total'], 255.0)  # 10 * 25.50
        self.assertEqual(sales_order['Created_Date'], '2024-01-01 12:00:00')
        
    def test_process_validated_orders_success(self):
        """Test successful processing of validated orders"""
        # Mock the required methods
        with patch.object(self.agent, 'read_validation_results') as mock_read_validation, \
             patch.object(self.agent, 'read_customer_orders') as mock_read_orders, \
             patch.object(self.agent, 'filter_valid_orders') as mock_filter, \
             patch.object(self.agent, 'get_validated_order_data') as mock_get_data, \
             patch.object(self.agent, 'transform_po_to_so') as mock_transform, \
             patch('builtins.print') as mock_print:
            
            # Setup mock returns
            mock_read_validation.return_value = [
                {'PO_Number': 'PO001', 'Status': 'Valid'},
                {'PO_Number': 'PO002', 'Status': 'Exception'}
            ]
            mock_read_orders.return_value = [
                {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': 10, 'Price': 25.50}
            ]
            mock_filter.return_value = ['PO001']
            mock_get_data.return_value = [
                {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': 10, 'Price': 25.50}
            ]
            mock_transform.return_value = {
                'SO_Number': 'SO2001',
                'PO_Number': 'PO001',
                'Customer': 'Acme Corp',
                'Material': 'SKU001',
                'Quantity': 10,
                'Price': 25.50,
                'Total': 255.0
            }
            
            sales_orders = self.agent.process_validated_orders()
            
        # Verify processing completed
        self.assertTrue(mock_read_validation.called)
        self.assertTrue(mock_read_orders.called)
        self.assertTrue(mock_filter.called)
        self.assertTrue(mock_get_data.called)
        self.assertTrue(mock_transform.called)
        self.assertEqual(len(sales_orders), 1)
        
    def test_process_validated_orders_no_validation_results(self):
        """Test processing when no validation results are found"""
        with patch.object(self.agent, 'read_validation_results') as mock_read_validation, \
             patch('builtins.print') as mock_print:
            
            mock_read_validation.return_value = []
            
            sales_orders = self.agent.process_validated_orders()
            
        # Verify empty result
        self.assertEqual(sales_orders, [])
        
    def test_process_validated_orders_no_customer_orders(self):
        """Test processing when no customer orders are found"""
        with patch.object(self.agent, 'read_validation_results') as mock_read_validation, \
             patch.object(self.agent, 'read_customer_orders') as mock_read_orders, \
             patch('builtins.print') as mock_print:
            
            mock_read_validation.return_value = [{'PO_Number': 'PO001', 'Status': 'Valid'}]
            mock_read_orders.return_value = []
            
            sales_orders = self.agent.process_validated_orders()
            
        # Verify empty result
        self.assertEqual(sales_orders, [])
        
    def test_generate_sales_order_dataset(self):
        """Test generation of sales order dataset"""
        # Setup sales orders
        self.agent.sales_orders = [
            {
                'SO_Number': 'SO2001',
                'PO_Number': 'PO001',
                'Customer': 'Acme Corp',
                'Material': 'SKU001',
                'Quantity': 10,
                'Price': 25.50,
                'Total': 255.0,
                'Created_Date': '2024-01-01 12:00:00'
            },
            {
                'SO_Number': 'SO2002',
                'PO_Number': 'PO002',
                'Customer': 'Beta Inc',
                'Material': 'SKU002',
                'Quantity': 5,
                'Price': 15.75,
                'Total': 78.75,
                'Created_Date': '2024-01-01 12:01:00'
            }
        ]
        
        dataset = self.agent.generate_sales_order_dataset()
        
        # Verify dataset structure
        self.assertEqual(len(dataset), 2)
        
        # Verify required columns are present
        required_columns = ['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total']
        for row in dataset:
            for column in required_columns:
                self.assertIn(column, row)
                
        # Verify data content
        self.assertEqual(dataset[0]['SO_Number'], 'SO2001')
        self.assertEqual(dataset[0]['Customer'], 'Acme Corp')
        self.assertEqual(dataset[0]['Material'], 'SKU001')
        
    def test_format_for_erp_consumption(self):
        """Test formatting dataset for ERP consumption"""
        dataset = [
            {
                'SO_Number': 'SO2001',
                'Customer': 'Acme Corp',
                'Material': 'SKU001',
                'Quantity': 10,
                'Price': 25.50,
                'Total': 255.0
            }
        ]
        
        formatted_dataset = self.agent.format_for_erp_consumption(dataset)
        
        # Verify formatting
        self.assertEqual(len(formatted_dataset), 1)
        
        formatted_row = formatted_dataset[0]
        
        # Verify data types and formatting
        self.assertIsInstance(formatted_row['SO_Number'], str)
        self.assertIsInstance(formatted_row['Customer'], str)
        self.assertIsInstance(formatted_row['Material'], str)
        self.assertIsInstance(formatted_row['Quantity'], int)
        self.assertEqual(formatted_row['Price'], '25.50')  # Should be formatted string
        self.assertEqual(formatted_row['Total'], '255.00')  # Should be formatted string
        
    def test_calculate_line_totals(self):
        """Test calculation of line totals and summary statistics"""
        # Setup sales orders
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.0},
            {'Customer': 'Beta Inc', 'Total': 78.75},
            {'Customer': 'Acme Corp', 'Total': 150.0}
        ]
        
        totals = self.agent.calculate_line_totals()
        
        # Verify totals structure
        self.assertIn('total_sales_value', totals)
        self.assertIn('customer_totals', totals)
        self.assertIn('order_count', totals)
        
        # Verify calculated values
        self.assertEqual(totals['total_sales_value'], 483.75)
        self.assertEqual(totals['order_count'], 3)
        self.assertEqual(totals['customer_totals']['Acme Corp'], 405.0)
        self.assertEqual(totals['customer_totals']['Beta Inc'], 78.75)
        
    def test_generate_csv_output_success(self):
        """Test successful CSV output generation"""
        # Setup sales orders
        self.agent.sales_orders = [
            {
                'SO_Number': 'SO2001',
                'PO_Number': 'PO001',
                'Customer': 'Acme Corp',
                'Material': 'SKU001',
                'Quantity': 10,
                'Price': 25.50,
                'Total': 255.0
            }
        ]
        
        output_file = os.path.join(self.test_output_dir, 'test_sales_orders.csv')
        
        with patch('builtins.print') as mock_print:
            generated_file = self.agent.generate_csv_output(output_file)
            
        # Verify file was created
        self.assertEqual(generated_file, output_file)
        self.assert_file_exists(output_file)
        
        # Verify CSV content
        with open(output_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['SO_Number'], 'SO2001')
        self.assertEqual(rows[0]['Customer'], 'Acme Corp')
        self.assertEqual(rows[0]['Material'], 'SKU001')
        
    def test_generate_csv_output_file_error(self):
        """Test CSV output generation with file system error"""
        # Setup sales orders
        self.agent.sales_orders = [
            {'SO_Number': 'SO2001', 'Customer': 'Acme Corp', 'Material': 'SKU001', 'Quantity': 10, 'Price': 25.50, 'Total': 255.0}
        ]
        
        # Use invalid path to trigger error
        invalid_path = "/invalid/path/that/does/not/exist/sales_orders.csv"
        
        with patch('builtins.print') as mock_print:
            generated_file = self.agent.generate_csv_output(invalid_path)
            
        # Verify error was handled
        self.assertEqual(generated_file, "")
        
    def test_validate_output_format_success(self):
        """Test successful validation of output format"""
        # Create valid CSV file
        csv_file = os.path.join(self.test_output_dir, 'valid_output.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
            writer.writerow(['SO2001', 'Acme Corp', 'SKU001', '10', '25.50', '255.00'])
            
        with patch('builtins.print') as mock_print:
            is_valid = self.agent.validate_output_format(csv_file)
            
        # Verify validation passed
        self.assertTrue(is_valid)
        
    def test_validate_output_format_invalid_headers(self):
        """Test validation with invalid headers"""
        # Create CSV with invalid headers
        csv_file = os.path.join(self.test_output_dir, 'invalid_headers.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SO_Number', 'Customer', 'SKU'])  # Missing required headers
            writer.writerow(['SO2001', 'Acme Corp', 'SKU001'])
            
        with patch('builtins.print') as mock_print:
            is_valid = self.agent.validate_output_format(csv_file)
            
        # Verify validation failed
        self.assertFalse(is_valid)
        
    def test_validate_output_format_invalid_so_number(self):
        """Test validation with invalid SO number format"""
        # Create CSV with invalid SO number
        csv_file = os.path.join(self.test_output_dir, 'invalid_so_number.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
            writer.writerow(['INVALID001', 'Acme Corp', 'SKU001', '10', '25.50', '255.00'])  # Should start with 'SO'
            
        with patch('builtins.print') as mock_print:
            is_valid = self.agent.validate_output_format(csv_file)
            
        # Verify validation failed
        self.assertFalse(is_valid)
        
    def test_validate_output_format_invalid_numeric_data(self):
        """Test validation with invalid numeric data"""
        # Create CSV with invalid numeric data
        csv_file = os.path.join(self.test_output_dir, 'invalid_numeric.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
            writer.writerow(['SO2001', 'Acme Corp', 'SKU001', 'ten', '25.50', '255.00'])  # Invalid quantity
            
        with patch('builtins.print') as mock_print:
            is_valid = self.agent.validate_output_format(csv_file)
            
        # Verify validation failed
        self.assertFalse(is_valid)
        
    def test_display_csv_preview(self):
        """Test display of CSV preview"""
        # Create test CSV file
        csv_file = os.path.join(self.test_output_dir, 'preview_test.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
            writer.writerow(['SO2001', 'Acme Corp', 'SKU001', '10', '25.50', '255.00'])
            writer.writerow(['SO2002', 'Beta Inc', 'SKU002', '5', '15.75', '78.75'])
            
        # Capture output
        with patch('builtins.print') as mock_print:
            self.agent.display_csv_preview(csv_file, max_rows=2)
            
        # Verify preview was displayed
        self.assertTrue(mock_print.called)
        
        # Check that preview content was printed
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        output_content = '\n'.join(print_calls)
        
        self.assertIn('CSV PREVIEW', output_content)
        self.assertIn('Headers:', output_content)
        self.assertIn('SO2001', output_content)
        
    def test_generate_sales_value_by_customer_chart(self):
        """Test generation of sales value by customer chart data"""
        # Setup sales orders
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.0},
            {'Customer': 'Beta Inc', 'Total': 78.75},
            {'Customer': 'Acme Corp', 'Total': 150.0}
        ]
        
        chart_data = self.agent.generate_sales_value_by_customer_chart()
        
        # Verify chart structure
        self.assertIn('chart_type', chart_data)
        self.assertIn('title', chart_data)
        self.assertIn('x_axis', chart_data)
        self.assertIn('y_axis', chart_data)
        self.assertIn('data', chart_data)
        
        # Verify chart content
        self.assertEqual(chart_data['chart_type'], 'bar')
        self.assertEqual(chart_data['title'], 'Total Sales Value by Customer')
        self.assertEqual(len(chart_data['data']), 2)
        
        # Verify data values
        acme_data = next(item for item in chart_data['data'] if item['customer'] == 'Acme Corp')
        self.assertEqual(acme_data['sales_value'], 405.0)
        
    def test_generate_exception_count_by_customer_chart(self):
        """Test generation of exception count by customer chart data"""
        # Setup customer orders
        self.agent.customer_orders = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc'},
            {'PO_Number': 'PO003', 'Customer_Name': 'Acme Corp'}
        ]
        
        validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Exception'}
        ]
        
        chart_data = self.agent.generate_exception_count_by_customer_chart(validation_results)
        
        # Verify chart structure
        self.assertEqual(chart_data['chart_type'], 'bar')
        self.assertEqual(chart_data['title'], 'Exception Count by Customer')
        self.assertEqual(len(chart_data['data']), 2)
        
        # Verify exception counts
        acme_data = next(item for item in chart_data['data'] if item['customer'] == 'Acme Corp')
        beta_data = next(item for item in chart_data['data'] if item['customer'] == 'Beta Inc')
        
        self.assertEqual(acme_data['exception_count'], 1)  # PO003
        self.assertEqual(beta_data['exception_count'], 1)  # PO002
        
    def test_save_chart_data(self):
        """Test saving chart data to JSON files"""
        # Setup sales orders
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.0}
        ]
        
        validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'}
        ]
        
        sales_chart_file, exception_chart_file = self.agent.save_chart_data(validation_results, self.test_output_dir)
        
        # Verify files were created
        self.assert_file_exists(sales_chart_file)
        self.assert_file_exists(exception_chart_file)
        
        # Verify file contents
        with open(sales_chart_file, 'r') as f:
            sales_chart = json.load(f)
        with open(exception_chart_file, 'r') as f:
            exception_chart = json.load(f)
            
        self.assertEqual(sales_chart['title'], 'Total Sales Value by Customer')
        self.assertEqual(exception_chart['title'], 'Exception Count by Customer')
        
    def test_create_sales_orders_complete_workflow(self):
        """Test complete sales order creation workflow"""
        # Mock all the required methods
        with patch.object(self.agent, 'process_validated_orders') as mock_process, \
             patch.object(self.agent, 'generate_csv_output') as mock_csv, \
             patch.object(self.agent, 'validate_output_format') as mock_validate, \
             patch.object(self.agent, 'display_csv_preview') as mock_preview, \
             patch.object(self.agent, 'read_validation_results') as mock_read_validation, \
             patch.object(self.agent, 'display_charts_in_kiro') as mock_charts, \
             patch.object(self.agent, 'save_chart_data') as mock_save_charts, \
             patch.object(self.agent, 'calculate_line_totals') as mock_totals, \
             patch('builtins.print') as mock_print:
            
            # Setup mock returns
            mock_process.return_value = [
                {'SO_Number': 'SO2001', 'Customer': 'Acme Corp', 'Total': 255.0}
            ]
            mock_csv.return_value = 'test_output.csv'
            mock_validate.return_value = True
            mock_read_validation.return_value = [{'PO_Number': 'PO001', 'Status': 'Valid'}]
            mock_save_charts.return_value = ('sales_chart.json', 'exception_chart.json')
            mock_totals.return_value = {
                'order_count': 1,
                'total_sales_value': 255.0,
                'customer_totals': {'Acme Corp': 255.0}
            }
            
            result = self.agent.create_sales_orders()
            
        # Verify workflow completed successfully
        self.assertTrue(result['success'])
        self.assertEqual(len(result['sales_orders']), 1)
        self.assertEqual(result['total_sales_value'], 255.0)
        self.assertEqual(result['order_count'], 1)
        
        # Verify all methods were called
        self.assertTrue(mock_process.called)
        self.assertTrue(mock_csv.called)
        self.assertTrue(mock_validate.called)
        self.assertTrue(mock_preview.called)
        self.assertTrue(mock_charts.called)
        self.assertTrue(mock_save_charts.called)
        
    def test_create_sales_orders_no_valid_orders(self):
        """Test sales order creation when no valid orders exist"""
        with patch.object(self.agent, 'process_validated_orders') as mock_process, \
             patch('builtins.print') as mock_print:
            
            mock_process.return_value = []
            
            result = self.agent.create_sales_orders()
            
        # Verify failure result
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'No valid orders found')


if __name__ == '__main__':
    unittest.main()