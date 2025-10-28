#!/usr/bin/env python3
"""
PO Acknowledgment Agent - Creates acknowledgment datasets for purchase orders
Generates Amazon-compatible PO acknowledgment data
"""

import csv
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class POAcknowledgmentAgent:
    def __init__(self):
        self.customer_orders = []
        self.validation_results = []
        self.acknowledgments = []
        
    def load_customer_orders(self, file_path: str = "data/customer_orders.csv") -> List[Dict[str, Any]]:
        """Load customer orders from CSV file"""
        orders = []
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert numeric fields
                    row['Quantity'] = int(row['Quantity'])
                    row['Price'] = float(row['Price'])
                    orders.append(row)
            self.customer_orders = orders
            return orders
        except FileNotFoundError:
            print(f"Error: Customer orders file not found at {file_path}")
            return []
        except Exception as e:
            print(f"Error reading customer orders: {str(e)}")
            return []
    
    def load_validation_results(self, file_path: str = "outputs/validation_results_detailed.json") -> List[Dict[str, Any]]:
        """Load validation results from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.validation_results = json.load(f)
            return self.validation_results
        except FileNotFoundError:
            print(f"Error: Validation results file not found at {file_path}")
            return []
        except Exception as e:
            print(f"Error loading validation results: {str(e)}")
            return []
    
    def generate_po_acknowledgment(self, po_data: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PO acknowledgment record for a single order"""
        
        # Determine acknowledgment status based on validation
        if validation_result.get('Status') == 'Valid':
            ack_status = 'ACCEPTED'
            ack_code = 'AC'
            estimated_ship_date = datetime.now() + timedelta(days=3)
            estimated_delivery_date = datetime.now() + timedelta(days=7)
            notes = 'Order accepted and will be processed'
        else:
            ack_status = 'REJECTED'
            ack_code = 'RJ'
            estimated_ship_date = None
            estimated_delivery_date = None
            reasons = validation_result.get('Reasons', [])
            notes = f"Order rejected: {'; '.join(reasons)}"
        
        # Create acknowledgment record
        acknowledgment = {
            'PO_Number': po_data['PO_Number'],
            'Customer_Name': po_data['Customer_Name'],
            'SKU': po_data['SKU'],
            'Quantity_Ordered': po_data['Quantity'],
            'Unit_Price': po_data['Price'],
            'Total_Amount': po_data['Quantity'] * po_data['Price'],
            'Acknowledgment_Status': ack_status,
            'Acknowledgment_Code': ack_code,
            'Acknowledgment_Date': datetime.now().strftime('%Y-%m-%d'),
            'Acknowledgment_Time': datetime.now().strftime('%H:%M:%S'),
            'Estimated_Ship_Date': estimated_ship_date.strftime('%Y-%m-%d') if estimated_ship_date else None,
            'Estimated_Delivery_Date': estimated_delivery_date.strftime('%Y-%m-%d') if estimated_delivery_date else None,
            'Vendor_ID': 'VENDOR001',  # Could be configurable
            'Vendor_Name': 'Demo Vendor Corp',
            'Notes': notes,
            'Contact_Email': 'orders@demovendor.com',
            'Reference_Number': f"ACK-{po_data['PO_Number']}-{datetime.now().strftime('%Y%m%d')}"
        }
        
        return acknowledgment
    
    def create_amazon_compatible_format(self, acknowledgments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert acknowledgments to Amazon-compatible format"""
        amazon_format = []
        
        for ack in acknowledgments:
            amazon_record = {
                'MessageType': 'OrderAcknowledgement',
                'MerchantOrderID': ack['PO_Number'],
                'AmazonOrderID': f"AMZ-{ack['PO_Number']}-{datetime.now().strftime('%Y%m%d')}",
                'StatusCode': ack['Acknowledgment_Code'],
                'ItemLevelAcknowledgements': [
                    {
                        'AmazonOrderItemCode': f"{ack['SKU']}-001",
                        'MerchantOrderItemID': ack['PO_Number'],
                        'CancelledQuantity': 0 if ack['Acknowledgment_Status'] == 'ACCEPTED' else ack['Quantity_Ordered'],
                        'AcknowledgedQuantity': ack['Quantity_Ordered'] if ack['Acknowledgment_Status'] == 'ACCEPTED' else 0,
                        'PerUnitPrice': ack['Unit_Price'],
                        'PerUnitDeclaredValue': ack['Unit_Price']
                    }
                ],
                'ExpectedShipDate': ack['Estimated_Ship_Date'],
                'ExpectedDeliveryDate': ack['Estimated_Delivery_Date'],
                'CarrierCode': 'UPS',  # Default carrier
                'CarrierName': 'United Parcel Service',
                'ShippingMethod': 'Standard',
                'ProcessedDateTime': f"{ack['Acknowledgment_Date']}T{ack['Acknowledgment_Time']}Z"
            }
            amazon_format.append(amazon_record)
        
        return amazon_format
    
    def generate_acknowledgment_dataset(self) -> List[Dict[str, Any]]:
        """Generate complete PO acknowledgment dataset"""
        print("=== GENERATING PO ACKNOWLEDGMENT DATASET ===")
        
        # Load required data
        self.load_customer_orders()
        self.load_validation_results()
        
        if not self.customer_orders:
            print("No customer orders found")
            return []
        
        if not self.validation_results:
            print("No validation results found")
            return []
        
        # Create acknowledgments
        acknowledgments = []
        
        # Create lookup for validation results
        validation_lookup = {result['PO_Number']: result for result in self.validation_results}
        
        for order in self.customer_orders:
            po_number = order['PO_Number']
            validation_result = validation_lookup.get(po_number, {})
            
            if validation_result:
                ack = self.generate_po_acknowledgment(order, validation_result)
                acknowledgments.append(ack)
                print(f"Generated acknowledgment for {po_number}: {ack['Acknowledgment_Status']}")
            else:
                print(f"Warning: No validation result found for {po_number}")
        
        self.acknowledgments = acknowledgments
        return acknowledgments
    
    def save_acknowledgment_datasets(self, output_dir: str = "outputs") -> Dict[str, str]:
        """Save acknowledgment datasets in multiple formats"""
        os.makedirs(output_dir, exist_ok=True)
        
        files_created = {}
        
        # 1. Standard CSV format
        csv_file = os.path.join(output_dir, "po_acknowledgments.csv")
        if self.acknowledgments:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.acknowledgments[0].keys())
                writer.writeheader()
                writer.writerows(self.acknowledgments)
            files_created['csv'] = csv_file
            print(f"✅ Standard CSV saved: {csv_file}")
        
        # 2. Amazon-compatible JSON format
        amazon_format = self.create_amazon_compatible_format(self.acknowledgments)
        amazon_file = os.path.join(output_dir, "amazon_po_acknowledgments.json")
        with open(amazon_file, 'w', encoding='utf-8') as f:
            json.dump(amazon_format, f, indent=2)
        files_created['amazon_json'] = amazon_file
        print(f"✅ Amazon JSON saved: {amazon_file}")
        
        # 3. Summary JSON
        summary = self.generate_acknowledgment_summary()
        summary_file = os.path.join(output_dir, "po_acknowledgment_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        files_created['summary'] = summary_file
        print(f"✅ Summary saved: {summary_file}")
        
        return files_created
    
    def generate_acknowledgment_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for acknowledgments"""
        if not self.acknowledgments:
            return {}
        
        total_orders = len(self.acknowledgments)
        accepted_orders = len([ack for ack in self.acknowledgments if ack['Acknowledgment_Status'] == 'ACCEPTED'])
        rejected_orders = total_orders - accepted_orders
        
        total_value = sum(ack['Total_Amount'] for ack in self.acknowledgments)
        accepted_value = sum(ack['Total_Amount'] for ack in self.acknowledgments if ack['Acknowledgment_Status'] == 'ACCEPTED')
        
        return {
            'total_orders': total_orders,
            'accepted_orders': accepted_orders,
            'rejected_orders': rejected_orders,
            'acceptance_rate': (accepted_orders / total_orders * 100) if total_orders > 0 else 0,
            'total_order_value': total_value,
            'accepted_order_value': accepted_value,
            'rejected_order_value': total_value - accepted_value,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'acknowledgment_files': ['po_acknowledgments.csv', 'amazon_po_acknowledgments.json']
        }
    
    def display_acknowledgment_summary(self):
        """Display acknowledgment summary in console"""
        summary = self.generate_acknowledgment_summary()
        
        print("\n=== PO ACKNOWLEDGMENT SUMMARY ===")
        print(f"Total Orders: {summary.get('total_orders', 0)}")
        print(f"Accepted Orders: {summary.get('accepted_orders', 0)}")
        print(f"Rejected Orders: {summary.get('rejected_orders', 0)}")
        print(f"Acceptance Rate: {summary.get('acceptance_rate', 0):.1f}%")
        print(f"Total Order Value: ${summary.get('total_order_value', 0):.2f}")
        print(f"Accepted Value: ${summary.get('accepted_order_value', 0):.2f}")
        print("=== END SUMMARY ===")
    
    def create_po_acknowledgments(self) -> Dict[str, Any]:
        """Main method to create PO acknowledgment datasets"""
        print("=== PO ACKNOWLEDGMENT AGENT ===")
        
        # Generate acknowledgments
        acknowledgments = self.generate_acknowledgment_dataset()
        
        if not acknowledgments:
            return {'success': False, 'message': 'No acknowledgments generated'}
        
        # Save datasets
        files_created = self.save_acknowledgment_datasets()
        
        # Display summary
        self.display_acknowledgment_summary()
        
        summary = self.generate_acknowledgment_summary()
        
        print(f"\n=== PO ACKNOWLEDGMENT CREATION COMPLETE ===")
        print(f"Files Created: {list(files_created.values())}")
        print("=== END PO ACKNOWLEDGMENT AGENT ===")
        
        return {
            'success': True,
            'acknowledgments': acknowledgments,
            'files_created': files_created,
            'summary': summary
        }


def main():
    """Test the PO Acknowledgment Agent"""
    agent = POAcknowledgmentAgent()
    result = agent.create_po_acknowledgments()
    
    if result['success']:
        print("✅ PO Acknowledgment generation completed successfully!")
    else:
        print("❌ PO Acknowledgment generation failed!")


if __name__ == "__main__":
    main()