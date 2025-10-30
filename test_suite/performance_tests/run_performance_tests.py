"""
Performance Test Suite Runner

Comprehensive runner for all performance and load tests including:
- Dataset scaling tests
- Execution time benchmarks  
- Resource monitoring tests
- Performance reporting and analysis
"""

import unittest
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.performance_tests.test_dataset_scaling import DatasetScalingTests
from test_suite.performance_tests.test_execution_benchmarks import ExecutionBenchmarkTests
from test_suite.performance_tests.test_resource_monitoring import ResourceMonitoringTests


class PerformanceTestRunner:
    """Comprehensive performance test runner with reporting"""
    
    def __init__(self, output_dir: str = "test_suite/reports"):
        self.output_dir = output_dir
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
    def run_all_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests and generate comprehensive report"""
        print("Starting comprehensive performance test suite...")
        self.start_time = time.time()
        
        # Test suites to run
        test_suites = [
            ('Dataset Scaling Tests', DatasetScalingTests),
            ('Execution Benchmark Tests', ExecutionBenchmarkTests),
            ('Resource Monitoring Tests', ResourceMonitoringTests)
        ]
        
        overall_results = {
            'test_suites': {},
            'summary': {},
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'python_version': sys.version,
                'platform': sys.platform
            }
        }
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        
        for suite_name, test_class in test_suites:
            print(f"\n{'='*60}")
            print(f"Running {suite_name}")
            print(f"{'='*60}")
            
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            
            # Run tests with custom result collector
            result_collector = PerformanceTestResult()
            suite.run(result_collector)
            
            # Collect results
            suite_results = {
                'tests_run': result_collector.testsRun,
                'failures': len(result_collector.failures),
                'errors': len(result_collector.errors),
                'success_rate': (result_collector.testsRun - len(result_collector.failures) - len(result_collector.errors)) / result_collector.testsRun * 100 if result_collector.testsRun > 0 else 0,
                'execution_time': result_collector.execution_time,
                'failure_details': [{'test': str(test), 'error': error} for test, error in result_collector.failures],
                'error_details': [{'test': str(test), 'error': error} for test, error in result_collector.errors]
            }
            
            overall_results['test_suites'][suite_name] = suite_results
            
            # Update totals
            total_tests += result_collector.testsRun
            total_passed += (result_collector.testsRun - len(result_collector.failures) - len(result_collector.errors))
            total_failed += len(result_collector.failures)
            total_errors += len(result_collector.errors)
            
            # Print suite summary
            print(f"\n{suite_name} Summary:")
            print(f"  Tests run: {result_collector.testsRun}")
            print(f"  Passed: {result_collector.testsRun - len(result_collector.failures) - len(result_collector.errors)}")
            print(f"  Failed: {len(result_collector.failures)}")
            print(f"  Errors: {len(result_collector.errors)}")
            print(f"  Success rate: {suite_results['success_rate']:.1f}%")
            print(f"  Execution time: {result_collector.execution_time:.2f}s")
            
        self.end_time = time.time()
        total_execution_time = self.end_time - self.start_time
        
        # Overall summary
        overall_results['summary'] = {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_errors': total_errors,
            'overall_success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'total_execution_time': total_execution_time
        }
        
        overall_results['metadata']['end_time'] = datetime.now().isoformat()
        overall_results['metadata']['total_execution_time'] = total_execution_time
        
        # Generate reports
        self._generate_performance_report(overall_results)
        
        # Print overall summary
        print(f"\n{'='*60}")
        print("PERFORMANCE TEST SUITE SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests run: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Errors: {total_errors}")
        print(f"Overall success rate: {overall_results['summary']['overall_success_rate']:.1f}%")
        print(f"Total execution time: {total_execution_time:.2f}s")
        
        if total_failed > 0 or total_errors > 0:
            print(f"\n⚠️  {total_failed + total_errors} tests did not pass. Check the detailed report for more information.")
        else:
            print(f"\n✅ All performance tests passed successfully!")
            
        return overall_results
        
    def run_specific_test_suite(self, test_suite_name: str) -> Dict[str, Any]:
        """Run a specific performance test suite"""
        test_suites = {
            'scaling': DatasetScalingTests,
            'benchmarks': ExecutionBenchmarkTests,
            'resources': ResourceMonitoringTests
        }
        
        if test_suite_name not in test_suites:
            raise ValueError(f"Unknown test suite: {test_suite_name}. Available: {list(test_suites.keys())}")
            
        print(f"Running {test_suite_name} performance tests...")
        
        test_class = test_suites[test_suite_name]
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        result_collector = PerformanceTestResult()
        suite.run(result_collector)
        
        results = {
            'test_suite': test_suite_name,
            'tests_run': result_collector.testsRun,
            'failures': len(result_collector.failures),
            'errors': len(result_collector.errors),
            'execution_time': result_collector.execution_time,
            'success_rate': (result_collector.testsRun - len(result_collector.failures) - len(result_collector.errors)) / result_collector.testsRun * 100 if result_collector.testsRun > 0 else 0
        }
        
        print(f"\n{test_suite_name} Results:")
        print(f"  Tests run: {results['tests_run']}")
        print(f"  Success rate: {results['success_rate']:.1f}%")
        print(f"  Execution time: {results['execution_time']:.2f}s")
        
        return results
        
    def _generate_performance_report(self, results: Dict[str, Any]):
        """Generate comprehensive performance test report"""
        # Generate JSON report
        json_report_path = os.path.join(self.output_dir, 'performance_test_results.json')
        with open(json_report_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        # Generate HTML report
        html_report_path = os.path.join(self.output_dir, 'performance_test_report.html')
        self._generate_html_report(results, html_report_path)
        
        # Generate summary report
        summary_report_path = os.path.join(self.output_dir, 'performance_summary.txt')
        self._generate_summary_report(results, summary_report_path)
        
        print(f"\nReports generated:")
        print(f"  JSON Report: {json_report_path}")
        print(f"  HTML Report: {html_report_path}")
        print(f"  Summary Report: {summary_report_path}")
        
    def _generate_html_report(self, results: Dict[str, Any], output_path: str):
        """Generate HTML performance test report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .test-suite {{ margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }}
        .test-suite-header {{ background-color: #e9e9e9; padding: 10px; font-weight: bold; }}
        .test-suite-content {{ padding: 15px; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .error {{ color: orange; }}
        .metric {{ margin: 5px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Performance Test Report</h1>
        <p>Generated: {results['metadata']['end_time']}</p>
        <p>Platform: {results['metadata']['platform']}</p>
        <p>Python Version: {results['metadata']['python_version']}</p>
    </div>
    
    <div class="summary">
        <h2>Overall Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Tests</td><td>{results['summary']['total_tests']}</td></tr>
            <tr><td>Passed</td><td class="success">{results['summary']['total_passed']}</td></tr>
            <tr><td>Failed</td><td class="failure">{results['summary']['total_failed']}</td></tr>
            <tr><td>Errors</td><td class="error">{results['summary']['total_errors']}</td></tr>
            <tr><td>Success Rate</td><td>{results['summary']['overall_success_rate']:.1f}%</td></tr>
            <tr><td>Total Execution Time</td><td>{results['summary']['total_execution_time']:.2f}s</td></tr>
        </table>
    </div>
"""
        
        # Add test suite details
        for suite_name, suite_results in results['test_suites'].items():
            html_content += f"""
    <div class="test-suite">
        <div class="test-suite-header">{suite_name}</div>
        <div class="test-suite-content">
            <div class="metric">Tests Run: {suite_results['tests_run']}</div>
            <div class="metric">Success Rate: {suite_results['success_rate']:.1f}%</div>
            <div class="metric">Execution Time: {suite_results['execution_time']:.2f}s</div>
            
            {f'<h4>Failures ({suite_results["failures"]})</h4>' if suite_results['failures'] > 0 else ''}
            {f'<h4>Errors ({suite_results["errors"]})</h4>' if suite_results['errors'] > 0 else ''}
        </div>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        with open(output_path, 'w') as f:
            f.write(html_content)
            
    def _generate_summary_report(self, results: Dict[str, Any], output_path: str):
        """Generate text summary report"""
        summary_content = f"""
PERFORMANCE TEST SUITE SUMMARY
{'='*50}

Execution Details:
  Start Time: {results['metadata']['start_time']}
  End Time: {results['metadata']['end_time']}
  Total Duration: {results['summary']['total_execution_time']:.2f}s
  Platform: {results['metadata']['platform']}

Overall Results:
  Total Tests: {results['summary']['total_tests']}
  Passed: {results['summary']['total_passed']}
  Failed: {results['summary']['total_failed']}
  Errors: {results['summary']['total_errors']}
  Success Rate: {results['summary']['overall_success_rate']:.1f}%

Test Suite Breakdown:
"""
        
        for suite_name, suite_results in results['test_suites'].items():
            summary_content += f"""
{suite_name}:
  Tests: {suite_results['tests_run']}
  Success Rate: {suite_results['success_rate']:.1f}%
  Execution Time: {suite_results['execution_time']:.2f}s
  Failures: {suite_results['failures']}
  Errors: {suite_results['errors']}
"""
        
        with open(output_path, 'w') as f:
            f.write(summary_content)


class PerformanceTestResult(unittest.TestResult):
    """Custom test result collector for performance tests"""
    
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.execution_time = 0
        
    def startTest(self, test):
        super().startTest(test)
        if self.start_time is None:
            self.start_time = time.time()
            
    def stopTest(self, test):
        super().stopTest(test)
        if self.start_time is not None:
            self.execution_time = time.time() - self.start_time


def main():
    """Main entry point for performance test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run performance tests')
    parser.add_argument('--suite', choices=['scaling', 'benchmarks', 'resources', 'all'], 
                       default='all', help='Test suite to run')
    parser.add_argument('--output-dir', default='test_suite/reports', 
                       help='Output directory for reports')
    
    args = parser.parse_args()
    
    runner = PerformanceTestRunner(args.output_dir)
    
    try:
        if args.suite == 'all':
            results = runner.run_all_performance_tests()
        else:
            results = runner.run_specific_test_suite(args.suite)
            
        # Exit with appropriate code
        if args.suite == 'all':
            exit_code = 0 if results['summary']['total_failed'] == 0 and results['summary']['total_errors'] == 0 else 1
        else:
            exit_code = 0 if results['failures'] == 0 and results['errors'] == 0 else 1
            
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"Error running performance tests: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()