"""
Test Suite Runner for coordinating test execution.
Provides parallel test execution, timeout management, and result collection.
"""

import unittest
import os
import sys
import time
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging
import traceback
import importlib.util
import signal

from .test_models import (
    TestConfiguration, TestResult, TestSuiteResults, ComprehensiveTestResults,
    TestStatus, TestExecutionContext, TestMetrics
)


class TestTimeout(Exception):
    """Exception raised when test execution times out"""
    pass


class TestSuiteRunner:
    """Main test execution engine with reporting and parallel execution capabilities"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.logger = self._setup_logging()
        self.test_suites = {}
        self.execution_context = None
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for test execution"""
        logger = logging.getLogger('TestSuiteRunner')
        logger.setLevel(logging.DEBUG if self.config.verbose_output else logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(self.config.output_path, 'test_execution.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
        
    def discover_test_suites(self, test_directory: str = "test_suite") -> Dict[str, List[str]]:
        """
        Discover test suites and test files.
        
        Args:
            test_directory: Root directory to search for tests
            
        Returns:
            Dictionary mapping suite names to test file lists
        """
        test_suites = {}
        
        for root, dirs, files in os.walk(test_directory):
            # Skip __pycache__ and other non-test directories
            dirs[:] = [d for d in dirs if not d.startswith('__pycache__') and d != 'reports']
            
            suite_name = os.path.basename(root)
            if suite_name == 'test_suite':
                continue
                
            test_files = []
            for file in files:
                if file.endswith('.py') and file.startswith('test_'):
                    if not any(pattern in file for pattern in self.config.excluded_patterns):
                        test_files.append(os.path.join(root, file))
                        
            if test_files:
                test_suites[suite_name] = test_files
                
        self.test_suites = test_suites
        self.logger.info(f"Discovered {len(test_suites)} test suites with {sum(len(files) for files in test_suites.values())} test files")
        
        return test_suites
        
    def run_unit_tests(self) -> TestSuiteResults:
        """Execute all unit tests"""
        return self._run_test_suite("unit_tests")
        
    def run_integration_tests(self) -> TestSuiteResults:
        """Execute integration test suite"""
        return self._run_test_suite("integration_tests")
        
    def run_performance_tests(self) -> TestSuiteResults:
        """Execute performance benchmarks"""
        return self._run_test_suite("performance_tests")
        
    def run_orchestration_tests(self) -> TestSuiteResults:
        """Execute orchestration system tests"""
        return self._run_test_suite("orchestration_tests")
        
    def run_error_handling_tests(self) -> TestSuiteResults:
        """Execute error handling tests"""
        return self._run_test_suite("error_handling_tests")
        
    def run_data_validation_tests(self) -> TestSuiteResults:
        """Execute data validation tests"""
        return self._run_test_suite("data_validation_tests")
        
    def run_web_dashboard_tests(self) -> TestSuiteResults:
        """Execute web dashboard tests"""
        return self._run_test_suite("web_dashboard_tests")
        
    def run_config_tests(self) -> TestSuiteResults:
        """Execute configuration tests"""
        return self._run_test_suite("config_tests")
        
    def run_security_tests(self) -> TestSuiteResults:
        """Execute security tests"""
        return self._run_test_suite("security_tests")
        
    def run_regression_tests(self) -> TestSuiteResults:
        """Execute regression tests"""
        return self._run_test_suite("regression_tests")
        
    def run_full_suite(self) -> ComprehensiveTestResults:
        """
        Execute complete test suite with reporting.
        
        Returns:
            Comprehensive test results across all suites
        """
        start_time = datetime.now()
        self.logger.info("Starting comprehensive test suite execution")
        
        # Discover all test suites
        self.discover_test_suites()
        
        # Initialize comprehensive results
        comprehensive_results = ComprehensiveTestResults(
            execution_timestamp=start_time,
            overall_status=TestStatus.IN_PROGRESS,
            total_execution_time=0.0
        )
        
        # Execute each test suite
        suite_execution_order = [
            "unit_tests",
            "integration_tests", 
            "orchestration_tests",
            "error_handling_tests",
            "data_validation_tests",
            "web_dashboard_tests",
            "performance_tests",
            "config_tests",
            "security_tests",
            "regression_tests"
        ]
        
        for suite_name in suite_execution_order:
            if suite_name in self.test_suites:
                try:
                    self.logger.info(f"Executing {suite_name}")
                    suite_results = self._run_test_suite(suite_name)
                    comprehensive_results.suite_results[suite_name] = suite_results
                    
                    # Stop on first failure if fail_fast is enabled
                    if self.config.fail_fast and suite_results.failed > 0:
                        self.logger.warning(f"Stopping execution due to failures in {suite_name} (fail_fast enabled)")
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error executing {suite_name}: {e}")
                    # Create error result for failed suite
                    error_result = TestSuiteResults(
                        suite_name=suite_name,
                        total_tests=0,
                        passed=0,
                        failed=0,
                        skipped=0,
                        errors=1,
                        execution_time=0.0,
                        start_time=datetime.now(),
                        end_time=datetime.now()
                    )
                    comprehensive_results.suite_results[suite_name] = error_result
                    
        # Calculate overall results
        end_time = datetime.now()
        comprehensive_results.total_execution_time = (end_time - start_time).total_seconds()
        
        # Determine overall status
        if comprehensive_results.total_errors > 0:
            comprehensive_results.overall_status = TestStatus.ERROR
        elif comprehensive_results.total_failed > 0:
            comprehensive_results.overall_status = TestStatus.FAILED
        else:
            comprehensive_results.overall_status = TestStatus.PASSED
            
        # Add environment info
        comprehensive_results.environment_info = self._get_environment_info()
        
        self.logger.info(f"Test suite execution completed in {comprehensive_results.total_execution_time:.2f} seconds")
        self.logger.info(f"Results: {comprehensive_results.total_passed} passed, {comprehensive_results.total_failed} failed, {comprehensive_results.total_errors} errors")
        
        return comprehensive_results
        
    def _run_test_suite(self, suite_name: str) -> TestSuiteResults:
        """
        Execute a specific test suite.
        
        Args:
            suite_name: Name of the test suite to execute
            
        Returns:
            Test suite results
        """
        start_time = datetime.now()
        
        if suite_name not in self.test_suites:
            self.logger.warning(f"Test suite {suite_name} not found")
            return TestSuiteResults(
                suite_name=suite_name,
                total_tests=0,
                passed=0,
                failed=0,
                skipped=0,
                errors=0,
                execution_time=0.0,
                start_time=start_time,
                end_time=datetime.now()
            )
            
        test_files = self.test_suites[suite_name]
        self.logger.info(f"Running {len(test_files)} test files in {suite_name}")
        
        # Execute tests
        if self.config.parallel_execution and len(test_files) > 1:
            test_results = self._run_tests_parallel(test_files)
        else:
            test_results = self._run_tests_sequential(test_files)
            
        # Calculate suite results
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        passed = sum(1 for result in test_results if result.status == TestStatus.PASSED)
        failed = sum(1 for result in test_results if result.status == TestStatus.FAILED)
        skipped = sum(1 for result in test_results if result.status == TestStatus.SKIPPED)
        errors = sum(1 for result in test_results if result.status == TestStatus.ERROR)
        
        suite_results = TestSuiteResults(
            suite_name=suite_name,
            total_tests=len(test_results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            execution_time=execution_time,
            start_time=start_time,
            end_time=end_time,
            test_results=test_results
        )
        
        self.logger.info(f"Suite {suite_name} completed: {passed} passed, {failed} failed, {errors} errors")
        
        return suite_results
        
    def _run_tests_sequential(self, test_files: List[str]) -> List[TestResult]:
        """Run tests sequentially"""
        results = []
        
        for test_file in test_files:
            try:
                result = self._execute_test_file(test_file)
                results.extend(result)
            except Exception as e:
                self.logger.error(f"Error executing test file {test_file}: {e}")
                error_result = TestResult(
                    test_name=os.path.basename(test_file),
                    status=TestStatus.ERROR,
                    execution_time=0.0,
                    start_time=datetime.now(),
                    error_message=str(e),
                    error_traceback=traceback.format_exc()
                )
                results.append(error_result)
                
        return results
        
    def _run_tests_parallel(self, test_files: List[str]) -> List[TestResult]:
        """Run tests in parallel using thread pool"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all test files for execution
            future_to_file = {
                executor.submit(self._execute_test_file, test_file): test_file 
                for test_file in test_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file, timeout=self.config.timeout_seconds):
                test_file = future_to_file[future]
                try:
                    test_results = future.result()
                    results.extend(test_results)
                except Exception as e:
                    self.logger.error(f"Error executing test file {test_file}: {e}")
                    error_result = TestResult(
                        test_name=os.path.basename(test_file),
                        status=TestStatus.ERROR,
                        execution_time=0.0,
                        start_time=datetime.now(),
                        error_message=str(e),
                        error_traceback=traceback.format_exc()
                    )
                    results.append(error_result)
                    
        return results
        
    def _execute_test_file(self, test_file: str) -> List[TestResult]:
        """
        Execute a single test file and return results.
        
        Args:
            test_file: Path to test file
            
        Returns:
            List of test results from the file
        """
        results = []
        
        try:
            # Load the test module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Discover test cases in the module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Execute tests with custom result collector
            result_collector = TestResultCollector()
            
            # Set up timeout handling
            if self.config.timeout_seconds > 0:
                signal.signal(signal.SIGALRM, self._timeout_handler)
                signal.alarm(self.config.timeout_seconds)
                
            try:
                suite.run(result_collector)
            finally:
                if self.config.timeout_seconds > 0:
                    signal.alarm(0)  # Cancel timeout
                    
            # Convert unittest results to our format
            results = result_collector.get_test_results()
            
        except Exception as e:
            self.logger.error(f"Error loading/executing test file {test_file}: {e}")
            error_result = TestResult(
                test_name=os.path.basename(test_file),
                status=TestStatus.ERROR,
                execution_time=0.0,
                start_time=datetime.now(),
                error_message=str(e),
                error_traceback=traceback.format_exc()
            )
            results.append(error_result)
            
        return results
        
    def _timeout_handler(self, signum, frame):
        """Handle test timeout"""
        raise TestTimeout("Test execution timed out")
        
    def _get_environment_info(self) -> Dict[str, str]:
        """Get environment information for reporting"""
        import platform
        
        return {
            'python_version': sys.version,
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'hostname': platform.node(),
            'working_directory': os.getcwd(),
            'test_runner_version': '1.0.0'
        }
        
    def run_selective_tests(self, test_patterns: List[str]) -> ComprehensiveTestResults:
        """
        Run tests matching specific patterns.
        
        Args:
            test_patterns: List of test patterns to match
            
        Returns:
            Comprehensive test results for matching tests
        """
        # Update configuration with selective patterns
        original_patterns = self.config.test_patterns
        self.config.test_patterns = test_patterns
        
        try:
            # Run full suite with updated patterns
            results = self.run_full_suite()
        finally:
            # Restore original patterns
            self.config.test_patterns = original_patterns
            
        return results


class TestResultCollector(unittest.TestResult):
    """Custom test result collector for converting unittest results"""
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.current_test_start = None
        
    def startTest(self, test):
        """Called when a test starts"""
        super().startTest(test)
        self.current_test_start = datetime.now()
        
    def addSuccess(self, test):
        """Called when a test passes"""
        super().addSuccess(test)
        self._add_result(test, TestStatus.PASSED)
        
    def addError(self, test, err):
        """Called when a test has an error"""
        super().addError(test, err)
        self._add_result(test, TestStatus.ERROR, err)
        
    def addFailure(self, test, err):
        """Called when a test fails"""
        super().addFailure(test, err)
        self._add_result(test, TestStatus.FAILED, err)
        
    def addSkip(self, test, reason):
        """Called when a test is skipped"""
        super().addSkip(test, reason)
        self._add_result(test, TestStatus.SKIPPED, error_message=reason)
        
    def _add_result(self, test, status: TestStatus, err=None, error_message=None):
        """Add a test result to the collection"""
        end_time = datetime.now()
        execution_time = (end_time - self.current_test_start).total_seconds()
        
        error_msg = error_message
        error_trace = None
        
        if err:
            error_msg = str(err[1])
            error_trace = ''.join(traceback.format_exception(*err))
            
        result = TestResult(
            test_name=str(test),
            status=status,
            execution_time=execution_time,
            start_time=self.current_test_start,
            end_time=end_time,
            error_message=error_msg,
            error_traceback=error_trace
        )
        
        self.test_results.append(result)
        
    def get_test_results(self) -> List[TestResult]:
        """Get collected test results"""
        return self.test_results