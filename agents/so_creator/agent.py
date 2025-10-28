# Sales Order Creator Agent - Transforms validated POs into sales orders
import csv
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class SalesOrderCreatorAgent:
    def __init__(self):
        self.validated_orders = []
        self.customer_orders = []
        self.sales_orders = []
        self.so_counter = 2001  # Starting SO number
    
    def read_validation_results(self, file_path: str = "outputs/validation_results_simple.json") -> List[Dict[str, str]]:
        """Read validation results from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                validation_results = json.load(file)
            return validation_results
        except FileNotFoundError:
            print(f"Error: Validation results file not found at {file_path}")
            return []
        except Exception as e:
            print(f"Error reading validation results: {str(e)}")
            return []
    
    def read_customer_orders(self, file_path: str = "data/customer_orders.csv") -> List[Dict[str, Any]]:
        """Read customer orders from CSV file"""
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
    
    def filter_valid_orders(self, validation_results: List[Dict[str, str]]) -> List[str]:
        """Filter validation results to get only orders with Status == 'Valid'"""
        valid_po_numbers = []
        for result in validation_results:
            if result.get('Status') == 'Valid':
                valid_po_numbers.append(result['PO_Number'])
        return valid_po_numbers
    
    def get_validated_order_data(self, valid_po_numbers: List[str]) -> List[Dict[str, Any]]:
        """Get order data for validated PO numbers"""
        validated_orders = []
        for order in self.customer_orders:
            if order['PO_Number'] in valid_po_numbers:
                validated_orders.append(order)
        self.validated_orders = validated_orders
        return validated_orders
    
    def generate_so_number(self, po_number: str) -> str:
        """Generate unique SO number for each valid order"""
        # Transform PO1001 → SO2001, PO1002 → SO2002, etc.
        so_number = f"SO{self.so_counter}"
        self.so_counter += 1
        return so_number
    
    def transform_po_to_so(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform validated PO data into sales order format"""
        so_number = self.generate_so_number(po_data['PO_Number'])
        
        # Calculate total (Quantity * Price)
        total = po_data['Quantity'] * po_data['Price']
        
        sales_order = {
            'SO_Number': so_number,
            'PO_Number': po_data['PO_Number'],  # Keep reference to original PO
            'Customer': po_data['Customer_Name'],
            'Material': po_data['SKU'],  # Map SKU to Material
            'Quantity': po_data['Quantity'],
            'Price': po_data['Price'],
            'Total': total,
            'Created_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return sales_order
    
    def process_validated_orders(self) -> List[Dict[str, Any]]:
        """Main method to process validated orders and create sales orders"""
        print("Starting Sales Order Creator process...")
        
        # Read validation results
        validation_results = self.read_validation_results()
        if not validation_results:
            print("No validation results found. Please run validation agent first.")
            return []
        
        # Read customer orders
        self.read_customer_orders()
        if not self.customer_orders:
            print("No customer orders found.")
            return []
        
        # Filter for valid orders only
        valid_po_numbers = self.filter_valid_orders(validation_results)
        print(f"Found {len(valid_po_numbers)} valid orders: {', '.join(valid_po_numbers)}")
        
        # Get validated order data
        validated_orders = self.get_validated_order_data(valid_po_numbers)
        
        # Transform each validated PO to sales order
        sales_orders = []
        for po_data in validated_orders:
            so_data = self.transform_po_to_so(po_data)
            sales_orders.append(so_data)
            print(f"Transformed {po_data['PO_Number']} → {so_data['SO_Number']}")
        
        self.sales_orders = sales_orders
        return sales_orders
    
    def generate_sales_order_dataset(self) -> List[Dict[str, Any]]:
        """Generate sales order dataset with proper column mapping"""
        dataset = []
        
        for so in self.sales_orders:
            # Create dataset row with required columns: SO_Number, Customer, Material, Quantity, Price, Total
            dataset_row = {
                'SO_Number': so['SO_Number'],
                'Customer': so['Customer'],
                'Material': so['Material'],  # SKU mapped to Material
                'Quantity': so['Quantity'],
                'Price': so['Price'],
                'Total': so['Total']
            }
            dataset.append(dataset_row)
        
        return dataset
    
    def format_for_erp_consumption(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format dataset for ERP consumption with proper data types and formatting"""
        formatted_dataset = []
        
        for row in dataset:
            formatted_row = {
                'SO_Number': str(row['SO_Number']),
                'Customer': str(row['Customer']),
                'Material': str(row['Material']),
                'Quantity': int(row['Quantity']),
                'Price': f"{float(row['Price']):.2f}",  # Format price to 2 decimal places
                'Total': f"{float(row['Total']):.2f}"   # Format total to 2 decimal places
            }
            formatted_dataset.append(formatted_row)
        
        return formatted_dataset
    
    def calculate_line_totals(self) -> Dict[str, float]:
        """Calculate line totals and summary statistics"""
        total_sales_value = 0.0
        customer_totals = {}
        
        for so in self.sales_orders:
            total_sales_value += so['Total']
            
            customer = so['Customer']
            if customer not in customer_totals:
                customer_totals[customer] = 0.0
            customer_totals[customer] += so['Total']
        
        return {
            'total_sales_value': total_sales_value,
            'customer_totals': customer_totals,
            'order_count': len(self.sales_orders)
        }
    
    def generate_csv_output(self, output_file: str = "outputs/sales_order_output.csv") -> str:
        """Generate properly formatted CSV file for ERP import"""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Generate dataset
        dataset = self.generate_sales_order_dataset()
        formatted_dataset = self.format_for_erp_consumption(dataset)
        
        # Define CSV headers
        headers = ['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                
                # Write headers
                writer.writeheader()
                
                # Write data rows
                for row in formatted_dataset:
                    writer.writerow(row)
            
            print(f"Sales order CSV generated: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error generating CSV output: {str(e)}")
            return ""
    
    def validate_output_format(self, csv_file: str) -> bool:
        """Validate output format against ERP requirements"""
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                # Check required headers
                required_headers = ['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total']
                if headers != required_headers:
                    print(f"Header validation failed. Expected: {required_headers}, Got: {headers}")
                    return False
                
                # Validate data format
                row_count = 0
                for row in reader:
                    row_count += 1
                    
                    # Validate SO_Number format (should start with 'SO')
                    if not row['SO_Number'].startswith('SO'):
                        print(f"Invalid SO_Number format: {row['SO_Number']}")
                        return False
                    
                    # Validate numeric fields
                    try:
                        int(row['Quantity'])
                        float(row['Price'])
                        float(row['Total'])
                    except ValueError as e:
                        print(f"Invalid numeric format in row {row_count}: {str(e)}")
                        return False
                
                print(f"CSV format validation passed. {row_count} rows processed.")
                return True
                
        except Exception as e:
            print(f"Error validating CSV format: {str(e)}")
            return False
    
    def display_csv_preview(self, csv_file: str, max_rows: int = 5) -> None:
        """Display preview of generated CSV file"""
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                print(f"\n=== CSV PREVIEW: {csv_file} ===")
                print(f"Headers: {', '.join(reader.fieldnames)}")
                print()
                
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        print("... (additional rows truncated)")
                        break
                    
                    print(f"Row {i+1}: {dict(row)}")
                
                print("=== END CSV PREVIEW ===\n")
                
        except Exception as e:
            print(f"Error displaying CSV preview: {str(e)}")
    
    def generate_sales_value_by_customer_chart(self) -> Dict[str, Any]:
        """Generate 'Total Sales Value by Customer' chart data"""
        totals = self.calculate_line_totals()
        customer_totals = totals['customer_totals']
        
        chart_data = {
            'chart_type': 'bar',
            'title': 'Total Sales Value by Customer',
            'x_axis': 'Customer',
            'y_axis': 'Sales Value ($)',
            'data': [
                {'customer': customer, 'sales_value': total}
                for customer, total in customer_totals.items()
            ]
        }
        
        return chart_data
    
    def generate_exception_count_by_customer_chart(self, validation_results: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate 'Exception Count by Customer' visualization"""
        # Read customer orders to map PO numbers to customers
        customer_orders_map = {order['PO_Number']: order['Customer_Name'] for order in self.customer_orders}
        
        # Count exceptions by customer
        exception_counts = {}
        for result in validation_results:
            if result.get('Status') == 'Exception':
                po_number = result['PO_Number']
                customer = customer_orders_map.get(po_number, 'Unknown')
                
                if customer not in exception_counts:
                    exception_counts[customer] = 0
                exception_counts[customer] += 1
        
        # Include customers with zero exceptions for complete view
        all_customers = set(order['Customer_Name'] for order in self.customer_orders)
        for customer in all_customers:
            if customer not in exception_counts:
                exception_counts[customer] = 0
        
        chart_data = {
            'chart_type': 'bar',
            'title': 'Exception Count by Customer',
            'x_axis': 'Customer',
            'y_axis': 'Exception Count',
            'data': [
                {'customer': customer, 'exception_count': count}
                for customer, count in exception_counts.items()
            ]
        }
        
        return chart_data
    
    def display_charts_in_kiro(self, validation_results: List[Dict[str, str]]) -> None:
        """Display charts in Kiro's chart output interface"""
        print("\n=== KIRO CHART VISUALIZATIONS ===")
        
        # Generate and display sales value chart
        sales_chart = self.generate_sales_value_by_customer_chart()
        print(f"\n📊 {sales_chart['title']}")
        print(f"Chart Type: {sales_chart['chart_type'].title()}")
        print(f"X-Axis: {sales_chart['x_axis']}, Y-Axis: {sales_chart['y_axis']}")
        print("Data:")
        for item in sales_chart['data']:
            print(f"  {item['customer']}: ${item['sales_value']:.2f}")
        
        # Generate and display exception count chart
        exception_chart = self.generate_exception_count_by_customer_chart(validation_results)
        print(f"\n📊 {exception_chart['title']}")
        print(f"Chart Type: {exception_chart['chart_type'].title()}")
        print(f"X-Axis: {exception_chart['x_axis']}, Y-Axis: {exception_chart['y_axis']}")
        print("Data:")
        for item in exception_chart['data']:
            print(f"  {item['customer']}: {item['exception_count']} exceptions")
        
        print("\n=== END CHART VISUALIZATIONS ===")
    
    def save_chart_data(self, validation_results: List[Dict[str, str]], output_dir: str = "outputs") -> Tuple[str, str]:
        """Save chart data to JSON files for Kiro visualization"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save sales value chart data
        sales_chart = self.generate_sales_value_by_customer_chart()
        sales_chart_file = os.path.join(output_dir, "sales_value_by_customer_chart.json")
        with open(sales_chart_file, 'w', encoding='utf-8') as f:
            json.dump(sales_chart, f, indent=2)
        
        # Save exception count chart data
        exception_chart = self.generate_exception_count_by_customer_chart(validation_results)
        exception_chart_file = os.path.join(output_dir, "exception_count_by_customer_chart.json")
        with open(exception_chart_file, 'w', encoding='utf-8') as f:
            json.dump(exception_chart, f, indent=2)
        
        return sales_chart_file, exception_chart_file
    
    def create_sales_orders(self) -> Dict[str, Any]:
        """Main method to create sales orders from validated POs"""
        print("=== SALES ORDER CREATOR AGENT ===")
        
        # Process validated orders
        sales_orders = self.process_validated_orders()
        
        if not sales_orders:
            print("No valid orders to process.")
            return {'success': False, 'message': 'No valid orders found'}
        
        # Generate CSV output
        csv_file = self.generate_csv_output()
        
        # Validate output format
        if csv_file and self.validate_output_format(csv_file):
            print("✅ CSV output validation passed")
        else:
            print("❌ CSV output validation failed")
            # Note: Continue execution even if validation fails for demo purposes
        
        # Display CSV preview
        if csv_file:
            self.display_csv_preview(csv_file)
        
        # Generate and display charts
        validation_results = self.read_validation_results()
        self.display_charts_in_kiro(validation_results)
        
        # Save chart data
        sales_chart_file, exception_chart_file = self.save_chart_data(validation_results)
        
        # Calculate summary statistics
        totals = self.calculate_line_totals()
        
        print(f"\n=== SALES ORDER CREATION SUMMARY ===")
        print(f"Valid Orders Processed: {totals['order_count']}")
        print(f"Total Sales Value: ${totals['total_sales_value']:.2f}")
        print(f"CSV Output: {csv_file}")
        print(f"Chart Data: {sales_chart_file}, {exception_chart_file}")
        print("=== END SALES ORDER CREATOR ===")
        
        return {
            'success': True,
            'sales_orders': sales_orders,
            'csv_file': csv_file,
            'total_sales_value': totals['total_sales_value'],
            'order_count': totals['order_count'],
            'customer_totals': totals['customer_totals'],
            'chart_files': [sales_chart_file, exception_chart_file]
        }
    
