# Product Overview

## PO to SO Agent Demo

A comprehensive agent-based system that transforms Purchase Orders (PO) into Sales Orders (SO) with validation, exception handling, and orchestration capabilities.

### Core Functionality
- **Purchase Order Processing**: Reads and validates customer orders from CSV data
- **Validation Engine**: Validates orders against master SKU data with price deviation checks
- **Exception Handling**: Generates email notifications for invalid orders
- **Sales Order Creation**: Converts valid POs to ERP-ready sales orders
- **Summary & Insights**: Provides executive reporting and analytics

### Key Features
- **Web Dashboard**: Interactive Flask-based UI with real-time data visualization
- **Orchestration System**: Supports both sequential and parallel agent execution
- **Error Recovery**: Graceful handling of failures with detailed logging
- **Data Pipeline**: Structured data flow between agents with shared state management

### Target Use Case
Automated order processing workflow for businesses that need to:
- Transform purchase orders into sales orders
- Validate order data against master records
- Handle exceptions with automated notifications
- Generate executive summaries and insights