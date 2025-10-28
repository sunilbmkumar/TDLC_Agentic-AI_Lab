#!/usr/bin/env python3
"""
Web UI for PO to SO Agent Demo Results
Simple Flask application to display results in browser
"""

import os
import json
import csv
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

class ResultsViewer:
    """Class to handle reading and formatting results for web display"""
    
    def __init__(self, outputs_dir="outputs"):
        self.outputs_dir = outputs_dir
    
    def get_validation_results(self):
        """Get validation results from JSON file"""
        file_path = os.path.join(self.outputs_dir, "validation_results_detailed.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    
    def get_sales_orders(self):
        """Get sales orders from CSV file"""
        file_path = os.path.join(self.outputs_dir, "sales_order_output.csv")
        if os.path.exists(file_path):
            sales_orders = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields to proper types
                    try:
                        row['Quantity'] = int(row['Quantity'])
                        row['Price'] = float(row['Price'])
                        row['Total'] = float(row['Total'])
                    except (ValueError, KeyError):
                        # Keep original values if conversion fails
                        pass
                    sales_orders.append(row)
            return sales_orders
        return []
    
    def get_exception_emails(self):
        """Get exception emails from JSON file"""
        file_path = os.path.join(self.outputs_dir, "exception_emails.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return []
    
    def get_summary_report(self):
        """Get summary report from JSON file"""
        file_path = os.path.join(self.outputs_dir, "summary_report.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_po_acknowledgments(self):
        """Get PO acknowledgments from CSV file"""
        file_path = os.path.join(self.outputs_dir, "po_acknowledgments.csv")
        if os.path.exists(file_path):
            acknowledgments = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields to proper types
                    try:
                        row['Quantity_Ordered'] = int(row['Quantity_Ordered'])
                        row['Unit_Price'] = float(row['Unit_Price'])
                        row['Total_Amount'] = float(row['Total_Amount'])
                    except (ValueError, KeyError):
                        # Keep original values if conversion fails
                        pass
                    acknowledgments.append(row)
            return acknowledgments
        return []
    
    def get_acknowledgment_summary(self):
        """Get PO acknowledgment summary"""
        file_path = os.path.join(self.outputs_dir, "po_acknowledgment_summary.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

    def get_chart_data(self):
        """Get chart data for visualization"""
        charts = {}
        
        # Sales value chart
        sales_chart_path = os.path.join(self.outputs_dir, "sales_value_by_customer_chart.json")
        if os.path.exists(sales_chart_path):
            with open(sales_chart_path, 'r') as f:
                charts['sales_value'] = json.load(f)
        
        # Exception count chart
        exception_chart_path = os.path.join(self.outputs_dir, "exception_count_by_customer_chart.json")
        if os.path.exists(exception_chart_path):
            with open(exception_chart_path, 'r') as f:
                charts['exception_count'] = json.load(f)
        
        return charts
    
    def get_dashboard_summary(self):
        """Get summary statistics for dashboard"""
        validation_results = self.get_validation_results()
        sales_orders = self.get_sales_orders()
        exception_emails = self.get_exception_emails()
        acknowledgments = self.get_po_acknowledgments()
        ack_summary = self.get_acknowledgment_summary()
        
        total_orders = len(validation_results)
        valid_orders = len([r for r in validation_results if r.get('Status') == 'Valid'])
        exception_orders = total_orders - valid_orders
        try:
            total_sales_value = sum(float(so.get('Total', 0)) for so in sales_orders)
        except (ValueError, TypeError):
            total_sales_value = 0.0
        
        return {
            'total_orders': total_orders,
            'valid_orders': valid_orders,
            'exception_orders': exception_orders,
            'sales_orders_created': len(sales_orders),
            'total_sales_value': total_sales_value,
            'exception_emails_sent': len(exception_emails),
            'po_acknowledgments_generated': len(acknowledgments),
            'acknowledgment_acceptance_rate': ack_summary.get('acceptance_rate', 0),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Initialize results viewer
viewer = ResultsViewer()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    summary = viewer.get_dashboard_summary()
    return render_template('dashboard.html', summary=summary)

@app.route('/validation')
def validation_results():
    """Validation results page"""
    results = viewer.get_validation_results()
    return render_template('validation.html', results=results)

@app.route('/sales-orders')
def sales_orders():
    """Sales orders page"""
    try:
        orders = viewer.get_sales_orders()
        return render_template('sales_orders.html', orders=orders)
    except Exception as e:
        print(f"Error loading sales orders: {e}")
        return render_template('sales_orders.html', orders=[], error=str(e))

@app.route('/exceptions')
def exceptions():
    """Exception emails page"""
    emails = viewer.get_exception_emails()
    return render_template('exceptions.html', emails=emails)

@app.route('/po-acknowledgments')
def po_acknowledgments():
    """PO acknowledgments page"""
    try:
        acknowledgments = viewer.get_po_acknowledgments()
        summary = viewer.get_acknowledgment_summary()
        return render_template('po_acknowledgments.html', acknowledgments=acknowledgments, summary=summary)
    except Exception as e:
        print(f"Error loading PO acknowledgments: {e}")
        return render_template('po_acknowledgments.html', acknowledgments=[], summary={}, error=str(e))

@app.route('/charts')
def charts():
    """Charts and visualizations page"""
    chart_data = viewer.get_chart_data()
    return render_template('charts.html', charts=chart_data)

@app.route('/api/summary')
def api_summary():
    """API endpoint for summary data"""
    return jsonify(viewer.get_dashboard_summary())

@app.route('/api/validation')
def api_validation():
    """API endpoint for validation results"""
    return jsonify(viewer.get_validation_results())

@app.route('/api/sales-orders')
def api_sales_orders():
    """API endpoint for sales orders"""
    return jsonify(viewer.get_sales_orders())

@app.route('/api/exceptions')
def api_exceptions():
    """API endpoint for exception emails"""
    return jsonify(viewer.get_exception_emails())

@app.route('/api/po-acknowledgments')
def api_po_acknowledgments():
    """API endpoint for PO acknowledgments"""
    return jsonify({
        'acknowledgments': viewer.get_po_acknowledgments(),
        'summary': viewer.get_acknowledgment_summary()
    })

@app.route('/api/charts')
def api_charts():
    """API endpoint for chart data"""
    return jsonify(viewer.get_chart_data())

@app.route('/refresh')
def refresh_data():
    """Refresh data from files"""
    global viewer
    viewer = ResultsViewer()
    return jsonify({'status': 'refreshed', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Starting PO to SO Agent Demo Web UI")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔄 Run your agents first, then refresh the browser to see results")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)