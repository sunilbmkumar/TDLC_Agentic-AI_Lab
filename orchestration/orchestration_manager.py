#!/usr/bin/env python3
"""
Orchestration Manager - Integrates pipeline execution with coordination system
Provides unified interface for agent workflow orchestration
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from .agent_pipeline import AgentExecutionPipeline, AgentStatus, AgentResult
from .agent_coordinator import AgentCoordinator


class OrchestrationManager:
    """
    Unified orchestration manager that combines pipeline execution with coordination
    Handles both sequential and parallel agent execution with dependency management
    """
    
    def __init__(self, config_path: str = "config/orchestration_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize pipeline and coordinator
        self.pipeline = AgentExecutionPipeline(config_path)
        self.coordinator = AgentCoordinator(
            max_parallel_agents=self.config.get('max_parallel_agents', 3)
        )
        
        # Setup coordination based on config
        self._setup_coordination()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load orchestration configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default orchestration configuration"""
        return {
            "execution_mode": "coordinated",  # "sequential" or "coordinated"
            "max_parallel_agents": 2,
            "enable_error_recovery": True,
            "enable_monitoring": True,
            "dependencies": {
                "po_reader": [],
                "validation": ["po_reader"],
                "exception_response": ["validation"],
                "so_creator": ["validation"],
                "summary_insights": ["exception_response", "so_creator"]
            },
            "parallel_groups": {
                "post_validation": ["exception_response", "so_creator"]
            },
            "agent_priorities": {
                "po_reader": 100,
                "validation": 90,
                "exception_response": 80,
                "so_creator": 80,
                "summary_insights": 70
            }
        }
    
    def _setup_coordination(self):
        """Setup agent coordination based on configuration"""
        # Register dependencies
        dependencies = self.config.get('dependencies', {})
        self.coordinator.register_agent_dependencies(dependencies)
        
        # Set parallel execution rules
        parallel_groups = self.config.get('parallel_groups', {})
        self.coordinator.set_parallel_execution_rules(parallel_groups)
        
        # Set agent priorities
        priorities = self.config.get('agent_priorities', {})
        for agent_name, priority in priorities.items():
            if agent_name in self.coordinator.agent_dependencies:
                self.coordinator.agent_dependencies[agent_name].priority = priority
    
    def execute_workflow(self) -> Dict[str, AgentResult]:
        """
        Execute the complete agent workflow using configured execution mode
        """
        execution_mode = self.config.get('execution_mode', 'sequential')
        
        print(f"=== STARTING ORCHESTRATED WORKFLOW ({execution_mode.upper()} MODE) ===")
        
        if execution_mode == 'coordinated':
            return self._execute_coordinated_workflow()
        else:
            return self._execute_sequential_workflow()
    
    def _execute_sequential_workflow(self) -> Dict[str, AgentResult]:
        """Execute workflow in sequential mode"""
        print("Executing in sequential mode...")
        results = self.pipeline.execute_pipeline()
        
        # Save results
        self.pipeline.save_pipeline_results()
        
        return results
    
    def _execute_coordinated_workflow(self) -> Dict[str, AgentResult]:
        """Execute workflow in coordinated mode with parallel execution"""
        print("Executing in coordinated mode with parallel execution...")
        
        # Setup monitoring callback if enabled
        if self.config.get('enable_monitoring', True):
            self.coordinator.add_status_callback(self._monitoring_callback)
        
        # Execute with coordination
        results = self.coordinator.execute_coordinated_pipeline(self.pipeline)
        
        # Save results
        self.pipeline.save_pipeline_results()
        self.coordinator.save_coordination_results()
        
        return results
    
    def _monitoring_callback(self, agent_name: str, status: AgentStatus, kwargs: Dict[str, Any]):
        """Callback for agent status monitoring"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if status == AgentStatus.RUNNING:
            operation = kwargs.get('current_operation', 'Running')
            print(f"[{timestamp}] 🔄 {agent_name}: {operation}")
        elif status == AgentStatus.COMPLETED:
            print(f"[{timestamp}] ✅ {agent_name}: Completed successfully")
        elif status == AgentStatus.FAILED:
            print(f"[{timestamp}] ❌ {agent_name}: Failed")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        return {
            'execution_mode': self.config.get('execution_mode'),
            'pipeline_status': self.pipeline.get_pipeline_status(),
            'coordination_status': self.coordinator.get_coordination_status(),
            'shared_data_summary': {
                'keys': list(self.pipeline.shared_data.keys()),
                'customer_orders': len(self.pipeline.shared_data.get('customer_orders', [])),
                'validation_results': len(self.pipeline.shared_data.get('validation_results', [])),
                'sales_orders': len(self.pipeline.shared_data.get('sales_orders', [])),
                'exception_emails': len(self.pipeline.shared_data.get('exception_emails', []))
            }
        }
    
    def create_config_file(self, output_path: str = "config/orchestration_config.json"):
        """Create configuration file with current settings"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"Configuration saved to: {output_path}")
        return output_path
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate orchestration configuration"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check dependencies
        dependencies = self.config.get('dependencies', {})
        all_agents = set(dependencies.keys())
        
        for agent, deps in dependencies.items():
            for dep in deps:
                if dep not in all_agents:
                    validation_results['errors'].append(
                        f"Agent '{agent}' depends on unknown agent '{dep}'"
                    )
                    validation_results['valid'] = False
        
        # Check for circular dependencies
        if self._has_circular_dependencies(dependencies):
            validation_results['errors'].append("Circular dependencies detected")
            validation_results['valid'] = False
        
        # Check parallel groups
        parallel_groups = self.config.get('parallel_groups', {})
        for group_name, agents in parallel_groups.items():
            for agent in agents:
                if agent not in all_agents:
                    validation_results['warnings'].append(
                        f"Parallel group '{group_name}' references unknown agent '{agent}'"
                    )
        
        return validation_results
    
    def _has_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> bool:
        """Check for circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(agent: str) -> bool:
            if agent in rec_stack:
                return True  # Circular dependency found
            if agent in visited:
                return False
            
            visited.add(agent)
            rec_stack.add(agent)
            
            for dep in dependencies.get(agent, []):
                if dfs(dep):
                    return True
            
            rec_stack.remove(agent)
            return False
        
        for agent in dependencies:
            if agent not in visited:
                if dfs(agent):
                    return True
        
        return False
    
    def display_workflow_summary(self):
        """Display comprehensive workflow summary"""
        print("\n=== ORCHESTRATION WORKFLOW SUMMARY ===")
        
        status = self.get_workflow_status()
        
        print(f"Execution Mode: {status['execution_mode']}")
        print(f"Configuration: {self.config_path}")
        
        # Display agent execution results
        pipeline_status = status.get('pipeline_status', {})
        execution_results = pipeline_status.get('execution_results', {})
        
        print(f"\nAgent Execution Results:")
        for agent_name, result in execution_results.items():
            status_icon = {
                'completed': "✅",
                'failed': "❌",
                'skipped': "⏭️",
                'running': "🔄"
            }.get(result.get('status'), "❓")
            
            execution_time = result.get('execution_time', 0)
            time_str = f" ({execution_time:.2f}s)" if execution_time else ""
            
            print(f"  {status_icon} {agent_name.upper()}: {result.get('status', 'unknown')}{time_str}")
        
        # Display data flow
        data_summary = status.get('shared_data_summary', {})
        print(f"\nData Flow Summary:")
        print(f"  📋 Customer Orders: {data_summary.get('customer_orders', 0)}")
        print(f"  ✅ Validation Results: {data_summary.get('validation_results', 0)}")
        print(f"  💰 Sales Orders: {data_summary.get('sales_orders', 0)}")
        print(f"  📧 Exception Emails: {data_summary.get('exception_emails', 0)}")
        
        print("=== END WORKFLOW SUMMARY ===")


def main():
    """Main entry point for orchestration manager"""
    # Create config directory if it doesn't exist
    os.makedirs('config', exist_ok=True)
    
    # Initialize orchestration manager
    manager = OrchestrationManager()
    
    # Validate configuration
    validation = manager.validate_configuration()
    if not validation['valid']:
        print("Configuration validation failed:")
        for error in validation['errors']:
            print(f"  ❌ {error}")
        return
    
    if validation['warnings']:
        print("Configuration warnings:")
        for warning in validation['warnings']:
            print(f"  ⚠️ {warning}")
    
    # Create config file for reference
    manager.create_config_file()
    
    # Execute workflow
    try:
        results = manager.execute_workflow()
        
        # Display summary
        manager.display_workflow_summary()
        
        print(f"\n🎉 Workflow completed successfully!")
        print(f"Results: {len(results)} agents executed")
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        raise


if __name__ == "__main__":
    main()