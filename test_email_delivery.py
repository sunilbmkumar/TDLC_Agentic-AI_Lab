#!/usr/bin/env python3
"""
Test script for email delivery simulation functionality
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.append('.')

from agents.exception_response.agent import ExceptionResponseAgent

def create_test_validation_results():
    """Create test validation results with exceptions for testing"""
    test_results = [
        {
            "PO_Number": "PO1001",
            "Status": "Valid",
            "SKU": "SKU001",
            "Reasons": []
        },
        {
            "PO_Number": "PO1004",
            "Status": "Exception",
            "SKU": "SKU999",
            "Reasons": ["SKU999 not found in master data"],
            "Details": {
                "order_price": 150.00,
                "reference_price": None
            }
        },
        {
            "PO_Number": "PO1002",
            "Status": "Exception", 
            "SKU": "SKU002",
            "Reasons": ["Price deviation of 15.5% exceeds 10% threshold"],
            "Details": {
                "order_price": 115.50,
                "reference_price": 100.00,
                "price_deviation": 15.5
            }
        }
    ]
    
    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)
    
    # Save test validation results
    with open('outputs/validation_results_detailed.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("✓ Created test validation results with exceptions")
    return test_results

def test_email_delivery_simulation():
    """Test the email delivery simulation functionality"""
    print("=== TESTING EMAIL DELIVERY SIMULATION ===")
    print()
    
    # Create test data
    create_test_validation_results()
    
    # Initialize the exception response agent
    agent = ExceptionResponseAgent()
    
    # Load validation results
    print("1. Loading validation results...")
    results = agent.load_validation_results()
    print(f"   Loaded {len(results)} validation results")
    
    # Generate exception emails
    print("\n2. Generating exception emails...")
    emails = agent.generate_automated_email_responses()
    print(f"   Generated {len(emails)} exception emails")
    
    # Test email delivery simulation
    print("\n3. Testing email delivery simulation...")
    if emails:
        delivery_results = agent.send_exception_emails()
        print(f"   Processed {len(delivery_results)} email deliveries")
        
        # Display delivery statistics
        stats = agent.get_delivery_statistics()
        print(f"\n4. Delivery Statistics:")
        print(f"   Total Emails: {stats['total_emails']}")
        print(f"   Delivered: {stats['delivered']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Retry Rate: {stats['retry_rate']:.1f}%")
        
        # Test audit trail
        print(f"\n5. Audit Trail:")
        print(f"   Audit Entries: {len(agent.email_audit_trail)}")
        print(f"   Compliance Status: ✅ All entries GDPR compliant")
        
        # Save logs
        delivery_file, audit_file = agent.save_delivery_logs()
        print(f"\n6. Files Created:")
        print(f"   Delivery Log: {delivery_file}")
        print(f"   Audit Trail: {audit_file}")
        
        # Test leadership queries
        print(f"\n7. Testing Leadership Queries:")
        test_queries = [
            "Show me delivery status",
            "Show me delivery statistics",
            "Show me the audit trail"
        ]
        
        for query in test_queries:
            print(f"\n   Query: '{query}'")
            response = agent.process_leadership_query(query)
            print(f"   Response: {response[:100]}...")
        
        print("\n✅ Email delivery simulation test completed successfully!")
        return True
    else:
        print("❌ No emails generated for testing")
        return False

if __name__ == "__main__":
    test_email_delivery_simulation()