"""
Test configuration and result data models for consistent test execution.
Defines data structures for test configuration, results, and reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test execution status enumeration"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"


@dataclass
class TestResult:
    """Individual test result data model"""
    test_name: str
    status: TestStatus
    execution_time: float
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    assertions_count: int = 0
    
    def __post_init__(self):
        if self.end_time is None:
            self.end_time = datetime.now()


@dataclass
class TestSuiteResults:
    """Test suite execution results"""
    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    execution_time: float
    start_time: datetime
    end_time: datetime
    test_results: List[TestResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100.0
        
    @property
    def status(self) -> TestStatus:
        """Overall suite status"""
        if self.errors > 0:
            return TestStatus.ERROR
        elif self.failed > 0:
            return TestStatus.FAILED
        elif self.passed == self.total_tests:
            return TestStatus.PASSED
        else:
            return TestStatus.SKIPPED


@dataclass
class ComprehensiveTestResults:
    """Complete test execution results across all suites"""
    execution_timestamp: datetime
    overall_status: TestStatus
    total_execution_time: float
    suite_results: Dict[str, TestSuiteResults] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    coverage_report: Dict[str, float] = field(default_factory=dict)
    environment_info: Dict[str, str] = field(default_factory=dict)
    
    @property
    def total_tests(self) -> int:
        """Total number of tests across all suites"""
        return sum(suite.total_tests for suite in self.suite_results.values())
        
    @property
    def total_passed(self) -> int:
        """Total number of passed tests"""
        return sum(suite.passed for suite in self.suite_results.values())
        
    @property
    def total_failed(self) -> int:
        """Total number of failed tests"""
        return sum(suite.failed for suite in self.suite_results.values())
        
    @property
    def total_errors(self) -> int:
        """Total number of error tests"""
        return sum(suite.errors for suite in self.suite_results.values())
        
    @property
    def overall_success_rate(self) -> float:
        """Overall success rate across all suites"""
        if self.total_tests == 0:
            return 0.0
        return (self.total_passed / self.total_tests) * 100.0


@dataclass
class TestConfiguration:
    """Test execution configuration"""
    test_data_path: str = "test_suite/fixtures"
    output_path: str = "test_suite/reports"
    parallel_execution: bool = False
    max_workers: int = 4
    timeout_seconds: int = 300
    cleanup_after_tests: bool = True
    generate_coverage: bool = True
    verbose_output: bool = False
    fail_fast: bool = False
    test_patterns: List[str] = field(default_factory=lambda: ["test_*.py"])
    excluded_patterns: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Ensure output directory exists
        import os
        os.makedirs(self.output_path, exist_ok=True)


@dataclass
class PerformanceTestConfig:
    """Performance testing specific configuration"""
    small_dataset_size: int = 10
    medium_dataset_size: int = 500
    large_dataset_size: int = 2000
    max_execution_time: float = 30.0
    memory_limit_mb: int = 512
    cpu_limit_percent: float = 80.0
    concurrent_users: int = 5
    warmup_iterations: int = 3
    measurement_iterations: int = 10
    
    
@dataclass
class SecurityTestConfig:
    """Security testing specific configuration"""
    enable_input_sanitization_tests: bool = True
    enable_file_permission_tests: bool = True
    enable_data_protection_tests: bool = True
    enable_audit_trail_tests: bool = True
    sensitive_data_patterns: List[str] = field(default_factory=lambda: [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
        r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card pattern
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email pattern
    ])


@dataclass
class AgentTestResult:
    """Agent-specific test result"""
    agent_name: str
    test_type: str  # 'unit', 'integration', 'performance'
    status: TestStatus
    execution_time: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    validation_results: Dict[str, bool] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_details: Optional[str] = None


@dataclass
class WorkflowTestResult:
    """Workflow execution test result"""
    workflow_name: str
    execution_mode: str  # 'sequential', 'parallel'
    agents_executed: List[str]
    total_execution_time: float
    agent_results: Dict[str, AgentTestResult] = field(default_factory=dict)
    data_flow_validation: bool = True
    shared_data_consistency: bool = True
    error_handling_validation: bool = True


@dataclass
class TestExecutionContext:
    """Context information for test execution"""
    test_id: str
    test_suite: str
    test_name: str
    start_time: datetime
    configuration: TestConfiguration
    environment_variables: Dict[str, str] = field(default_factory=dict)
    temp_directories: List[str] = field(default_factory=list)
    created_files: List[str] = field(default_factory=list)
    
    def cleanup(self):
        """Cleanup test execution context"""
        import os
        import shutil
        
        # Remove created files
        for file_path in self.created_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
                
        # Remove temporary directories
        for dir_path in self.temp_directories:
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass


@dataclass
class TestMetrics:
    """Test execution metrics and statistics"""
    total_assertions: int = 0
    successful_assertions: int = 0
    failed_assertions: int = 0
    average_execution_time: float = 0.0
    peak_memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_io_operations: int = 0
    network_requests: int = 0
    
    @property
    def assertion_success_rate(self) -> float:
        """Calculate assertion success rate"""
        if self.total_assertions == 0:
            return 0.0
        return (self.successful_assertions / self.total_assertions) * 100.0


@dataclass
class TestReport:
    """Comprehensive test report data model"""
    report_id: str
    generation_time: datetime
    test_results: ComprehensiveTestResults
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    charts_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.summary = {
            'total_tests': self.test_results.total_tests,
            'success_rate': self.test_results.overall_success_rate,
            'execution_time': self.test_results.total_execution_time,
            'suites_count': len(self.test_results.suite_results),
            'failed_tests': self.test_results.total_failed,
            'error_tests': self.test_results.total_errors
        }
        
        # Generate basic recommendations
        if self.test_results.overall_success_rate < 90:
            self.recommendations.append("Consider reviewing failed tests to improve success rate")
        if self.test_results.total_execution_time > 300:  # 5 minutes
            self.recommendations.append("Consider optimizing test execution time")
        if self.test_results.total_errors > 0:
            self.recommendations.append("Address test errors to improve test reliability")