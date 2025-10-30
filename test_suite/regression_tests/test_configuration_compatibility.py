#!/usr/bin/env python3
"""
Configuration Compatibility Tests - Test backward compatibility of configuration formats
Tests configuration format compatibility, migration procedures, and version handling
"""

import unittest
import os
import sys
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from orchestration.orchestration_manager import OrchestrationManager
from orchestration.agent_pipeline import AgentExecutionPipeline


class ConfigurationFormatCompatibilityTest(unittest.TestCase):
    """Test backward compatibility of orchestration configuration formats"""
    
    def setUp(self):
        """Setup test environment with temporary directories"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test config directory
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_v1_orchestration_config_compatibility(self):
        """Test compatibility with version 1 orchestration configuration format"""
        # V1 format - minimal configuration
        v1_config = {
            "execution_mode": "sequential",
            "agents": {
                "po_reader": {"enabled": True},
                "validation": {"enabled": True},
                "so_creator": {"enabled": True}
            }
        }
        
        config_path = os.path.join(self.config_dir, 'orchestration_config.json')
        with open(config_path, 'w') as f:
            json.dump(v1_config, f, indent=2)
        
        # Test that OrchestrationManager can load V1 config
        manager = OrchestrationManager(config_path=config_path)
        
        # Verify default values are applied for missing fields
        self.assertEqual(manager.config['execution_mode'], 'sequential')
        self.assertIn('max_parallel_agents', manager.config)
        self.assertIn('dependencies', manager.config)
        
        # Test configuration validation
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'], "V1 config should be valid with defaults")
    
    def test_v2_orchestration_config_compatibility(self):
        """Test compatibility with version 2 orchestration configuration format"""
        # V2 format - added dependencies and parallel execution
        v2_config = {
            "execution_mode": "coordinated",
            "max_parallel_agents": 2,
            "dependencies": {
                "po_reader": [],
                "validation": ["po_reader"],
                "so_creator": ["validation"]
            },
            "agents": {
                "po_reader": {"enabled": True, "timeout": 30},
                "validation": {"enabled": True, "timeout": 60},
                "so_creator": {"enabled": True, "timeout": 30}
            }
        }
        
        config_path = os.path.join(self.config_dir, 'orchestration_config.json')
        with open(config_path, 'w') as f:
            json.dump(v2_config, f, indent=2)
        
        # Test that OrchestrationManager can load V2 config
        manager = OrchestrationManager(config_path=config_path)
        
        # Verify V2 features are properly loaded
        self.assertEqual(manager.config['execution_mode'], 'coordinated')
        self.assertEqual(manager.config['max_parallel_agents'], 2)
        self.assertIn('dependencies', manager.config)
        
        # Test configuration validation
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'], "V2 config should be valid")
    
    def test_current_orchestration_config_compatibility(self):
        """Test compatibility with current orchestration configuration format"""
        # Current format - full feature set
        current_config = {
            "execution_mode": "coordinated",
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
            },
            "agents": {
                "po_reader": {"enabled": True, "timeout": 30, "retry_count": 2},
                "validation": {"enabled": True, "timeout": 60, "retry_count": 2},
                "exception_response": {"enabled": True, "timeout": 45, "retry_count": 1},
                "so_creator": {"enabled": True, "timeout": 30, "retry_count": 2},
                "summary_insights": {"enabled": True, "timeout": 30, "retry_count": 1}
            }
        }
        
        config_path = os.path.join(self.config_dir, 'orchestration_config.json')
        with open(config_path, 'w') as f:
            json.dump(current_config, f, indent=2)
        
        # Test that OrchestrationManager can load current config
        manager = OrchestrationManager(config_path=config_path)
        
        # Verify all current features are properly loaded
        self.assertEqual(manager.config['execution_mode'], 'coordinated')
        self.assertEqual(manager.config['max_parallel_agents'], 2)
        self.assertTrue(manager.config['enable_error_recovery'])
        self.assertTrue(manager.config['enable_monitoring'])
        self.assertIn('parallel_groups', manager.config)
        self.assertIn('agent_priorities', manager.config)
        
        # Test configuration validation
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'], "Current config should be valid")
    
    def test_agent_config_format_compatibility(self):
        """Test backward compatibility of agent configuration formats"""
        # V1 agent config format - basic structure
        v1_agent_config = {
            "agents": {
                "po_reader": {
                    "name": "PO Reader Agent",
                    "description": "Reads customer orders"
                },
                "validation": {
                    "name": "Validation Agent",
                    "description": "Validates orders"
                }
            },
            "execution_order": ["po_reader", "validation"]
        }
        
        config_path = os.path.join(self.config_dir, 'agent_config.json')
        with open(config_path, 'w') as f:
            json.dump(v1_agent_config, f, indent=2)
        
        # Test that AgentExecutionPipeline can load V1 agent config
        pipeline = AgentExecutionPipeline(config_path=config_path)
        
        # Verify basic structure is maintained
        self.assertIn('agents', pipeline.config)
        self.assertIn('execution_order', pipeline.config)
        self.assertEqual(len(pipeline.config['execution_order']), 2)
    
    def test_deprecated_configuration_options_handling(self):
        """Test handling of deprecated configuration options"""
        # Config with deprecated options
        deprecated_config = {
            "execution_mode": "sequential",
            "legacy_timeout": 120,  # Deprecated option
            "old_retry_logic": True,  # Deprecated option
            "agents": {
                "po_reader": {
                    "enabled": True,
                    "legacy_setting": "old_value"  # Deprecated agent setting
                }
            }
        }
        
        config_path = os.path.join(self.config_dir, 'orchestration_config.json')
        with open(config_path, 'w') as f:
            json.dump(deprecated_config, f, indent=2)
        
        # Test that deprecated options are handled gracefully
        manager = OrchestrationManager(config_path=config_path)
        
        # Should still load successfully
        self.assertEqual(manager.config['execution_mode'], 'sequential')
        
        # Deprecated options should be ignored (not cause errors)
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'], "Config with deprecated options should still be valid")
    
    def test_configuration_migration_procedures(self):
        """Test configuration migration and upgrade procedures"""
        # Old format that needs migration
        old_config = {
            "mode": "sequential",  # Old field name
            "max_agents": 1,       # Old field name
            "agent_list": ["po_reader", "validation"]  # Old structure
        }
        
        config_path = os.path.join(self.config_dir, 'orchestration_config.json')
        with open(config_path, 'w') as f:
            json.dump(old_config, f, indent=2)
        
        # Test migration by creating manager (should use defaults for missing fields)
        manager = OrchestrationManager(config_path=config_path)
        
        # Should have migrated to current format with defaults
        self.assertIn('execution_mode', manager.config)
        self.assertIn('max_parallel_agents', manager.config)
        self.assertIn('dependencies', manager.config)
        
        # Test that migrated config can be saved in new format
        new_config_path = os.path.join(self.config_dir, 'migrated_config.json')
        manager.create_config_file(new_config_path)
        
        # Verify migrated config file exists and is valid
        self.assertTrue(os.path.exists(new_config_path))
        
        with open(new_config_path, 'r') as f:
            migrated_config = json.load(f)
        
        self.assertIn('execution_mode', migrated_config)
        self.assertIn('dependencies', migrated_config)


class ConfigurationVersionMismatchTest(unittest.TestCase):
    """Test graceful handling of version mismatches"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_missing_configuration_file_handling(self):
        """Test handling when configuration file is missing"""
        # Test with non-existent config file
        non_existent_path = os.path.join(self.config_dir, 'missing_config.json')
        
        # Should not raise exception, should use defaults
        manager = OrchestrationManager(config_path=non_existent_path)
        
        # Should have default configuration
        self.assertIn('execution_mode', manager.config)
        self.assertIn('dependencies', manager.config)
        
        # Should be valid with defaults
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'])
    
    def test_malformed_configuration_file_handling(self):
        """Test handling of malformed configuration files"""
        # Create malformed JSON file
        config_path = os.path.join(self.config_dir, 'malformed_config.json')
        with open(config_path, 'w') as f:
            f.write('{ "execution_mode": "sequential", invalid_json }')
        
        # Should handle malformed JSON gracefully
        manager = OrchestrationManager(config_path=config_path)
        
        # Should fall back to default configuration
        self.assertIn('execution_mode', manager.config)
        
        # Should be valid with defaults
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'])
    
    def test_partial_configuration_handling(self):
        """Test handling of partial configuration files"""
        # Config with only some fields
        partial_config = {
            "execution_mode": "coordinated"
            # Missing other required fields
        }
        
        config_path = os.path.join(self.config_dir, 'partial_config.json')
        with open(config_path, 'w') as f:
            json.dump(partial_config, f, indent=2)
        
        # Should merge with defaults
        manager = OrchestrationManager(config_path=config_path)
        
        # Should have specified value
        self.assertEqual(manager.config['execution_mode'], 'coordinated')
        
        # Should have default values for missing fields
        self.assertIn('max_parallel_agents', manager.config)
        self.assertIn('dependencies', manager.config)
        
        # Should be valid
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'])
    
    def test_unknown_configuration_fields_handling(self):
        """Test handling of unknown configuration fields"""
        # Config with unknown fields
        unknown_config = {
            "execution_mode": "sequential",
            "unknown_field": "unknown_value",
            "future_feature": {"setting": "value"},
            "agents": {
                "po_reader": {
                    "enabled": True,
                    "unknown_agent_setting": "value"
                }
            }
        }
        
        config_path = os.path.join(self.config_dir, 'unknown_config.json')
        with open(config_path, 'w') as f:
            json.dump(unknown_config, f, indent=2)
        
        # Should handle unknown fields gracefully
        manager = OrchestrationManager(config_path=config_path)
        
        # Known fields should be loaded
        self.assertEqual(manager.config['execution_mode'], 'sequential')
        
        # Unknown fields should be preserved (for forward compatibility)
        self.assertIn('unknown_field', manager.config)
        self.assertIn('future_feature', manager.config)
        
        # Should still be valid
        validation = manager.validate_configuration()
        self.assertTrue(validation['valid'])


class ConfigurationValidationTest(unittest.TestCase):
    """Test configuration validation and error detection"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        self.config_dir = os.path.join(self.test_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        os.chdir(self.test_dir)
        
    def tearDown(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies in configuration"""
        # Config with circular dependencies
        circular_config = {
            "execution_mode": "coordinated",
            "dependencies": {
                "agent_a": ["agent_b"],
                "agent_b": ["agent_c"],
                "agent_c": ["agent_a"]  # Creates circular dependency
            }
        }
        
        config_path = os.path.join(self.config_dir, 'circular_config.json')
        with open(config_path, 'w') as f:
            json.dump(circular_config, f, indent=2)
        
        manager = OrchestrationManager(config_path=config_path)
        
        # Should detect circular dependency
        validation = manager.validate_configuration()
        self.assertFalse(validation['valid'])
        self.assertTrue(any('circular' in error.lower() for error in validation['errors']))
    
    def test_invalid_dependency_detection(self):
        """Test detection of invalid dependencies"""
        # Config with invalid dependencies
        invalid_config = {
            "execution_mode": "coordinated",
            "dependencies": {
                "po_reader": [],
                "validation": ["po_reader"],
                "so_creator": ["nonexistent_agent"]  # Invalid dependency
            }
        }
        
        config_path = os.path.join(self.config_dir, 'invalid_config.json')
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f, indent=2)
        
        manager = OrchestrationManager(config_path=config_path)
        
        # Should detect invalid dependency
        validation = manager.validate_configuration()
        self.assertFalse(validation['valid'])
        self.assertTrue(any('unknown agent' in error.lower() for error in validation['errors']))
    
    def test_configuration_type_validation(self):
        """Test validation of configuration field types"""
        # Config with wrong types
        wrong_type_config = {
            "execution_mode": "coordinated",
            "max_parallel_agents": "not_a_number",  # Should be int
            "enable_monitoring": "not_a_boolean",   # Should be bool
            "dependencies": "not_a_dict"            # Should be dict
        }
        
        config_path = os.path.join(self.config_dir, 'wrong_type_config.json')
        with open(config_path, 'w') as f:
            json.dump(wrong_type_config, f, indent=2)
        
        # Should handle type mismatches gracefully
        manager = OrchestrationManager(config_path=config_path)
        
        # Should fall back to defaults for invalid types
        self.assertIsInstance(manager.config.get('max_parallel_agents'), int)
        self.assertIsInstance(manager.config.get('dependencies'), dict)


if __name__ == '__main__':
    unittest.main()