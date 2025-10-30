#!/usr/bin/env python3
"""
Simple test runner for individual unit tests
"""
import sys
import os
import unittest

# Add current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def run_po_reader_tests():
    """Run PO Reader Agent tests"""
    try:
        from test_suite.unit_tests.test_po_reader_agent import TestPOReaderAgent
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPOReaderAgent)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print(f"\nTest Summary:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success: {result.wasSuccessful()}")
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_po_reader_tests()
    sys.exit(0 if success else 1)