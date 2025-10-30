#!/usr/bin/env python3
"""
Regression Test Runner - Execute all regression and compatibility tests
Provides automated regression detection and reporting capabilities
"""

import unittest
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import StringIO

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import test modules
from test_baseline_functionality import (
    BaselineWorkflowTest,
    BaselineOutputFormatTest,
    BaselineAgentInterfaceTest
)
from test_configuration_compatibility import (
    ConfigurationFormatCompatibilityTest,
    ConfigurationVersionMismatchTest,
    ConfigurationValidationTest
)
from test_api_stability import (
    AgentInterfaceStabilityTest,
    OrchestrationAPIStabilityTest,
    SharedDataStructureStabilityTest,
    APIBackwardCompatibilityTest
)


class RegressionTestResult:
    """Container for regression test results"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.test_results = {}
        self.failures = []
        self.errors = []
        self.execution_time = 0.0
    
    def finalize(self):
        """Finalize test results"""
        self.end_time = datetime.now()
        self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    def add_test_suite_result(self, suite_name: str, result: unittest.TestResult):
        """Add results from a test suite"""
        self.test_results[suite_name] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        }
        
        self.total_tests += result.testsRun
        self.failed_tests += len(result.failures)
        self.error_tests += len(result.errors)
        self.skipped_tests += len(result.skipped) if hasattr(result, 'skipped') else 0
        
        # Store failure and error details
        for test, traceback in result.failures:
            self.failures.append({
                'suite': suite_name,
                'test': str(test),
                'traceback': traceback
            })
        
        for test, traceback in result.errors:
            self.errors.append({
                'suite': suite_name,
                'test': str(test),
                'traceback': traceback
            })
        
        self.passed_tests = self.total_tests - self.failed_tests - self.error_tests
    
    def get_overall_success_rate(self) -> float:
        """Get overall success rate"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    def is_regression_detected(self, baseline_success_rate: float = 95.0) -> bool:
        """Check if regression is detected based on success rate"""
        return self.get_overall_success_rate() < baseline_success_rate


class RegressionTestRunner:
    """Main regression test runner with reporting capabilities"""
    
    def __init__(self):
        self.test_suites = [
            ('Baseline Workflow Tests', BaselineWorkflowTest),
            ('Baseline Output Format Tests', BaselineOutputFormatTest),
            ('Baseline Agent Interface Tests', BaselineAgentInterfaceTest),
            ('Configuration Format Compatibility Tests', ConfigurationFormatCompatibilityTest),
            ('Configuration Version Mismatch Tests', ConfigurationVersionMismatchTest),
            ('Configuration Validation Tests', ConfigurationValidationTest),
            ('Agent Interface Stability Tests', AgentInterfaceStabilityTest),
            ('Orchestration API Stability Tests', OrchestrationAPIStabilityTest),
            ('Shared Data Structure Stability Tests', SharedDataStructureStabilityTest),
            ('API Backward Compatibility Tests', APIBackwardCompatibilityTest)
        ]
        
        self.result = RegressionTestResult()
    
    def run_all_tests(self, verbose: bool = True) -> RegressionTestResult:
        """Run all regression test suites"""
        print("=" * 80)
        print("REGRESSION TEST SUITE EXECUTION")
        print("=" * 80)
        print(f"Start Time: {self.result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test Suites: {len(self.test_suites)}")
        print("=" * 80)
        
        for suite_name, test_class in self.test_suites:
            print(f"\n--- Running {suite_name} ---")
            
            # Create test suite
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            
            # Run tests with custom result collector
            stream = StringIO() if not verbose else sys.stdout
            runner = unittest.TextTestRunner(stream=stream, verbosity=2 if verbose else 1)
            
            suite_result = runner.run(suite)
            
            # Add results to overall result
            self.result.add_test_suite_result(suite_name, suite_result)
            
            # Print suite summary
            success_rate = self.result.test_results[suite_name]['success_rate']
            print(f"Suite Results: {suite_result.testsRun} tests, {success_rate:.1f}% success rate")
            
            if suite_result.failures:
                print(f"  Failures: {len(suite_result.failures)}")
            if suite_result.errors:
                print(f"  Errors: {len(suite_result.errors)}")
        
        # Finalize results
        self.result.finalize()
        
        # Print overall summary
        self._print_summary()
        
        return self.result
    
    def _print_summary(self):
        """Print overall test execution summary"""
        print("\n" + "=" * 80)
        print("REGRESSION TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        print(f"Execution Time: {self.result.execution_time:.2f} seconds")
        print(f"Total Tests: {self.result.total_tests}")
        print(f"Passed: {self.result.passed_tests}")
        print(f"Failed: {self.result.failed_tests}")
        print(f"Errors: {self.result.error_tests}")
        print(f"Skipped: {self.result.skipped_tests}")
        print(f"Overall Success Rate: {self.result.get_overall_success_rate():.1f}%")
        
        # Regression detection
        if self.result.is_regression_detected():
            print("\n⚠️  REGRESSION DETECTED!")
            print("Success rate is below acceptable threshold (95%)")
        else:
            print("\n✅ NO REGRESSION DETECTED")
            print("All tests passed within acceptable thresholds")
        
        # Suite breakdown
        print(f"\nTest Suite Breakdown:")
        for suite_name, results in self.result.test_results.items():
            status_icon = "✅" if results['success_rate'] >= 95.0 else "❌"
            print(f"  {status_icon} {suite_name}: {results['success_rate']:.1f}% ({results['tests_run']} tests)")
        
        # Failure summary
        if self.result.failures or self.result.errors:
            print(f"\nFailure Summary:")
            
            if self.result.failures:
                print(f"Test Failures ({len(self.result.failures)}):")
                for failure in self.result.failures[:5]:  # Show first 5 failures
                    print(f"  - {failure['suite']}: {failure['test']}")
                if len(self.result.failures) > 5:
                    print(f"  ... and {len(self.result.failures) - 5} more failures")
            
            if self.result.errors:
                print(f"Test Errors ({len(self.result.errors)}):")
                for error in self.result.errors[:5]:  # Show first 5 errors
                    print(f"  - {error['suite']}: {error['test']}")
                if len(self.result.errors) > 5:
                    print(f"  ... and {len(self.result.errors) - 5} more errors")
        
        print("=" * 80)
    
    def save_results_report(self, output_file: str = "outputs/regression_test_results.json") -> str:
        """Save detailed test results to JSON file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        report_data = {
            'execution_summary': {
                'start_time': self.result.start_time.isoformat(),
                'end_time': self.result.end_time.isoformat() if self.result.end_time else None,
                'execution_time': self.result.execution_time,
                'total_tests': self.result.total_tests,
                'passed_tests': self.result.passed_tests,
                'failed_tests': self.result.failed_tests,
                'error_tests': self.result.error_tests,
                'skipped_tests': self.result.skipped_tests,
                'overall_success_rate': self.result.get_overall_success_rate(),
                'regression_detected': self.result.is_regression_detected()
            },
            'test_suite_results': self.result.test_results,
            'failures': self.result.failures,
            'errors': self.result.errors
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed test results saved to: {output_file}")
        return output_file
    
    def generate_html_report(self, output_file: str = "test_suite/reports/regression_test_report.html") -> str:
        """Generate comprehensive HTML report for regression test results"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Determine status and colors
        success_rate = self.result.get_overall_success_rate()
        if success_rate >= 95:
            status = "EXCELLENT"
            status_color = "#28a745"
        elif success_rate >= 80:
            status = "GOOD"
            status_color = "#17a2b8"
        elif success_rate >= 60:
            status = "FAIR"
            status_color = "#ffc107"
        else:
            status = "POOR"
            status_color = "#dc3545"
        
        if self.result.is_regression_detected():
            status = "REGRESSION DETECTED"
            status_color = "#ffc107"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Regression Test Report - PO to SO Agent Demo</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .summary {{
            padding: 30px;
            background: white;
            border-bottom: 1px solid #eee;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid {status_color};
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: {status_color};
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            color: white;
            background-color: {status_color};
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 1px;
        }}
        .components {{
            padding: 30px;
        }}
        .component {{
            margin-bottom: 30px;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
        }}
        .component-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .component-header h3 {{
            margin: 0;
            color: #333;
        }}
        .component-status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-passed {{
            background: #d4edda;
            color: #155724;
        }}
        .status-failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        .component-details {{
            padding: 20px;
        }}
        .detail-item {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .detail-item:last-child {{
            border-bottom: none;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        .metric {{
            text-align: center;
        }}
        .metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .metric-label {{
            font-size: 0.8em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .recommendations {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .recommendations h2 {{
            margin-top: 0;
            color: #333;
        }}
        .recommendation {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 4px solid #17a2b8;
        }}
        .failure-details {{
            padding: 30px;
            background: #fff3cd;
            border-top: 1px solid #eee;
        }}
        .failure-item {{
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border-left: 3px solid #dc3545;
        }}
        .footer {{
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Regression Test Report</h1>
            <p>PO to SO Agent Demo System Analysis</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Execution Time: {self.result.execution_time:.2f} seconds</p>
        </div>
        
        <div class="summary">
            <h2>System Status: <span class="status-badge">{status}</span></h2>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Tests</h3>
                    <div class="value">{self.result.total_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>Passed</h3>
                    <div class="value">{self.result.passed_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>Failed</h3>
                    <div class="value">{self.result.failed_tests + self.result.error_tests}</div>
                </div>
                <div class="summary-card">
                    <h3>Success Rate</h3>
                    <div class="value">{success_rate:.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="components">
            <h2>Test Suite Results</h2>
"""
        
        # Add test suite details
        for suite_name, results in self.result.test_results.items():
            status_class = 'status-passed' if results['success_rate'] >= 95.0 else 'status-failed'
            status_text = 'PASSED' if results['success_rate'] >= 95.0 else 'FAILED'
            
            html_content += f"""
            <div class="component">
                <div class="component-header">
                    <h3>{suite_name}</h3>
                    <span class="component-status {status_class}">{status_text}</span>
                </div>
                <div class="component-details">
                    <div class="detail-item">Tests Run: {results['tests_run']}</div>
                    <div class="detail-item">Failures: {results['failures']}</div>
                    <div class="detail-item">Errors: {results['errors']}</div>
                    <div class="detail-item">Success Rate: {results['success_rate']:.1f}%</div>
                    
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{results['tests_run']}</div>
                            <div class="metric-label">Total Tests</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{results['tests_run'] - results['failures'] - results['errors']}</div>
                            <div class="metric-label">Passed</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{results['failures'] + results['errors']}</div>
                            <div class="metric-label">Failed</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{results['success_rate']:.1f}%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                    </div>
                </div>
            </div>
"""
        
        html_content += "</div>"
        
        # Add failure details if there are any
        if self.result.failures or self.result.errors:
            html_content += f"""
        <div class="failure-details">
            <h2>Failure Details</h2>
"""
            
            if self.result.failures:
                html_content += f"<h3>Test Failures ({len(self.result.failures)}):</h3>"
                for failure in self.result.failures[:10]:  # Show first 10 failures
                    html_content += f"""
            <div class="failure-item">
                <strong>{failure['suite']}</strong>: {failure['test']}
            </div>
"""
                if len(self.result.failures) > 10:
                    html_content += f"<p>... and {len(self.result.failures) - 10} more failures</p>"
            
            if self.result.errors:
                html_content += f"<h3>Test Errors ({len(self.result.errors)}):</h3>"
                for error in self.result.errors[:10]:  # Show first 10 errors
                    html_content += f"""
            <div class="failure-item">
                <strong>{error['suite']}</strong>: {error['test']}
            </div>
"""
                if len(self.result.errors) > 10:
                    html_content += f"<p>... and {len(self.result.errors) - 10} more errors</p>"
            
            html_content += "</div>"
        
        # Add recommendations
        recommendations = []
        if self.result.is_regression_detected():
            recommendations.append("⚠️ REGRESSION DETECTED: Success rate is below acceptable threshold (95%)")
            recommendations.append("🔧 Review and fix failing tests to improve system stability")
        
        if self.result.failed_tests > 0:
            recommendations.append(f"📋 Address {self.result.failed_tests} failed tests")
        
        if self.result.error_tests > 0:
            recommendations.append(f"🔍 Investigate {self.result.error_tests} test errors")
        
        if not recommendations:
            recommendations.append("✅ All tests passed - system is functioning well")
        
        html_content += f"""
        <div class="recommendations">
            <h2>Recommendations</h2>
"""
        
        for recommendation in recommendations:
            html_content += f'<div class="recommendation">{recommendation}</div>'
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>Report generated by PO to SO Agent Demo Regression Test Suite</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report saved to: {output_file}")
        return output_file


def main():
    """Main function to run regression tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run regression tests for PO to SO Agent Demo')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--save-report', '-s', action='store_true', help='Save detailed JSON report')
    parser.add_argument('--html-report', '--html', action='store_true', help='Generate HTML report')
    
    args = parser.parse_args()
    
    try:
        # Create and run regression test runner
        runner = RegressionTestRunner()
        result = runner.run_all_tests(verbose=args.verbose)
        
        # Always generate HTML report
        runner.generate_html_report()
        
        # Save JSON report if requested
        if args.save_report:
            runner.save_results_report()
        
        # Exit with appropriate code
        if result.is_regression_detected():
            print("\n❌ REGRESSION TESTS FAILED")
            sys.exit(1)
        else:
            print("\n✅ REGRESSION TESTS PASSED")
            sys.exit(0)
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Some test modules may be missing or have import issues.")
        print("Please check that all required test files exist and are properly structured.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()