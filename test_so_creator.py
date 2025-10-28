#!/usr/bin/env python3
"""
Test script for Sales Order Creator Agent
"""

import sys
import os
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.so_creator.agent import SalesOrderCreatorAgent
from agents.validation.agent import ValidationAgent

def test_sales_order_creator():
    """Test the complete Sales Order Creator workflow"""
    print("=== TESTING SALES ORDER CREATOR ===\n")
    
    # First, run validation to generate validation results
    print("Step 1: Running validation agent to generate validation results...")
    validation_agent = ValidationAgent()
    validation_results = validation_agent.validate_orders()
    
    if not validation_results:
        print("❌ Failed to generate validation results")
        return False
    
    print(f"✅ Generated validation results for {len(validation_results)} orders\n")
    
    # Now run the Sales Order Creator
    print("Step 2: Running Sales Order Creator...")
    so_creator = SalesOrderCreatorAgent()
    result = so_creator.create_sales_orders()
    
    if result['success']:
        print("✅ Sales Order Creator completed successfully")
        print(f"   - Processed {result['order_count']} valid orders")
        print(f"   - Total sales value: ${result['total_sales_value']:.2f}")
        print(f"   - CSV file: {result['csv_file']}")
        print(f"   - Chart files: {', '.join(result['chart_files'])}")
        return True
    else:
        print("❌ Sales Order Creator failed")
        print(f"   - Message: {result['message']}")
        return False

if __name__ == "__main__":
    success = test_sales_order_creator()
    sys.exit(0 if success else 1)