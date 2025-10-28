#!/usr/bin/env python3
"""
Simple test for Summary & Insights Agent
Tests basic functionality without external dependencies
"""

import sys
import os
import json
import csv
from datetime import datetime

# Add the agents directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

def create_test_data():
    """Create minimal test data"""
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Create validation results
    validation_results = [
        {"PO_Number": "PO1001", "SKU": "SKU001", "Status": "Valid", "Reasons": ["Valid"], "Details": {"order_price": 45.50, "reference_price": 42.00, "price_deviation": 8.3}},
        {"PO_Number": "PO1002", "SKU": "SKU002", "Status": "Valid", "Reasons": ["Valid"], "Details": {"order_price": 32.00, "reference_price": 35.00, "price_deviation": 8.6}},
        {"PO_Number": "PO1003", "SKU": "SKU004", "Status": "Valid", "Reasons": ["Valid"], "Details": {"order_price": 28.75, "reference_price": 26.50, "price_deviation": 8.5}},
        {"PO_Number": "PO1004", "SKU": "SKU999", "Status": "Exception", "Reasons": ["SKU not found"], "Details": {"order_price": 15.00, "reference_price": None, "price_deviation": None}}
    ]
    
    with open('outputs/validation_results_detailed.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    # Create sales orders
    with open('outputs/sales_order_output.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
        writer.writeheader()
        writer.writerows([
            {"SO_Number": "SO2001", "Customer": "ACME Corp", "Material": "SKU001", "Quantity": 100, "Price": 45.50, "Total": 4550.00},
            {"SO_Number": "SO2002", "Customer": "Zenith Ltd", "Material": "SKU002", "Quantity": 75, "Price": 32.00, "Total": 2400.00},
            {"SO_Number": "SO2003", "Customer": "ACME Corp", "Material": "SKU004", "Quantity": 200, "Price": 28.75, "Total": 5750.00}
        ])
    
    # Create exception emails
    with open('outputs/exception_email_responses.json', 'w') as f:
        json.dump([{"po_number": "PO1004", "customer_name": "Innova Inc", "exception_type": "SKU_NOT_FOUND"}], f, indent=2)

def test_summary_agent():
    """Test the Summary & Insights Agent"""
    print("=== TESTING SUMMARY & INSIGHTS AGENT ===")
    
    # Create test data
    create_test_data()
    print("✓ Test data created")
    
    try:
        # Import and test the agent
        from summary_insights.agent import SummaryInsightsAgent
        
        agent = SummaryInsightsAgent()
        
        # Test summary generation
        print("\n📊 Testing summary generation...")
        summary = agent.generate_comprehensive_summary()
        print(f"✓ Summary generated: {summary['total_orders']} orders, ${summary['total_sales_value']:,.2f} value")
        
        # Test insights generation
        print("\n💡 Testing insights generation...")
        insights = agent.generate_insights()
        print(f"✓ Generated {len(insights)} insights")
        for insight in insights:
            print(f"   • {insight}")
        
        # Test one-line summary
        print("\n🗣️ Testing one-line executive summary...")
        one_line = agent.generate_one_line_executive_summary()
        print(f"✓ One-line summary: {one_line}")
        
        # Test conversational queries
        print("\n💬 Testing conversational queries...")
        test_queries = [
            "Generate a one-line executive summary",
            "How many orders were processed?",
            "What's the total sales value?",
            "Who is the top customer?"
        ]
        
        for query in test_queries:
            response = agent.process_leadership_query(query)
            print(f"   Q: {query}")
            print(f"   A: {response}")
            print()
        
        print("✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_summary_agent()
    if success:
        print("\n🎉 Summary & Insights Agent implementation is working correctly!")
    else:
        print("\n💥 Summary & Insights Agent needs debugging.")