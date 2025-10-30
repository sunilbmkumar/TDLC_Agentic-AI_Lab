# Unit Tests for Agent System

This directory contains comprehensive unit tests for all agents in the PO to SO transformation system.

## Test Files

### Core Agent Tests
- **`test_po_reader_agent.py`** - Tests for PO Reader Agent
  - CSV file reading and parsing
  - Data validation and error handling
  - Natural language query processing
  - Summary statistics generation

- **`test_validation_agent.py`** - Tests for Validation Agent
  - SKU existence validation
  - Price deviation detection
  - Validation result generation
  - Cross-referencing logic

- **`test_exception_response_agent.py`** - Tests for Exception Response Agent
  - Email template generation
  - Delivery simulation
  - Audit trail creation
  - Leadership query processing

- **`test_so_creator_agent.py`** - Tests for Sales Order Creator Agent
  - PO to SO transformation
  - CSV output generation
  - Chart data creation
  - Format validation

- **`test_summary_insights_agent.py`** - Tests for Summary Insights Agent
  - Comprehensive summary generation
  - Customer contribution analysis
  - Executive dashboard creation
  - Report formatting

### Performance Tests
- **`test_agent_performance.py`** - Performance and scalability tests
  - Execution time measurement
  - Memory usage monitoring (when psutil available)
  - Resource constraint testing
  - Concurrent execution testing

### Infrastructure Tests
- **`test_example.py`** - Example test demonstrating infrastructure
  - Base test class usage
  - Test data generation
  - Environment isolation

## Test Coverage

### PO Reader Agent (22 tests)
- ✅ Valid CSV file reading
- ✅ Missing file handling
- ✅ Malformed data handling
- ✅ Header validation
- ✅ Data type conversion
- ✅ Natural language queries
- ✅ Summary statistics
- ✅ Large file handling
- ✅ Permission error handling

### Validation Agent (25 tests)
- ✅ Customer order loading
- ✅ Master SKU loading
- ✅ SKU existence validation
- ✅ Price deviation calculation
- ✅ Validation result generation
- ✅ JSON output formatting
- ✅ Cross-referencing logic
- ✅ Complete workflow testing

### Exception Response Agent (28 tests)
- ✅ Validation result loading
- ✅ Exception detection
- ✅ Email template generation
- ✅ Delivery simulation
- ✅ Audit trail creation
- ✅ Leadership queries
- ✅ Statistics generation
- ✅ Complete workflow testing

### SO Creator Agent (25 tests)
- ✅ Validation result processing
- ✅ Order data filtering
- ✅ PO to SO transformation
- ✅ CSV output generation
- ✅ Format validation
- ✅ Chart data generation
- ✅ Performance calculations
- ✅ Complete workflow testing

### Summary Insights Agent (30 tests)
- ✅ Data loading from multiple sources
- ✅ Comprehensive summary generation
- ✅ Customer contribution analysis
- ✅ Exception pattern identification
- ✅ Executive dashboard creation
- ✅ Report formatting
- ✅ Leadership query processing
- ✅ Complete workflow testing

### Performance Tests (12 tests)
- ✅ Small dataset performance
- ✅ Medium dataset performance
- ✅ Large dataset performance
- ✅ Scaling characteristics
- ✅ Memory usage patterns
- ✅ Timeout handling
- ✅ Resource constraints
- ✅ Concurrent execution
- ✅ Regression detection

## Running Tests

### Run All Unit Tests
```bash
python test_suite/run_unit_tests.py
```

### Run Specific Test Module
```bash
python -m unittest test_suite.unit_tests.test_po_reader_agent -v
```

### Run Individual Test
```bash
python -m unittest test_suite.unit_tests.test_po_reader_agent.TestPOReaderAgent.test_read_valid_orders_success -v
```

## Test Infrastructure

### Base Test Classes
- **`BaseAgentTest`** - Common setup/teardown for agent tests
- **`BaseIntegrationTest`** - Workflow testing utilities

### Test Data Generation
- **`TestDataGenerator`** - Creates various test scenarios
- **`TestDataFixtures`** - Manages test data files

### Test Utilities
- Isolated test environments
- Automatic cleanup
- Mock data generation
- Performance measurement
- Error simulation

## Test Scenarios

### Data Scenarios
- **Valid Data** - All orders pass validation
- **Invalid Data** - Orders with various validation errors
- **Mixed Data** - Combination of valid and invalid orders
- **Empty Data** - Edge case with no orders
- **Large Data** - Performance testing with 1000+ orders

### Error Scenarios
- Missing files
- Corrupted data
- Permission errors
- Network timeouts
- Resource constraints
- Invalid formats

### Performance Scenarios
- Small datasets (1-10 orders)
- Medium datasets (100-500 orders)
- Large datasets (1000+ orders)
- Concurrent execution
- Memory constraints
- Timeout conditions

## Dependencies

### Required
- Python 3.7+
- Standard library modules

### Optional
- `psutil` - For detailed memory usage monitoring in performance tests

## Notes

- Tests use temporary directories for isolation
- All test data is automatically generated
- Performance tests adapt based on available system resources
- Tests are designed to run without external dependencies
- Mock objects are used to simulate external services