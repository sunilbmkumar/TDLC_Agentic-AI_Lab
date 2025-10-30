#!/usr/bin/env python3
"""
Test verification script to check if unit tests are working
"""
import sys
import os
import importlib.util

# Add current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def verify_test_imports():
    """Verify that test modules can be imported"""
    test_modules = [
        'test_suite.unit_tests.test_po_reader_agent',
        'test_suite.unit_tests.test_validation_agent',
        'test_suite.unit_tests.test_exception_response_agent',
        'test_suite.unit_tests.test_so_creator_agent',
        'test_suite.unit_tests.test_summary_insights_agent',
        'test_suite.unit_tests.test_agent_performance'
    ]
    
    results = {}
    
    for module_name in test_modules:
        try:
            module = importlib.import_module(module_name)
            results[module_name] = "SUCCESS"
            print(f"✓ {module_name}")
        except ImportError as e:
            results[module_name] = f"IMPORT ERROR: {e}"
            print(f"✗ {module_name}: {e}")
        except Exception as e:
            results[module_name] = f"ERROR: {e}"
            print(f"✗ {module_name}: {e}")
    
    return results

def verify_agent_imports():
    """Verify that agent modules can be imported"""
    agent_modules = [
        'agents.po_reader.agent',
        'agents.validation.agent',
        'agents.exception_response.agent',
        'agents.so_creator.agent',
        'agents.summary_insights.agent'
    ]
    
    results = {}
    
    print("\nVerifying agent imports:")
    for module_name in agent_modules:
        try:
            module = importlib.import_module(module_name)
            results[module_name] = "SUCCESS"
            print(f"✓ {module_name}")
        except ImportError as e:
            results[module_name] = f"IMPORT ERROR: {e}"
            print(f"✗ {module_name}: {e}")
        except Exception as e:
            results[module_name] = f"ERROR: {e}"
            print(f"✗ {module_name}: {e}")
    
    return results

def main():
    """Main verification function"""
    print("Verifying test infrastructure...")
    print("=" * 50)
    
    print("Verifying test module imports:")
    test_results = verify_test_imports()
    
    agent_results = verify_agent_imports()
    
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    test_success = sum(1 for result in test_results.values() if result == "SUCCESS")
    agent_success = sum(1 for result in agent_results.values() if result == "SUCCESS")
    
    print(f"Test modules: {test_success}/{len(test_results)} successful")
    print(f"Agent modules: {agent_success}/{len(agent_results)} successful")
    
    if test_success == len(test_results) and agent_success == len(agent_results):
        print("\n✓ All modules imported successfully!")
        print("Unit tests should be ready to run.")
        return True
    else:
        print("\n✗ Some modules failed to import.")
        print("Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)