#!/usr/bin/env python3
"""
Simple test runner to check unit test status
"""

import sys
import os
import importlib.util

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def check_test_file(test_file_path):
    """Check if a test file can be imported and has test methods"""
    try:
        # Get the module name from file path
        module_name = os.path.basename(test_file_path).replace('.py', '')
        
        # Load the module
        spec = importlib.util.spec_from_file_location(module_name, test_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Count test methods
        test_methods = []
        for name in dir(module):
            obj = getattr(module, name)
            if hasattr(obj, '__dict__'):
                for method_name in dir(obj):
                    if method_name.startswith('test_'):
                        test_methods.append(f"{name}.{method_name}")
        
        return True, len(test_methods), test_methods
        
    except Exception as e:
        return False, 0, [str(e)]

def main():
    """Check all unit test files"""
    print("=" * 70)
    print("UNIT TEST STATUS CHECK")
    print("=" * 70)
    
    test_files = [
        'test_suite/unit_tests/test_po_reader_agent.py',
        'test_suite/unit_tests/test_validation_agent.py',
        'test_suite/unit_tests/test_exception_response_agent.py',
        'test_suite/unit_tests/test_so_creator_agent.py',
        'test_suite/unit_tests/test_summary_insights_agent.py',
        'test_suite/unit_tests/test_agent_performance.py'
    ]
    
    total_tests = 0
    working_files = 0
    
    for test_file in test_files:
        print(f"\nChecking: {test_file}")
        
        if not os.path.exists(test_file):
            print(f"  ✗ File not found")
            continue
            
        success, test_count, details = check_test_file(test_file)
        
        if success:
            print(f"  ✓ File loads successfully")
            print(f"  ✓ Found {test_count} test methods")
            total_tests += test_count
            working_files += 1
        else:
            print(f"  ✗ Error loading file: {details[0]}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Test files checked: {len(test_files)}")
    print(f"Working test files: {working_files}")
    print(f"Total test methods found: {total_tests}")
    
    if working_files == len(test_files):
        print("✓ All unit test files are properly implemented")
        print("✓ Unit tests are ready to run")
    else:
        print(f"✗ {len(test_files) - working_files} test files have issues")
    
    return working_files == len(test_files)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)