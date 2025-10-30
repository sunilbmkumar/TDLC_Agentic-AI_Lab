#!/usr/bin/env python3
"""
Regression Test Report Generator - Creates HTML report for regression test results
"""

import sys
import os
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def run_regression_analysis():
    """Run regression analysis and collect results"""
    print("Running regression analysis...")
    
    results = {
        'execution_time': datetime.now().isoformat(),
        'system_status': 'unknown',
        'total_components': 0,
        'passed_components': 0,
        'failed_components': 0,
        'component_results': [],
        'detailed_results': {},
        'recommendations': []
    }
    
    # Test 1: Agent System Analysis
    print("  Analyzing agent system...")
    agent_results = analyze_agent_system()
    results['component_results'].append(agent_results)
    results['detailed_results']['agents'] = agent_results
    
    # Test 2: Orchestration System Analysis
    print("  Analyzing orchestration system...")
    orchestration_results = analyze_orchestration_system()
    results['component_results'].append(orchestration_results)
    results['detailed_results']['orchestration'] = orchestration_results
    
    # Test 3: Data Pipeline Analysis
    print("  Analyzing data pipeline...")
    data_results = analyze_data_pipeline()
    results['component_results'].append(data_results)
    results['detailed_results']['data_pipeline'] = data_results
    
    # Test 4: Output Generation Analysis
    print("  Analyzing output generation...")
    output_results = analyze_output_generation()
    results['component_results'].append(output_results)
    results['detailed_results']['outputs'] = output_results
    
    # Test 5: Configuration Analysis
    print("  Analyzing configuration...")
    config_results = analyze_configuration()
    results['component_results'].append(config_results)
    results['detailed_results']['configuration'] = config_results
    
    # Calculate overall results
    results['total_components'] = len(results['component_results'])
    results['passed_components'] = sum(1 for r in results['component_results'] if r['status'] == 'passed')
    results['failed_components'] = results['total_components'] - results['passed_components']
    
    # Determine system status
    success_rate = (results['passed_components'] / results['total_components']) * 100 if results['total_components'] > 0 else 0
    
    if success_rate >= 95:
        results['system_status'] = 'excellent'
    elif success_rate >= 80:
        results['system_status'] = 'good'
    elif success_rate >= 60:
        results['system_status'] = 'fair'
    else:
        results['system_status'] = 'poor'
    
    # Generate recommendations
    results['recommendations'] = generate_recommendations(results)
    
    return results

def analyze_agent_system():
    """Analyze the agent system components"""
    result = {
        'name': 'Agent System',
        'status': 'passed',
        'details': [],
        'issues': [],
        'metrics': {}
    }
    
    agents = [
        ('PO Reader Agent', 'agents.po_reader.agent', 'POReaderAgent'),
        ('Validation Agent', 'agents.validation.agent', 'ValidationAgent'),
        ('Exception Response Agent', 'agents.exception_response.agent', 'ExceptionResponseAgent'),
        ('Sales Order Creator Agent', 'agents.so_creator.agent', 'SalesOrderCreatorAgent'),
        ('Summary Insights Agent', 'agents.summary_insights.agent', 'SummaryInsightsAgent'),
        ('PO Acknowledgment Agent', 'agents.po_acknowledgment.agent', 'POAcknowledgmentAgent')
    ]
    
    passed_agents = 0
    failed_agents = 0
    
    for agent_name, module_path, class_name in agents:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            
            # Test instantiation
            agent_instance = agent_class()
            
            result['details'].append(f"✅ {agent_name}: Import and instantiation successful")
            passed_agents += 1
            
        except Exception as e:
            result['details'].append(f"❌ {agent_name}: {str(e)}")
            result['issues'].append(f"{agent_name} failed: {str(e)}")
            failed_agents += 1
            result['status'] = 'failed'
    
    result['metrics'] = {
        'total_agents': len(agents),
        'passed_agents': passed_agents,
        'failed_agents': failed_agents,
        'success_rate': (passed_agents / len(agents)) * 100
    }
    
    return result

def analyze_orchestration_system():
    """Analyze the orchestration system"""
    result = {
        'name': 'Orchestration System',
        'status': 'passed',
        'details': [],
        'issues': [],
        'metrics': {}
    }
    
    components = [
        ('Orchestration Manager', 'orchestration.orchestration_manager', 'OrchestrationManager'),
        ('Agent Pipeline', 'orchestration.agent_pipeline', 'AgentExecutionPipeline'),
        ('Agent Coordinator', 'orchestration.agent_coordinator', 'AgentCoordinator')
    ]
    
    passed_components = 0
    failed_components = 0
    
    for comp_name, module_path, class_name in components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            comp_class = getattr(module, class_name)
            
            result['details'].append(f"✅ {comp_name}: Import successful")
            passed_components += 1
            
        except Exception as e:
            result['details'].append(f"❌ {comp_name}: {str(e)}")
            result['issues'].append(f"{comp_name} failed: {str(e)}")
            failed_components += 1
            result['status'] = 'failed'
    
    result['metrics'] = {
        'total_components': len(components),
        'passed_components': passed_components,
        'failed_components': failed_components,
        'success_rate': (passed_components / len(components)) * 100
    }
    
    return result

def analyze_data_pipeline():
    """Analyze the data pipeline"""
    result = {
        'name': 'Data Pipeline',
        'status': 'passed',
        'details': [],
        'issues': [],
        'metrics': {}
    }
    
    # Check data files
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    data_files = [
        ('Customer Orders', 'data/customer_orders.csv'),
        ('Master SKU Data', 'data/master_sku.csv')
    ]
    
    passed_files = 0
    failed_files = 0
    
    for file_name, file_path in data_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            # Check file size
            file_size = os.path.getsize(full_path)
            result['details'].append(f"✅ {file_name}: Present ({file_size} bytes)")
            passed_files += 1
        else:
            result['details'].append(f"❌ {file_name}: Missing")
            result['issues'].append(f"{file_name} file is missing")
            failed_files += 1
            result['status'] = 'failed'
    
    result['metrics'] = {
        'total_files': len(data_files),
        'passed_files': passed_files,
        'failed_files': failed_files,
        'success_rate': (passed_files / len(data_files)) * 100
    }
    
    return result

def analyze_output_generation():
    """Analyze output generation capabilities"""
    result = {
        'name': 'Output Generation',
        'status': 'passed',
        'details': [],
        'issues': [],
        'metrics': {}
    }
    
    # Check output files
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    output_files = [
        ('Validation Results', 'outputs/validation_results_detailed.json'),
        ('Sales Orders', 'outputs/sales_order_output.csv'),
        ('Exception Emails', 'outputs/exception_emails.json'),
        ('PO Acknowledgments', 'outputs/po_acknowledgments.csv'),
        ('Executive Summary', 'outputs/executive_summary_report.txt')
    ]
    
    passed_outputs = 0
    failed_outputs = 0
    
    for output_name, output_path in output_files:
        full_path = os.path.join(project_root, output_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            result['details'].append(f"✅ {output_name}: Generated ({file_size} bytes)")
            passed_outputs += 1
        else:
            result['details'].append(f"⚠️ {output_name}: Not generated")
            # Don't mark as failed since outputs might not exist until system runs
    
    result['metrics'] = {
        'total_outputs': len(output_files),
        'generated_outputs': passed_outputs,
        'missing_outputs': len(output_files) - passed_outputs,
        'generation_rate': (passed_outputs / len(output_files)) * 100
    }
    
    return result

def analyze_configuration():
    """Analyze system configuration"""
    result = {
        'name': 'Configuration',
        'status': 'passed',
        'details': [],
        'issues': [],
        'metrics': {}
    }
    
    # Check configuration files
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    config_files = [
        ('Orchestration Config', 'config/orchestration_config.json'),
        ('Agent Config', 'config/agent_config.json')
    ]
    
    passed_configs = 0
    failed_configs = 0
    
    for config_name, config_path in config_files:
        full_path = os.path.join(project_root, config_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r') as f:
                    config_data = json.load(f)
                result['details'].append(f"✅ {config_name}: Valid JSON ({len(config_data)} keys)")
                passed_configs += 1
            except json.JSONDecodeError as e:
                result['details'].append(f"❌ {config_name}: Invalid JSON - {str(e)}")
                result['issues'].append(f"{config_name} has invalid JSON")
                failed_configs += 1
                result['status'] = 'failed'
        else:
            result['details'].append(f"⚠️ {config_name}: Using defaults")
            # Don't mark as failed since defaults might be acceptable
    
    result['metrics'] = {
        'total_configs': len(config_files),
        'valid_configs': passed_configs,
        'invalid_configs': failed_configs,
        'config_validity_rate': (passed_configs / len(config_files)) * 100 if len(config_files) > 0 else 100
    }
    
    return result

def generate_recommendations(results):
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    # Check for failed components
    for component in results['component_results']:
        if component['status'] == 'failed':
            recommendations.append(f"Fix issues in {component['name']}: {', '.join(component['issues'])}")
    
    # Check success rates
    overall_success = (results['passed_components'] / results['total_components']) * 100
    
    if overall_success < 80:
        recommendations.append("System has significant issues that need immediate attention")
    elif overall_success < 95:
        recommendations.append("System is mostly functional but has some issues to address")
    else:
        recommendations.append("System is in excellent condition with no major issues detected")
    
    # Specific recommendations
    if results['detailed_results']['outputs']['metrics']['generation_rate'] < 80:
        recommendations.append("Run the main workflow to generate missing output files")
    
    if not recommendations:
        recommendations.append("No specific recommendations - system appears to be functioning well")
    
    return recommendations

def generate_html_report(results):
    """Generate HTML report from results"""
    
    # Determine status colors
    status_colors = {
        'excellent': '#28a745',
        'good': '#17a2b8', 
        'fair': '#ffc107',
        'poor': '#dc3545'
    }
    
    status_color = status_colors.get(results['system_status'], '#6c757d')
    
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
        </div>
        
        <div class="summary">
            <h2>System Status: <span class="status-badge">{results['system_status'].upper()}</span></h2>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Components</h3>
                    <div class="value">{results['total_components']}</div>
                </div>
                <div class="summary-card">
                    <h3>Passed</h3>
                    <div class="value">{results['passed_components']}</div>
                </div>
                <div class="summary-card">
                    <h3>Failed</h3>
                    <div class="value">{results['failed_components']}</div>
                </div>
                <div class="summary-card">
                    <h3>Success Rate</h3>
                    <div class="value">{(results['passed_components']/results['total_components']*100):.1f}%</div>
                </div>
            </div>
        </div>
        
        <div class="components">
            <h2>Component Analysis</h2>
"""
    
    # Add component details
    for component in results['component_results']:
        status_class = 'status-passed' if component['status'] == 'passed' else 'status-failed'
        
        html_content += f"""
            <div class="component">
                <div class="component-header">
                    <h3>{component['name']}</h3>
                    <span class="component-status {status_class}">{component['status']}</span>
                </div>
                <div class="component-details">
"""
        
        # Add details
        for detail in component['details']:
            html_content += f'<div class="detail-item">{detail}</div>'
        
        # Add metrics if available
        if component.get('metrics'):
            html_content += '<div class="metrics">'
            for key, value in component['metrics'].items():
                label = key.replace('_', ' ').title()
                if isinstance(value, float):
                    value_str = f"{value:.1f}{'%' if 'rate' in key else ''}"
                else:
                    value_str = str(value)
                
                html_content += f"""
                <div class="metric">
                    <div class="metric-value">{value_str}</div>
                    <div class="metric-label">{label}</div>
                </div>
"""
            html_content += '</div>'
        
        html_content += '</div></div>'
    
    # Add recommendations
    html_content += f"""
        </div>
        
        <div class="recommendations">
            <h2>Recommendations</h2>
"""
    
    for recommendation in results['recommendations']:
        html_content += f'<div class="recommendation">{recommendation}</div>'
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Report generated by PO to SO Agent Demo Regression Test Suite</p>
            <p>For technical support, please review the system logs and component details above.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def main():
    """Main function to generate regression test report"""
    try:
        print("=" * 60)
        print("REGRESSION TEST REPORT GENERATOR")
        print("=" * 60)
        
        # Run analysis
        results = run_regression_analysis()
        
        # Generate HTML report
        print("Generating HTML report...")
        html_content = generate_html_report(results)
        
        # Save to reports directory
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, 'regression_test_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved to: {report_path}")
        
        # Also save JSON results
        json_path = os.path.join(reports_dir, 'regression_test_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ JSON results saved to: {json_path}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"System Status: {results['system_status'].upper()}")
        print(f"Components Analyzed: {results['total_components']}")
        print(f"Passed: {results['passed_components']}")
        print(f"Failed: {results['failed_components']}")
        print(f"Success Rate: {(results['passed_components']/results['total_components']*100):.1f}%")
        
        return results['failed_components'] == 0
        
    except Exception as e:
        print(f"Error generating regression report: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)