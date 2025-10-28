#!/usr/bin/env python3
"""
Test script for PO Acknowledgment Agent
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.po_acknowledgment.agent import POAcknowledgmentAgent

def test_po_acknowledgment_agent():
    """Test the PO Acknowledgment Agent functionality"""
    print("=== TESTING PO ACKNOWLEDGMENT AGENT ===\n")
    
    # Create agent instance
    agent = POAcknowledgmentAgent()
    
    # Run the complete acknowledgment workflow
    result = agent.create_po_acknowledgments()
    
    if result['success']:
        print("\n✅ PO Acknowledgment Agent test completed successfully!")
        print(f"📋 Acknowledgments generated: {len(result['acknowledgments'])}")
        print(f"📁 Files created: {len(result['files_created'])}")
        
        # Display file locations
        for file_type, file_path in result['files_created'].items():
            print(f"   {file_type}: {file_path}")
        
        return True
    else:
        print("\n❌ PO Acknowledgment Agent test failed!")
        print(f"   Message: {result.get('message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_po_acknowledgment_agent()
    sys.exit(0 if success else 1)