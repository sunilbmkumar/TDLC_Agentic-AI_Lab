#!/usr/bin/env python3
"""
Generate test data for Summary & Insights Agent
Creates the required output files if they don't exist
"""

import json
import csv
import os
from datetime import datetime

def create_validation_results():
    """Create validation results file"""
    validation_results = [
        {
            "PO_Number": "PO1001",
            "SKU": "SKU001",
            "Status": "Valid",
            "Reasons": ["Price deviation of 8.3% is within acceptable range for SKU SKU001"],
            "Details": {
                "order_price": 45.50,
                "reference_price": 42.00,
                "price_deviation": 8.3
            }
        },
        {
            "PO_Number": "PO1002",
            "SKU": "SKU002",
            "Status": "Valid",
            "Reasons": ["Price deviation of 8.6% is within acceptable range for SKU SKU002"],
            "Details": {
                "order_price": 32.00,
                "reference_price": 35.00,
                "price_deviation": 8.6
            }
        },
        {
            "PO_Number": "PO1003",
            "SKU": "SKU004",
            "Status": "Valid",
            "Reasons": ["Price deviation of 8.5% is within acceptable range for SKU SKU004"],
            "Details": {
                "order_price": 28.75,
                "reference_price": 26.50,
                "price_deviation": 8.5
            }
        },
        {
            "PO_Number": "PO1004",
            "SKU": "SKU999",
            "Status": "Exception",
            "Reasons": ["SKU SKU999 not found in master data"],
            "Details": {
                "order_price": 15.00,
                "reference_price": None,
                "price_deviation": None
            }
        }
    ]
    
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/validation_results_detailed.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print("✓ Created validation_results_detailed.json")

def create_sales_orders():
    """Create sales orders CSV file"""
    sales_orders = [
        {
            "SO_Number": "SO2001",
            "Customer": "ACME Corp",
            "Material": "SKU001",
            "Quantity": 100,
            "Price": 45.50,
            "Total": 4550.00
        },
        {
            "SO_Number": "SO2002",
            "Customer": "Zenith Ltd",
            "Material": "SKU002",
            "Quantity": 75,
            "Price": 32.00,
            "Total": 2400.00
        },
        {
            "SO_Number": "SO2003",
            "Customer": "ACME Corp",
            "Material": "SKU004",
            "Quantity": 200,
            "Price": 28.75,
            "Total": 5750.00
        }
    ]
    
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/sales_order_output.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
        writer.writeheader()
        writer.writerows(sales_orders)
    
    print("✓ Created sales_order_output.csv")

def create_exception_emails():
    """Create exception email responses file"""
    exception_emails = [
        {
            "to": "procurement@innovainc.com",
            "customer_name": "Innova Inc",
            "subject": "Invalid SKU Found in PO1004",
            "message": "Dear Innova Inc,\n\nWe have identified an issue with your purchase order PO1004.\n\nIssue: The product code SKU999 is invalid and not found in our master product catalog.\n\nPlease review your order and provide a valid SKU from our current product catalog. You can contact our sales team for assistance with product selection.\n\nWe apologize for any inconvenience and look forward to processing your corrected order promptly.\n\nBest regards,\nOrder Processing Team",
            "po_number": "PO1004",
            "exception_type": "SKU_NOT_FOUND",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    os.makedirs('outputs', exist_ok=True)
    with open('outputs/exception_email_responses.json', 'w') as f:
        json.dump(exception_emails, f, indent=2)
    
    print("✓ Created exception_email_responses.json")

def main():
    """Generate all required test data"""
    print("Generating test data for Summary & Insights Agent...")
    
    create_validation_results()
    create_sales_orders()
    create_exception_emails()
    
    print("\n✅ All test data files created successfully!")

if __name__ == "__main__":
    main()