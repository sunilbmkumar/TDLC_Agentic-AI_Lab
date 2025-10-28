#!/usr/bin/env python3
"""
Update PO Acknowledgments with latest data
"""

import sys
import os
sys.path.append('.')

from agents.po_acknowledgment.agent import POAcknowledgmentAgent

def main():
    print("=== UPDATING PO ACKNOWLEDGMENTS ===")
    
    agent = POAcknowledgmentAgent()
    result = agent.create_po_acknowledgments()
    
    if result['success']:
        print("✅ PO Acknowledgments updated successfully!")
        print(f"Total acknowledgments: {len(result['acknowledgments'])}")
        for ack in result['acknowledgments']:
            print(f"  {ack['PO_Number']}: {ack['Acknowledgment_Status']}")
    else:
        print("❌ Failed to update PO acknowledgments")
        print(f"Error: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    main()