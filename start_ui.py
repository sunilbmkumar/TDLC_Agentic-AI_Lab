#!/usr/bin/env python3
"""
Quick start script for PO to SO Agent Demo with Web UI
"""

import os
import subprocess
import sys
import time

def check_flask():
    """Check if Flask is installed"""
    try:
        import flask
        return True
    except ImportError:
        return False

def install_flask():
    """Install Flask if not present"""
    print("📦 Installing Flask for Web UI...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask>=2.0.0"])
        print("✅ Flask installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Flask. Please install manually: pip install Flask")
        return False

def run_setup():
    """Run setup to create sample data"""
    print("🔧 Setting up sample data...")
    try:
        subprocess.run([sys.executable, "setup.py"], check=True)
        print("✅ Setup completed!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Setup failed. Please run manually: python setup.py")
        return False

def run_workflow():
    """Run the main workflow to generate data"""
    print("🚀 Running PO to SO workflow...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
        print("✅ Workflow completed!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Workflow had issues, but continuing with UI...")
        return False

def start_web_ui():
    """Start the web UI"""
    print("🌐 Starting Web UI...")
    print("=" * 50)
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔄 The page will auto-refresh every 30 seconds")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, "web_ui.py"])
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped. Goodbye!")

def main():
    """Main function"""
    print("🚀 PO to SO Agent Demo - Web UI Launcher")
    print("=" * 50)
    
    # Check Flask installation
    if not check_flask():
        if not install_flask():
            sys.exit(1)
    
    # Run setup if no data exists
    if not os.path.exists('data/customer_orders.csv'):
        if not run_setup():
            sys.exit(1)
    
    # Run workflow if no outputs exist
    if not os.path.exists('outputs/validation_results_detailed.json'):
        print("📋 No results found. Running workflow to generate sample data...")
        run_workflow()
    
    # Start web UI
    start_web_ui()

if __name__ == "__main__":
    main()