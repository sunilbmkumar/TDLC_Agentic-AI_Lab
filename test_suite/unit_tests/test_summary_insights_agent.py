"""
Unit tests for Summary Insights Agent.
Tests report generation, analytics calculations, dashboard data preparation, and data handling.
"""

import unittest
import os
import sys
import csv
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from agents.summary_insights.agent import SummaryInsightsAgent


class TestSummaryInsightsAgent(BaseAgentTest):
    """Unit tests for Summary Insights Agent functionality"""
    
    def setUp(self):
        """Setup test environment for Summary Insights Agent tests"""
        super().setUp()
        self.agent = SummaryInsightsAgent()
        
    def create_test_customer_orders(self, orders_data):
        """Helper method to create test customer orders CSV file"""
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writeheader()
            writer.writerows(orders_data)
        return orders_file
        
    def create_test_validation_results(self, results_data):
        """Helper method to create test validation results JSON file"""
        results_file = os.path.join(self.test_output_dir, 'validation_results_detailed.json')
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        return results_file
        
    def create_test_sales_orders(self, orders_data):
        """Helper method to create test sales orders CSV file"""
        orders_file = os.path.join(self.test_output_dir, 'sales_order_output.csv')
        with open(orders_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
            writer.writeheader()
            writer.writerows(orders_data)
        return orders_file
        
    def test_load_customer_orders_success(self):
        """Test successful loading of customer orders"""
        orders_data = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp', 'SKU': 'SKU001', 'Quantity': '10', 'Price': '25.50'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc', 'SKU': 'SKU002', 'Quantity': '5', 'Price': '15.75'}
        ]
        
        orders_file = self.create_test_customer_orders(orders_data)
        
        loaded_orders = self.agent.load_customer_orders(orders_file)
        
        # Verify orders were loaded correctly
        self.assertEqual(len(loaded_orders), 2)
        self.assertEqual(loaded_orders[0]['PO_Number'], 'PO001')
        self.assertEqual(loaded_orders[0]['Quantity'], 10)  # Should be converted to int
        self.assertEqual(loaded_orders[0]['Price'], 25.50)  # Should be converted to float
        self.assertEqual(self.agent.customer_orders, loaded_orders)
        
    def test_load_customer_orders_file_not_found(self):
        """Test handling of missing customer orders file"""
        loaded_orders = self.agent.load_customer_orders("nonexistent_file.csv")
        
        self.assertEqual(loaded_orders, [])
        self.assertEqual(len(self.agent.customer_orders), 0)
        
    def test_load_validation_results_success(self):
        """Test successful loading of validation results"""
        results_data = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'}
        ]
        
        results_file = self.create_test_validation_results(results_data)
        
        loaded_results = self.agent.load_validation_results(results_file)
        
        # Verify results were loaded correctly
        self.assertEqual(len(loaded_results), 2)
        self.assertEqual(loaded_results[0]['PO_Number'], 'PO001')
        self.assertEqual(self.agent.validation_results, loaded_results)
        
    def test_load_validation_results_file_not_found(self):
        """Test handling of missing validation results file"""
        loaded_results = self.agent.load_validation_results("nonexistent_file.json")
        
        self.assertEqual(loaded_results, [])
        self.assertEqual(len(self.agent.validation_results), 0)
        
    def test_load_sales_orders_success(self):
        """Test successful loading of sales orders"""
        orders_data = [
            {'SO_Number': 'SO2001', 'Customer': 'Acme Corp', 'Material': 'SKU001', 'Quantity': '10', 'Price': '25.50', 'Total': '255.00'},
            {'SO_Number': 'SO2002', 'Customer': 'Beta Inc', 'Material': 'SKU002', 'Quantity': '5', 'Price': '15.75', 'Total': '78.75'}
        ]
        
        orders_file = self.create_test_sales_orders(orders_data)
        
        loaded_orders = self.agent.load_sales_orders(orders_file)
        
        # Verify orders were loaded correctly
        self.assertEqual(len(loaded_orders), 2)
        self.assertEqual(loaded_orders[0]['SO_Number'], 'SO2001')
        self.assertEqual(loaded_orders[0]['Quantity'], 10)  # Should be converted to int
        self.assertEqual(loaded_orders[0]['Price'], 25.50)  # Should be converted to float
        self.assertEqual(loaded_orders[0]['Total'], 255.00)  # Should be converted to float
        self.assertEqual(self.agent.sales_orders, loaded_orders)
        
    def test_load_sales_orders_file_not_found(self):
        """Test handling of missing sales orders file"""
        loaded_orders = self.agent.load_sales_orders("nonexistent_file.csv")
        
        self.assertEqual(loaded_orders, [])
        self.assertEqual(len(self.agent.sales_orders), 0)
        
    def test_calculate_total_orders(self):
        """Test calculation of total orders"""
        # Setup customer orders
        self.agent.customer_orders = [
            {'PO_Number': 'PO001'},
            {'PO_Number': 'PO002'},
            {'PO_Number': 'PO003'}
        ]
        
        total_orders = self.agent.calculate_total_orders()
        
        self.assertEqual(total_orders, 3)
        
    def test_calculate_total_orders_empty(self):
        """Test calculation of total orders with empty data"""
        total_orders = self.agent.calculate_total_orders()
        
        self.assertEqual(total_orders, 0)
        
    def test_calculate_validated_orders(self):
        """Test calculation of validated orders"""
        # Setup validation results
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'},
            {'PO_Number': 'PO004', 'Status': 'Exception'}
        ]
        
        validated_orders = self.agent.calculate_validated_orders()
        
        self.assertEqual(validated_orders, 2)
        
    def test_calculate_validated_orders_empty(self):
        """Test calculation of validated orders with empty data"""
        validated_orders = self.agent.calculate_validated_orders()
        
        self.assertEqual(validated_orders, 0)
        
    def test_calculate_exceptions(self):
        """Test calculation of exception orders"""
        # Setup validation results
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'},
            {'PO_Number': 'PO004', 'Status': 'Exception'}
        ]
        
        exceptions = self.agent.calculate_exceptions()
        
        self.assertEqual(exceptions, 2)
        
    def test_calculate_total_sales_value(self):
        """Test calculation of total sales value"""
        # Setup sales orders
        self.agent.sales_orders = [
            {'Total': 255.00},
            {'Total': 78.75},
            {'Total': 150.25}
        ]
        
        total_sales_value = self.agent.calculate_total_sales_value()
        
        self.assertEqual(total_sales_value, 484.00)
        
    def test_calculate_total_sales_value_empty(self):
        """Test calculation of total sales value with empty data"""
        total_sales_value = self.agent.calculate_total_sales_value()
        
        self.assertEqual(total_sales_value, 0.0)
        
    def test_generate_comprehensive_summary(self):
        """Test generation of comprehensive summary"""
        # Setup test data
        self.agent.customer_orders = [
            {'PO_Number': 'PO001'},
            {'PO_Number': 'PO002'},
            {'PO_Number': 'PO003'}
        ]
        
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'},
            {'PO_Number': 'PO002', 'Status': 'Exception'},
            {'PO_Number': 'PO003', 'Status': 'Valid'}
        ]
        
        self.agent.sales_orders = [
            {'Total': 255.00},
            {'Total': 150.25}
        ]
        
        # Mock the load methods to avoid file operations
        with patch.object(self.agent, 'load_customer_orders'), \
             patch.object(self.agent, 'load_validation_results'), \
             patch.object(self.agent, 'load_sales_orders'), \
             patch.object(self.agent, 'load_exception_data'):
            
            summary = self.agent.generate_comprehensive_summary()
            
        # Verify summary structure
        self.assertIn('total_orders', summary)
        self.assertIn('validated_orders', summary)
        self.assertIn('exceptions', summary)
        self.assertIn('total_sales_value', summary)
        self.assertIn('processing_statistics', summary)
        self.assertIn('summary_text', summary)
        self.assertIn('generated_timestamp', summary)
        
        # Verify summary values
        self.assertEqual(summary['total_orders'], 3)
        self.assertEqual(summary['validated_orders'], 2)
        self.assertEqual(summary['exceptions'], 1)
        self.assertEqual(summary['total_sales_value'], 405.25)
        
        # Verify processing statistics
        stats = summary['processing_statistics']
        self.assertAlmostEqual(stats['validation_success_rate'], 66.67, places=1)
        self.assertAlmostEqual(stats['exception_rate'], 33.33, places=1)
        self.assertAlmostEqual(stats['sales_conversion_rate'], 66.67, places=1)
        
    def test_display_comprehensive_summary(self):
        """Test display of comprehensive summary"""
        # Setup summary data
        self.agent.summary_data = {
            'total_orders': 3,
            'validated_orders': 2,
            'exceptions': 1,
            'total_sales_value': 405.25,
            'processing_statistics': {
                'validation_success_rate': 66.7,
                'exception_rate': 33.3,
                'sales_conversion_rate': 66.7
            },
            'summary_text': 'Test summary',
            'generated_timestamp': '2024-01-01T12:00:00'
        }
        
        # Capture output
        with patch('builtins.print') as mock_print:
            self.agent.display_comprehensive_summary()
            
        # Verify print was called with summary content
        self.assertTrue(mock_print.called)
        
        # Check that summary content was displayed
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        output_content = '\n'.join(print_calls)
        
        self.assertIn('COMPREHENSIVE PROCESSING SUMMARY', output_content)
        self.assertIn('ORDER PROCESSING METRICS', output_content)
        self.assertIn('PROCESSING STATISTICS', output_content)
        self.assertIn('Total Orders: 3', output_content)
        
    def test_save_summary_data(self):
        """Test saving summary data to JSON file"""
        # Setup summary data
        self.agent.summary_data = {
            'total_orders': 3,
            'validated_orders': 2,
            'exceptions': 1,
            'total_sales_value': 405.25
        }
        
        summary_file = self.agent.save_summary_data(self.test_output_dir)
        
        # Verify file was created
        self.assert_file_exists(summary_file)
        
        # Verify file content
        with open(summary_file, 'r') as f:
            saved_summary = json.load(f)
            
        self.assertEqual(saved_summary['total_orders'], 3)
        self.assertEqual(saved_summary['validated_orders'], 2)
        
    def test_analyze_customer_contributions(self):
        """Test analysis of customer contributions"""
        # Setup sales orders
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.00},
            {'Customer': 'Beta Inc', 'Total': 78.75},
            {'Customer': 'Acme Corp', 'Total': 150.25},
            {'Customer': 'Gamma LLC', 'Total': 100.00}
        ]
        
        contributions = self.agent.analyze_customer_contributions()
        
        # Verify contributions structure
        self.assertIn('Acme Corp', contributions)
        self.assertIn('Beta Inc', contributions)
        self.assertIn('Gamma LLC', contributions)
        
        # Verify Acme Corp data
        acme_data = contributions['Acme Corp']
        self.assertEqual(acme_data['total_value'], 405.25)
        self.assertEqual(acme_data['order_count'], 2)
        self.assertAlmostEqual(acme_data['percentage'], 69.4, places=1)
        
        # Verify Beta Inc data
        beta_data = contributions['Beta Inc']
        self.assertEqual(beta_data['total_value'], 78.75)
        self.assertEqual(beta_data['order_count'], 1)
        self.assertAlmostEqual(beta_data['percentage'], 13.5, places=1)
        
    def test_analyze_customer_contributions_empty(self):
        """Test customer contributions analysis with empty data"""
        contributions = self.agent.analyze_customer_contributions()
        
        self.assertEqual(contributions, {})
        
    def test_identify_exception_patterns(self):
        """Test identification of exception patterns"""
        # Setup customer orders
        self.agent.customer_orders = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc'},
            {'PO_Number': 'PO003', 'Customer_Name': 'Acme Corp'}
        ]
        
        # Setup validation results
        self.agent.validation_results = [
            {
                'PO_Number': 'PO001',
                'Status': 'Exception',
                'Reasons': ['SKU SKU999 not found in master data']
            },
            {
                'PO_Number': 'PO002',
                'Status': 'Exception',
                'Reasons': ['Price deviation of 25.0% exceeds 10% threshold for SKU001']
            },
            {
                'PO_Number': 'PO003',
                'Status': 'Valid',
                'Reasons': ['Price within acceptable range']
            }
        ]
        
        patterns = self.agent.identify_exception_patterns()
        
        # Verify patterns structure
        self.assertIn('by_customer', patterns)
        self.assertIn('by_exception_type', patterns)
        self.assertIn('root_causes', patterns)
        
        # Verify customer patterns
        self.assertIn('Acme Corp', patterns['by_customer'])
        self.assertIn('Beta Inc', patterns['by_customer'])
        self.assertEqual(patterns['by_customer']['Acme Corp']['count'], 1)
        self.assertEqual(patterns['by_customer']['Beta Inc']['count'], 1)
        
        # Verify exception type patterns
        self.assertIn('SKU_NOT_FOUND', patterns['by_exception_type'])
        self.assertIn('PRICE_DEVIATION', patterns['by_exception_type'])
        self.assertEqual(patterns['by_exception_type']['SKU_NOT_FOUND'], 1)
        self.assertEqual(patterns['by_exception_type']['PRICE_DEVIATION'], 1)
        
    def test_generate_insights(self):
        """Test generation of insights from analysis"""
        # Setup data for insights generation
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 300.00},
            {'Customer': 'Beta Inc', 'Total': 100.00},
            {'Customer': 'Acme Corp', 'Total': 200.00}
        ]
        
        self.agent.customer_orders = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp'},
            {'PO_Number': 'PO002', 'Customer_Name': 'Beta Inc'},
            {'PO_Number': 'PO003', 'Customer_Name': 'Acme Corp'}
        ]
        
        self.agent.validation_results = [
            {
                'PO_Number': 'PO001',
                'Status': 'Exception',
                'Reasons': ['SKU SKU999 not found in master data']
            },
            {
                'PO_Number': 'PO002',
                'Status': 'Exception',
                'Reasons': ['Price deviation of 25.0% exceeds 10% threshold']
            },
            {
                'PO_Number': 'PO003',
                'Status': 'Valid',
                'Reasons': ['Price within acceptable range']
            }
        ]
        
        self.agent.summary_data = {
            'processing_statistics': {
                'validation_success_rate': 80.0
            }
        }
        
        insights = self.agent.generate_insights()
        
        # Verify insights were generated
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        # Check for specific insight patterns
        insights_text = ' '.join(insights)
        self.assertIn('Acme Corp', insights_text)  # Should mention top customer
        
    def test_build_insights_analysis(self):
        """Test building complete insights analysis"""
        # Setup minimal data
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.00}
        ]
        
        self.agent.customer_orders = [
            {'PO_Number': 'PO001', 'Customer_Name': 'Acme Corp'}
        ]
        
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Valid'}
        ]
        
        analysis = self.agent.build_insights_analysis()
        
        # Verify analysis structure
        self.assertIn('customer_contributions', analysis)
        self.assertIn('exception_patterns', analysis)
        self.assertIn('insights', analysis)
        self.assertIn('analysis_timestamp', analysis)
        
        # Verify timestamp format
        self.assertIsInstance(analysis['analysis_timestamp'], str)
        
    def test_generate_executive_dashboard(self):
        """Test generation of executive dashboard"""
        # Setup summary data
        self.agent.summary_data = {
            'total_orders': 3,
            'validated_orders': 2,
            'exceptions': 1,
            'total_sales_value': 405.25,
            'processing_statistics': {
                'validation_success_rate': 66.7
            }
        }
        
        # Setup sales orders for customer contributions
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.00},
            {'Customer': 'Beta Inc', 'Total': 150.25}
        ]
        
        dashboard = self.agent.generate_executive_dashboard()
        
        # Verify dashboard structure
        self.assertIn('title', dashboard)
        self.assertIn('metrics', dashboard)
        self.assertIn('charts', dashboard)
        self.assertIn('generated_timestamp', dashboard)
        
        # Verify metrics
        metrics = dashboard['metrics']
        self.assertIn('total_orders', metrics)
        self.assertIn('validated_orders', metrics)
        self.assertIn('exceptions', metrics)
        self.assertIn('total_sales_value', metrics)
        
        # Verify metric values
        self.assertEqual(metrics['total_orders']['value'], 3)
        self.assertEqual(metrics['validated_orders']['value'], 2)
        self.assertEqual(metrics['exceptions']['value'], 1)
        self.assertEqual(metrics['total_sales_value']['value'], '$405.25')
        
        # Verify charts
        charts = dashboard['charts']
        self.assertIn('validation_success_rate', charts)
        self.assertIn('customer_contributions', charts)
        
    def test_format_executive_report(self):
        """Test formatting of executive report"""
        # Setup summary data
        self.agent.summary_data = {
            'total_orders': 3,
            'validated_orders': 2,
            'exceptions': 1,
            'total_sales_value': 405.25,
            'processing_statistics': {
                'validation_success_rate': 66.7,
                'exception_rate': 33.3
            }
        }
        
        # Setup sales orders
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.00},
            {'Customer': 'Beta Inc', 'Total': 150.25}
        ]
        
        # Mock the build_insights_analysis method
        with patch.object(self.agent, 'build_insights_analysis') as mock_analysis:
            mock_analysis.return_value = {
                'insights': ['Acme Corp contributed 63% of total value'],
                'customer_contributions': {
                    'Acme Corp': {'total_value': 255.00, 'percentage': 62.9, 'order_count': 1},
                    'Beta Inc': {'total_value': 150.25, 'percentage': 37.1, 'order_count': 1}
                },
                'exception_patterns': {'by_customer': {}}
            }
            
            report = self.agent.format_executive_report()
            
        # Verify report content
        self.assertIsInstance(report, str)
        self.assertIn('EXECUTIVE SUMMARY REPORT', report)
        self.assertIn('PROCESSING OVERVIEW', report)
        self.assertIn('KEY INSIGHTS', report)
        self.assertIn('CUSTOMER PERFORMANCE', report)
        self.assertIn('Total Orders Processed: 3', report)
        self.assertIn('Total Sales Value: $405.25', report)
        
    def test_generate_one_line_executive_summary(self):
        """Test generation of one-line executive summary"""
        # Setup summary data
        self.agent.summary_data = {
            'validated_orders': 2,
            'total_sales_value': 1500.0,
            'exceptions': 1
        }
        
        summary = self.agent.generate_one_line_executive_summary()
        
        # Verify summary format
        self.assertIsInstance(summary, str)
        self.assertIn('2 valid customer orders', summary)
        self.assertIn('$1.5K', summary)  # Should format in K
        self.assertIn('one exception auto-handled', summary)
        
    def test_generate_one_line_executive_summary_no_exceptions(self):
        """Test one-line summary with no exceptions"""
        # Setup summary data
        self.agent.summary_data = {
            'validated_orders': 3,
            'total_sales_value': 750.0,
            'exceptions': 0
        }
        
        summary = self.agent.generate_one_line_executive_summary()
        
        # Verify summary format
        self.assertIn('3 customer orders', summary)
        self.assertIn('$750', summary)  # Should not format in K for smaller amounts
        self.assertIn('all orders validated successfully', summary)
        
    def test_process_leadership_query_executive_summary(self):
        """Test leadership query processing for executive summary"""
        # Setup summary data
        self.agent.summary_data = {
            'validated_orders': 2,
            'total_sales_value': 1500.0,
            'exceptions': 1
        }
        
        response = self.agent.process_leadership_query("Generate a one-line executive summary")
        
        self.assertIsInstance(response, str)
        self.assertIn('2 valid customer orders', response)
        self.assertIn('$1.5K', response)
        
    def test_process_leadership_query_total_orders(self):
        """Test leadership query processing for total orders"""
        self.agent.summary_data = {'total_orders': 5}
        
        response = self.agent.process_leadership_query("How many orders were processed?")
        
        self.assertIn('Total orders processed: 5', response)
        
    def test_process_leadership_query_sales_value(self):
        """Test leadership query processing for sales value"""
        self.agent.summary_data = {'total_sales_value': 1234.56}
        
        response = self.agent.process_leadership_query("What's the total sales value?")
        
        self.assertIn('Total sales order value: $1,234.56', response)
        
    def test_process_leadership_query_exceptions(self):
        """Test leadership query processing for exceptions"""
        self.agent.summary_data = {'exceptions': 2}
        
        response = self.agent.process_leadership_query("Were there any exceptions?")
        
        self.assertIn('2 exceptions identified', response)
        self.assertIn('auto-handled with email notifications', response)
        
    def test_process_leadership_query_no_exceptions(self):
        """Test leadership query processing when no exceptions"""
        self.agent.summary_data = {'exceptions': 0}
        
        response = self.agent.process_leadership_query("Were there any exceptions?")
        
        self.assertIn('No exceptions found', response)
        self.assertIn('all orders processed successfully', response)
        
    def test_save_executive_report(self):
        """Test saving executive report to file"""
        # Setup summary data
        self.agent.summary_data = {
            'total_orders': 3,
            'validated_orders': 2,
            'exceptions': 1,
            'total_sales_value': 405.25,
            'processing_statistics': {
                'validation_success_rate': 66.7,
                'exception_rate': 33.3
            }
        }
        
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.00}
        ]
        
        # Mock the build_insights_analysis method
        with patch.object(self.agent, 'build_insights_analysis') as mock_analysis:
            mock_analysis.return_value = {
                'insights': ['Test insight'],
                'customer_contributions': {'Acme Corp': {'total_value': 255.00, 'percentage': 100.0, 'order_count': 1}},
                'exception_patterns': {'by_customer': {}}
            }
            
            report_file = self.agent.save_executive_report(self.test_output_dir)
            
        # Verify file was created
        self.assert_file_exists(report_file)
        
        # Verify file content
        with open(report_file, 'r') as f:
            report_content = f.read()
            
        self.assertIn('EXECUTIVE SUMMARY REPORT', report_content)
        self.assertIn('Total Orders Processed: 3', report_content)
        
    def test_save_dashboard_data(self):
        """Test saving dashboard data to JSON file"""
        # Setup summary data
        self.agent.summary_data = {
            'total_orders': 3,
            'validated_orders': 2,
            'exceptions': 1,
            'total_sales_value': 405.25,
            'processing_statistics': {
                'validation_success_rate': 66.7
            }
        }
        
        self.agent.sales_orders = [
            {'Customer': 'Acme Corp', 'Total': 255.00}
        ]
        
        dashboard_file = self.agent.save_dashboard_data(self.test_output_dir)
        
        # Verify file was created
        self.assert_file_exists(dashboard_file)
        
        # Verify file content
        with open(dashboard_file, 'r') as f:
            dashboard_data = json.load(f)
            
        self.assertIn('title', dashboard_data)
        self.assertIn('metrics', dashboard_data)
        self.assertEqual(dashboard_data['title'], 'Purchase Order Processing Dashboard')
        
    def test_run_summary_insights_agent_complete_workflow(self):
        """Test complete Summary Insights Agent workflow"""
        # Mock all the required methods
        with patch.object(self.agent, 'generate_comprehensive_summary') as mock_summary, \
             patch.object(self.agent, 'display_comprehensive_summary') as mock_display_summary, \
             patch.object(self.agent, 'display_insights_analysis') as mock_display_insights, \
             patch.object(self.agent, 'display_visual_dashboard') as mock_display_dashboard, \
             patch.object(self.agent, 'save_summary_data') as mock_save_summary, \
             patch.object(self.agent, 'save_executive_report') as mock_save_report, \
             patch.object(self.agent, 'save_dashboard_data') as mock_save_dashboard, \
             patch.object(self.agent, 'demonstrate_conversational_queries') as mock_demo, \
             patch.object(self.agent, 'generate_one_line_executive_summary') as mock_one_line, \
             patch('builtins.print') as mock_print:
            
            # Setup mock returns
            mock_summary.return_value = {
                'total_orders': 3,
                'validated_orders': 2,
                'exceptions': 1,
                'total_sales_value': 405.25
            }
            mock_save_summary.return_value = 'summary.json'
            mock_save_report.return_value = 'report.txt'
            mock_save_dashboard.return_value = 'dashboard.json'
            mock_one_line.return_value = 'Test summary line'
            
            result = self.agent.run_summary_insights_agent()
            
        # Verify workflow completed successfully
        self.assertTrue(result['success'])
        self.assertEqual(result['summary']['total_orders'], 3)
        self.assertEqual(result['one_line_summary'], 'Test summary line')
        self.assertEqual(len(result['files_generated']), 3)
        
        # Verify all methods were called
        self.assertTrue(mock_summary.called)
        self.assertTrue(mock_display_summary.called)
        self.assertTrue(mock_display_insights.called)
        self.assertTrue(mock_display_dashboard.called)
        self.assertTrue(mock_save_summary.called)
        self.assertTrue(mock_save_report.called)
        self.assertTrue(mock_save_dashboard.called)
        self.assertTrue(mock_demo.called)


if __name__ == '__main__':
    unittest.main()