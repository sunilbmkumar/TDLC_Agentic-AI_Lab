#!/usr/bin/env python3
"""
Agent Coordination System - Manages agent dependencies, monitoring, and parallel execution
Handles agent status monitoring, dependency management, and execution coordination
"""

import asyncio
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import queue

from .agent_pipeline import AgentStatus, AgentResult

class DependencyStatus(Enum):
    """Agent dependency status"""
    PENDING = "pending"
    SATISFIED = "satisfied"
    FAILED = "failed"

@dataclass
class AgentDependency:
    """Agent dependency definition"""
    agent_name: str
    depends_on: List[str] = field(default_factory=list)
    status: DependencyStatus = DependencyStatus.PENDING
    can_run_parallel: bool = False
    priority: int = 0  # Higher number = higher priority

@dataclass
class AgentMonitoringData:
    """Agent monitoring and status data"""
    agent_name: str
    status: AgentStatus
    start_time: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_operation: str = ""
    resource_usage: Dict[str, Any] = field(default_factory=dict)

class AgentCoordinator:
    """
    Agent coordination system with dependency management and parallel execution
    Manages agent execution order, dependencies, and monitoring
    """
    
    def __init__(self, max_parallel_agents: int = 3):
        self.max_parallel_agents = max_parallel_agents
        self.agent_dependencies: Dict[str, AgentDependency] = {}
        self.agent_monitoring: Dict[str, AgentMonitoringData] = {}
        self.execution_queue = queue.PriorityQueue()
        self.completed_agents: Set[str] = set()
        self.failed_agents: Set[str] = set()
        self.running_agents: Set[str] = set()
        self.agent_results: Dict[str, AgentResult] = {}
        self.shared_data: Dict[str, Any] = {}
        self.status_callbacks: List[Callable] = []
        self.coordination_lock = threading.Lock()
        
    def register_agent_dependencies(self, dependencies: Dict[str, List[str]]):
        """
        Register agent dependencies
        Format: {'agent_name': ['dependency1', 'dependency2']}
        """
        for agent_name, deps in dependencies.items():
            self.agent_dependencies[agent_name] = AgentDependency(
                agent_name=agent_name,
                depends_on=deps
            )
            
            # Initialize monitoring data
            self.agent_monitoring[agent_name] = AgentMonitoringData(
                agent_name=agent_name,
                status=AgentStatus.NOT_STARTED
            )
    
    def set_parallel_execution_rules(self, parallel_groups: Dict[str, List[str]]):
        """
        Set which agents can run in parallel
        Format: {'group_name': ['agent1', 'agent2']}
        """
        for group_name, agents in parallel_groups.items():
            for agent in agents:
                if agent in self.agent_dependencies:
                    self.agent_dependencies[agent].can_run_parallel = True
    
    def check_dependencies_satisfied(self, agent_name: str) -> bool:
        """Check if all dependencies for an agent are satisfied"""
        if agent_name not in self.agent_dependencies:
            return True
        
        dependency = self.agent_dependencies[agent_name]
        
        for dep_agent in dependency.depends_on:
            if dep_agent not in self.completed_agents:
                return False
        
        return True
    
    def get_ready_agents(self) -> List[str]:
        """Get list of agents ready to execute (dependencies satisfied)"""
        ready_agents = []
        
        for agent_name, dependency in self.agent_dependencies.items():
            if (agent_name not in self.completed_agents and 
                agent_name not in self.failed_agents and
                agent_name not in self.running_agents and
                self.check_dependencies_satisfied(agent_name)):
                ready_agents.append(agent_name)
        
        # Sort by priority (higher priority first)
        ready_agents.sort(key=lambda x: self.agent_dependencies[x].priority, reverse=True)
        
        return ready_agents
    
    def can_run_parallel(self, agent_name: str, currently_running: Set[str]) -> bool:
        """Check if agent can run in parallel with currently running agents"""
        if agent_name not in self.agent_dependencies:
            return True
        
        agent_dep = self.agent_dependencies[agent_name]
        
        if not agent_dep.can_run_parallel:
            return len(currently_running) == 0
        
        # Check if any currently running agents conflict
        for running_agent in currently_running:
            if running_agent in self.agent_dependencies:
                running_dep = self.agent_dependencies[running_agent]
                if not running_dep.can_run_parallel:
                    return False
        
        return True
    
    def update_agent_status(self, agent_name: str, status: AgentStatus, **kwargs):
        """Update agent status and monitoring data"""
        with self.coordination_lock:
            if agent_name in self.agent_monitoring:
                monitoring_data = self.agent_monitoring[agent_name]
                monitoring_data.status = status
                monitoring_data.last_heartbeat = datetime.now()
                
                # Update specific fields if provided
                if 'progress_percentage' in kwargs:
                    monitoring_data.progress_percentage = kwargs['progress_percentage']
                if 'current_operation' in kwargs:
                    monitoring_data.current_operation = kwargs['current_operation']
                if 'resource_usage' in kwargs:
                    monitoring_data.resource_usage = kwargs['resource_usage']
                
                # Update agent sets based on status
                if status == AgentStatus.RUNNING:
                    self.running_agents.add(agent_name)
                    if monitoring_data.start_time is None:
                        monitoring_data.start_time = datetime.now()
                elif status == AgentStatus.COMPLETED:
                    self.running_agents.discard(agent_name)
                    self.completed_agents.add(agent_name)
                elif status == AgentStatus.FAILED:
                    self.running_agents.discard(agent_name)
                    self.failed_agents.add(agent_name)
        
        # Notify status callbacks
        for callback in self.status_callbacks:
            try:
                callback(agent_name, status, kwargs)
            except Exception as e:
                print(f"Error in status callback: {e}")
    
    def execute_agent_with_coordination(self, agent_name: str, pipeline_executor) -> AgentResult:
        """Execute agent with coordination and monitoring"""
        try:
            # Update status to running
            self.update_agent_status(agent_name, AgentStatus.RUNNING, 
                                   current_operation="Starting execution")
            
            # Execute the agent using the pipeline executor
            result = pipeline_executor._execute_agent(agent_name)
            
            # Store result and update status
            self.agent_results[agent_name] = result
            
            if result.status == AgentStatus.COMPLETED:
                self.update_agent_status(agent_name, AgentStatus.COMPLETED,
                                       progress_percentage=100.0,
                                       current_operation="Completed successfully")
            else:
                self.update_agent_status(agent_name, AgentStatus.FAILED,
                                       current_operation=f"Failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            error_msg = f"Coordination error for {agent_name}: {str(e)}"
            result = AgentResult(
                agent_name=agent_name,
                status=AgentStatus.FAILED,
                error_message=error_msg
            )
            
            self.agent_results[agent_name] = result
            self.update_agent_status(agent_name, AgentStatus.FAILED,
                                   current_operation=f"Failed: {error_msg}")
            
            return result
    
    def execute_coordinated_pipeline(self, pipeline_executor) -> Dict[str, AgentResult]:
        """
        Execute pipeline with coordination, dependency management, and parallel execution
        """
        print("=== STARTING COORDINATED AGENT EXECUTION ===")
        
        # Setup default dependencies if not configured
        if not self.agent_dependencies:
            self._setup_default_dependencies()
        
        start_time = datetime.now()
        
        with ThreadPoolExecutor(max_workers=self.max_parallel_agents) as executor:
            future_to_agent = {}
            
            while (len(self.completed_agents) + len(self.failed_agents) < 
                   len(self.agent_dependencies)):
                
                # Get agents ready to execute
                ready_agents = self.get_ready_agents()
                
                # Submit agents for parallel execution if possible
                for agent_name in ready_agents:
                    if (len(future_to_agent) < self.max_parallel_agents and
                        self.can_run_parallel(agent_name, self.running_agents)):
                        
                        print(f"Submitting agent for execution: {agent_name}")
                        future = executor.submit(
                            self.execute_agent_with_coordination,
                            agent_name,
                            pipeline_executor
                        )
                        future_to_agent[future] = agent_name
                
                # Wait for at least one agent to complete
                if future_to_agent:
                    completed_futures = as_completed(future_to_agent, timeout=1.0)
                    
                    for future in completed_futures:
                        agent_name = future_to_agent[future]
                        try:
                            result = future.result()
                            print(f"Agent {agent_name} completed with status: {result.status.value}")
                        except Exception as e:
                            print(f"Agent {agent_name} failed with exception: {e}")
                        
                        # Remove completed future
                        del future_to_agent[future]
                        break  # Process one completion at a time
                else:
                    # No agents ready or running, wait a bit
                    time.sleep(0.1)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"\n=== COORDINATED EXECUTION COMPLETED in {execution_time:.2f}s ===")
        self._display_coordination_summary()
        
        return self.agent_results
    
    def _setup_default_dependencies(self):
        """Setup default agent dependencies for PO-to-SO workflow"""
        dependencies = {
            'po_reader': [],  # No dependencies
            'validation': ['po_reader'],  # Depends on PO reader
            'exception_response': ['validation'],  # Depends on validation
            'so_creator': ['validation'],  # Depends on validation (parallel with exception)
            'summary_insights': ['exception_response', 'so_creator']  # Depends on both
        }
        
        self.register_agent_dependencies(dependencies)
        
        # Set parallel execution rules
        parallel_groups = {
            'validation_processing': ['exception_response', 'so_creator']
        }
        self.set_parallel_execution_rules(parallel_groups)
    
    def _display_coordination_summary(self):
        """Display coordination execution summary"""
        print("\n=== COORDINATION SUMMARY ===")
        
        print(f"Completed Agents: {len(self.completed_agents)}")
        print(f"Failed Agents: {len(self.failed_agents)}")
        print(f"Total Agents: {len(self.agent_dependencies)}")
        
        print("\nAgent Execution Timeline:")
        for agent_name, monitoring_data in self.agent_monitoring.items():
            status_icon = {
                AgentStatus.COMPLETED: "✅",
                AgentStatus.FAILED: "❌",
                AgentStatus.RUNNING: "🔄",
                AgentStatus.NOT_STARTED: "⏸️"
            }.get(monitoring_data.status, "❓")
            
            execution_time = ""
            if (monitoring_data.start_time and 
                agent_name in self.agent_results and 
                self.agent_results[agent_name].execution_time):
                execution_time = f" ({self.agent_results[agent_name].execution_time:.2f}s)"
            
            print(f"  {status_icon} {agent_name}: {monitoring_data.status.value}{execution_time}")
        
        print("\nDependency Resolution:")
        for agent_name, dependency in self.agent_dependencies.items():
            if dependency.depends_on:
                deps_str = ", ".join(dependency.depends_on)
                print(f"  {agent_name} ← {deps_str}")
        
        print("=== END COORDINATION SUMMARY ===")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status"""
        return {
            'completed_agents': list(self.completed_agents),
            'failed_agents': list(self.failed_agents),
            'running_agents': list(self.running_agents),
            'agent_monitoring': {
                name: {
                    'status': data.status.value,
                    'progress_percentage': data.progress_percentage,
                    'current_operation': data.current_operation,
                    'start_time': data.start_time.isoformat() if data.start_time else None,
                    'last_heartbeat': data.last_heartbeat.isoformat() if data.last_heartbeat else None
                }
                for name, data in self.agent_monitoring.items()
            },
            'dependencies': {
                name: {
                    'depends_on': dep.depends_on,
                    'can_run_parallel': dep.can_run_parallel,
                    'priority': dep.priority
                }
                for name, dep in self.agent_dependencies.items()
            }
        }
    
    def add_status_callback(self, callback: Callable):
        """Add callback function for status updates"""
        self.status_callbacks.append(callback)
    
    def save_coordination_results(self, output_file: str = "outputs/coordination_results.json"):
        """Save coordination results to JSON file"""
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        coordination_data = {
            'coordination_status': self.get_coordination_status(),
            'execution_results': {
                name: {
                    'agent_name': result.agent_name,
                    'status': result.status.value,
                    'execution_time': result.execution_time,
                    'error_message': result.error_message,
                    'output_files': result.output_files
                }
                for name, result in self.agent_results.items()
            },
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coordination_data, f, indent=2)
        
        print(f"Coordination results saved to: {output_file}")
        return output_file