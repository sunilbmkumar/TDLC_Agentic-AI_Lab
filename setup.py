#!/usr/bin/env python3
"""
Setup script for PO to SO Agent Demo
Creates necessary directories and sample data files
"""

import os
import csv
import json

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'outputs',
        'config'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_sample_data():
    """Create sample data files for testing"""
    
    # Sample customer orders
    customer_orders = [
        {"PO_Number": "PO1001", "Customer_Name": "ACME Corp", "SKU": "SKU001", "Quantity": 100, "Price": 50.00},
        {"PO_Number": "PO1002", "Customer_Name": "Zenith Ltd", "SKU": "SKU002", "Quantity": 50, "Price": 100.00},
        {"PO_Number": "PO1003", "Customer_Name": "Valid Corp", "SKU": "SKU004", "Quantity": 75, "Price": 80.00},
        {"PO_Number": "PO1004", "Customer_Name": "Innova Inc", "SKU": "SKU999", "Quantity": 25, "Price": 150.00}
    ]
    
    # Sample master SKU data
    master_sku = [
        {"SKU": "SKU001", "Product_Name": "Widget A", "Reference_Price": 50.00},
        {"SKU": "SKU002", "Product_Name": "Widget B", "Reference_Price": 100.00},
        {"SKU": "SKU004", "Product_Name": "Widget D", "Reference_Price": 80.00}
    ]
    
    # Write customer orders CSV
    with open('data/customer_orders.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=customer_orders[0].keys())
        writer.writeheader()
        writer.writerows(customer_orders)
    
    print("✅ Created sample customer orders: data/customer_orders.csv")
    
    # Write master SKU CSV
    with open('data/master_sku.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=master_sku[0].keys())
        writer.writeheader()
        writer.writerows(master_sku)
    
    print("✅ Created sample master SKU data: data/master_sku.csv")

def create_config_file():
    """Create default orchestration config"""
    config = {
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
        }
    }
    
    with open('config/orchestration_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created orchestration config: config/orchestration_config.json")

def main():
    """Main setup function"""
    print("🚀 Setting up PO to SO Agent Demo")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Create sample data
    create_sample_data()
    
    # Create config
    create_config_file()
    
    print("\n" + "=" * 40)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Or test individual components:")
    print("   - python test_workflow_validation.py")
    print("   - python test_workflow_integration.py")
    print("3. Check outputs/ folder for results")

if __name__ == "__main__":
    main()