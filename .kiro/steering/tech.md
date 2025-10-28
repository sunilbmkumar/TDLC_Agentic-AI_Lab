# Technology Stack

## Core Technologies
- **Python 3.7+**: Primary programming language
- **Flask**: Web framework for dashboard UI
- **Standard Library**: Heavy reliance on built-in modules (csv, json, os, datetime)

## Dependencies
- **Flask >= 2.0.0**: Required for web UI dashboard
- **Standard Library Only**: Core application works without external dependencies

## Project Structure
- **Agent-Based Architecture**: Individual agents in `agents/` directory
- **Orchestration System**: Pipeline and coordination in `orchestration/`
- **Configuration-Driven**: JSON configs in `config/` directory
- **Template-Based UI**: Jinja2 templates in `templates/`

## Common Commands

### Setup & Installation
```bash
# Initial setup (creates directories and sample data)
python setup.py

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Web UI (recommended) - handles setup automatically
python start_ui.py

# Command line execution
python main.py

# Web server only
python web_ui.py
```

### Testing
```bash
# Quick validation test
python test_workflow_validation.py

# Integration test
python test_workflow_integration.py

# End-to-end test
python test_end_to_end_workflow.py

# Individual agent tests
python test_so_creator.py
python test_summary_insights.py
python test_email_delivery.py

# Orchestration tests
python test_orchestration.py
python demo_orchestration.py
```

### Data Generation
```bash
# Generate test data
python generate_test_data.py
```

## Architecture Patterns
- **Agent Pattern**: Each agent implements standard interface with execute methods
- **Pipeline Pattern**: Sequential execution with shared data passing
- **Coordination Pattern**: Parallel execution with dependency management
- **Configuration Pattern**: JSON-based configuration for orchestration and agents