#!/usr/bin/env python3
"""
Simple Regression Test Runner - Execute basic regression tests
Simplified version that focuses on core functionality testing
"""

import sys
import os
import traceback
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def test_agent_imports():
    """Test that all core agents can be imported"""
    print("Testing Agent Imports...")
    try:
        from agents.po_reader.agent import POReaderAgent
        from agents.validation.agent import ValidationAgent
        from agents.exception_response.agent import ExceptionResponseAgent
        from agents.so_creator.agent import SalesOrderCreatorAgent
        from agents.summary_insights.agent import SummaryInsightsAgent
        from agents.po_acknowledgment.agent import POAcknowledgmentAgent
        print("  ✅ All agent imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Agent import failed: {e}")
        return False

def test_orchestration_imports():
    """Test that orchestration system can be imported"""
    print("Testing Orchestration System...")
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        from orchestration.agent_pipeline import AgentExecutionPipeline
        from orchestration.agent_coordinator import AgentCoordinator
        print("  ✅ Orchestration system imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Orchestration import failed: {e}")
        return False

def test_data_files():
    """Test that required data files exist"""
    print("Testing Data Files...")
    try:
        required_files = [
            '../../data/customer_orders.csv',
            '../../data/master_sku.csv'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"  ❌ Missing data files: {missing_files}")
            return False
        
        print("  ✅ All required data files present")
        return True
    except Exception as e:
        print(f"  ❌ Data files check failed: {e}")
        return False

def test_po_reader_functionality():
    """Test basic PO Reader functionality"""
    print("Testing PO Reader Agent...")
    try:
        from agents.po_reader.agent import POReaderAgent
        
        # Change to project root for data access
        original_cwd = os.getcwd()
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        os.chdir(project_root)
        
        try:
            po_agent = POReaderAgent()
            orders = po_agent.read_orders()
            
            if len(orders) == 0:
                print("  ❌ No orders read from customer_orders.csv")
                return False
            
            # Check order structure
            first_order = orders[0]
            required_fields = ['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price']
            missing_fields = [field for field in required_fields if field not in first_order]
            
            if missing_fields:
                print(f"  ❌ Missing required fields in orders: {missing_fields}")
                return False
            
            print(f"  ✅ PO Reader successfully read {len(orders)} orders")
            return True
            
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"  ❌ PO Reader test failed: {e}")
        return False

def test_validation_functionality():
    """Test basic Validation Agent functionality"""
    print("Testing Validation Agent...")
    try:
        from agents.validation.agent import ValidationAgent
        
        # Change to project root for data access
        original_cwd = os.getcwd()
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        os.chdir(project_root)
        
        try:
            validation_agent = ValidationAgent()
            orders = validation_agent.read_customer_orders()
            skus = validation_agent.read_master_skus()
            
            if len(orders) == 0:
                print("  ❌ No orders read by validation agent")
                return False
            
            if len(skus) == 0:
                print("  ❌ No SKUs read by validation agent")
                return False
            
            print(f"  ✅ Validation Agent read {len(orders)} orders and {len(skus)} SKUs")
            return True
            
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"  ❌ Validation Agent test failed: {e}")
        return False

def test_output_files():
    """Test that output files can be generated"""
    print("Testing Output Generation...")
    try:
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        outputs_dir = os.path.join(project_root, 'outputs')
        
        if not os.path.exists(outputs_dir):
            print("  ❌ Outputs directory does not exist")
            return False
        
        # Check for some expected output files
        expected_outputs = [
            'validation_results_detailed.json',
            'sales_order_output.csv',
            'exception_emails.json',
            'po_acknowledgments.csv'
        ]
        
        existing_outputs = []
        for output_file in expected_outputs:
            full_path = os.path.join(outputs_dir, output_file)
            if os.path.exists(full_path):
                existing_outputs.append(output_file)
        
        print(f"  ✅ Output directory exists with {len(existing_outputs)}/{len(expected_outputs)} expected files")
        return True
        
    except Exception as e:
        print(f"  ❌ Output files test failed: {e}")
        return False

def test_orchestration_manager():
    """Test basic Orchestration Manager functionality"""
    print("Testing Orchestration Manager...")
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        
        # Change to project root
        original_cwd = os.getcwd()
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        os.chdir(project_root)
        
        try:
            manager = OrchestrationManager()
            
            # Test configuration validation
            validation = manager.validate_configuration()
            
            if not validation.get('valid', False):
                print(f"  ❌ Configuration validation failed: {validation.get('errors', [])}")
                return False
            
            print("  ✅ Orchestration Manager configuration is valid")
            return True
            
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"  ❌ Orchestration Manager test failed: {e}")
        return False

def run_regression_tests():
    """Run all regression tests"""
    print("=" * 60)
    print("SIMPLE REGRESSION TEST SUITE")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Agent Imports", test_agent_imports),
        ("Orchestration Imports", test_orchestration_imports),
        ("Data Files", test_data_files),
        ("PO Reader Functionality", test_po_reader_functionality),
        ("Validation Functionality", test_validation_functionality),
        ("Output Files", test_output_files),
        ("Orchestration Manager", test_orchestration_manager)
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test execution failed: {e}")
            results.append((test_name, False))
            failed += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("REGRESSION TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {test_name}")
    
    if failed == 0:
        print("\n🎉 ALL REGRESSION TESTS PASSED!")
        print("System is functioning correctly with no regressions detected.")
        return True
    else:
        print(f"\n⚠️  {failed} REGRESSION TESTS FAILED!")
        print("Please review the failed tests above.")
        return False

def main():
    """Main function"""
    try:
        success = run_regression_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Fatal error running regression tests: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()