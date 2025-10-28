# PO to SO Agent Demo

A comprehensive agent-based system that transforms Purchase Orders (PO) into Sales Orders (SO) with validation, exception handling, and orchestration capabilities.

## 🚀 Quick Start

### Option 1: Web UI Dashboard (Recommended)

```bash
# One-command start with Web UI
python start_ui.py
```

This will:
- Install Flask if needed
- Set up sample data automatically
- Run the complete workflow
- Launch web dashboard at **http://localhost:5000**

### Option 2: Command Line Only

```bash
# 1. Setup Environment
python setup.py

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Run the complete workflow
python main.py

# 4. Check results in outputs/ folder
```

### 3. View Results

**Web Dashboard**: Open **http://localhost:5000** in your browser for:
- 📊 Interactive dashboard with statistics
- 📈 Visual charts and graphs
- 📋 Detailed data tables
- 🔄 Real-time data refresh

**File Output**: Check the `outputs/` folder for:
- `validation_results_detailed.json` - Validation results
- `sales_order_output.csv` - Generated sales orders
- `exception_emails.json` - Exception notifications
- `summary_report.json` - Executive summary

## 📋 System Requirements

- **Python**: 3.7 or higher
- **Dependencies**: Mostly standard library (see requirements.txt)
- **OS**: Windows, macOS, or Linux

## 🌐 Web Dashboard Features

### Dashboard Pages

- **📊 Dashboard** (`/`) - Main overview with key statistics and workflow status
- **✅ Validation** (`/validation`) - Detailed validation results with reasons and price deviations
- **💰 Sales Orders** (`/sales-orders`) - Generated sales orders with customer breakdowns
- **⚠️ Exceptions** (`/exceptions`) - Exception emails and delivery status
- **📈 Charts** (`/charts`) - Interactive visualizations (sales by customer, exception counts)

### Key Features

- **🔄 Auto-refresh** - Data updates every 30 seconds automatically
- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **🎨 Interactive Charts** - Powered by Chart.js for beautiful visualizations
- **⚡ Real-time Updates** - Manual refresh button for instant data updates
- **🛡️ Error Handling** - Graceful handling of missing or malformed data

## 🧪 Testing Options

### Option 1: Web UI Testing (Recommended)
```bash
# Start web dashboard and run workflow
python start_ui.py

# Then open http://localhost:5000 to see results
```

### Option 2: Quick Validation Test
```bash
python test_workflow_validation.py
```
Tests that all components are properly set up without running the full workflow.

### Option 3: Integration Test
```bash
python test_workflow_integration.py
```
Tests the complete workflow with real data processing.

### Option 4: Comprehensive End-to-End Test
```bash
python test_end_to_end_workflow.py
```
Runs all scenarios including exception handling and failure recovery.

### Option 5: Individual Agent Tests
```bash
python test_so_creator.py
python test_summary_insights.py
python test_email_delivery.py
```

### Option 6: Orchestration System Tests
```bash
python test_orchestration.py
python demo_orchestration.py
```

## 📁 Project Structure

```
├── agents/                     # Individual agent implementations
│   ├── po_reader/             # Purchase Order Reader Agent
│   ├── validation/            # Validation Agent
│   ├── exception_response/    # Exception Response Agent
│   ├── so_creator/           # Sales Order Creator Agent
│   └── summary_insights/     # Summary & Insights Agent
├── orchestration/             # Orchestration system
│   ├── agent_pipeline.py     # Sequential execution pipeline
│   ├── agent_coordinator.py  # Parallel execution coordinator
│   └── orchestration_manager.py # Unified orchestration manager
├── templates/                 # Web UI HTML templates
│   ├── base.html             # Base template with navigation
│   ├── dashboard.html        # Main dashboard page
│   ├── validation.html       # Validation results page
│   ├── sales_orders.html     # Sales orders page
│   ├── exceptions.html       # Exception emails page
│   └── charts.html           # Charts and visualizations
├── config/                   # Configuration files
├── data/                    # Input data files
├── outputs/                 # Generated output files
├── test_*.py               # Test files
├── main.py                 # Main application entry point
├── web_ui.py              # Flask web dashboard
├── start_ui.py            # Web UI launcher script
├── setup.py               # Setup script
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Execution Modes

The system supports two execution modes:

1. **Sequential Mode**: Agents run one after another
2. **Coordinated Mode**: Agents run with dependency management and parallel execution

Configure in `config/orchestration_config.json`:

```json
{
  "execution_mode": "coordinated",  // or "sequential"
  "max_parallel_agents": 2,
  "dependencies": {
    "po_reader": [],
    "validation": ["po_reader"],
    "exception_response": ["validation"],
    "so_creator": ["validation"],
    "summary_insights": ["exception_response", "so_creator"]
  }
}
```

### Web UI Configuration

The web dashboard runs on **http://localhost:5000** by default. You can modify `web_ui.py` to change:

- **Port**: Change `port=5000` to your preferred port
- **Host**: Change `host='0.0.0.0'` for network access
- **Auto-refresh**: Modify the 30-second refresh interval in templates
- **Theme**: Customize CSS in `templates/base.html`

## 📊 Sample Data

The system includes sample data for testing:

### Customer Orders (`data/customer_orders.csv`)
```csv
PO_Number,Customer_Name,SKU,Quantity,Price
PO1001,ACME Corp,SKU001,100,50.00
PO1002,Zenith Ltd,SKU002,50,100.00
PO1003,Valid Corp,SKU004,75,80.00
PO1004,Innova Inc,SKU999,25,150.00
```

### Master SKU Data (`data/master_sku.csv`)
```csv
SKU,Product_Name,Reference_Price
SKU001,Widget A,50.00
SKU002,Widget B,100.00
SKU004,Widget D,80.00
```

## 🎯 Expected Results

### Normal Flow (3 valid orders, 1 exception)
- **Valid Orders**: PO1001, PO1002, PO1003 → SO2001, SO2002, SO2003
- **Exception**: PO1004 (SKU999 not found) → Exception email generated

### Web Dashboard Display
- **📊 Dashboard**: Overview showing 4 total orders, 3 valid, 1 exception
- **✅ Validation**: Table with detailed validation results and reasons
- **💰 Sales Orders**: 3 generated sales orders with customer breakdown
- **⚠️ Exceptions**: 1 exception email for PO1004 (missing SKU)
- **📈 Charts**: Bar charts showing sales by customer and exception counts

### Output Files Generated
- `validation_results_detailed.json` - Detailed validation results
- `sales_order_output.csv` - ERP-ready sales orders
- `exception_emails.json` - Exception notifications
- `summary_report.json` - Executive summary and insights
- Chart data files for web visualization

## 🔍 Troubleshooting

### Common Issues

1. **Python not found**
   ```bash
   # Make sure Python is installed and in PATH
   python --version
   # or try
   python3 --version
   ```

2. **Flask not installed (for Web UI)**
   ```bash
   # Install Flask for web dashboard
   pip install Flask
   # or install all dependencies
   pip install -r requirements.txt
   ```

3. **Web UI not loading**
   ```bash
   # Check if Flask is running
   python start_ui.py
   # Then open http://localhost:5000 in browser
   ```

4. **File not found errors**
   ```bash
   # Run setup to create necessary files
   python setup.py
   ```

5. **Permission errors**
   ```bash
   # Make sure outputs directory is writable
   mkdir outputs
   chmod 755 outputs
   ```

6. **Web UI shows no data**
   ```bash
   # Run the workflow first to generate data
   python main.py
   # Then refresh the web page or click "Refresh Data"
   ```

### Test Sequence for Debugging

1. **Start with web UI**: `python start_ui.py` (easiest way to test everything)
2. **Or start with validation**: `python test_workflow_validation.py`
3. **Check setup**: `python setup.py`
4. **Test main workflow**: `python main.py`
5. **Check outputs**: Look in `outputs/` folder or web dashboard
6. **Run integration tests**: `python test_workflow_integration.py`

## 📈 Performance

### Sequential vs Coordinated Execution

- **Sequential**: Predictable, simple error handling, ~30-60 seconds
- **Coordinated**: Parallel execution, faster completion, ~20-40 seconds

### Resource Usage

- **Memory**: ~50-100MB for typical datasets
- **CPU**: Light usage, mostly I/O bound
- **Storage**: Minimal, generates small output files

## 🛠️ Development

### Adding New Agents

1. Create agent directory in `agents/`
2. Implement agent class with required methods
3. Update orchestration configuration
4. Add tests

### Modifying Workflow

1. Update `config/orchestration_config.json`
2. Modify dependencies as needed
3. Test with validation scripts

## 📚 Documentation

- `test_documentation.md` - Comprehensive testing documentation
- Agent-specific documentation in each agent directory
- Configuration examples in `config/` directory

## 🎉 Success Indicators

### Console Output
When everything is working correctly, you should see:

```
=== PO to SO Agent Demo - Advanced Orchestration ===
✅ Configuration validated successfully
🔄 po_reader: Loading customer orders
✅ po_reader: Completed successfully
🔄 validation: Validating orders
✅ validation: Completed successfully
🔄 exception_response: Processing exceptions
✅ exception_response: Completed successfully
🔄 so_creator: Creating sales orders
✅ so_creator: Completed successfully
🔄 summary_insights: Generating insights
✅ summary_insights: Completed successfully

🎉 Workflow execution completed!
   ✅ Completed: 5 agents
   ❌ Failed: 0 agents
   📊 Total: 5 agents
```

### Web Dashboard Success
When accessing **http://localhost:5000**, you should see:

- **📊 Dashboard**: Statistics showing 4 total orders, 3 valid, 1 exception
- **✅ Green status indicators** for all completed agents
- **📈 Interactive charts** with sales data and exception counts
- **📋 Data tables** with properly formatted validation results and sales orders
- **🔄 Auto-refresh** working every 30 seconds
- **⚠️ Exception emails** displayed with delivery status

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the validation tests to identify the problem
3. Check the `outputs/` folder for error logs
4. Review the test documentation for detailed guidance

## 🚀 Quick Commands Reference

```bash
# 🌐 Start Web UI (Recommended)
python start_ui.py

# 🔧 Setup only
python setup.py

# ⚡ Run workflow only
python main.py

# 🧪 Test validation
python test_workflow_validation.py

# 🌐 Start web server only
python web_ui.py

# 📊 View results
# Open http://localhost:5000 in browser
```

## 📞 Support

If you encounter issues:

1. **Try the Web UI first**: `python start_ui.py` - it handles most setup automatically
2. Check the troubleshooting section above
3. Run the validation tests to identify the problem
4. Check the `outputs/` folder for error logs or use the web dashboard
5. Review the test documentation for detailed guidance

---

**Happy Testing! 🚀 Access your dashboard at http://localhost:5000**