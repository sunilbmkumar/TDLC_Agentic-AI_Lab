#!/usr/bin/env python3
"""
Test script for Summary & Insights Agent
Tests the complete functionality of the Summary & Insights Agent
"""

import sys
import os

# Add the agents directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from summary_insights.agent import SummaryInsightsAgent

def test_summary_insights_agent():
    """Test the Summary & Insights Agent functionality"""
    print("=== TESTING SUMMARY & INSIGHTS AGENT ===")
    print()
    
    # Create agent instance
    agent = SummaryInsightsAgent()
    
    # Run the complete agent workflow
    try:
        result = agent.run_summary_insights_agent()
        
        if result['success']:
            print("\n✅ Summary & Insights Agent test completed successfully!")
            print(f"📋 One-line summary: {result['one_line_summary']}")
            print(f"📁 Files generated: {len(result['files_generated'])}")
            print(f"💡 Insights generated: {len(result['insights'])}")
        else:
            print("\n❌ Summary & Insights Agent test failed!")
            
    except Exception as e:
        print(f"\n❌ Error testing Summary & Insights Agent: {str(e)}")
        import traceback
        traceback.print_exc()

def test_individual_components():
    """Test individual components of the agent"""
    print("\n=== TESTING INDIVIDUAL COMPONENTS ===")
    print()
    
    agent = SummaryInsightsAgent()
    
    try:
        # Test data loading
        print("📂 Testing data loading...")
        agent.load_customer_orders()
        print(f"   Loaded {len(agent.customer_orders)} customer orders")
        
        # Test summary generation
        print("📊 Testing summary generation...")
        summary = agent.generate_comprehensive_summary()
        print(f"   Generated summary with {summary['total_orders']} orders")
        
        # Test insights generation
        print("💡 Testing insights generation...")
        insights = agent.generate_insights()
        print(f"   Generated {len(insights)} insights")
        
        # Test conversational queries
        print("🗣️ Testing conversational queries...")
        test_queries = [
            "Generate a one-line executive summary",
            "How many orders were processed?",
            "What's the total sales value?"
        ]
        
        for query in test_queries:
            response = agent.process_leadership_query(query)
            print(f"   Query: '{query}' -> Response length: {len(response)} chars")
        
        print("\n✅ Individual component tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing individual components: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the tests
    test_summary_insights_agent()
    test_individual_components()
    
    print("\n=== ALL TESTS COMPLETE ===")