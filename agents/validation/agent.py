# Validation Agent - Validates orders against master SKU data
import csv
import os
import json
from typing import List, Dict, Any, Tuple

class ValidationAgent:
    def __init__(self):
        self.customer_orders = []
        self.master_skus = {}
        self.validation_results = []
    
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
    
    def read_master_skus(self, file_path: str = "data/master_sku.csv") -> Dict[str, Dict[str, Any]]:
        """Read master SKU data from CSV file"""
        skus = {}
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert price to float
                    row['Reference_Price'] = float(row['Reference_Price'])
                    skus[row['SKU']] = row
            self.master_skus = skus
            return skus
        except FileNotFoundError:
            print(f"Error: Master SKU file not found at {file_path}")
            return {}
        except Exception as e:
            print(f"Error reading master SKUs: {str(e)}")
            return {}
    
    def cross_reference_skus(self) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Cross-reference SKUs between order data and master data"""
        cross_referenced = []
        for order in self.customer_orders:
            sku = order['SKU']
            master_data = self.master_skus.get(sku, None)
            cross_referenced.append((order, master_data))
        return cross_referenced
    
    def check_price_deviation(self, order_price: float, reference_price: float, threshold: float = 0.10) -> Tuple[bool, float]:
        """Check if price deviation exceeds threshold (default 10%)"""
        deviation = abs(order_price - reference_price) / reference_price
        exceeds_threshold = deviation > threshold
        return exceeds_threshold, deviation * 100  # Return percentage
    
    def validate_sku_existence(self, sku: str) -> Tuple[bool, str]:
        """Validate if SKU exists in master data"""
        if sku in self.master_skus:
            return True, f"SKU {sku} found in master data"
        else:
            return False, f"SKU {sku} not found in master data"
    
    def validate_price_deviation(self, order_price: float, reference_price: float, sku: str, threshold: float = 0.10) -> Tuple[bool, str]:
        """Validate price deviation against threshold"""
        exceeds_threshold, deviation_percent = self.check_price_deviation(order_price, reference_price, threshold)
        if exceeds_threshold:
            return False, f"Price deviation of {deviation_percent:.1f}% exceeds {threshold*100}% threshold for SKU {sku}"
        else:
            return True, f"Price deviation of {deviation_percent:.1f}% is within acceptable range for SKU {sku}"
    
    def determine_validation_status(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Determine validation status for a single order"""
        po_number = order['PO_Number']
        sku = order['SKU']
        order_price = order['Price']
        
        validation_result = {
            'PO_Number': po_number,
            'SKU': sku,
            'Status': 'Valid',
            'Reasons': [],
            'Details': {
                'order_price': order_price,
                'reference_price': None,
                'price_deviation': None
            }
        }
        
        # Check SKU existence
        sku_exists, sku_message = self.validate_sku_existence(sku)
        if not sku_exists:
            validation_result['Status'] = 'Exception'
            validation_result['Reasons'].append(sku_message)
            return validation_result
        
        # If SKU exists, check price deviation
        reference_price = self.master_skus[sku]['Reference_Price']
        validation_result['Details']['reference_price'] = reference_price
        
        price_valid, price_message = self.validate_price_deviation(order_price, reference_price, sku)
        _, deviation_percent = self.check_price_deviation(order_price, reference_price)
        validation_result['Details']['price_deviation'] = deviation_percent
        
        if not price_valid:
            validation_result['Status'] = 'Exception'
            validation_result['Reasons'].append(price_message)
        else:
            validation_result['Reasons'].append(price_message)
        
        return validation_result
    
    def run_validation_engine(self) -> List[Dict[str, Any]]:
        """Run the complete validation rule engine"""
        # Load data
        self.read_customer_orders()
        self.read_master_skus()
        
        # Validate each order
        validation_results = []
        for order in self.customer_orders:
            result = self.determine_validation_status(order)
            validation_results.append(result)
        
        self.validation_results = validation_results
        return validation_results
    
    def generate_simple_json_output(self) -> List[Dict[str, str]]:
        """Generate simple JSON output format for downstream consumption"""
        simple_results = []
        for result in self.validation_results:
            simple_result = {
                'PO_Number': result['PO_Number'],
                'Status': result['Status']
            }
            simple_results.append(simple_result)
        return simple_results
    
    def generate_detailed_json_output(self) -> List[Dict[str, Any]]:
        """Generate detailed JSON output with exception reasons"""
        return self.validation_results
    
    def save_validation_results(self, output_dir: str = "outputs") -> Tuple[str, str]:
        """Save validation results to JSON files"""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save simple format
        simple_file = os.path.join(output_dir, "validation_results_simple.json")
        simple_data = self.generate_simple_json_output()
        with open(simple_file, 'w', encoding='utf-8') as f:
            json.dump(simple_data, f, indent=2)
        
        # Save detailed format
        detailed_file = os.path.join(output_dir, "validation_results_detailed.json")
        detailed_data = self.generate_detailed_json_output()
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2)
        
        return simple_file, detailed_file
    
    def generate_validation_explanations(self) -> List[str]:
        """Generate automatic explanations for validation results"""
        explanations = []
        
        for result in self.validation_results:
            po_number = result['PO_Number']
            status = result['Status']
            sku = result['SKU']
            
            if status == 'Exception':
                # Generate exception explanations
                for reason in result['Reasons']:
                    if "not found in master data" in reason:
                        explanation = f"{po_number} failed validation because {sku} is not in master data"
                    elif "exceeds" in reason and "threshold" in reason:
                        deviation = result['Details']['price_deviation']
                        explanation = f"{po_number} failed validation because price deviation of {deviation:.1f}% exceeds 10% threshold for {sku}"
                    else:
                        explanation = f"{po_number} failed validation: {reason}"
                    explanations.append(explanation)
            else:
                # Generate success explanations
                if result['Details']['reference_price']:
                    deviation = result['Details']['price_deviation']
                    explanation = f"{po_number} passed validation - {sku} exists in master data with acceptable price deviation of {deviation:.1f}%"
                else:
                    explanation = f"{po_number} passed validation - {sku} exists in master data"
                explanations.append(explanation)
        
        return explanations
    
    def display_validation_reasoning(self) -> None:
        """Display validation logic and decision rationale in Kiro's reasoning interface"""
        print("=== VALIDATION AGENT REASONING ===")
        print()
        
        # Display summary
        total_orders = len(self.validation_results)
        valid_orders = len([r for r in self.validation_results if r['Status'] == 'Valid'])
        exception_orders = total_orders - valid_orders
        
        print(f"Processing {total_orders} customer orders for validation...")
        print(f"Validation Rules Applied:")
        print("  1. SKU Existence Check - Verify SKU exists in master data")
        print("  2. Price Deviation Check - Ensure price is within 10% of reference price")
        print()
        
        # Display detailed explanations
        explanations = self.generate_validation_explanations()
        for explanation in explanations:
            print(f"• {explanation}")
        
        print()
        print(f"VALIDATION SUMMARY: {valid_orders} Valid, {exception_orders} Exceptions")
        print("=== END VALIDATION REASONING ===")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary for display in Kiro interface"""
        total_orders = len(self.validation_results)
        valid_orders = len([r for r in self.validation_results if r['Status'] == 'Valid'])
        exception_orders = total_orders - valid_orders
        
        return {
            'total_orders': total_orders,
            'valid_orders': valid_orders,
            'exception_orders': exception_orders,
            'explanations': self.generate_validation_explanations(),
            'detailed_results': self.validation_results
        }
    
    def validate_orders(self):
        """Main validation method that runs the complete validation process"""
        print("Starting validation process...")
        
        # Run validation engine
        results = self.run_validation_engine()
        
        # Save results to JSON files
        simple_file, detailed_file = self.save_validation_results()
        print(f"Validation results saved to: {simple_file} and {detailed_file}")
        
        # Display reasoning
        self.display_validation_reasoning()
        
        return results