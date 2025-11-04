#!/usr/bin/env python3
"""
Agent Execution Pipeline - Sequential agent execution with data passing
Implements the core orchestration logic for PO to SO processing
"""

import json
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class AgentStatus(Enum):
    """Agent execution status enumeration"""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class AgentResult:
    """Data structure for agent execution results"""
    agent_name: str
    status: AgentStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    output_files: Optional[List[str]] = None

class AgentExecutionPipeline:
    """
    Sequential agent execution pipeline with inter-agent data passing
    Handles: PO Reader → Validation → Exception → SO Creator → Summary
    """
    
    def __init__(self, config_path: str = "config/agent_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.execution_results: Dict[str, AgentResult] = {}
        self.shared_data: Dict[str, Any] = {}
        self.pipeline_start_time: Optional[datetime] = None
        self.pipeline_end_time: Optional[datetime] = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found, using default config")
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for agent pipeline"""
        return {
            "execution_order": ["po_reader", "validation", "exception_response", "so_creator", "po_acknowledgment", "summary_insights"],
            "agents": {
                "po_reader": {
                    "enabled": True,
                    "timeout": 30,
                    "retry_count": 2
                },
                "validation": {
                    "enabled": True,
                    "timeout": 60,
                    "retry_count": 2
                },
                "exception_response": {
                    "enabled": True,
                    "timeout": 45,
                    "retry_count": 1
                },
                "so_creator": {
                    "enabled": True,
                    "timeout": 30,
                    "retry_count": 2
                },
                "po_acknowledgment": {
                    "enabled": True,
                    "timeout": 30,
                    "retry_count": 2
                },
                "summary_insights": {
                    "enabled": True,
                    "timeout": 30,
                    "retry_count": 1
                }
            }
        }
    
    def execute_pipeline(self) -> Dict[str, AgentResult]:
        """
        Execute the complete agent pipeline in sequence
        Returns execution results for all agents
        """
        print("=== STARTING AGENT EXECUTION PIPELINE ===")
        self.pipeline_start_time = datetime.now()
        
        # Ensure output directory exists
        os.makedirs('outputs', exist_ok=True)
        
        # Execute agents in configured order
        execution_order = self.config.get('execution_order', [])
        
        for agent_name in execution_order:
            if not self._is_agent_enabled(agent_name):
                print(f"Skipping disabled agent: {agent_name}")
                self._record_agent_result(agent_name, AgentStatus.SKIPPED)
                continue
            
            print(f"\n--- Executing Agent: {agent_name.upper()} ---")
            
            try:
                result = self._execute_agent(agent_name)
                self.execution_results[agent_name] = result
                
                if result.status == AgentStatus.FAILED:
                    print(f"Agent {agent_name} failed: {result.error_message}")
                    if self._should_stop_on_failure(agent_name):
                        print("Stopping pipeline due to critical agent failure")
                        break
                else:
                    print(f"Agent {agent_name} completed successfully")
                    
            except Exception as e:
                error_msg = f"Unexpected error executing {agent_name}: {str(e)}"
                print(f"✗ {error_msg}")
                self._record_agent_result(agent_name, AgentStatus.FAILED, error_message=error_msg)
                
                if self._should_stop_on_failure(agent_name):
                    print("Stopping pipeline due to critical agent failure")
                    break
        
        self.pipeline_end_time = datetime.now()
        
        # Generate pipeline summary
        self._display_pipeline_summary()
        
        return self.execution_results
    
    def _execute_agent(self, agent_name: str) -> AgentResult:
        """Execute a single agent with error handling and data passing"""
        start_time = datetime.now()
        
        try:
            if agent_name == "po_reader":
                result = self._execute_po_reader()
            elif agent_name == "validation":
                result = self._execute_validation()
            elif agent_name == "exception_response":
                result = self._execute_exception_response()
            elif agent_name == "so_creator":
                result = self._execute_so_creator()
            elif agent_name == "po_acknowledgment":
                result = self._execute_po_acknowledgment()
            elif agent_name == "summary_insights":
                result = self._execute_summary_insights()
            else:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            result.start_time = start_time
            result.end_time = end_time
            result.execution_time = execution_time
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                start_time=start_time,
                end_time=end_time,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _execute_po_reader(self) -> AgentResult:
        """Execute PO Reader Agent"""
        from agents.po_reader.agent import POReaderAgent
        
        po_agent = POReaderAgent()
        orders = po_agent.read_orders()
        
        if not orders:
            return AgentResult(
                agent_name="po_reader",
                status=AgentStatus.FAILED,
                error_message="No orders loaded from data source"
            )
        
        # Store data for next agent
        self.shared_data['customer_orders'] = orders
        self.shared_data['po_reader_stats'] = po_agent.get_summary_stats()
        
        # Display results
        po_agent.display_orders_table()
        po_agent.display_reasoning_output()
        
        return AgentResult(
            agent_name="po_reader",
            status=AgentStatus.COMPLETED,
            data={
                'orders_count': len(orders),
                'total_value': sum(order.get('Total_Value', 0) for order in orders),
                'customers': len(set(order['Customer_Name'] for order in orders))
            }
        )
    
    def _execute_validation(self) -> AgentResult:
        """Execute Validation Agent"""
        from agents.validation.agent import ValidationAgent
        
        validation_agent = ValidationAgent()
        validation_results = validation_agent.validate_orders()
        
        if not validation_results:
            return AgentResult(
                agent_name="validation",
                status=AgentStatus.FAILED,
                error_message="No validation results generated"
            )
        
        # Store data for next agents
        self.shared_data['validation_results'] = validation_results
        self.shared_data['validation_summary'] = validation_agent.get_validation_summary()
        
        # Display results
        validation_agent.display_validation_reasoning()
        
        return AgentResult(
            agent_name="validation",
            status=AgentStatus.COMPLETED,
            data={
                'total_orders': len(validation_results),
                'valid_orders': len([r for r in validation_results if r['Status'] == 'Valid']),
                'exceptions': len([r for r in validation_results if r['Status'] == 'Exception'])
            },
            output_files=['outputs/validation_results_simple.json', 'outputs/validation_results_detailed.json']
        )
    
    def _execute_exception_response(self) -> AgentResult:
        """Execute Exception Response Agent"""
        try:
            print("Importing ExceptionResponseAgent...")
            from agents.exception_response.agent import ExceptionResponseAgent
            
            print("Creating ExceptionResponseAgent instance...")
            exception_agent = ExceptionResponseAgent()
            
            print("Checking for exceptions to process...")
            # Check if there are exceptions to process
            validation_results = self.shared_data.get('validation_results', [])
            exceptions = [r for r in validation_results if r.get('Status') == 'Exception']
            
            print(f"Found {len(exceptions)} exceptions in {len(validation_results)} validation results")
            
            if not exceptions:
                print("No exceptions found - skipping exception response generation")
                return AgentResult(
                    agent_name="exception_response",
                    status=AgentStatus.COMPLETED,
                    data={'exceptions_processed': 0, 'emails_generated': 0}
                )
                
        except Exception as e:
            print(f"Error in exception response setup: {e}")
            import traceback
            traceback.print_exc()
            return AgentResult(
                agent_name="exception_response",
                status=AgentStatus.FAILED,
                error_message=f"Setup error: {str(e)}"
            )
        
        # Process exceptions
        try:
            emails = exception_agent.process_exceptions()
            if emails is None:
                emails = []
            
            # Store data for summary agent
            self.shared_data['exception_emails'] = emails
            self.shared_data['exception_summary'] = exception_agent.get_exception_summary()
            
            # Display results and send emails
            try:
                exception_agent.display_kiro_ui_format()
                exception_agent.send_exception_emails()
            except Exception as e:
                print(f"Warning: Exception display/email error: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"Error in exception processing: {e}")
            import traceback
            traceback.print_exc()
            emails = []
            self.shared_data['exception_emails'] = []
            self.shared_data['exception_summary'] = {'total_exceptions': 0}
        
        return AgentResult(
            agent_name="exception_response",
            status=AgentStatus.COMPLETED,
            data={
                'exceptions_processed': len(exceptions),
                'emails_generated': len(emails)
            },
            output_files=['outputs/exception_emails.json']
        )
    
    def _execute_so_creator(self) -> AgentResult:
        """Execute Sales Order Creator Agent"""
        try:
            from agents.so_creator.agent import SalesOrderCreatorAgent
            
            so_agent = SalesOrderCreatorAgent()
            result = so_agent.create_sales_orders()
            
            print(f"SO Creator result: {result}")  # Debug output
            
            if not result.get('success', False):
                return AgentResult(
                    agent_name="so_creator",
                    status=AgentStatus.FAILED,
                    error_message=result.get('message', 'Sales order creation failed')
                )
        except Exception as e:
            print(f"SO Creator exception: {e}")
            return AgentResult(
                agent_name="so_creator",
                status=AgentStatus.FAILED,
                error_message=f"SO Creator exception: {str(e)}"
            )
        
        # Store data for summary agent
        self.shared_data['sales_orders'] = result.get('sales_orders', [])
        self.shared_data['so_creator_summary'] = {
            'total_sales_value': result.get('total_sales_value', 0),
            'order_count': result.get('order_count', 0),
            'customer_totals': result.get('customer_totals', {})
        }
        
        return AgentResult(
            agent_name="so_creator",
            status=AgentStatus.COMPLETED,
            data={
                'sales_orders_created': result.get('order_count', 0),
                'total_sales_value': result.get('total_sales_value', 0)
            },
            output_files=[result.get('csv_file')] + result.get('chart_files', [])
        )
    
    def _execute_po_acknowledgment(self) -> AgentResult:
        """Execute PO Acknowledgment Agent"""
        from agents.po_acknowledgment.agent import POAcknowledgmentAgent
        
        po_ack_agent = POAcknowledgmentAgent()
        
        # Create PO acknowledgments
        result = po_ack_agent.create_po_acknowledgments()
        
        if not result.get('success', False):
            return AgentResult(
                agent_name="po_acknowledgment",
                status=AgentStatus.FAILED,
                error_message=result.get('message', 'PO acknowledgment creation failed')
            )
        
        # Store acknowledgment data for other agents
        self.shared_data['po_acknowledgments'] = result.get('acknowledgments', [])
        self.shared_data['po_acknowledgment_summary'] = result.get('summary', {})
        
        return AgentResult(
            agent_name="po_acknowledgment",
            status=AgentStatus.COMPLETED,
            data={
                'acknowledgments_created': len(result.get('acknowledgments', [])),
                'acceptance_rate': result.get('summary', {}).get('acceptance_rate', 0),
                'total_order_value': result.get('summary', {}).get('total_order_value', 0)
            },
            output_files=list(result.get('files_created', {}).values())
        )
    
    def _execute_summary_insights(self) -> AgentResult:
        """Execute Summary & Insights Agent"""
        from agents.summary_insights.agent import SummaryInsightsAgent
        
        summary_agent = SummaryInsightsAgent()
        
        # Generate comprehensive summary
        summary_data = summary_agent.generate_comprehensive_summary()
        
        # Store final results
        self.shared_data['final_summary'] = summary_data
        
        # Display results
        summary_agent.display_console_report()
        
        # Save executive report
        report_file = summary_agent.save_executive_report()
        dashboard_file = summary_agent.save_dashboard_data()
        
        return AgentResult(
            agent_name="summary_insights",
            status=AgentStatus.COMPLETED,
            data=summary_data,
            output_files=[report_file, dashboard_file]
        )
    
    def _is_agent_enabled(self, agent_name: str) -> bool:
        """Check if agent is enabled in configuration"""
        return self.config.get('agents', {}).get(agent_name, {}).get('enabled', True)
    
    def _should_stop_on_failure(self, agent_name: str) -> bool:
        """Determine if pipeline should stop on agent failure"""
        # Critical agents that should stop the pipeline
        critical_agents = ['po_reader', 'validation']
        return agent_name in critical_agents
    
    def _record_agent_result(self, agent_name: str, status: AgentStatus, **kwargs):
        """Record agent execution result"""
        self.execution_results[agent_name] = AgentResult(
            agent_name=agent_name,
            status=status,
            **kwargs
        )
    
    def _display_pipeline_summary(self):
        """Display pipeline execution summary"""
        print("\n=== PIPELINE EXECUTION SUMMARY ===")
        
        if self.pipeline_start_time and self.pipeline_end_time:
            total_time = (self.pipeline_end_time - self.pipeline_start_time).total_seconds()
            print(f"Total Pipeline Execution Time: {total_time:.2f} seconds")
        
        print("\nAgent Execution Results:")
        for agent_name, result in self.execution_results.items():
            status_icon = {
                AgentStatus.COMPLETED: "✅",
                AgentStatus.FAILED: "❌",
                AgentStatus.SKIPPED: "⏭️",
                AgentStatus.RUNNING: "🔄"
            }.get(result.status, "❓")
            
            execution_time = f" ({result.execution_time:.2f}s)" if result.execution_time else ""
            print(f"  {status_icon} {agent_name.upper()}: {result.status.value}{execution_time}")
            
            if result.error_message:
                print(f"    Error: {result.error_message}")
        
        # Display data flow summary
        print(f"\nData Flow Summary:")
        if 'customer_orders' in self.shared_data:
            orders_count = len(self.shared_data['customer_orders'])
            print(f"  📋 Customer Orders: {orders_count}")
        
        if 'validation_results' in self.shared_data:
            validation_summary = self.shared_data.get('validation_summary', {})
            valid_orders = validation_summary.get('valid_orders', 0)
            exceptions = validation_summary.get('exception_orders', 0)
            print(f"  ✅ Valid Orders: {valid_orders}")
            print(f"  ⚠️ Exceptions: {exceptions}")
        
        if 'sales_orders' in self.shared_data:
            so_count = len(self.shared_data['sales_orders'])
            so_summary = self.shared_data.get('so_creator_summary', {})
            total_value = so_summary.get('total_sales_value', 0)
            print(f"  💰 Sales Orders: {so_count} (${total_value:,.2f})")
        
        print("=== END PIPELINE SUMMARY ===")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline execution status"""
        return {
            'pipeline_start_time': self.pipeline_start_time.isoformat() if self.pipeline_start_time else None,
            'pipeline_end_time': self.pipeline_end_time.isoformat() if self.pipeline_end_time else None,
            'execution_results': {name: asdict(result) for name, result in self.execution_results.items()},
            'shared_data_keys': list(self.shared_data.keys())
        }
    
    def save_pipeline_results(self, output_file: str = "outputs/pipeline_execution_results.json"):
        """Save pipeline execution results to JSON file"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        pipeline_results = {
            'pipeline_execution': self.get_pipeline_status(),
            'shared_data_summary': {
                'customer_orders_count': len(self.shared_data.get('customer_orders', [])),
                'validation_results_count': len(self.shared_data.get('validation_results', [])),
                'sales_orders_count': len(self.shared_data.get('sales_orders', [])),
                'exception_emails_count': len(self.shared_data.get('exception_emails', []))
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pipeline_results, f, indent=2, default=str)
        
        print(f"Pipeline results saved to: {output_file}")
        return output_file