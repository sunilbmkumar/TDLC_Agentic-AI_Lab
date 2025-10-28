# PO Reader Agent - Reads and displays customer orders
import csv
import os
from typing import List, Dict, Any

class POReaderAgent:
    def __init__(self, data_path: str = "data/customer_orders.csv"):
        self.data_path = data_path
        self.orders = []
    
    def read_orders(self) -> List[Dict[str, Any]]:
        """
        Read customer orders from CSV file with validation and error handling
        Returns structured order data for display
        """
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Customer orders file not found: {self.data_path}")
            
            orders = []
            with open(self.data_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Validate CSV headers
                expected_headers = {'PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'}
                if not expected_headers.issubset(set(reader.fieldnames)):
                    missing_headers = expected_headers - set(reader.fieldnames)
                    raise ValueError(f"Missing required CSV headers: {missing_headers}")
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header row
                    try:
                        # Validate and parse order data
                        order = self._validate_and_parse_order(row, row_num)
                        orders.append(order)
                    except ValueError as e:
                        print(f"Warning: Skipping malformed row {row_num}: {e}")
                        continue
            
            self.orders = orders
            return orders
            
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return []
        except Exception as e:
            print(f"Error reading customer orders: {e}")
            return []
    
    def _validate_and_parse_order(self, row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """
        Validate and parse a single order row with data validation
        """
        # Check for empty required fields
        required_fields = ['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price']
        for field in required_fields:
            if not row.get(field, '').strip():
                raise ValueError(f"Empty required field '{field}'")
        
        try:
            # Parse and validate quantity
            quantity = int(row['Quantity'])
            if quantity <= 0:
                raise ValueError(f"Invalid quantity: {quantity}. Must be positive integer")
            
            # Parse and validate price
            price = float(row['Price'])
            if price < 0:
                raise ValueError(f"Invalid price: {price}. Must be non-negative")
            
            # Calculate total value
            total_value = quantity * price
            
            return {
                'PO_Number': row['PO_Number'].strip(),
                'Customer_Name': row['Customer_Name'].strip(),
                'SKU': row['SKU'].strip(),
                'Quantity': quantity,
                'Price': price,
                'Total_Value': round(total_value, 2)
            }
            
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Invalid data format in row {row_num}")
            raise e
    
    def display_orders_table(self) -> None:
        """
        Display customer orders in a formatted table for Kiro console
        Shows PO Number, Customer, SKU, Quantity, Price columns with styling
        """
        if not self.orders:
            print("No customer orders to display.")
            return
        
        # Table headers
        headers = ["PO Number", "Customer", "SKU", "Quantity", "Price"]
        
        # Calculate column widths for proper alignment
        col_widths = [len(header) for header in headers]
        
        for order in self.orders:
            col_widths[0] = max(col_widths[0], len(str(order['PO_Number'])))
            col_widths[1] = max(col_widths[1], len(str(order['Customer_Name'])))
            col_widths[2] = max(col_widths[2], len(str(order['SKU'])))
            col_widths[3] = max(col_widths[3], len(str(order['Quantity'])))
            col_widths[4] = max(col_widths[4], len(f"${order['Price']:.2f}"))
        
        # Add padding
        col_widths = [w + 2 for w in col_widths]
        
        # Print table header
        print("\n" + "=" * sum(col_widths))
        print("CUSTOMER ORDERS - PENDING VALIDATION")
        print("=" * sum(col_widths))
        
        # Print column headers
        header_row = ""
        for i, header in enumerate(headers):
            header_row += header.ljust(col_widths[i])
        print(header_row)
        print("-" * sum(col_widths))
        
        # Print order data
        for order in self.orders:
            row = ""
            row += str(order['PO_Number']).ljust(col_widths[0])
            row += str(order['Customer_Name']).ljust(col_widths[1])
            row += str(order['SKU']).ljust(col_widths[2])
            row += str(order['Quantity']).ljust(col_widths[3])
            row += f"${order['Price']:.2f}".ljust(col_widths[4])
            print(row)
        
        print("=" * sum(col_widths))
        print(f"Total Orders: {len(self.orders)}")
        print("=" * sum(col_widths) + "\n")
    
    def process_natural_language_query(self, query: str) -> str:
        """
        Process natural language queries about customer orders
        Supports queries like "Show me all customer orders pending validation"
        """
        query_lower = query.lower().strip()
        
        # Handle different query types
        if "show" in query_lower and ("orders" in query_lower or "order" in query_lower):
            if "pending validation" in query_lower or "pending" in query_lower:
                return self._handle_pending_orders_query()
            elif "customer" in query_lower:
                return self._handle_customer_filter_query(query_lower)
            else:
                return self._handle_show_all_orders_query()
        
        elif "filter" in query_lower or "customer" in query_lower:
            return self._handle_customer_filter_query(query_lower)
        
        elif "total" in query_lower or "count" in query_lower:
            return self._handle_count_query()
        
        elif "help" in query_lower:
            return self._get_help_text()
        
        else:
            return self._handle_unknown_query(query)
    
    def _handle_pending_orders_query(self) -> str:
        """Handle query for orders pending validation"""
        if not self.orders:
            return "No customer orders found. Please ensure orders are loaded first."
        
        response = f"Found {len(self.orders)} customer orders pending validation:\n\n"
        
        for order in self.orders:
            response += f"• {order['PO_Number']} - {order['Customer_Name']} - {order['SKU']} - Qty: {order['Quantity']} - ${order['Price']:.2f}\n"
        
        total_value = sum(order['Total_Value'] for order in self.orders)
        response += f"\nTotal pending order value: ${total_value:.2f}"
        
        return response
    
    def _handle_customer_filter_query(self, query: str) -> str:
        """Handle queries filtering by customer"""
        # Extract customer name from query
        customers = set(order['Customer_Name'].lower() for order in self.orders)
        found_customer = None
        
        for customer in customers:
            if customer in query:
                found_customer = customer
                break
        
        if found_customer:
            filtered_orders = [order for order in self.orders 
                             if order['Customer_Name'].lower() == found_customer]
            
            response = f"Orders for {found_customer.title()}:\n\n"
            for order in filtered_orders:
                response += f"• {order['PO_Number']} - {order['SKU']} - Qty: {order['Quantity']} - ${order['Price']:.2f}\n"
            
            total_value = sum(order['Total_Value'] for order in filtered_orders)
            response += f"\nTotal value for {found_customer.title()}: ${total_value:.2f}"
            
            return response
        else:
            available_customers = ", ".join(set(order['Customer_Name'] for order in self.orders))
            return f"Customer not found in query. Available customers: {available_customers}"
    
    def _handle_show_all_orders_query(self) -> str:
        """Handle general show orders query"""
        if not self.orders:
            return "No customer orders found."
        
        return f"Displaying all {len(self.orders)} customer orders. Use display_orders_table() for formatted view."
    
    def _handle_count_query(self) -> str:
        """Handle count/total queries"""
        if not self.orders:
            return "No orders loaded."
        
        total_orders = len(self.orders)
        total_value = sum(order['Total_Value'] for order in self.orders)
        unique_customers = len(set(order['Customer_Name'] for order in self.orders))
        
        return f"Order Summary: {total_orders} orders, ${total_value:.2f} total value, {unique_customers} unique customers"
    
    def _handle_unknown_query(self, query: str) -> str:
        """Handle unrecognized queries"""
        return f"I don't understand the query: '{query}'. Try 'help' for available commands."
    
    def _get_help_text(self) -> str:
        """Return help text for available queries"""
        return """
Available queries:
• "Show me all customer orders pending validation" - Display all pending orders
• "Show orders for [customer name]" - Filter orders by customer
• "Total orders" or "Count orders" - Get order summary statistics
• "Help" - Show this help text

Example customers: ACME Corp, Zenith Ltd, Innova Inc
        """.strip()
    
    def generate_reasoning_summary(self) -> str:
        """
        Generate automatic summary for Kiro's reasoning output
        Format: "Detected X incoming purchase orders totaling $Y from Z customers"
        """
        if not self.orders:
            return "No customer orders detected for processing."
        
        total_orders = len(self.orders)
        total_value = sum(order['Total_Value'] for order in self.orders)
        unique_customers = len(set(order['Customer_Name'] for order in self.orders))
        
        # Generate main summary
        summary = f"Detected {total_orders} incoming purchase orders totaling ${total_value:.2f} from {unique_customers} customers"
        
        # Add detailed breakdown
        customer_breakdown = {}
        for order in self.orders:
            customer = order['Customer_Name']
            if customer not in customer_breakdown:
                customer_breakdown[customer] = {'orders': 0, 'value': 0.0}
            customer_breakdown[customer]['orders'] += 1
            customer_breakdown[customer]['value'] += order['Total_Value']
        
        # Create detailed reasoning output
        reasoning_output = f"""
REASONING OUTPUT - PO READER AGENT
================================

SUMMARY: {summary}

DETAILED BREAKDOWN:
"""
        
        for customer, data in customer_breakdown.items():
            reasoning_output += f"• {customer}: {data['orders']} orders, ${data['value']:.2f} total value\n"
        
        reasoning_output += f"""
ORDER DETAILS:
"""
        
        for order in self.orders:
            reasoning_output += f"• {order['PO_Number']}: {order['Customer_Name']} - {order['SKU']} (Qty: {order['Quantity']}, ${order['Price']:.2f})\n"
        
        reasoning_output += f"""
NEXT STEPS:
• Orders are ready for validation processing
• {total_orders} orders will be sent to Validation Agent
• Exception handling will be applied for any validation failures
"""
        
        return reasoning_output.strip()
    
    def display_reasoning_output(self) -> None:
        """
        Display the reasoning output in Kiro's reasoning format
        """
        reasoning = self.generate_reasoning_summary()
        print(reasoning)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for use by other agents or reporting
        """
        if not self.orders:
            return {
                'total_orders': 0,
                'total_value': 0.0,
                'unique_customers': 0,
                'customer_breakdown': {}
            }
        
        total_orders = len(self.orders)
        total_value = sum(order['Total_Value'] for order in self.orders)
        unique_customers = len(set(order['Customer_Name'] for order in self.orders))
        
        customer_breakdown = {}
        for order in self.orders:
            customer = order['Customer_Name']
            if customer not in customer_breakdown:
                customer_breakdown[customer] = {'orders': 0, 'value': 0.0, 'order_numbers': []}
            customer_breakdown[customer]['orders'] += 1
            customer_breakdown[customer]['value'] += order['Total_Value']
            customer_breakdown[customer]['order_numbers'].append(order['PO_Number'])
        
        return {
            'total_orders': total_orders,
            'total_value': round(total_value, 2),
            'unique_customers': unique_customers,
            'customer_breakdown': customer_breakdown
        }