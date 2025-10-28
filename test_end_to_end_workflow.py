#!/usr/bin/env python3
"""
Comprehensive End-to-End Workflow Testing
Tests the complete PO to SO transformation pipeline with exception scenarios
and agent failure recovery validation
"""

import sys
import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

class EndToEndWorkflowTester:
    """Comprehensive end-to-end workflow testing system"""
    
    def __init__(self):
        self.test_data_dir = "test_data"
        self.backup_data_dir = "data_backup"
        self.test_results = {}
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Setup isolated test environment"""
        print("🔧 Setting up test environment...")
        
        # Create test directories
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs('outputs', exist_ok=True)
        
        # Backup original data files if they exist
        if os.path.exists('data'):
            if os.path.exists(self.backup_data_dir):
                shutil.rmtree(self.backup_data_dir)
            shutil.copytree('data', self.backup_data_dir)
        
        print("✅ Test environment ready")
    
    def cleanup_test_environment(self):
        """Cleanup test environment and restore original data"""
        print("🧹 Cleaning up test environment...")
        
        # Remove test data
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
        
        # Restore original data if backup exists
        if os.path.exists(self.backup_data_dir):
            if os.path.exists('data'):
                shutil.rmtree('data')
            shutil.copytree(self.backup_data_dir, 'data')
            shutil.rmtree(self.backup_data_dir)
        
        print("✅ Test environment cleaned up")
    
    def create_test_data_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Create test data for different scenarios"""
        scenarios = {
            'normal_flow': {
                'customer_orders': [
                    {"PO_Number": "PO1001", "Customer": "ACME Corp", "SKU": "SKU001", "Quantity": 100, "Price": 50.00},
                    {"PO_Number": "PO1002", "Customer": "Zenith Ltd", "SKU": "SKU002", "Quantity": 50, "Price": 100.00},
                    {"PO_Number": "PO1003", "Customer": "Innova Inc", "SKU": "SKU004", "Quantity": 75, "Price": 80.00}
                ],
                'master_sku': [
                    {"SKU": "SKU001", "Product_Name": "Widget A", "Reference_Price": 50.00},
                    {"SKU": "SKU002", "Product_Name": "Widget B", "Reference_Price": 100.00},
                    {"SKU": "SKU004", "Product_Name": "Widget D", "Reference_Price": 80.00}
                ]
            },
            'exception_flow': {
                'customer_orders': [
                    {"PO_Number": "PO1001", "Customer": "ACME Corp", "SKU": "SKU001", "Quantity": 100, "Price": 50.00},
                    {"PO_Number": "PO1004", "Customer": "Innova Inc", "SKU": "SKU999", "Quantity": 25, "Price": 150.00},
                    {"PO_Number": "PO1005", "Customer": "Test Corp", "SKU": "SKU002", "Quantity": 30, "Price": 120.00}
                ],
                'master_sku': [
                    {"SKU": "SKU001", "Product_Name": "Widget A", "Reference_Price": 50.00},
                    {"SKU": "SKU002", "Product_Name": "Widget B", "Reference_Price": 100.00}
                ]
            },
            'mixed_scenario': {
                'customer_orders': [
                    {"PO_Number": "PO1001", "Customer": "ACME Corp", "SKU": "SKU001", "Quantity": 100, "Price": 50.00},
                    {"PO_Number": "PO1002", "Customer": "Zenith Ltd", "SKU": "SKU002", "Quantity": 50, "Price": 115.00},
                    {"PO_Number": "PO1003", "Customer": "Valid Corp", "SKU": "SKU004", "Quantity": 75, "Price": 80.00},
                    {"PO_Number": "PO1004", "Customer": "Innova Inc", "SKU": "SKU999", "Quantity": 25, "Price": 150.00}
                ],
                'master_sku': [
                    {"SKU": "SKU001", "Product_Name": "Widget A", "Reference_Price": 50.00},
                    {"SKU": "SKU002", "Product_Name": "Widget B", "Reference_Price": 100.00},
                    {"SKU": "SKU004", "Product_Name": "Widget D", "Reference_Price": 80.00}
                ]
            }
        }
        
        scenario_data = scenarios.get(scenario_name, scenarios['normal_flow'])
        
        # Write CSV files
        self.write_csv_file('data/customer_orders.csv', scenario_data['customer_orders'])
        self.write_csv_file('data/master_sku.csv', scenario_data['master_sku'])
        
        return scenario_data
    
    def write_csv_file(self, filepath: str, data: List[Dict[str, Any]]):
        """Write data to CSV file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if not data:
            return
        
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    def test_complete_workflow_normal_flow(self) -> bool:
        """Test complete workflow with normal data (no exceptions)"""
        print("\n=== TEST: Complete Workflow - Normal Flow ===")
        
        try:
            # Setup test data
            self.create_test_data_scenario('normal_flow')
            
            # Import orchestration manager
            from orchestration.orchestration_manager import OrchestrationManager
            
            # Execute workflow
            manager = OrchestrationManager()
            results = manager.execute_workflow()
            
            # Validate results
            validation_results = self.validate_workflow_results(results, expected_valid_orders=3, expected_exceptions=0)
            
            self.test_results['normal_flow'] = {
                'passed': validation_results['success'],
                'details': validation_results,
                'agent_results': {name: result.status.value for name, result in results.items()}
            }
            
            if validation_results['success']:
                print("✅ Normal flow test PASSED")
                return True
            else:
                print("❌ Normal flow test FAILED")
                print(f"   Reason: {validation_results.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Normal flow test FAILED with exception: {e}")
            self.test_results['normal_flow'] = {'passed': False, 'error': str(e)}
            return False
    
    def test_complete_workflow_exception_flow(self) -> bool:
        """Test complete workflow with exception scenarios"""
        print("\n=== TEST: Complete Workflow - Exception Flow ===")
        
        try:
            # Setup test data with exceptions
            self.create_test_data_scenario('exception_flow')
            
            # Import orchestration manager
            from orchestration.orchestration_manager import OrchestrationManager
            
            # Execute workflow
            manager = OrchestrationManager()
            results = manager.execute_workflow()
            
            # Validate results - expect 1 valid order, 2 exceptions
            validation_results = self.validate_workflow_results(results, expected_valid_orders=1, expected_exceptions=2)
            
            # Additional validation for exception handling
            exception_validation = self.validate_exception_handling()
            
            self.test_results['exception_flow'] = {
                'passed': validation_results['success'] and exception_validation['success'],
                'workflow_validation': validation_results,
                'exception_validation': exception_validation,
                'agent_results': {name: result.status.value for name, result in results.items()}
            }
            
            if validation_results['success'] and exception_validation['success']:
                print("✅ Exception flow test PASSED")
                return True
            else:
                print("❌ Exception flow test FAILED")
                return False
                
        except Exception as e:
            print(f"❌ Exception flow test FAILED with exception: {e}")
            self.test_results['exception_flow'] = {'passed': False, 'error': str(e)}
            return False
    
    def test_agent_failure_recovery(self) -> bool:
        """Test agent failure scenarios and recovery mechanisms"""
        print("\n=== TEST: Agent Failure Recovery ===")
        
        try:
            # Setup normal test data
            self.create_test_data_scenario('normal_flow')
            
            # Test individual agent failures
            failure_tests = []
            
            # Test 1: Simulate validation agent failure
            failure_tests.append(self.simulate_agent_failure('validation'))
            
            # Test 2: Simulate exception response agent failure
            failure_tests.append(self.simulate_agent_failure('exception_response'))
            
            # Test 3: Test recovery after fixing data
            failure_tests.append(self.test_recovery_after_fix())
            
            all_passed = all(failure_tests)
            
            self.test_results['failure_recovery'] = {
                'passed': all_passed,
                'individual_tests': failure_tests
            }
            
            if all_passed:
                print("✅ Agent failure recovery test PASSED")
                return True
            else:
                print("❌ Agent failure recovery test FAILED")
                return False
                
        except Exception as e:
            print(f"❌ Agent failure recovery test FAILED with exception: {e}")
            self.test_results['failure_recovery'] = {'passed': False, 'error': str(e)}
            return False
    
    def test_sequential_vs_coordinated_execution(self) -> bool:
        """Test both sequential and coordinated execution modes"""
        print("\n=== TEST: Sequential vs Coordinated Execution ===")
        
        try:
            # Setup test data
            self.create_test_data_scenario('mixed_scenario')
            
            # Test sequential execution
            sequential_results = self.test_execution_mode('sequential')
            
            # Clean outputs for coordinated test
            self.clean_output_files()
            
            # Test coordinated execution
            coordinated_results = self.test_execution_mode('coordinated')
            
            # Compare results
            comparison = self.compare_execution_modes(sequential_results, coordinated_results)
            
            self.test_results['execution_modes'] = {
                'passed': comparison['success'],
                'sequential_results': sequential_results,
                'coordinated_results': coordinated_results,
                'comparison': comparison
            }
            
            if comparison['success']:
                print("✅ Execution modes test PASSED")
                return True
            else:
                print("❌ Execution modes test FAILED")
                return False
                
        except Exception as e:
            print(f"❌ Execution modes test FAILED with exception: {e}")
            self.test_results['execution_modes'] = {'passed': False, 'error': str(e)}
            return False
    
    def test_data_flow_integrity(self) -> bool:
        """Test data flow integrity between agents"""
        print("\n=== TEST: Data Flow Integrity ===")
        
        try:
            # Setup test data
            self.create_test_data_scenario('mixed_scenario')
            
            # Execute workflow and track data flow
            from orchestration.orchestration_manager import OrchestrationManager
            
            manager = OrchestrationManager()
            results = manager.execute_workflow()
            
            # Validate data flow at each stage
            data_flow_validation = self.validate_data_flow_integrity(manager)
            
            self.test_results['data_flow'] = {
                'passed': data_flow_validation['success'],
                'details': data_flow_validation
            }
            
            if data_flow_validation['success']:
                print("✅ Data flow integrity test PASSED")
                return True
            else:
                print("❌ Data flow integrity test FAILED")
                return False
                
        except Exception as e:
            print(f"❌ Data flow integrity test FAILED with exception: {e}")
            self.test_results['data_flow'] = {'passed': False, 'error': str(e)}
            return False
    
    def validate_workflow_results(self, results: Dict[str, Any], expected_valid_orders: int, expected_exceptions: int) -> Dict[str, Any]:
        """Validate complete workflow results"""
        validation = {'success': True, 'details': {}}
        
        try:
            # Check all agents completed successfully
            failed_agents = [name for name, result in results.items() if result.status.value == 'failed']
            if failed_agents:
                validation['success'] = False
                validation['error'] = f"Agents failed: {failed_agents}"
                return validation
            
            # Check validation results file
            if os.path.exists('outputs/validation_results_detailed.json'):
                with open('outputs/validation_results_detailed.json', 'r') as f:
                    validation_data = json.load(f)
                
                valid_count = sum(1 for item in validation_data if item.get('Status') == 'Valid')
                exception_count = sum(1 for item in validation_data if item.get('Status') == 'Exception')
                
                validation['details']['validation_results'] = {
                    'valid_orders': valid_count,
                    'exceptions': exception_count,
                    'expected_valid': expected_valid_orders,
                    'expected_exceptions': expected_exceptions
                }
                
                if valid_count != expected_valid_orders or exception_count != expected_exceptions:
                    validation['success'] = False
                    validation['error'] = f"Expected {expected_valid_orders} valid, {expected_exceptions} exceptions. Got {valid_count} valid, {exception_count} exceptions"
            
            # Check sales order output for valid orders
            if expected_valid_orders > 0 and os.path.exists('outputs/sales_order_output.csv'):
                import csv
                with open('outputs/sales_order_output.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    so_count = len(list(reader))
                
                validation['details']['sales_orders'] = so_count
                
                if so_count != expected_valid_orders:
                    validation['success'] = False
                    validation['error'] = f"Expected {expected_valid_orders} sales orders, got {so_count}"
            
            # Check exception emails if exceptions expected
            if expected_exceptions > 0:
                exception_files = ['outputs/exception_emails.json', 'outputs/email_delivery_log.json']
                for file_path in exception_files:
                    if not os.path.exists(file_path):
                        validation['success'] = False
                        validation['error'] = f"Missing exception file: {file_path}"
                        break
            
            return validation
            
        except Exception as e:
            validation['success'] = False
            validation['error'] = f"Validation error: {e}"
            return validation
    
    def validate_exception_handling(self) -> Dict[str, Any]:
        """Validate exception handling mechanisms"""
        validation = {'success': True, 'details': {}}
        
        try:
            # Check exception emails were generated
            if os.path.exists('outputs/exception_emails.json'):
                with open('outputs/exception_emails.json', 'r') as f:
                    emails = json.load(f)
                
                validation['details']['exception_emails'] = len(emails)
                
                # Validate email content
                for email in emails:
                    required_fields = ['to', 'subject', 'message', 'po_number']
                    if not all(field in email for field in required_fields):
                        validation['success'] = False
                        validation['error'] = "Exception email missing required fields"
                        break
            else:
                validation['success'] = False
                validation['error'] = "Exception emails file not found"
            
            # Check delivery simulation
            if os.path.exists('outputs/email_delivery_log.json'):
                with open('outputs/email_delivery_log.json', 'r') as f:
                    delivery_log = json.load(f)
                
                validation['details']['delivery_attempts'] = len(delivery_log)
            
            return validation
            
        except Exception as e:
            validation['success'] = False
            validation['error'] = f"Exception validation error: {e}"
            return validation
    
    def simulate_agent_failure(self, agent_name: str) -> bool:
        """Simulate agent failure scenario"""
        print(f"   Testing {agent_name} failure scenario...")
        
        try:
            # Create corrupted data to cause agent failure
            if agent_name == 'validation':
                # Create invalid master SKU file
                with open('data/master_sku.csv', 'w') as f:
                    f.write("invalid,csv,format\n")
            elif agent_name == 'exception_response':
                # Create invalid validation results
                os.makedirs('outputs', exist_ok=True)
                with open('outputs/validation_results_detailed.json', 'w') as f:
                    f.write("invalid json content")
            
            # Try to run workflow - should handle failure gracefully
            from orchestration.orchestration_manager import OrchestrationManager
            
            manager = OrchestrationManager()
            results = manager.execute_workflow()
            
            # Check if failure was handled gracefully
            failed_agent = results.get(agent_name)
            if failed_agent and failed_agent.status.value == 'failed':
                print(f"   ✅ {agent_name} failure handled gracefully")
                return True
            else:
                print(f"   ❌ {agent_name} failure not handled properly")
                return False
                
        except Exception as e:
            print(f"   ❌ {agent_name} failure test error: {e}")
            return False
        finally:
            # Restore valid data
            self.create_test_data_scenario('normal_flow')
    
    def test_recovery_after_fix(self) -> bool:
        """Test recovery after fixing data issues"""
        print("   Testing recovery after data fix...")
        
        try:
            # Ensure we have valid data
            self.create_test_data_scenario('normal_flow')
            
            # Run workflow - should succeed
            from orchestration.orchestration_manager import OrchestrationManager
            
            manager = OrchestrationManager()
            results = manager.execute_workflow()
            
            # Check all agents completed successfully
            failed_agents = [name for name, result in results.items() if result.status.value == 'failed']
            
            if not failed_agents:
                print("   ✅ Recovery after fix successful")
                return True
            else:
                print(f"   ❌ Recovery failed, agents still failing: {failed_agents}")
                return False
                
        except Exception as e:
            print(f"   ❌ Recovery test error: {e}")
            return False
    
    def test_execution_mode(self, mode: str) -> Dict[str, Any]:
        """Test specific execution mode"""
        print(f"   Testing {mode} execution mode...")
        
        try:
            # Create config for specific mode
            config = {
                "execution_mode": mode,
                "max_parallel_agents": 2,
                "dependencies": {
                    "po_reader": [],
                    "validation": ["po_reader"],
                    "exception_response": ["validation"],
                    "so_creator": ["validation"],
                    "summary_insights": ["exception_response", "so_creator"]
                },
                "parallel_groups": {
                    "post_validation": ["exception_response", "so_creator"]
                }
            }
            
            # Save config
            os.makedirs('config', exist_ok=True)
            with open('config/orchestration_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            # Execute workflow
            from orchestration.orchestration_manager import OrchestrationManager
            
            manager = OrchestrationManager()
            start_time = datetime.now()
            results = manager.execute_workflow()
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'execution_time': execution_time,
                'agent_results': {name: result.status.value for name, result in results.items()},
                'completed_agents': sum(1 for result in results.values() if result.status.value == 'completed')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def compare_execution_modes(self, sequential: Dict[str, Any], coordinated: Dict[str, Any]) -> Dict[str, Any]:
        """Compare results from different execution modes"""
        comparison = {'success': True, 'details': {}}
        
        try:
            # Both should succeed
            if not (sequential['success'] and coordinated['success']):
                comparison['success'] = False
                comparison['error'] = "One or both execution modes failed"
                return comparison
            
            # Both should complete same number of agents
            seq_completed = sequential['completed_agents']
            coord_completed = coordinated['completed_agents']
            
            if seq_completed != coord_completed:
                comparison['success'] = False
                comparison['error'] = f"Different completion counts: sequential={seq_completed}, coordinated={coord_completed}"
                return comparison
            
            # Coordinated should potentially be faster (though not guaranteed in test environment)
            comparison['details'] = {
                'sequential_time': sequential['execution_time'],
                'coordinated_time': coordinated['execution_time'],
                'time_difference': sequential['execution_time'] - coordinated['execution_time']
            }
            
            print(f"   Sequential time: {sequential['execution_time']:.2f}s")
            print(f"   Coordinated time: {coordinated['execution_time']:.2f}s")
            
            return comparison
            
        except Exception as e:
            comparison['success'] = False
            comparison['error'] = f"Comparison error: {e}"
            return comparison
    
    def validate_data_flow_integrity(self, manager) -> Dict[str, Any]:
        """Validate data flow integrity between agents"""
        validation = {'success': True, 'details': {}}
        
        try:
            # Get shared data from pipeline
            shared_data = manager.pipeline.shared_data
            
            # Validate data flow stages
            stages = {
                'customer_orders': 'PO Reader should populate customer orders',
                'validation_results': 'Validation should populate validation results',
                'exception_emails': 'Exception Response should populate exception emails',
                'sales_orders': 'SO Creator should populate sales orders'
            }
            
            for stage, description in stages.items():
                if stage not in shared_data or not shared_data[stage]:
                    validation['success'] = False
                    validation['error'] = f"Data flow broken at {stage}: {description}"
                    break
                else:
                    validation['details'][stage] = len(shared_data[stage])
            
            # Validate data consistency
            if validation['success']:
                customer_orders = shared_data.get('customer_orders', [])
                validation_results = shared_data.get('validation_results', [])
                
                if len(customer_orders) != len(validation_results):
                    validation['success'] = False
                    validation['error'] = f"Data inconsistency: {len(customer_orders)} orders vs {len(validation_results)} validation results"
            
            return validation
            
        except Exception as e:
            validation['success'] = False
            validation['error'] = f"Data flow validation error: {e}"
            return validation
    
    def clean_output_files(self):
        """Clean output files between tests"""
        output_files = [
            'outputs/validation_results_detailed.json',
            'outputs/sales_order_output.csv',
            'outputs/exception_emails.json',
            'outputs/email_delivery_log.json',
            'outputs/summary_report.json'
        ]
        
        for file_path in output_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("=" * 60)
        report.append("END-TO-END WORKFLOW TEST REPORT")
        report.append("=" * 60)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('passed', False))
        
        report.append(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
        report.append("")
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result.get('passed', False) else "❌ FAILED"
            report.append(f"{test_name.upper()}: {status}")
            
            if not result.get('passed', False) and 'error' in result:
                report.append(f"  Error: {result['error']}")
            
            if 'details' in result:
                report.append(f"  Details: {result['details']}")
            
            report.append("")
        
        return "\n".join(report)
    
    def run_all_tests(self) -> bool:
        """Run all end-to-end workflow tests"""
        print("🧪 Starting Comprehensive End-to-End Workflow Tests")
        print("=" * 60)
        
        tests = [
            ("Complete Workflow - Normal Flow", self.test_complete_workflow_normal_flow),
            ("Complete Workflow - Exception Flow", self.test_complete_workflow_exception_flow),
            ("Agent Failure Recovery", self.test_agent_failure_recovery),
            ("Sequential vs Coordinated Execution", self.test_sequential_vs_coordinated_execution),
            ("Data Flow Integrity", self.test_data_flow_integrity)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            try:
                print(f"\n🔍 Running: {test_name}")
                result = test_func()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ Test {test_name} crashed: {e}")
                all_passed = False
        
        # Generate and save report
        report = self.generate_test_report()
        
        with open('outputs/end_to_end_test_report.txt', 'w') as f:
            f.write(report)
        
        print("\n" + "=" * 60)
        print("END-TO-END WORKFLOW TEST RESULTS")
        print("=" * 60)
        print(report)
        
        return all_passed


def main():
    """Main test execution function"""
    tester = EndToEndWorkflowTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 All end-to-end workflow tests PASSED!")
            print("The complete PO to SO transformation pipeline is working correctly.")
            return 0
        else:
            print("\n❌ Some end-to-end workflow tests FAILED!")
            print("Please check the test report for details.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        tester.cleanup_test_environment()


if __name__ == "__main__":
    sys.exit(main())