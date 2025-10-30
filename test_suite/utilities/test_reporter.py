"""
Test Report Generator for creating comprehensive test reports.
Generates HTML and JSON reports with charts and detailed analysis.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from jinja2 import Template

from .test_models import ComprehensiveTestResults, TestReport, TestStatus


class TestReportGenerator:
    """Generates comprehensive test reports in various formats"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_html_report(self, results: ComprehensiveTestResults) -> str:
        """
        Generate HTML test report with charts and details.
        
        Args:
            results: Comprehensive test results
            
        Returns:
            Path to generated HTML report
        """
        report = TestReport(
            report_id=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            generation_time=datetime.now(),
            test_results=results
        )
        
        # Generate charts data
        report.charts_data = self._generate_charts_data(results)
        
        # Create HTML content
        html_content = self._create_html_content(report)
        
        # Save HTML report
        html_path = os.path.join(self.output_dir, f"{report.report_id}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return html_path
        
    def generate_json_report(self, results: ComprehensiveTestResults) -> str:
        """
        Generate machine-readable JSON report.
        
        Args:
            results: Comprehensive test results
            
        Returns:
            Path to generated JSON report
        """
        report_data = {
            'report_id': f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generation_time': datetime.now().isoformat(),
            'overall_status': results.overall_status.value,
            'total_execution_time': results.total_execution_time,
            'summary': {
                'total_tests': results.total_tests,
                'total_passed': results.total_passed,
                'total_failed': results.total_failed,
                'total_errors': results.total_errors,
                'success_rate': results.overall_success_rate
            },
            'suite_results': {},
            'environment_info': results.environment_info
        }
        
        # Add suite results
        for suite_name, suite_result in results.suite_results.items():
            report_data['suite_results'][suite_name] = {
                'total_tests': suite_result.total_tests,
                'passed': suite_result.passed,
                'failed': suite_result.failed,
                'skipped': suite_result.skipped,
                'errors': suite_result.errors,
                'execution_time': suite_result.execution_time,
                'success_rate': suite_result.success_rate,
                'status': suite_result.status.value,
                'test_results': [
                    {
                        'test_name': test.test_name,
                        'status': test.status.value,
                        'execution_time': test.execution_time,
                        'error_message': test.error_message
                    }
                    for test in suite_result.test_results
                ]
            }
        
        # Save JSON report
        json_path = os.path.join(self.output_dir, f"{report_data['report_id']}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        return json_path
        
    def _generate_charts_data(self, results: ComprehensiveTestResults) -> Dict[str, Any]:
        """Generate data for charts and visualizations"""
        charts_data = {}
        
        # Overall status pie chart
        charts_data['overall_status'] = {
            'labels': ['Passed', 'Failed', 'Errors'],
            'data': [results.total_passed, results.total_failed, results.total_errors],
            'colors': ['#28a745', '#dc3545', '#ffc107']
        }
        
        # Suite comparison bar chart
        suite_names = list(results.suite_results.keys())
        suite_passed = [results.suite_results[name].passed for name in suite_names]
        suite_failed = [results.suite_results[name].failed for name in suite_names]
        suite_errors = [results.suite_results[name].errors for name in suite_names]
        
        charts_data['suite_comparison'] = {
            'labels': suite_names,
            'datasets': [
                {
                    'label': 'Passed',
                    'data': suite_passed,
                    'backgroundColor': '#28a745'
                },
                {
                    'label': 'Failed',
                    'data': suite_failed,
                    'backgroundColor': '#dc3545'
                },
                {
                    'label': 'Errors',
                    'data': suite_errors,
                    'backgroundColor': '#ffc107'
                }
            ]
        }
        
        # Execution time comparison
        suite_times = [results.suite_results[name].execution_time for name in suite_names]
        charts_data['execution_times'] = {
            'labels': suite_names,
            'data': suite_times,
            'backgroundColor': '#17a2b8'
        }
        
        return charts_data
        
    def _create_html_content(self, report: TestReport) -> str:
        """Create HTML content for the report"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {{ report.report_id }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-passed { background-color: #d4edda; color: #155724; }
        .status-failed { background-color: #f8d7da; color: #721c24; }
        .status-error { background-color: #fff3cd; color: #856404; }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-number {
            font-size: 2em;
            font-weight: bold;
            color: #495057;
        }
        .summary-label {
            color: #6c757d;
            margin-top: 5px;
        }
        .charts-section {
            margin-bottom: 30px;
        }
        .chart-container {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
        }
        .suite-results {
            margin-top: 30px;
        }
        .suite-card {
            margin-bottom: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }
        .suite-header {
            background: #e9ecef;
            padding: 15px;
            font-weight: bold;
        }
        .suite-content {
            padding: 15px;
        }
        .test-result {
            padding: 8px 0;
            border-bottom: 1px solid #f1f3f4;
        }
        .test-result:last-child {
            border-bottom: none;
        }
        .test-name {
            font-weight: 500;
        }
        .test-status {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .recommendations {
            background: #e7f3ff;
            border-left: 4px solid #0066cc;
            padding: 15px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Execution Report</h1>
            <p>Generated on {{ report.generation_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
            <span class="status-badge status-{{ report.test_results.overall_status.value }}">
                {{ report.test_results.overall_status.value.upper() }}
            </span>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-number">{{ report.test_results.total_tests }}</div>
                <div class="summary-label">Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{{ report.test_results.total_passed }}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{{ report.test_results.total_failed }}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{{ report.test_results.total_errors }}</div>
                <div class="summary-label">Errors</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{{ "%.1f"|format(report.test_results.overall_success_rate) }}%</div>
                <div class="summary-label">Success Rate</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{{ "%.2f"|format(report.test_results.total_execution_time) }}s</div>
                <div class="summary-label">Execution Time</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <div class="chart-title">Test Results Overview</div>
                <canvas id="overallChart" width="400" height="200"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">Suite Comparison</div>
                <canvas id="suiteChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="suite-results">
            <h2>Detailed Results by Suite</h2>
            {% for suite_name, suite_result in report.test_results.suite_results.items() %}
            <div class="suite-card">
                <div class="suite-header">
                    {{ suite_name }} - {{ suite_result.passed }}/{{ suite_result.total_tests }} passed 
                    ({{ "%.1f"|format(suite_result.success_rate) }}%)
                </div>
                <div class="suite-content">
                    {% for test_result in suite_result.test_results %}
                    <div class="test-result">
                        <span class="test-name">{{ test_result.test_name }}</span>
                        <span class="test-status status-{{ test_result.status.value }}">
                            {{ test_result.status.value.upper() }}
                        </span>
                        <span style="float: right; color: #6c757d;">
                            {{ "%.3f"|format(test_result.execution_time) }}s
                        </span>
                        {% if test_result.error_message %}
                        <div style="color: #dc3545; font-size: 0.9em; margin-top: 5px;">
                            {{ test_result.error_message }}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        {% if report.recommendations %}
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
                {% for recommendation in report.recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    
    <script>
        // Overall status pie chart
        const overallCtx = document.getElementById('overallChart').getContext('2d');
        new Chart(overallCtx, {
            type: 'pie',
            data: {
                labels: {{ report.charts_data.overall_status.labels | tojson }},
                datasets: [{
                    data: {{ report.charts_data.overall_status.data | tojson }},
                    backgroundColor: {{ report.charts_data.overall_status.colors | tojson }}
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
        
        // Suite comparison bar chart
        const suiteCtx = document.getElementById('suiteChart').getContext('2d');
        new Chart(suiteCtx, {
            type: 'bar',
            data: {{ report.charts_data.suite_comparison | tojson }},
            options: {
                responsive: true,
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>
        """
        
        template = Template(html_template)
        return template.render(report=report)
        
    def generate_coverage_report(self) -> str:
        """Generate code coverage analysis report"""
        # This would integrate with coverage.py or similar tool
        # For now, return placeholder
        coverage_path = os.path.join(self.output_dir, 'coverage_report.html')
        
        with open(coverage_path, 'w') as f:
            f.write("""
            <html>
            <head><title>Coverage Report</title></head>
            <body>
                <h1>Code Coverage Report</h1>
                <p>Coverage analysis would be implemented here using coverage.py</p>
            </body>
            </html>
            """)
            
        return coverage_path