#!/usr/bin/env python3
"""
Test script for the agent orchestration system
Validates coordination, dependency management, and parallel execution
"""

import sys
import os
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch

# Add orchestration module to path
sys.path.append(str(Path(__file__).parent))

def test_agent_pipeline():
    """Test the agent execution pipeline"""
    print("=== Testing Agent Pipeline ===")
    
    try:
        from orchestration.agent_pipeline import AgentExecutionPipeline, AgentStatus, AgentResult
        
        # Test pipeline initialization
        pipeline = AgentExecutionPipeline()
        assert pipeline.config is not None, "Pipeline config should be loaded"
        
        # Test configuration loading
        config = pipeline._get_default_config()
        assert 'execution_order' in config, "Config should have execution_order"
        assert 'agents' in config, "Config should have agents section"
        
        print("  ✅ Pipeline initialization: PASSED")
        
        # Test agent status tracking
        pipeline.shared_data['test'] = 'data'
        assert 'test' in pipeline.shared_data, "Shared data should be accessible"
        
        print("  ✅ Shared data management: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Pipeline test failed: {e}")
        return False

def test_agent_coordinator():
    """Test the agent coordination system"""
    print("\n=== Testing Agent Coordinator ===")
    
    try:
        from orchestration.agent_coordinator import AgentCoordinator, AgentStatus, DependencyStatus
        
        # Test coordinator initialization
        coordinator = AgentCoordinator(max_parallel_agents=2)
        assert coordinator.max_parallel_agents == 2, "Max parallel agents should be set"
        
        print("  ✅ Coordinator initialization: PASSED")
        
        # Test dependency registration
        dependencies = {
            'agent1': [],
            'agent2': ['agent1'],
            'agent3': ['agent1', 'agent2']
        }
        coordinator.register_agent_dependencies(dependencies)
        
        assert len(coordinator.agent_dependencies) == 3, "Should have 3 registered agents"
        assert 'agent1' in coordinator.agent_dependencies, "Agent1 should be registered"
        
        print("  ✅ Dependency registration: PASSED")
        
        # Test dependency checking
        assert coordinator.check_dependencies_satisfied('agent1'), "Agent1 should have no dependencies"
        assert not coordinator.check_dependencies_satisfied('agent2'), "Agent2 should depend on agent1"
        
        # Complete agent1 and check again
        coordinator.completed_agents.add('agent1')
        assert coordinator.check_dependencies_satisfied('agent2'), "Agent2 dependencies should be satisfied"
        
        print("  ✅ Dependency checking: PASSED")
        
        # Test ready agents detection
        ready_agents = coordinator.get_ready_agents()
        assert 'agent2' in ready_agents, "Agent2 should be ready"
        assert 'agent3' not in ready_agents, "Agent3 should not be ready yet"
        
        print("  ✅ Ready agents detection: PASSED")
        
        # Test parallel execution rules
        parallel_groups = {'group1': ['agent2', 'agent3']}
        coordinator.set_parallel_execution_rules(parallel_groups)
        
        agent2_dep = coordinator.agent_dependencies['agent2']
        assert agent2_dep.can_run_parallel, "Agent2 should be marked for parallel execution"
        
        print("  ✅ Parallel execution rules: PASSED")
        
        # Test status monitoring
        coordinator.update_agent_status('agent1', AgentStatus.RUNNING, progress_percentage=50.0)
        
        monitoring_data = coordinator.agent_monitoring['agent1']
        assert monitoring_data.status == AgentStatus.RUNNING, "Status should be updated"
        assert monitoring_data.progress_percentage == 50.0, "Progress should be updated"
        
        print("  ✅ Status monitoring: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Coordinator test failed: {e}")
        return False

def test_orchestration_manager():
    """Test the orchestration manager"""
    print("\n=== Testing Orchestration Manager ===")
    
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        
        # Test manager initialization
        manager = OrchestrationManager()
        assert manager.pipeline is not None, "Pipeline should be initialized"
        assert manager.coordinator is not None, "Coordinator should be initialized"
        
        print("  ✅ Manager initialization: PASSED")
        
        # Test configuration validation
        validation = manager.validate_configuration()
        assert 'valid' in validation, "Validation should return valid field"
        assert 'errors' in validation, "Validation should return errors field"
        assert 'warnings' in validation, "Validation should return warnings field"
        
        print("  ✅ Configuration validation: PASSED")
        
        # Test workflow status
        status = manager.get_workflow_status()
        assert 'execution_mode' in status, "Status should include execution mode"
        assert 'pipeline_status' in status, "Status should include pipeline status"
        
        print("  ✅ Workflow status: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Manager test failed: {e}")
        return False

def test_dependency_resolution():
    """Test complex dependency resolution scenarios"""
    print("\n=== Testing Dependency Resolution ===")
    
    try:
        from orchestration.agent_coordinator import AgentCoordinator
        
        coordinator = AgentCoordinator()
        
        # Test complex dependency chain
        dependencies = {
            'po_reader': [],
            'validation': ['po_reader'],
            'exception_response': ['validation'],
            'so_creator': ['validation'],
            'summary_insights': ['exception_response', 'so_creator']
        }
        
        coordinator.register_agent_dependencies(dependencies)
        
        # Test initial state
        ready = coordinator.get_ready_agents()
        assert ready == ['po_reader'], f"Only po_reader should be ready initially, got: {ready}"
        
        print("  ✅ Initial dependency state: PASSED")
        
        # Complete po_reader
        coordinator.completed_agents.add('po_reader')
        ready = coordinator.get_ready_agents()
        assert ready == ['validation'], f"Only validation should be ready after po_reader, got: {ready}"
        
        print("  ✅ Single dependency resolution: PASSED")
        
        # Complete validation
        coordinator.completed_agents.add('validation')
        ready = coordinator.get_ready_agents()
        expected = {'exception_response', 'so_creator'}
        ready_set = set(ready)
        assert ready_set == expected, f"Both exception_response and so_creator should be ready, got: {ready_set}"
        
        print("  ✅ Parallel dependency resolution: PASSED")
        
        # Complete both parallel agents
        coordinator.completed_agents.add('exception_response')
        coordinator.completed_agents.add('so_creator')
        ready = coordinator.get_ready_agents()
        assert ready == ['summary_insights'], f"Only summary_insights should be ready at end, got: {ready}"
        
        print("  ✅ Final dependency resolution: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dependency resolution test failed: {e}")
        return False

def test_parallel_execution_simulation():
    """Test parallel execution capabilities"""
    print("\n=== Testing Parallel Execution Simulation ===")
    
    try:
        from orchestration.agent_coordinator import AgentCoordinator, AgentStatus
        
        coordinator = AgentCoordinator(max_parallel_agents=2)
        
        # Setup agents that can run in parallel
        dependencies = {
            'agent1': [],
            'agent2': [],
            'agent3': ['agent1', 'agent2']
        }
        
        coordinator.register_agent_dependencies(dependencies)
        
        # Set parallel execution
        parallel_groups = {'parallel_group': ['agent1', 'agent2']}
        coordinator.set_parallel_execution_rules(parallel_groups)
        
        # Test parallel execution capability
        assert coordinator.can_run_parallel('agent1', set()), "Agent1 should be able to run in parallel"
        assert coordinator.can_run_parallel('agent2', {'agent1'}), "Agent2 should be able to run with agent1"
        
        print("  ✅ Parallel execution capability: PASSED")
        
        # Simulate concurrent execution
        coordinator.update_agent_status('agent1', AgentStatus.RUNNING)
        coordinator.update_agent_status('agent2', AgentStatus.RUNNING)
        
        assert len(coordinator.running_agents) == 2, "Should have 2 running agents"
        assert 'agent1' in coordinator.running_agents, "Agent1 should be running"
        assert 'agent2' in coordinator.running_agents, "Agent2 should be running"
        
        print("  ✅ Concurrent execution tracking: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Parallel execution test failed: {e}")
        return False

def test_error_handling():
    """Test error handling and recovery"""
    print("\n=== Testing Error Handling ===")
    
    try:
        from orchestration.agent_coordinator import AgentCoordinator, AgentStatus
        
        coordinator = AgentCoordinator()
        
        dependencies = {
            'agent1': [],
            'agent2': ['agent1']
        }
        coordinator.register_agent_dependencies(dependencies)
        
        # Test agent failure handling
        coordinator.update_agent_status('agent1', AgentStatus.FAILED)
        
        assert 'agent1' in coordinator.failed_agents, "Agent1 should be marked as failed"
        assert 'agent1' not in coordinator.running_agents, "Agent1 should not be running"
        assert 'agent1' not in coordinator.completed_agents, "Agent1 should not be completed"
        
        print("  ✅ Agent failure tracking: PASSED")
        
        # Test that dependent agents are not ready when dependency fails
        ready = coordinator.get_ready_agents()
        assert 'agent2' not in ready, "Agent2 should not be ready when agent1 failed"
        
        print("  ✅ Failure propagation prevention: PASSED")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Run all orchestration tests"""
    print("🧪 Agent Orchestration System Tests")
    print("=" * 50)
    
    tests = [
        test_agent_pipeline,
        test_agent_coordinator,
        test_orchestration_manager,
        test_dependency_resolution,
        test_parallel_execution_simulation,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Orchestration system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)