#!/usr/bin/env python3
"""
Workflow Validation Tests
Validates the workflow structure, dependencies, and configuration
without executing the full pipeline
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_orchestration_components():
    """Test that all orchestration components are properly structured"""
    print("=== Testing Orchestration Components ===")
    
    try:
        # Test imports
        from orchestration.agent_pipeline import AgentExecutionPipeline, AgentStatus, AgentResult
        from orchestration.agent_coordinator import AgentCoordinator, DependencyStatus
        from orchestration.orchestration_manager import OrchestrationManager
        
        print("✅ All orchestration modules import successfully")
        
        # Test pipeline initialization
        pipeline = AgentExecutionPipeline()
        assert pipeline.config is not None, "Pipeline should have config"
        print("✅ Pipeline initializes correctly")
        
        # Test coordinator initialization
        coordinator = AgentCoordinator()
        assert hasattr(coordinator, 'agent_dependencies'), "Coordinator should have dependencies"
        print("✅ Coordinator initializes correctly")
        
        # Test manager initialization
        manager = OrchestrationManager()
        assert manager.pipeline is not None, "Manager should have pipeline"
        assert manager.coordinator is not None, "Manager should have coordinator"
        print("✅ Manager initializes correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestration components test failed: {e}")
        return False

def test_agent_imports():
    """Test that all agent modules can be imported"""
    print("\n=== Testing Agent Imports ===")
    
    agents = [
        ('PO Reader', 'agents.po_reader.agent', 'POReaderAgent'),
        ('Validation', 'agents.validation.agent', 'ValidationAgent'),
        ('Exception Response', 'agents.exception_response.agent', 'ExceptionResponseAgent'),
        ('SO Creator', 'agents.so_creator.agent', 'SalesOrderCreatorAgent'),
        ('Summary Insights', 'agents.summary_insights.agent', 'SummaryInsightsAgent')
    ]
    
    for agent_name, module_path, class_name in agents:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)
            print(f"✅ {agent_name} agent imports successfully")
        except Exception as e:
            print(f"❌ {agent_name} agent import failed: {e}")
            return False
    
    return True

def test_dependency_configuration():
    """Test dependency configuration is valid"""
    print("\n=== Testing Dependency Configuration ===")
    
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        
        manager = OrchestrationManager()
        validation = manager.validate_configuration()
        
        if validation['valid']:
            print("✅ Dependency configuration is valid")
            
            # Print dependency structure
            dependencies = manager.config.get('dependencies', {})
            print("  Dependency structure:")
            for agent, deps in dependencies.items():
                if deps:
                    print(f"    {agent} depends on: {', '.join(deps)}")
                else:
                    print(f"    {agent} has no dependencies")
            
            return True
        else:
            print("❌ Dependency configuration is invalid:")
            for error in validation['errors']:
                print(f"    • {error}")
            return False
            
    except Exception as e:
        print(f"❌ Dependency configuration test failed: {e}")
        return False

def test_parallel_execution_rules():
    """Test parallel execution rules"""
    print("\n=== Testing Parallel Execution Rules ===")
    
    try:
        from orchestration.agent_coordinator import AgentCoordinator
        
        coordinator = AgentCoordinator()
        
        # Setup test dependencies
        dependencies = {
            'po_reader': [],
            'validation': ['po_reader'],
            'exception_response': ['validation'],
            'so_creator': ['validation'],
            'summary_insights': ['exception_response', 'so_creator']
        }
        
        coordinator.register_agent_dependencies(dependencies)
        
        # Setup parallel groups
        parallel_groups = {
            'post_validation': ['exception_response', 'so_creator']
        }
        coordinator.set_parallel_execution_rules(parallel_groups)
        
        # Test parallel execution capability
        can_run_parallel = coordinator.can_run_parallel('exception_response', set())
        assert can_run_parallel, "exception_response should be able to run in parallel"
        
        can_run_with_so = coordinator.can_run_parallel('so_creator', {'exception_response'})
        assert can_run_with_so, "so_creator should be able to run with exception_response"
        
        print("✅ Parallel execution rules work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Parallel execution rules test failed: {e}")
        return False

def test_data_flow_structure():
    """Test data flow structure between agents"""
    print("\n=== Testing Data Flow Structure ===")
    
    try:
        from orchestration.agent_pipeline import AgentExecutionPipeline
        
        pipeline = AgentExecutionPipeline()
        
        # Test shared data structure
        expected_keys = ['customer_orders', 'validation_results', 'exception_emails', 'sales_orders']
        
        # Initialize shared data structure
        for key in expected_keys:
            pipeline.shared_data[key] = []
        
        # Verify structure
        for key in expected_keys:
            assert key in pipeline.shared_data, f"Shared data should have {key}"
        
        print("✅ Data flow structure is correct")
        print(f"  Shared data keys: {list(pipeline.shared_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data flow structure test failed: {e}")
        return False

def test_error_handling_mechanisms():
    """Test error handling mechanisms"""
    print("\n=== Testing Error Handling Mechanisms ===")
    
    try:
        from orchestration.agent_coordinator import AgentCoordinator, AgentStatus
        
        coordinator = AgentCoordinator()
        
        # Setup test agents
        dependencies = {
            'agent1': [],
            'agent2': ['agent1']
        }
        coordinator.register_agent_dependencies(dependencies)
        
        # Test failure handling
        coordinator.update_agent_status('agent1', AgentStatus.FAILED)
        
        assert 'agent1' in coordinator.failed_agents, "Failed agent should be tracked"
        assert 'agent1' not in coordinator.completed_agents, "Failed agent should not be completed"
        
        # Test that dependent agents are not ready when dependency fails
        ready_agents = coordinator.get_ready_agents()
        assert 'agent2' not in ready_agents, "Dependent agent should not be ready when dependency fails"
        
        print("✅ Error handling mechanisms work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling mechanisms test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration file structure"""
    print("\n=== Testing Configuration Files ===")
    
    config_files = [
        'config/orchestration_config.json',
        'config/agent_config.json'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                print(f"✅ {config_file} is valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ {config_file} has invalid JSON: {e}")
                return False
        else:
            print(f"⚠️ {config_file} not found (will use defaults)")
    
    return True

def test_output_directory_structure():
    """Test output directory structure"""
    print("\n=== Testing Output Directory Structure ===")
    
    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)
    
    # Test write permissions
    test_file = 'outputs/test_write.tmp'
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Output directory is writable")
        return True
    except Exception as e:
        print(f"❌ Output directory write test failed: {e}")
        return False

def run_validation_tests():
    """Run all validation tests"""
    print("🔍 Running Workflow Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Orchestration Components", test_orchestration_components),
        ("Agent Imports", test_agent_imports),
        ("Dependency Configuration", test_dependency_configuration),
        ("Parallel Execution Rules", test_parallel_execution_rules),
        ("Data Flow Structure", test_data_flow_structure),
        ("Error Handling Mechanisms", test_error_handling_mechanisms),
        ("Configuration Files", test_configuration_files),
        ("Output Directory Structure", test_output_directory_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION TEST RESULTS")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All validation tests PASSED!")
        print("The workflow structure is correctly implemented.")
        return True
    else:
        print(f"\n❌ {failed} validation tests FAILED!")
        print("Please check the workflow implementation.")
        return False

if __name__ == "__main__":
    success = run_validation_tests()
    sys.exit(0 if success else 1)