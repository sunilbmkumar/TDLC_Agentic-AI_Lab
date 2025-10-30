"""
Unit tests for Exception Response Agent.
Tests email generation, content formatting, delivery simulation, and error handling.
"""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from agents.exception_response.agent import ExceptionResponseAgent


class TestExceptionResponseAgent(BaseAgentTest):
    """Unit tests for Exception Response Agent functionality"""
    
    def setUp(self):
        """Setup test environment for Exception Response Agent tests"""
        super().setUp()
        self.agent = ExceptionResponseAgent()
        
    def create_test_validation_results(self, results_data):
        """Helper method to create test validation results JSON file"""
        results_file = os.path.join(self.test_output_dir, 'validation_results_detailed.json')
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        return results_file
        
    def test_load_validation_results_success(self):
        """Test successful loading of validation results"""
        test_results = [
            {
                'PO_Number': 'PO001',
                'SKU': 'SKU001',
                'Status': 'Exception',
                'Reasons': ['SKU SKU001 not found in master data'],
                'Details': {'order_price': 25.50, 'reference_price': None}
            },
            {
                'PO_Number': 'PO002',
                'SKU': 'SKU002',
                'Status': 'Valid',
                'Reasons': ['Price within acceptable range'],
                'Details': {'order_price': 15.75, 'reference_price': 15.00}
            }
        ]
        
        results_file = self.create_test_validation_results(test_results)
        
        loaded_results = self.agent.load_validation_results(results_file)
        
        # Verify results were loaded correctly
        self.assertEqual(len(loaded_results), 2)
        self.assertEqual(loaded_results[0]['PO_Number'], 'PO001')
        self.assertEqual(loaded_results[0]['Status'], 'Exception')
        self.assertEqual(self.agent.validation_results, test_results)
        
    def test_load_validation_results_file_not_found(self):
        """Test handling of missing validation results file"""
        loaded_results = self.agent.load_validation_results("nonexistent_file.json")
        
        self.assertEqual(loaded_results, [])
        self.assertEqual(len(self.agent.validation_results), 0)
        
    def test_load_validation_results_invalid_json(self):
        """Test handling of invalid JSON in validation results file"""
        # Create invalid JSON file
        invalid_file = os.path.join(self.test_output_dir, 'invalid.json')
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json content")
            
        loaded_results = self.agent.load_validation_results(invalid_file)
        
        self.assertEqual(loaded_results, [])
        
    def test_detect_exceptions(self):
        """Test detection of exception orders from validation results"""
        self.agent.validation_results = [
            {'PO_Number': 'PO001', 'Status': 'Exception'},
            {'PO_Number': 'PO002', 'Status': 'Valid'},
            {'PO_Number': 'PO003', 'Status': 'Exception'},
            {'PO_Number': 'PO004', 'Status': 'Valid'}
        ]
        
        exceptions = self.agent.detect_exceptions()
        
        # Verify only exception orders are returned
        self.assertEqual(len(exceptions), 2)
        self.assertEqual(exceptions[0]['PO_Number'], 'PO001')
        self.assertEqual(exceptions[1]['PO_Number'], 'PO003')
        
    def test_get_customer_email(self):
        """Test customer email lookup based on PO number"""
        # Test known PO numbers
        self.assertEqual(self.agent.get_customer_email('PO1001'), 'orders@acmecorp.com')
        self.assertEqual(self.agent.get_customer_email('PO1002'), 'purchasing@zenithltd.com')
        self.assertEqual(self.agent.get_customer_email('PO1003'), 'orders@acmecorp.com')
        self.assertEqual(self.agent.get_customer_email('PO1004'), 'procurement@innovainc.com')
        
        # Test unknown PO number
        self.assertEqual(self.agent.get_customer_email('PO9999'), 'unknown@customer.com')
        
    def test_get_customer_name(self):
        """Test customer name lookup based on PO number"""
        # Test known PO numbers
        self.assertEqual(self.agent.get_customer_name('PO1001'), 'ACME Corp')
        self.assertEqual(self.agent.get_customer_name('PO1002'), 'Zenith Ltd')
        self.assertEqual(self.agent.get_customer_name('PO1003'), 'ACME Corp')
        self.assertEqual(self.agent.get_customer_name('PO1004'), 'Innova Inc')
        
        # Test unknown PO number
        self.assertEqual(self.agent.get_customer_name('PO9999'), 'Unknown Customer')
        
    def test_generate_sku_not_found_email(self):
        """Test generation of SKU not found email template"""
        exception_data = {
            'PO_Number': 'PO1001',
            'SKU': 'INVALID_SKU',
            'Status': 'Exception',
            'Reasons': ['SKU INVALID_SKU not found in master data']
        }
        
        email = self.agent.generate_sku_not_found_email(exception_data)
        
        # Verify email structure
        self.assertIn('to', email)
        self.assertIn('customer_email', email)
        self.assertIn('customer_name', email)
        self.assertIn('subject', email)
        self.assertIn('message', email)
        self.assertIn('po_number', email)
        self.assertIn('exception_type', email)
        self.assertIn('timestamp', email)
        self.assertIn('delivery_status', email)
        
        # Verify email content
        self.assertEqual(email['customer_name'], 'ACME Corp')
        self.assertEqual(email['customer_email'], 'orders@acmecorp.com')
        self.assertEqual(email['po_number'], 'PO1001')
        self.assertEqual(email['exception_type'], 'SKU_NOT_FOUND')
        self.assertIn('Invalid SKU Found', email['subject'])
        self.assertIn('INVALID_SKU is invalid', email['message'])
        
    def test_generate_price_deviation_email(self):
        """Test generation of price deviation email template"""
        exception_data = {
            'PO_Number': 'PO1002',
            'SKU': 'SKU001',
            'Status': 'Exception',
            'Reasons': ['Price deviation of 25.0% exceeds 10% threshold for SKU001'],
            'Details': {
                'order_price': 31.25,
                'reference_price': 25.00,
                'price_deviation': 25.0
            }
        }
        
        email = self.agent.generate_price_deviation_email(exception_data)
        
        # Verify email content
        self.assertEqual(email['customer_name'], 'Zenith Ltd')
        self.assertEqual(email['customer_email'], 'purchasing@zenithltd.com')
        self.assertEqual(email['po_number'], 'PO1002')
        self.assertEqual(email['exception_type'], 'PRICE_DEVIATION')
        self.assertIn('Price Deviation Alert', email['subject'])
        self.assertIn('25.0% detected', email['message'])
        self.assertIn('$31.25', email['message'])
        self.assertIn('$25.00', email['message'])
        
    def test_generate_generic_exception_email(self):
        """Test generation of generic exception email template"""
        exception_data = {
            'PO_Number': 'PO1003',
            'SKU': 'SKU002',
            'Status': 'Exception',
            'Reasons': ['Unknown validation error']
        }
        
        email = self.agent.generate_generic_exception_email(exception_data)
        
        # Verify email content
        self.assertEqual(email['customer_name'], 'ACME Corp')
        self.assertEqual(email['exception_type'], 'GENERIC')
        self.assertIn('Order Processing Issue', email['subject'])
        self.assertIn('Unknown validation error', email['message'])
        
    def test_generate_automated_email_responses_sku_not_found(self):
        """Test automated email generation for SKU not found exceptions"""
        self.agent.validation_results = [
            {
                'PO_Number': 'PO1001',
                'SKU': 'INVALID_SKU',
                'Status': 'Exception',
                'Reasons': ['SKU INVALID_SKU not found in master data']
            }
        ]
        
        emails = self.agent.generate_automated_email_responses()
        
        # Verify email was generated
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['exception_type'], 'SKU_NOT_FOUND')
        self.assertEqual(emails[0]['po_number'], 'PO1001')
        
    def test_generate_automated_email_responses_price_deviation(self):
        """Test automated email generation for price deviation exceptions"""
        self.agent.validation_results = [
            {
                'PO_Number': 'PO1002',
                'SKU': 'SKU001',
                'Status': 'Exception',
                'Reasons': ['Price deviation of 25.0% exceeds 10% threshold for SKU001'],
                'Details': {
                    'order_price': 31.25,
                    'reference_price': 25.00,
                    'price_deviation': 25.0
                }
            }
        ]
        
        emails = self.agent.generate_automated_email_responses()
        
        # Verify email was generated
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['exception_type'], 'PRICE_DEVIATION')
        self.assertEqual(emails[0]['po_number'], 'PO1002')
        
    def test_generate_automated_email_responses_mixed_exceptions(self):
        """Test automated email generation for mixed exception types"""
        self.agent.validation_results = [
            {
                'PO_Number': 'PO1001',
                'SKU': 'INVALID_SKU',
                'Status': 'Exception',
                'Reasons': ['SKU INVALID_SKU not found in master data']
            },
            {
                'PO_Number': 'PO1002',
                'SKU': 'SKU001',
                'Status': 'Exception',
                'Reasons': ['Price deviation of 25.0% exceeds 10% threshold for SKU001'],
                'Details': {
                    'order_price': 31.25,
                    'reference_price': 25.00,
                    'price_deviation': 25.0
                }
            },
            {
                'PO_Number': 'PO1003',
                'SKU': 'SKU002',
                'Status': 'Valid',
                'Reasons': ['Price within acceptable range']
            }
        ]
        
        emails = self.agent.generate_automated_email_responses()
        
        # Verify only exception emails were generated
        self.assertEqual(len(emails), 2)
        
        # Verify email types
        email_types = [email['exception_type'] for email in emails]
        self.assertIn('SKU_NOT_FOUND', email_types)
        self.assertIn('PRICE_DEVIATION', email_types)
        
    def test_save_email_responses(self):
        """Test saving email responses to JSON file"""
        self.agent.exception_emails = [
            {
                'to': 'ACME Corp',
                'customer_email': 'orders@acmecorp.com',
                'subject': 'Test Subject',
                'message': 'Test Message',
                'po_number': 'PO1001',
                'exception_type': 'SKU_NOT_FOUND'
            }
        ]
        
        email_file = self.agent.save_email_responses(self.test_output_dir)
        
        # Verify file was created
        self.assert_file_exists(email_file)
        
        # Verify file content
        with open(email_file, 'r') as f:
            saved_emails = json.load(f)
            
        self.assertEqual(len(saved_emails), 1)
        self.assertEqual(saved_emails[0]['po_number'], 'PO1001')
        
    def test_process_exceptions_complete_workflow(self):
        """Test complete exception processing workflow"""
        # Setup test validation results
        test_results = [
            {
                'PO_Number': 'PO1001',
                'SKU': 'INVALID_SKU',
                'Status': 'Exception',
                'Reasons': ['SKU INVALID_SKU not found in master data']
            }
        ]
        results_file = self.create_test_validation_results(test_results)
        
        # Mock the load_validation_results to use our test file
        with patch.object(self.agent, 'load_validation_results') as mock_load, \
             patch.object(self.agent, 'save_email_responses') as mock_save, \
             patch('builtins.print') as mock_print:
            
            mock_load.return_value = test_results
            mock_save.return_value = 'test_emails.json'
            
            emails = self.agent.process_exceptions()
            
        # Verify workflow completed
        self.assertTrue(mock_load.called)
        self.assertTrue(mock_save.called)
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['exception_type'], 'SKU_NOT_FOUND')
        
    def test_get_exception_summary(self):
        """Test generation of exception summary"""
        self.agent.exception_emails = [
            {'exception_type': 'SKU_NOT_FOUND', 'po_number': 'PO1001'},
            {'exception_type': 'PRICE_DEVIATION', 'po_number': 'PO1002'},
            {'exception_type': 'SKU_NOT_FOUND', 'po_number': 'PO1003'}
        ]
        
        summary = self.agent.get_exception_summary()
        
        # Verify summary structure
        self.assertIn('total_exceptions', summary)
        self.assertIn('exception_types', summary)
        self.assertIn('emails_generated', summary)
        
        # Verify summary values
        self.assertEqual(summary['total_exceptions'], 3)
        self.assertEqual(summary['exception_types']['SKU_NOT_FOUND'], 2)
        self.assertEqual(summary['exception_types']['PRICE_DEVIATION'], 1)
        
    def test_display_email_log(self):
        """Test display of email log"""
        self.agent.exception_emails = [
            {
                'po_number': 'PO1001',
                'customer_name': 'ACME Corp',
                'subject': 'Invalid SKU Found',
                'message': 'Test message',
                'exception_type': 'SKU_NOT_FOUND',
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        
        # Capture output
        with patch('builtins.print') as mock_print:
            self.agent.display_email_log()
            
        # Verify print was called with email log content
        self.assertTrue(mock_print.called)
        
        # Check that email log was displayed
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        output_content = '\n'.join(print_calls)
        
        self.assertIn('EXCEPTION EMAIL RESPONSE LOG', output_content)
        self.assertIn('PO1001', output_content)
        self.assertIn('ACME Corp', output_content)
        
    def test_display_formatted_email_responses(self):
        """Test display of formatted email responses"""
        self.agent.exception_emails = [
            {
                'customer_name': 'ACME Corp',
                'subject': 'Invalid SKU Found',
                'message': 'The product code INVALID_SKU is invalid. Please review and resend your order.'
            }
        ]
        
        # Capture output
        with patch('builtins.print') as mock_print:
            self.agent.display_formatted_email_responses()
            
        # Verify print was called
        self.assertTrue(mock_print.called)
        
        # Check output format
        print_calls = [call[0][0] for call in mock_print.call_args_list if call[0]]
        output_content = '\n'.join(print_calls)
        
        self.assertIn('AUTO-RESPONSE EMAIL LOG', output_content)
        self.assertIn('To: ACME Corp', output_content)
        self.assertIn('Subject: Invalid SKU Found', output_content)
        
    def test_simulate_email_delivery(self):
        """Test email delivery simulation"""
        test_email = {
            'po_number': 'PO1001',
            'customer_name': 'ACME Corp',
            'to': 'ACME Corp',
            'subject': 'Test Subject',
            'message': 'Test message',
            'exception_type': 'SKU_NOT_FOUND'
        }
        
        # Mock random to ensure predictable results
        with patch('random.random', return_value=0.9):  # Should succeed (< 0.95)
            delivery_record = self.agent.simulate_email_delivery(test_email)
            
        # Verify delivery record structure
        self.assertIn('email_id', delivery_record)
        self.assertIn('po_number', delivery_record)
        self.assertIn('recipient_email', delivery_record)
        self.assertIn('recipient_name', delivery_record)
        self.assertIn('delivery_status', delivery_record)
        self.assertIn('delivery_timestamp', delivery_record)
        self.assertIn('smtp_response', delivery_record)
        
        # Verify successful delivery
        self.assertEqual(delivery_record['delivery_status'], 'DELIVERED')
        self.assertEqual(delivery_record['smtp_response'], '250 OK')
        
    def test_simulate_email_delivery_failure_and_retry(self):
        """Test email delivery simulation with failure and retry"""
        test_email = {
            'po_number': 'PO1001',
            'customer_name': 'ACME Corp',
            'to': 'ACME Corp',
            'subject': 'Test Subject',
            'message': 'Test message',
            'exception_type': 'SKU_NOT_FOUND'
        }
        
        # Mock random to simulate failure then success on retry
        with patch('random.random', side_effect=[0.97, 0.7]):  # First call fails, second succeeds
            delivery_record = self.agent.simulate_email_delivery(test_email)
            
        # Verify retry was successful
        self.assertEqual(delivery_record['delivery_status'], 'DELIVERED')
        self.assertEqual(delivery_record['delivery_attempt'], 2)
        self.assertIn('retry successful', delivery_record['smtp_response'])
        
    def test_send_exception_emails(self):
        """Test sending exception emails with delivery simulation"""
        self.agent.exception_emails = [
            {
                'po_number': 'PO1001',
                'customer_name': 'ACME Corp',
                'to': 'ACME Corp',
                'subject': 'Test Subject',
                'message': 'Test message',
                'exception_type': 'SKU_NOT_FOUND'
            }
        ]
        
        # Mock delivery simulation
        with patch.object(self.agent, 'simulate_email_delivery') as mock_delivery, \
             patch.object(self.agent, 'create_audit_trail_entry') as mock_audit, \
             patch('builtins.print') as mock_print:
            
            mock_delivery.return_value = {
                'email_id': 'email_0001',
                'delivery_status': 'DELIVERED',
                'smtp_response': '250 OK'
            }
            mock_audit.return_value = {'audit_id': 'audit_000001'}
            
            delivery_results = self.agent.send_exception_emails()
            
        # Verify emails were processed
        self.assertEqual(len(delivery_results), 1)
        self.assertTrue(mock_delivery.called)
        self.assertTrue(mock_audit.called)
        self.assertEqual(len(self.agent.email_delivery_log), 1)
        self.assertEqual(len(self.agent.email_audit_trail), 1)
        
    def test_create_audit_trail_entry(self):
        """Test creation of audit trail entries"""
        test_email = {
            'po_number': 'PO1001',
            'customer_name': 'ACME Corp',
            'to': 'ACME Corp',
            'subject': 'Test Subject',
            'message': 'Test message',
            'exception_type': 'SKU_NOT_FOUND'
        }
        
        test_delivery_record = {
            'delivery_status': 'DELIVERED',
            'delivery_timestamp': '2024-01-01T12:00:00',
            'delivery_attempt': 1,
            'smtp_response': '250 OK'
        }
        
        audit_entry = self.agent.create_audit_trail_entry(test_email, test_delivery_record)
        
        # Verify audit entry structure
        self.assertIn('audit_id', audit_entry)
        self.assertIn('timestamp', audit_entry)
        self.assertIn('event_type', audit_entry)
        self.assertIn('po_number', audit_entry)
        self.assertIn('customer_name', audit_entry)
        self.assertIn('compliance_flags', audit_entry)
        self.assertIn('system_metadata', audit_entry)
        
        # Verify audit entry content
        self.assertEqual(audit_entry['event_type'], 'EMAIL_SENT')
        self.assertEqual(audit_entry['po_number'], 'PO1001')
        self.assertTrue(audit_entry['compliance_flags']['gdpr_compliant'])
        self.assertEqual(audit_entry['compliance_flags']['retention_period_days'], 2555)
        
    def test_get_delivery_statistics(self):
        """Test generation of delivery statistics"""
        # Setup delivery log
        self.agent.email_delivery_log = [
            {'delivery_status': 'DELIVERED', 'delivery_attempt': 1},
            {'delivery_status': 'DELIVERED', 'delivery_attempt': 2},
            {'delivery_status': 'FAILED', 'delivery_attempt': 1}
        ]
        
        # Setup audit trail
        self.agent.email_audit_trail = [
            {'audit_id': 'audit_001'},
            {'audit_id': 'audit_002'},
            {'audit_id': 'audit_003'}
        ]
        
        stats = self.agent.get_delivery_statistics()
        
        # Verify statistics
        self.assertEqual(stats['total_emails'], 3)
        self.assertEqual(stats['delivered'], 2)
        self.assertEqual(stats['failed'], 1)
        self.assertAlmostEqual(stats['success_rate'], 66.67, places=1)
        self.assertAlmostEqual(stats['retry_rate'], 33.33, places=1)
        self.assertEqual(stats['delivery_log_entries'], 3)
        self.assertEqual(stats['audit_trail_entries'], 3)
        
    def test_get_delivery_statistics_no_data(self):
        """Test delivery statistics with no data"""
        stats = self.agent.get_delivery_statistics()
        
        # Verify empty statistics
        self.assertEqual(stats['total_emails'], 0)
        self.assertEqual(stats['delivered'], 0)
        self.assertEqual(stats['failed'], 0)
        self.assertEqual(stats['success_rate'], 0.0)
        self.assertEqual(stats['retry_rate'], 0.0)
        
    def test_process_leadership_query_show_exceptions(self):
        """Test leadership query processing for showing exception messages"""
        self.agent.exception_emails = [
            {
                'po_number': 'PO1001',
                'customer_name': 'ACME Corp',
                'subject': 'Invalid SKU Found',
                'message': 'Test message',
                'exception_type': 'SKU_NOT_FOUND'
            }
        ]
        
        response = self.agent.process_leadership_query("Show me all exception messages generated today")
        
        self.assertIsInstance(response, str)
        self.assertIn('Exception Messages Generated Today', response)
        self.assertIn('PO1001', response)
        self.assertIn('ACME Corp', response)
        
    def test_process_leadership_query_exception_count(self):
        """Test leadership query processing for exception counts"""
        self.agent.exception_emails = [
            {'exception_type': 'SKU_NOT_FOUND'},
            {'exception_type': 'PRICE_DEVIATION'}
        ]
        
        response = self.agent.process_leadership_query("How many exceptions occurred?")
        
        self.assertIsInstance(response, str)
        self.assertIn('Total Exceptions Today: 2', response)
        self.assertIn('SKU_NOT_FOUND: 1', response)
        self.assertIn('PRICE_DEVIATION: 1', response)
        
    def test_process_leadership_query_no_exceptions(self):
        """Test leadership query processing when no exceptions exist"""
        response = self.agent.process_leadership_query("Show me all exception messages generated today")
        
        self.assertIsInstance(response, str)
        self.assertIn('No exception messages have been generated today', response)
        self.assertIn('All orders passed validation successfully', response)


if __name__ == '__main__':
    unittest.main()