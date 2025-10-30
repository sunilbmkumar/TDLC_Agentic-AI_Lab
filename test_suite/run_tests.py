#!/usr/bin/env python3
"""
Main test execution script for the comprehensive test suite.
Provides command-line interface for running tests with various options.
"""

import argparse
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_suite.utilities.test_runner import TestSuiteRunner
from test_suite.utilities.test_models import TestConfiguration, TestStatus
from test_suite.utilities.test_reporter import TestReportGenerator


def main():
    """Main entry point for test execution"""
    parser = argparse.ArgumentParser(description='Comprehensive Test Suite Runner')
    
    # Test selection arguments
    parser.add_argument('--suite', choices=[
        'unit', 'integration', 'orchestration', 'error_handling',
        'data_validation', 'web_dashboard', 'performance', 
        'config', 'security', 'regression', 'all'
    ], default='all', help='Test suite to run')
    
    parser.add_argument('--pattern', nargs='+', default=['test_*.py'],
                       help='Test file patterns to match')
    
    parser.add_argument('--exclude', nargs='+', default=[],
                       help='Test patterns to exclude')
    
    # Execution options
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel')
    
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers')
    
    parser.add_argument('--timeout', type=int, default=300,
                       help='Test timeout in seconds')
    
    parser.add_argument('--fail-fast', action='store_true',
                       help='Stop on first failure')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--output-dir', default='test_suite/reports',
                       help='Output directory for reports')
    
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Skip cleanup after tests')
    
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    
    # Report options
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML report')
    
    parser.add_argument('--json-report', action='store_true',
                       help='Generate JSON report')
    
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfiguration(
        test_data_path="test_suite/fixtures",
        output_path=args.output_dir,
        parallel_execution=args.parallel,
        max_workers=args.workers,
        timeout_seconds=args.timeout,
        cleanup_after_tests=not args.no_cleanup,
        generate_coverage=args.coverage,
        verbose_output=args.verbose,
        fail_fast=args.fail_fast,
        test_patterns=args.pattern,
        excluded_patterns=args.exclude
    )
    
    # Create test runner
    runner = TestSuiteRunner(config)
    
    print(f"Starting test execution at {datetime.now()}")
    print(f"Configuration: {args.suite} suite, parallel={args.parallel}, workers={args.workers}")
    
    try:
        # Run selected test suite
        if args.suite == 'all':
            results = runner.run_full_suite()
        elif args.suite == 'unit':
            suite_result = runner.run_unit_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'integration':
            suite_result = runner.run_integration_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'orchestration':
            suite_result = runner.run_orchestration_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'error_handling':
            suite_result = runner.run_error_handling_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'data_validation':
            suite_result = runner.run_data_validation_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'web_dashboard':
            suite_result = runner.run_web_dashboard_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'performance':
            suite_result = runner.run_performance_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'config':
            suite_result = runner.run_config_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'security':
            suite_result = runner.run_security_tests()
            results = _create_comprehensive_results(suite_result)
        elif args.suite == 'regression':
            suite_result = runner.run_regression_tests()
            results = _create_comprehensive_results(suite_result)
        
        # Print summary
        print_test_summary(results)
        
        # Generate reports if requested
        if args.html_report or args.json_report:
            report_generator = TestReportGenerator(config.output_path)
            
            if args.html_report:
                html_path = report_generator.generate_html_report(results)
                print(f"HTML report generated: {html_path}")
                
            if args.json_report:
                json_path = report_generator.generate_json_report(results)
                print(f"JSON report generated: {json_path}")
        
        # Exit with appropriate code
        if results.overall_status == TestStatus.PASSED:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Error during test execution: {e}")
        sys.exit(1)


def _create_comprehensive_results(suite_result):
    """Create comprehensive results from single suite result"""
    from test_suite.utilities.test_models import ComprehensiveTestResults
    
    results = ComprehensiveTestResults(
        execution_timestamp=suite_result.start_time,
        overall_status=suite_result.status,
        total_execution_time=suite_result.execution_time
    )
    results.suite_results[suite_result.suite_name] = suite_result
    
    return results


def print_test_summary(results):
    """Print test execution summary"""
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    
    print(f"Overall Status: {results.overall_status.value.upper()}")
    print(f"Total Tests: {results.total_tests}")
    print(f"Passed: {results.total_passed}")
    print(f"Failed: {results.total_failed}")
    print(f"Errors: {results.total_errors}")
    print(f"Success Rate: {results.overall_success_rate:.1f}%")
    print(f"Execution Time: {results.total_execution_time:.2f} seconds")
    
    if results.suite_results:
        print("\nSuite Results:")
        print("-" * 40)
        for suite_name, suite_result in results.suite_results.items():
            status_symbol = "✓" if suite_result.status == TestStatus.PASSED else "✗"
            print(f"{status_symbol} {suite_name}: {suite_result.passed}/{suite_result.total_tests} passed "
                  f"({suite_result.success_rate:.1f}%) in {suite_result.execution_time:.2f}s")
    
    if results.total_failed > 0 or results.total_errors > 0:
        print("\nFailed/Error Tests:")
        print("-" * 40)
        for suite_result in results.suite_results.values():
            for test_result in suite_result.test_results:
                if test_result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"✗ {test_result.test_name}: {test_result.error_message}")
    
    print("="*60)


if __name__ == '__main__':
    main()