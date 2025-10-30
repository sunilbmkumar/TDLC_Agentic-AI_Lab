#!/usr/bin/env python3
"""
Unit Test Verification Script
Verifies that unit tests are properly implemented and can run.
"""

import sys
import os
import unittest
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_po_reader_basic():
    """Test basic PO Reader functionality"""
    try:
        from agents.po_reader.agent import POReaderAgent
        
        # Create a temporary test file
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, 'test_orders.csv')
        
        with open(test_file, 'w') as f:
            f.write("PO_Number,Customer_Name,SKU,Quantity,Price\n")
            f.write("PO001,Test Corp,SKU001,10,25.50\n")
        
        # Test the agent
        agent = POReaderAgent(data_path=test_file)
        orders = agent.read_orders()
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        # Verify results
        assert len(orders) == 1
        assert orders[0]['PO_Number'] == 'PO001'
        assert orders[0]['Customer_Name'] == 'Test Corp'
        
        print("✓ PO Reader Agent - Basic functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ PO Reader Agent - Basic functionality test FAILED: {e}")
        return False

def test_validation_basic():
    """Test basic Validation Agent functionality"""
    try:
        from agents.validation.agent import ValidationAgent
        
        agent = ValidationAgent()
        
        # Test price deviation calculation
        exceeds, deviation = agent.check_price_deviation(30.0, 25.0, 0.10)
        
        assert exceeds == True  # 20% deviation exceeds 10% threshold
        assert abs(deviation - 20.0) < 0.1
        
        print("✓ Validation Agent - Basic functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Validation Agent - Basic functionality test FAILED: {e}")
        return False

def test_exception_response_basic():
    """Test basic Exception Response Agent functionality"""
    try:
        from agents.exception_response.agent import ExceptionResponseAgent
        
        agent = ExceptionResponseAgent()
        
        # Test customer email lookup
        email = agent.get_customer_email('PO1001')
        name = agent.get_customer_name('PO1001')
        
        assert email == 'orders@acmecorp.com'
        assert name == 'ACME Corp'
        
        print("✓ Exception Response Agent - Basic functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Exception Response Agent - Basic functionality test FAILED: {e}")
        return False

def test_so_creator_basic():
    """Test basic SO Creator Agent functionality"""
    try:
        from agents.so_creator.agent import SalesOrderCreatorAgent
        
        agent = SalesOrderCreatorAgent()
        
        # Test SO number generation
        so_number = agent.generate_so_number('PO001')
        
        assert so_number.startswith('SO')
        assert len(so_number) == 6  # SO + 4 digits
        
        print("✓ SO Creator Agent - Basic functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ SO Creator Agent - Basic functionality test FAILED: {e}")
        return False

def test_summary_insights_basic():
    """Test basic Summary Insights Agent functionality"""
    try:
        from agents.summary_insights.agent import SummaryInsightsAgent
        
        agent = SummaryInsightsAgent()
        
        # Test basic calculation
        total_orders = agent.calculate_total_orders()
        
        assert total_orders == 0  # No data loaded yet
        
        print("✓ Summary Insights Agent - Basic functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Summary Insights Agent - Basic functionality test FAILED: {e}")
        return False

def main():
    """Run basic verification tests"""
    print("=" * 60)
    print("UNIT TESTS VERIFICATION")
    print("=" * 60)
    print("Running basic functionality tests for all agents...")
    print()
    
    tests = [
        test_po_reader_basic,
        test_validation_basic,
        test_exception_response_basic,
        test_so_creator_basic,
        test_summary_insights_basic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print()
    print("=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All basic functionality tests PASSED")
        print("✓ Unit test infrastructure is working correctly")
        print("✓ All agents are properly implemented and testable")
        return True
    else:
        print(f"✗ {total - passed} tests FAILED")
        print("✗ Some issues need to be resolved")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)