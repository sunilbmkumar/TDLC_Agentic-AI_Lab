#!/usr/bin/env python3
"""
Main orchestration script for PO to SO Agent Demo
Uses the new orchestration system with pipeline execution and coordination
"""

import sys
import os
from pathlib import Path

# Add orchestration module to path
sys.path.append(str(Path(__file__).parent))

def main():
    """Main orchestration function using the new orchestration system"""
    print("=== PO to SO Agent Demo - Advanced Orchestration ===")
    
    try:
        from orchestration.orchestration_manager import OrchestrationManager
        
        # Initialize orchestration manager
        manager = OrchestrationManager()
        
        # Validate configuration
        print("Validating orchestration configuration...")
        validation = manager.validate_configuration()
        
        if not validation['valid']:
            print("❌ Configuration validation failed:")
            for error in validation['errors']:
                print(f"  • {error}")
            return 1
        
        if validation['warnings']:
            print("⚠️ Configuration warnings:")
            for warning in validation['warnings']:
                print(f"  • {warning}")
        
        print("✅ Configuration validated successfully")
        
        # Execute the complete workflow
        print("\nStarting agent workflow execution...")
        results = manager.execute_workflow()
        
        # Display comprehensive summary
        manager.display_workflow_summary()
        
        # Check results
        completed_agents = sum(1 for result in results.values() 
                             if result.status.value == 'completed')
        failed_agents = sum(1 for result in results.values() 
                          if result.status.value == 'failed')
        
        print(f"\n🎉 Workflow execution completed!")
        print(f"   ✅ Completed: {completed_agents} agents")
        print(f"   ❌ Failed: {failed_agents} agents")
        print(f"   📊 Total: {len(results)} agents")
        
        if failed_agents > 0:
            print("\n❌ Failed agents:")
            for name, result in results.items():
                if result.status.value == 'failed':
                    print(f"   • {name}: {result.error_message}")
            return 1
        
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required modules are available")
        return 1
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_legacy_mode():
    """Fallback to legacy sequential execution"""
    print("=== Running in Legacy Mode ===")
    
    try:
        from orchestration.agent_pipeline import AgentExecutionPipeline
        
        # Use just the pipeline without coordination
        pipeline = AgentExecutionPipeline()
        results = pipeline.execute_pipeline()
        
        pipeline.save_pipeline_results()
        
        print("✅ Legacy mode execution completed")
        return 0
        
    except Exception as e:
        print(f"❌ Legacy mode failed: {e}")
        return 1


if __name__ == "__main__":
    # Try advanced orchestration first, fallback to legacy if needed
    exit_code = main()
    
    if exit_code != 0:
        print("\n🔄 Falling back to legacy mode...")
        exit_code = run_legacy_mode()
    
    sys.exit(exit_code)