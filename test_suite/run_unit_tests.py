#!/usr/bin/env python3
"""
Unit Test Runner for Comprehensive Test Suite
Runs all unit tests for the agent system and provides summary results.
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def discover_and_run_unit_tests():
    """Discover and run all unit tests"""
    print("=" * 60)
    print("COMPREHENSIVE AGENT UNIT TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Discover tests in unit_tests directory
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'unit_tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=True
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
            
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0


def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    print(f"Running tests from module: {module_name}")
    print("-" * 40)
    
    try:
        # Import and run specific module
        suite = unittest.TestLoader().loadTestsFromName(f'unit_tests.{module_name}')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
        
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
        return False


def main():
    """Main test runner function"""
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        success = run_specific_test_module(module_name)
    else:
        # Run all unit tests
        success = discover_and_run_unit_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()