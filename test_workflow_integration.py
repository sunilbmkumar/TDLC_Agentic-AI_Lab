#!/usr/bin/env python3
"""
Workflow Integration Tests
Focused tests for the complete PO to SO transformation pipeline
"""

import sys
import os
import json
import csv
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def setup_test_data():
    """Setup test data for integration testing"""
    print("🔧 Setting up test data...")
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    # Create customer orders CSV
    customer_orders = [
        {"PO_Number": "PO1001", "Customer": "ACME Corp", "SKU": "SKU001", "Quantity": 100, "Price": 50.00},
        {"PO_Number": "PO1002", "Customer": "Zenith Ltd", "SKU": "SKU002", "Quantity": 50, "Price": 100.00},
        {"PO_Number": "PO1003", "Customer": "Valid Corp", "SKU": "SKU004", "Quantity": 75, "Price": 80.00},
        {"PO_Number": "PO1004", "Customer": "Innova Inc", "SKU": "SKU999", "Quantity": 25, "Price": 150.00}
    ]
    
    with open('data/customer_orders.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=customer_orders[0].keys())
        writer.writeheader()
        writer.writerows(customer_orders)
    
    # Create master SKU CSV
    master_sku = [
        {"SKU": "SKU001", "Product_Name": "Widget A", "Reference_Price": 50.00},
        {"SKU": "SKU002", "Product_Name": "Widget B", "Reference_Price": 100.00},
        {"SKU": "SKU004", "Product_Name": "Widget D", "Reference_Price": 80.00}
    ]
    
    with open('data/master_sku.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=master_sku[0].keys())
        writer.writeheader()
        writer.writerows(master_sku)
    
    print("✅ Test data created")
    return len(customer_orders), len(master_sku)

def test_sequential_pipeline():
    """Test sequential pipeline execution"""
    print("\n=== Testing Sequential Pipeline ===")
    
    try:
        from orchestration.agent_pipeline import AgentExecutionPipeline
        
        # Create and execute pipeline
        pipeline = AgentExecutionPipeline()
        results = pipeline.execute_pipeline()
        
        # Validate results
        completed_agents = sum(1 for result in results.values() if result.status.value == 'completed')
        failed_agents = sum(1 for result in results.values() if result.status.value == 'failed')
        
        print(f"  Completed agents: {completed_agents}")
        print(f"  Failed agents: {failed_agents}")
        
        # Check shared data
        shared_data = pipeline.shared_data
        print(f"  Customer orders: {len(shared_data.get('customer_orders', []))}")
        print(f"  Validation results: {len(shared_data.get('validation_results', []))}")
        print(f"  Sales orders: {len(shared_data.get('sales_orders', []))}")
        
        if completed_agents >= 4:  # At least 4 agents should complete
            print("✅ Sequential pipeline test PASSED")
            return True
        else:
            print("❌ Sequential pipeline test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Sequential pipeline test FAILED: {e}")
        return False

def test_coordinated_execution():
    """Test coordinated execution with orchestration manager"""
    print("\n=== Testing Coordinated Execution ===")
    
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        
        # Create and execute orchestrated workflow
        manager = OrchestrationManager()
        
        # Validate configuration first
        validation = manager.validate_configuration()
        if not validation['valid']:
            print(f"❌ Configuration validation failed: {validation['errors']}")
            return False
        
        # Execute workflow
        results = manager.execute_workflow()
        
        # Validate results
        completed_agents = sum(1 for result in results.values() if result.status.value == 'completed')
        failed_agents = sum(1 for result in results.values() if result.status.value == 'failed')
        
        print(f"  Completed agents: {completed_agents}")
        print(f"  Failed agents: {failed_agents}")
        
        # Get workflow status
        status = manager.get_workflow_status()
        data_summary = status.get('shared_data_summary', {})
        
        print(f"  Customer orders processed: {data_summary.get('customer_orders', 0)}")
        print(f"  Validation results: {data_summary.get('validation_results', 0)}")
        print(f"  Sales orders created: {data_summary.get('sales_orders', 0)}")
        print(f"  Exception emails: {data_summary.get('exception_emails', 0)}")
        
        if completed_agents >= 4:  # At least 4 agents should complete
            print("✅ Coordinated execution test PASSED")
            return True
        else:
            print("❌ Coordinated execution test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Coordinated execution test FAILED: {e}")
        return False

def test_exception_handling():
    """Test exception handling in the workflow"""
    print("\n=== Testing Exception Handling ===")
    
    try:
        # Check if validation results contain exceptions
        if os.path.exists('outputs/validation_results_detailed.json'):
            with open('outputs/validation_results_detailed.json', 'r') as f:
                validation_results = json.load(f)
            
            exceptions = [r for r in validation_results if r.get('Status') == 'Exception']
            valid_orders = [r for r in validation_results if r.get('Status') == 'Valid']
            
            print(f"  Valid orders: {len(valid_orders)}")
            print(f"  Exception orders: {len(exceptions)}")
            
            # Check if exception emails were generated
            if os.path.exists('outputs/exception_emails.json'):
                with open('outputs/exception_emails.json', 'r') as f:
                    emails = json.load(f)
                
                print(f"  Exception emails generated: {len(emails)}")
                
                # Validate email structure
                for email in emails:
                    if not all(key in email for key in ['to', 'subject', 'message']):
                        print("❌ Exception email missing required fields")
                        return False
            
            # Check if sales orders were created only for valid orders
            if os.path.exists('outputs/sales_order_output.csv'):
                with open('outputs/sales_order_output.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    sales_orders = list(reader)
                
                print(f"  Sales orders created: {len(sales_orders)}")
                
                if len(sales_orders) == len(valid_orders):
                    print("✅ Exception handling test PASSED")
                    return True
                else:
                    print("❌ Sales order count doesn't match valid orders")
                    return False
            else:
                print("❌ Sales order output file not found")
                return False
        else:
            print("❌ Validation results file not found")
            return False
            
    except Exception as e:
        print(f"❌ Exception handling test FAILED: {e}")
        return False

def test_data_transformation():
    """Test complete data transformation from PO to SO"""
    print("\n=== Testing Data Transformation ===")
    
    try:
        # Read original customer orders
        original_orders = []
        if os.path.exists('data/customer_orders.csv'):
            with open('data/customer_orders.csv', 'r') as f:
                reader = csv.DictReader(f)
                original_orders = list(reader)
        
        # Read validation results
        validation_results = []
        if os.path.exists('outputs/validation_results_detailed.json'):
            with open('outputs/validation_results_detailed.json', 'r') as f:
                validation_results = json.load(f)
        
        # Read sales orders
        sales_orders = []
        if os.path.exists('outputs/sales_order_output.csv'):
            with open('outputs/sales_order_output.csv', 'r') as f:
                reader = csv.DictReader(f)
                sales_orders = list(reader)
        
        print(f"  Original orders: {len(original_orders)}")
        print(f"  Validation results: {len(validation_results)}")
        print(f"  Sales orders: {len(sales_orders)}")
        
        # Validate transformation logic
        valid_pos = [r['PO_Number'] for r in validation_results if r.get('Status') == 'Valid']
        so_pos = []
        
        for so in sales_orders:
            # Extract PO number from SO number (assuming SO2001 -> PO1001 mapping)
            so_number = so.get('SO_Number', '')
            if so_number.startswith('SO'):
                po_number = 'PO' + so_number[2:]
                so_pos.append(po_number)
        
        # Check if all valid POs became SOs
        missing_sos = set(valid_pos) - set(so_pos)
        if missing_sos:
            print(f"❌ Missing sales orders for valid POs: {missing_sos}")
            return False
        
        print("✅ Data transformation test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Data transformation test FAILED: {e}")
        return False

def test_output_file_generation():
    """Test that all expected output files are generated"""
    print("\n=== Testing Output File Generation ===")
    
    expected_files = [
        'outputs/validation_results_detailed.json',
        'outputs/sales_order_output.csv',
        'outputs/exception_emails.json',
        'outputs/summary_report.json'
    ]
    
    missing_files = []
    for file_path in expected_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            # Check if file has content
            if os.path.getsize(file_path) == 0:
                missing_files.append(f"{file_path} (empty)")
    
    if missing_files:
        print(f"❌ Missing or empty files: {missing_files}")
        return False
    else:
        print("✅ All expected output files generated")
        return True

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Workflow Integration Tests")
    print("=" * 50)
    
    # Setup test environment
    order_count, sku_count = setup_test_data()
    print(f"Test data: {order_count} orders, {sku_count} SKUs")
    
    # Run tests
    tests = [
        ("Sequential Pipeline", test_sequential_pipeline),
        ("Coordinated Execution", test_coordinated_execution),
        ("Exception Handling", test_exception_handling),
        ("Data Transformation", test_data_transformation),
        ("Output File Generation", test_output_file_generation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Running: {test_name}")
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All integration tests PASSED!")
        print("The complete PO to SO workflow is working correctly.")
        return True
    else:
        print(f"\n❌ {failed} integration tests FAILED!")
        print("Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)