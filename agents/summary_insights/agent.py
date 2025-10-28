# Summary & Insights Agent - Generates comprehensive summaries and insights
import json
import os
import csv
from typing import Dict, List, Any, Tuple
from datetime import datetime

class SummaryInsightsAgent:
    def __init__(self):
        self.customer_orders = []
        self.validation_results = []
        self.sales_orders = []
        self.exception_data = {}
        self.summary_data = {}
        self.insights = []
    
    def load_customer_orders(self, file_path: str = "data/customer_orders.csv") -> List[Dict[str, Any]]:
        """Load customer orders from CSV file"""
        orders = []
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
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
    
    def load_sales_orders(self, file_path: str = "outputs/sales_order_output.csv") -> List[Dict[str, Any]]:
        """Load sales orders from CSV file"""
        orders = []
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row['Quantity'] = int(row['Quantity'])
                    row['Price'] = float(row['Price'])
                    row['Total'] = float(row['Total'])
                    orders.append(row)
            self.sales_orders = orders
            return orders
        except FileNotFoundError:
            print(f"Error: Sales orders file not found at {file_path}")
            return []
        except Exception as e:
            print(f"Error reading sales orders: {str(e)}")
            return []
    
    def load_exception_data(self, file_path: str = "outputs/exception_email_responses.json") -> Dict[str, Any]:
        """Load exception data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                exception_emails = json.load(f)
            self.exception_data = {
                'exception_emails': exception_emails,
                'total_exceptions': len(exception_emails)
            }
            return self.exception_data
        except FileNotFoundError:
            print(f"Error: Exception data file not found at {file_path}")
            return {}
        except Exception as e:
            print(f"Error loading exception data: {str(e)}")
            return {}
    
    def calculate_total_orders(self) -> int:
        """Calculate total number of orders"""
        return len(self.customer_orders)
    
    def calculate_validated_orders(self) -> int:
        """Calculate number of validated orders"""
        if not self.validation_results:
            return 0
        return len([r for r in self.validation_results if r['Status'] == 'Valid'])
    
    def calculate_exceptions(self) -> int:
        """Calculate number of exceptions"""
        if not self.validation_results:
            return 0
        return len([r for r in self.validation_results if r['Status'] == 'Exception'])
    
    def calculate_total_sales_value(self) -> float:
        """Calculate total sales order value"""
        if not self.sales_orders:
            return 0.0
        return sum(order['Total'] for order in self.sales_orders)
    
    def generate_comprehensive_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary with all key metrics"""
        # Load all required data
        self.load_customer_orders()
        self.load_validation_results()
        self.load_sales_orders()
        self.load_exception_data()
        
        # Calculate key metrics
        total_orders = self.calculate_total_orders()
        validated_orders = self.calculate_validated_orders()
        exceptions = self.calculate_exceptions()
        total_sales_value = self.calculate_total_sales_value()
        
        # Generate processing statistics
        processing_stats = {
            'orders_processed': total_orders,
            'validation_success_rate': (validated_orders / total_orders * 100) if total_orders > 0 else 0,
            'exception_rate': (exceptions / total_orders * 100) if total_orders > 0 else 0,
            'sales_conversion_rate': (len(self.sales_orders) / total_orders * 100) if total_orders > 0 else 0
        }
        
        # Create comprehensive summary
        summary = {
            'total_orders': total_orders,
            'validated_orders': validated_orders,
            'exceptions': exceptions,
            'total_sales_value': total_sales_value,
            'processing_statistics': processing_stats,
            'summary_text': f"Total Orders: {total_orders}, Validated Orders: {validated_orders}, Exceptions: {exceptions}, Total Sales Order Value: ${total_sales_value:,.2f}",
            'generated_timestamp': datetime.now().isoformat()
        }
        
        self.summary_data = summary
        return summary
    
    def display_comprehensive_summary(self) -> None:
        """Display comprehensive summary in Kiro console"""
        print("=== COMPREHENSIVE PROCESSING SUMMARY ===")
        print()
        
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        summary = self.summary_data
        
        print("📊 ORDER PROCESSING METRICS")
        print(f"   Total Orders: {summary['total_orders']}")
        print(f"   Validated Orders: {summary['validated_orders']}")
        print(f"   Exceptions: {summary['exceptions']}")
        print(f"   Total Sales Order Value: ${summary['total_sales_value']:,.2f}")
        print()
        
        print("📈 PROCESSING STATISTICS")
        stats = summary['processing_statistics']
        print(f"   Validation Success Rate: {stats['validation_success_rate']:.1f}%")
        print(f"   Exception Rate: {stats['exception_rate']:.1f}%")
        print(f"   Sales Conversion Rate: {stats['sales_conversion_rate']:.1f}%")
        print()
        
        print("📋 SUMMARY STATEMENT")
        print(f"   {summary['summary_text']}")
        print()
        
        print(f"🕒 Generated: {summary['generated_timestamp']}")
        print("=== END COMPREHENSIVE SUMMARY ===")
    
    def save_summary_data(self, output_dir: str = "outputs") -> str:
        """Save summary data to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        summary_file = os.path.join(output_dir, "processing_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.summary_data, f, indent=2)
        
        return summary_file
    
    def analyze_customer_contributions(self) -> Dict[str, Any]:
        """Analyze customer contribution percentages"""
        if not self.sales_orders:
            return {}
        
        # Calculate total sales value
        total_sales = sum(order['Total'] for order in self.sales_orders)
        
        # Calculate customer contributions
        customer_totals = {}
        for order in self.sales_orders:
            customer = order['Customer']
            if customer not in customer_totals:
                customer_totals[customer] = 0.0
            customer_totals[customer] += order['Total']
        
        # Calculate percentages
        customer_contributions = {}
        for customer, total in customer_totals.items():
            percentage = (total / total_sales * 100) if total_sales > 0 else 0
            customer_contributions[customer] = {
                'total_value': total,
                'percentage': percentage,
                'order_count': len([o for o in self.sales_orders if o['Customer'] == customer])
            }
        
        return customer_contributions
    
    def identify_exception_patterns(self) -> Dict[str, Any]:
        """Identify exception patterns and root causes"""
        if not self.validation_results:
            return {}
        
        exception_patterns = {
            'by_customer': {},
            'by_exception_type': {},
            'root_causes': []
        }
        
        # Map PO numbers to customers (from customer orders)
        po_to_customer = {order['PO_Number']: order['Customer_Name'] for order in self.customer_orders}
        
        # Analyze exceptions by customer
        for result in self.validation_results:
            if result['Status'] == 'Exception':
                po_number = result['PO_Number']
                customer = po_to_customer.get(po_number, 'Unknown')
                
                if customer not in exception_patterns['by_customer']:
                    exception_patterns['by_customer'][customer] = {
                        'count': 0,
                        'po_numbers': [],
                        'reasons': []
                    }
                
                exception_patterns['by_customer'][customer]['count'] += 1
                exception_patterns['by_customer'][customer]['po_numbers'].append(po_number)
                exception_patterns['by_customer'][customer]['reasons'].extend(result['Reasons'])
        
        # Analyze by exception type
        for result in self.validation_results:
            if result['Status'] == 'Exception':
                for reason in result['Reasons']:
                    if "not found in master data" in reason:
                        exc_type = 'SKU_NOT_FOUND'
                    elif "exceeds" in reason and "threshold" in reason:
                        exc_type = 'PRICE_DEVIATION'
                    else:
                        exc_type = 'OTHER'
                    
                    if exc_type not in exception_patterns['by_exception_type']:
                        exception_patterns['by_exception_type'][exc_type] = 0
                    exception_patterns['by_exception_type'][exc_type] += 1
        
        # Generate root cause analysis
        for customer, data in exception_patterns['by_customer'].items():
            for reason in data['reasons']:
                if "SKU999" in reason:
                    exception_patterns['root_causes'].append(f"{customer} PO failed due to missing SKU")
                elif "exceeds" in reason:
                    exception_patterns['root_causes'].append(f"{customer} PO failed due to price deviation")
        
        return exception_patterns
    
    def generate_insights(self) -> List[str]:
        """Generate insights from analysis"""
        insights = []
        
        # Customer contribution insights
        contributions = self.analyze_customer_contributions()
        if contributions:
            # Find top contributor
            top_customer = max(contributions.items(), key=lambda x: x[1]['percentage'])
            insights.append(f"{top_customer[0]} contributed {top_customer[1]['percentage']:.0f}% of total value")
            
            # Find customers with multiple orders
            multi_order_customers = [c for c, data in contributions.items() if data['order_count'] > 1]
            if multi_order_customers:
                for customer in multi_order_customers:
                    count = contributions[customer]['order_count']
                    insights.append(f"{customer} placed {count} orders")
        
        # Exception pattern insights
        patterns = self.identify_exception_patterns()
        if patterns['by_customer']:
            for customer, data in patterns['by_customer'].items():
                if 'SKU999' in str(data['reasons']):
                    insights.append(f"{customer} PO failed due to missing SKU")
                if any("exceeds" in reason for reason in data['reasons']):
                    insights.append(f"{customer} PO failed due to price deviation")
        
        # Processing efficiency insights
        if self.summary_data:
            success_rate = self.summary_data['processing_statistics']['validation_success_rate']
            if success_rate >= 75:
                insights.append(f"High validation success rate of {success_rate:.0f}%")
            elif success_rate < 50:
                insights.append(f"Low validation success rate of {success_rate:.0f}% requires attention")
        
        self.insights = insights
        return insights
    
    def build_insights_analysis(self) -> Dict[str, Any]:
        """Build complete insights analysis engine"""
        # Generate all analysis components
        customer_contributions = self.analyze_customer_contributions()
        exception_patterns = self.identify_exception_patterns()
        insights = self.generate_insights()
        
        analysis = {
            'customer_contributions': customer_contributions,
            'exception_patterns': exception_patterns,
            'insights': insights,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def display_insights_analysis(self) -> None:
        """Display insights analysis in Kiro console"""
        print("=== INSIGHTS ANALYSIS ENGINE ===")
        print()
        
        # Generate analysis
        analysis = self.build_insights_analysis()
        
        print("💡 KEY INSIGHTS")
        for insight in analysis['insights']:
            print(f"   • {insight}")
        print()
        
        print("👥 CUSTOMER CONTRIBUTION ANALYSIS")
        contributions = analysis['customer_contributions']
        for customer, data in contributions.items():
            print(f"   • {customer}: ${data['total_value']:,.2f} ({data['percentage']:.1f}%) - {data['order_count']} orders")
        print()
        
        print("⚠️ EXCEPTION PATTERN ANALYSIS")
        patterns = analysis['exception_patterns']
        
        if patterns['by_customer']:
            print("   By Customer:")
            for customer, data in patterns['by_customer'].items():
                print(f"     • {customer}: {data['count']} exceptions ({', '.join(data['po_numbers'])})")
        
        if patterns['by_exception_type']:
            print("   By Exception Type:")
            for exc_type, count in patterns['by_exception_type'].items():
                print(f"     • {exc_type}: {count} occurrences")
        
        if patterns['root_causes']:
            print("   Root Causes:")
            for cause in patterns['root_causes']:
                print(f"     • {cause}")
        
        print()
        print(f"🕒 Analysis Generated: {analysis['analysis_timestamp']}")
        print("=== END INSIGHTS ANALYSIS ===")    

    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Create visual dashboard with key metrics"""
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        dashboard = {
            'title': 'Purchase Order Processing Dashboard',
            'metrics': {
                'total_orders': {
                    'value': self.summary_data['total_orders'],
                    'label': 'Total Orders',
                    'icon': '📋'
                },
                'validated_orders': {
                    'value': self.summary_data['validated_orders'],
                    'label': 'Validated Orders',
                    'icon': '✅'
                },
                'exceptions': {
                    'value': self.summary_data['exceptions'],
                    'label': 'Exceptions',
                    'icon': '⚠️'
                },
                'total_sales_value': {
                    'value': f"${self.summary_data['total_sales_value']:,.2f}",
                    'label': 'Total Sales Value',
                    'icon': '💰'
                }
            },
            'charts': {
                'validation_success_rate': {
                    'type': 'gauge',
                    'value': self.summary_data['processing_statistics']['validation_success_rate'],
                    'label': 'Validation Success Rate (%)',
                    'color': 'green' if self.summary_data['processing_statistics']['validation_success_rate'] >= 75 else 'orange'
                },
                'customer_contributions': {
                    'type': 'pie',
                    'data': self.analyze_customer_contributions(),
                    'label': 'Customer Contribution by Value'
                }
            },
            'generated_timestamp': datetime.now().isoformat()
        }
        
        return dashboard
    
    def display_visual_dashboard(self) -> None:
        """Display visual dashboard in Kiro's chart output interface"""
        dashboard = self.generate_executive_dashboard()
        
        print("=== EXECUTIVE VISUAL DASHBOARD ===")
        print(f"📊 {dashboard['title']}")
        print()
        
        print("🎯 KEY METRICS")
        for metric_key, metric in dashboard['metrics'].items():
            print(f"   {metric['icon']} {metric['label']}: {metric['value']}")
        print()
        
        print("📈 PERFORMANCE CHARTS")
        
        # Display validation success rate gauge
        gauge = dashboard['charts']['validation_success_rate']
        print(f"   📊 {gauge['label']}")
        print(f"      Value: {gauge['value']:.1f}%")
        print(f"      Status: {'🟢 Good' if gauge['color'] == 'green' else '🟡 Needs Attention'}")
        print()
        
        # Display customer contribution pie chart
        pie_chart = dashboard['charts']['customer_contributions']
        print(f"   🥧 {pie_chart['label']}")
        for customer, data in pie_chart['data'].items():
            print(f"      • {customer}: {data['percentage']:.1f}% (${data['total_value']:,.2f})")
        print()
        
        print(f"🕒 Dashboard Generated: {dashboard['generated_timestamp']}")
        print("=== END VISUAL DASHBOARD ===")
    
    def format_executive_report(self) -> str:
        """Format reports for executive consumption"""
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        analysis = self.build_insights_analysis()
        
        report = f"""
EXECUTIVE SUMMARY REPORT
========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PROCESSING OVERVIEW
-------------------
• Total Orders Processed: {self.summary_data['total_orders']}
• Successfully Validated: {self.summary_data['validated_orders']} ({self.summary_data['processing_statistics']['validation_success_rate']:.1f}%)
• Exceptions Handled: {self.summary_data['exceptions']} ({self.summary_data['processing_statistics']['exception_rate']:.1f}%)
• Sales Orders Created: {len(self.sales_orders)}
• Total Sales Value: ${self.summary_data['total_sales_value']:,.2f}

KEY INSIGHTS
------------"""
        
        for insight in analysis['insights']:
            report += f"\n• {insight}"
        
        report += f"""

CUSTOMER PERFORMANCE
--------------------"""
        
        contributions = analysis['customer_contributions']
        for customer, data in contributions.items():
            report += f"\n• {customer}: ${data['total_value']:,.2f} ({data['percentage']:.1f}%) - {data['order_count']} orders"
        
        if analysis['exception_patterns']['by_customer']:
            report += f"""

EXCEPTION SUMMARY
-----------------"""
            for customer, data in analysis['exception_patterns']['by_customer'].items():
                report += f"\n• {customer}: {data['count']} exceptions requiring attention"
        
        report += f"""

RECOMMENDATIONS
---------------
• Validation Success Rate: {'Excellent performance' if self.summary_data['processing_statistics']['validation_success_rate'] >= 75 else 'Review validation processes'}
• Exception Handling: {'Minimal exceptions detected' if self.summary_data['exceptions'] <= 1 else 'Multiple exceptions require process review'}
• Customer Engagement: Focus on top contributing customers for relationship management

END OF REPORT
=============
"""
        
        return report
    
    def display_console_report(self) -> None:
        """Display summary and insights in Kiro console"""
        print("=== CONSOLE SUMMARY REPORT ===")
        print()
        
        # Display comprehensive summary
        self.display_comprehensive_summary()
        print()
        
        # Display insights analysis
        self.display_insights_analysis()
        print()
        
        # Display visual dashboard
        self.display_visual_dashboard()
        print()
        
        print("=== END CONSOLE REPORT ===")
    
    def save_executive_report(self, output_dir: str = "outputs") -> str:
        """Save executive report to file"""
        os.makedirs(output_dir, exist_ok=True)
        
        report_content = self.format_executive_report()
        report_file = os.path.join(output_dir, "executive_summary_report.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_file
    
    def save_dashboard_data(self, output_dir: str = "outputs") -> str:
        """Save dashboard data to JSON file for Kiro visualization"""
        os.makedirs(output_dir, exist_ok=True)
        
        dashboard = self.generate_executive_dashboard()
        dashboard_file = os.path.join(output_dir, "executive_dashboard.json")
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2)
        
        return dashboard_file    

    def generate_one_line_executive_summary(self) -> str:
        """Generate one-line executive summary"""
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        validated = self.summary_data['validated_orders']
        total_value = self.summary_data['total_sales_value']
        exceptions = self.summary_data['exceptions']
        
        # Format value in K format
        if total_value >= 1000:
            value_str = f"${total_value/1000:.1f}K"
        else:
            value_str = f"${total_value:.0f}"
        
        # Generate summary based on data
        if exceptions == 0:
            summary = f"{validated} customer orders processed worth {value_str}; all orders validated successfully"
        elif exceptions == 1:
            summary = f"{validated} valid customer orders processed worth {value_str}; one exception auto-handled"
        else:
            summary = f"{validated} valid customer orders processed worth {value_str}; {exceptions} exceptions auto-handled"
        
        return summary
    
    def process_leadership_query(self, query: str) -> str:
        """Process natural language queries from leadership"""
        query_lower = query.lower().strip()
        
        # Handle different types of leadership queries
        if "one-line executive summary" in query_lower or "executive summary" in query_lower:
            return self.generate_one_line_executive_summary()
        elif "total orders" in query_lower or "how many orders" in query_lower:
            return f"Total orders processed: {self.summary_data.get('total_orders', 0)}"
        elif "sales value" in query_lower or "total value" in query_lower:
            value = self.summary_data.get('total_sales_value', 0)
            return f"Total sales order value: ${value:,.2f}"
        elif "exceptions" in query_lower or "problems" in query_lower:
            exceptions = self.summary_data.get('exceptions', 0)
            if exceptions == 0:
                return "No exceptions found - all orders processed successfully"
            else:
                return f"{exceptions} exceptions identified and auto-handled with email notifications"
        elif "success rate" in query_lower or "validation rate" in query_lower:
            rate = self.summary_data.get('processing_statistics', {}).get('validation_success_rate', 0)
            return f"Validation success rate: {rate:.1f}%"
        elif "top customer" in query_lower or "biggest customer" in query_lower:
            contributions = self.analyze_customer_contributions()
            if contributions:
                top_customer = max(contributions.items(), key=lambda x: x[1]['percentage'])
                return f"Top customer: {top_customer[0]} with {top_customer[1]['percentage']:.0f}% of total value"
            else:
                return "No customer data available"
        elif "insights" in query_lower or "key findings" in query_lower:
            insights = self.generate_insights()
            if insights:
                return "Key insights: " + "; ".join(insights[:3])  # Top 3 insights
            else:
                return "No specific insights identified"
        elif "dashboard" in query_lower or "metrics" in query_lower:
            return self.format_dashboard_summary()
        elif "report" in query_lower or "full summary" in query_lower:
            return self.format_executive_report()
        else:
            return self.handle_generic_leadership_query(query)
    
    def format_dashboard_summary(self) -> str:
        """Format dashboard summary for conversational response"""
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        summary = f"""Dashboard Summary:
• Orders: {self.summary_data['total_orders']} total, {self.summary_data['validated_orders']} validated
• Sales Value: ${self.summary_data['total_sales_value']:,.2f}
• Success Rate: {self.summary_data['processing_statistics']['validation_success_rate']:.1f}%
• Exceptions: {self.summary_data['exceptions']} handled"""
        
        return summary
    
    def handle_generic_leadership_query(self, query: str) -> str:
        """Handle generic queries about the processing summary"""
        if not self.summary_data:
            return "No processing data available. Please run the summary generation first."
        
        return f"""I can provide information about:
• 'Generate a one-line executive summary'
• 'How many orders were processed?'
• 'What's the total sales value?'
• 'Were there any exceptions?'
• 'What's the validation success rate?'
• 'Who is the top customer?'
• 'What are the key insights?'
• 'Show me the dashboard metrics'
• 'Generate a full report'

Current status: {self.summary_data['validated_orders']} valid orders worth ${self.summary_data['total_sales_value']:,.2f}"""
    
    def create_conversational_interface(self) -> None:
        """Create conversational interface for leadership queries"""
        print("=== LEADERSHIP CONVERSATIONAL INTERFACE ===")
        print("Ask me about order processing results and insights!")
        print("Type 'exit' to quit, 'help' for available queries")
        print()
        
        # Ensure data is loaded
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        while True:
            try:
                query = input("Leadership Query: ").strip()
                
                if query.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                elif query.lower() == 'help':
                    print("\nAvailable queries:")
                    print("• Generate a one-line executive summary")
                    print("• How many orders were processed?")
                    print("• What's the total sales value?")
                    print("• Were there any exceptions?")
                    print("• What's the validation success rate?")
                    print("• Who is the top customer?")
                    print("• What are the key insights?")
                    print("• Show me the dashboard metrics")
                    print("• Generate a full report")
                    print()
                    continue
                elif not query:
                    continue
                
                response = self.process_leadership_query(query)
                print(f"\n{response}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error processing query: {e}")
    
    def demonstrate_conversational_queries(self) -> None:
        """Demonstrate conversational query functionality"""
        print("=== CONVERSATIONAL QUERY DEMONSTRATION ===")
        print()
        
        # Ensure data is loaded
        if not self.summary_data:
            self.generate_comprehensive_summary()
        
        # Demonstrate the main query
        main_query = "Generate a one-line executive summary"
        print(f"Query: '{main_query}'")
        print("Response:")
        response = self.process_leadership_query(main_query)
        print(response)
        print()
        
        # Demonstrate other queries
        demo_queries = [
            "How many orders were processed?",
            "What's the total sales value?",
            "Were there any exceptions?",
            "Who is the top customer?",
            "What are the key insights?"
        ]
        
        for query in demo_queries:
            print(f"Query: '{query}'")
            print("Response:")
            response = self.process_leadership_query(query)
            print(response)
            print()
        
        print("=== END DEMONSTRATION ===")
    
    def run_summary_insights_agent(self) -> Dict[str, Any]:
        """Main method to run the complete Summary & Insights Agent"""
        print("=== SUMMARY & INSIGHTS AGENT ===")
        print()
        
        # Generate comprehensive summary
        print("📊 Generating comprehensive summary...")
        summary = self.generate_comprehensive_summary()
        
        # Display summary
        self.display_comprehensive_summary()
        print()
        
        # Generate and display insights
        print("💡 Generating insights analysis...")
        self.display_insights_analysis()
        print()
        
        # Display visual dashboard
        print("📈 Generating visual dashboard...")
        self.display_visual_dashboard()
        print()
        
        # Save all outputs
        print("💾 Saving reports and data...")
        summary_file = self.save_summary_data()
        report_file = self.save_executive_report()
        dashboard_file = self.save_dashboard_data()
        
        print(f"   Summary data: {summary_file}")
        print(f"   Executive report: {report_file}")
        print(f"   Dashboard data: {dashboard_file}")
        print()
        
        # Demonstrate conversational interface
        print("🗣️ Demonstrating conversational interface...")
        self.demonstrate_conversational_queries()
        
        print("=== SUMMARY & INSIGHTS AGENT COMPLETE ===")
        
        return {
            'success': True,
            'summary': summary,
            'insights': self.insights,
            'files_generated': [summary_file, report_file, dashboard_file],
            'one_line_summary': self.generate_one_line_executive_summary()
        }