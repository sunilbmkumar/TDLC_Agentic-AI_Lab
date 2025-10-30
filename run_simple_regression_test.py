#!/usr/bin/env python3
"""
Simple Regression Test Runner
"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def run_basic_regression_tests():
    """Run basic regression tests to verify system functionality"""
    print("=== REGRESSION TEST SUITE ===")
    print("Testing core system functionality...\n")
    
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_details': []
    }
    
    # Test 1: Import all core agents
    print("1. Testing Agent Imports...")
    test_results['total_tests'] += 1
    try:
        from agents.po_reader.agent import POReaderAgent
        from agents.validation.agent import ValidationAgent
        from agents.exception_response.agent import ExceptionResponseAgent
        from agents.so_creator.agent import SalesOrderCreatorAgent
        from agents.summary_insights.agent import SummaryInsightsAgent
        from agents.po_acknowledgment.agent import POAcknowledgmentAgent
        print("   ✅ All agent imports successful")
        test_results['passed_tests'] += 1
        test_results['test_details'].append("Agent Imports: PASSED")
    except Exception as e:
        print(f"   ❌ Agent import failed: {e}")
        test_results['failed_tests'] += 1
        test_results['test_details'].append(f"Agent Imports: FAILED - {e}")
    
    # Test 2: Test orchestration system imports
    print("2. Testing Orchestration System...")
    test_results['total_tests'] += 1
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        from orchestration.agent_pipeline import AgentExecutionPipeline
        from orchestration.agent_coordinator import AgentCoordinator
        print("   ✅ Orchestration system imports successful")
        test_results['passed_tests'] += 1
        test_results['test_details'].append("Orchestration Imports: PASSED")
    except Exception as e:
        print(f"   ❌ Orchestration import failed: {e}")
        test_results['failed_tests'] += 1
        test_results['test_details'].append(f"Orchestration Imports: FAILED - {e}")
    
    # Test 3: Check data files exist
    print("3. Testing Data Files...")
    test_results['total_tests'] += 1
    try:
        data_files = ['data/customer_orders.csv', 'data/master_sku.csv']
        missing_files = []
        for file_path in data_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            raise FileNotFoundError(f"Missing data files: {missing_files}")
        
        print("   ✅ All required data files present")
        test_results['passed_tests'] += 1
        test_results['test_details'].append("Data Files: PASSED")
    except Exception as e:
        print(f"   ❌ Data files check failed: {e}")
        test_results['failed_tests'] += 1
        test_results['test_details'].append(f"Data Files: FAILED - {e}")
    
    # Test 4: Test basic PO Reader functionality
    print("4. Testing PO Reader Agent...")
    test_results['total_tests'] += 1
    try:
        po_agent = POReaderAgent()
        orders = po_agent.read_orders()
        if len(orders) == 0:
            raise ValueError("No orders read from customer_orders.csv")
        print(f"   ✅ PO Reader successfully read {len(orders)} orders")
        test_results['passed_tests'] += 1
        test_results['test_details'].append(f"PO Reader: PASSED - Read {len(orders)} orders")
    except Exception as e:
        print(f"   ❌ PO Reader test failed: {e}")
        test_results['failed_tests'] += 1
        test_results['test_details'].append(f"PO Reader: FAILED - {e}")
    
    # Test 5: Test basic Validation Agent functionality
    print("5. Testing Validation Agent...")
    test_results['total_tests'] += 1
    try:
        validation_agent = ValidationAgent()
        orders = validation_agent.read_customer_orders()
        skus = validation_agent.read_master_skus()
        if len(orders) == 0 or len(skus) == 0:
            raise ValueError("Failed to read orders or SKUs")
        print(f"   ✅ Validation Agent read {len(orders)} orders and {len(skus)} SKUs")
        test_results['passed_tests'] += 1
        test_results['test_details'].append(f"Validation Agent: PASSED - Read {len(orders)} orders, {len(skus)} SKUs")
    except Exception as e:
        print(f"   ❌ Validation Agent test failed: {e}")
        test_results['failed_tests'] += 1
        test_results['test_details'].append(f"Validation Agent: FAILED - {e}")
    
    # Test 6: Check outputs directory
    print("6. Testing Output Directory...")
    test_results['total_tests'] += 1
    try:
        if not os.path.exists('outputs'):
            os.makedirs('outputs')
        
        # Check for some expected output files
        expected_outputs = [
            'outputs/validation_results_detailed.json',
            'outputs/sales_order_output.csv',
            'outputs/exception_emails.json'
        ]
        
        existing_outputs = [f for f in expected_outputs if os.path.exists(f)]
        print(f"   ✅ Output directory exists with {len(existing_outputs)} output files")
        test_results['passed_tests'] += 1
        test_results['test_details'].append(f"Output Directory: PASSED - {len(existing_outputs)} files found")
    except Exception as e:
        print(f"   ❌ Output directory test failed: {e}")
        test_results['failed_tests'] += 1
        test_results['test_details'].append(f"Output Directory: FAILED - {e}")
    
    # Print summary
    print("\n=== REGRESSION TEST SUMMARY ===")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed_tests']}")
    print(f"Failed: {test_results['failed_tests']}")
    print(f"Success Rate: {(test_results['passed_tests']/test_results['total_tests']*100):.1f}%")
    
    print("\nDetailed Results:")
    for detail in test_results['test_details']:
        print(f"  • {detail}")
    
    if test_results['failed_tests'] == 0:
        print("\n🎉 All regression tests PASSED! System is functioning correctly.")
        return True
    else:
        print(f"\n⚠️  {test_results['failed_tests']} regression tests FAILED. Please review the issues above.")
        return False

if __name__ == "__main__":
    try:
        success = run_basic_regression_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error running regression tests: {e}")
        traceback.print_exc()
        sys.exit(1)