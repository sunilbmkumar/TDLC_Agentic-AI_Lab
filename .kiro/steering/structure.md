# Project Structure

## Directory Organization

### Core Application
- **`main.py`**: Main orchestration entry point using advanced orchestration system
- **`setup.py`**: Setup script that creates directories and sample data
- **`requirements.txt`**: Python dependencies (primarily Flask for web UI)

### Agent System
- **`agents/`**: Individual agent implementations
  - **`po_reader/`**: Purchase Order Reader Agent - loads and validates CSV data
  - **`validation/`**: Validation Agent - validates orders against master SKU data
  - **`exception_response/`**: Exception Response Agent - generates email notifications
  - **`so_creator/`**: Sales Order Creator Agent - converts valid POs to sales orders
  - **`summary_insights/`**: Summary & Insights Agent - generates reports and analytics

### Orchestration System
- **`orchestration/`**: Agent coordination and pipeline management
  - **`orchestration_manager.py`**: Unified orchestration manager (sequential + parallel)
  - **`agent_pipeline.py`**: Sequential execution pipeline with data passing
  - **`agent_coordinator.py`**: Parallel execution coordinator with dependency management
  - **`__init__.py`**: Module initialization

### Web Interface
- **`web_ui.py`**: Flask web dashboard application
- **`start_ui.py`**: Web UI launcher script (handles setup + server start)
- **`templates/`**: Jinja2 HTML templates
  - **`base.html`**: Base template with navigation and styling
  - **`dashboard.html`**: Main dashboard with statistics overview
  - **`validation.html`**: Validation results display
  - **`sales_orders.html`**: Sales orders table view
  - **`exceptions.html`**: Exception emails display
  - **`charts.html`**: Interactive charts and visualizations

### Configuration & Data
- **`config/`**: Configuration files
  - **`orchestration_config.json`**: Orchestration settings (execution mode, dependencies, parallel groups)
  - **`agent_config.json`**: Individual agent configurations
- **`data/`**: Input data files
  - **`customer_orders.csv`**: Sample purchase orders
  - **`master_sku.csv`**: Master SKU reference data
- **`outputs/`**: Generated output files (created by agents)

### Testing
- **`test_*.py`**: Various test files
  - **`test_workflow_validation.py`**: Quick validation test
  - **`test_workflow_integration.py`**: Integration test
  - **`test_end_to_end_workflow.py`**: Comprehensive end-to-end test
  - **`test_orchestration.py`**: Orchestration system tests
  - **`demo_orchestration.py`**: Orchestration demo
  - **`test_so_creator.py`**: Sales Order Creator tests
  - **`test_summary_insights.py`**: Summary agent tests
  - **`test_email_delivery.py`**: Email delivery tests

### Utilities
- **`generate_test_data.py`**: Test data generation utility

## Agent Structure Pattern
Each agent follows a consistent structure:
```
agents/[agent_name]/
├── agent.py          # Main agent class implementation
└── [other files]     # Agent-specific resources
```

## Configuration Pattern
- **JSON-based configuration**: All settings in JSON format
- **Hierarchical config**: Orchestration config includes agent-specific settings
- **Default fallbacks**: Agents provide default configurations if files missing

## Data Flow Pattern
1. **Input**: CSV files in `data/` directory
2. **Processing**: Agents pass data through `shared_data` dictionary
3. **Output**: Results saved to `outputs/` directory
4. **Display**: Web UI reads from `outputs/` for visualization

## Execution Modes
- **Sequential Mode**: Agents run one after another via `agent_pipeline.py`
- **Coordinated Mode**: Agents run with dependency management via `agent_coordinator.py`
- **Web UI Mode**: Includes automatic setup and web dashboard launch