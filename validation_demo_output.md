# Validation Agent Demo Output

## Sample Data Analysis

### Customer Orders (data/customer_orders.csv):
- PO1001: ACME Corp, SKU001, Qty: 100, Price: $45.50
- PO1002: Zenith Ltd, SKU002, Qty: 75, Price: $32.00  
- PO1003: ACME Corp, SKU004, Qty: 200, Price: $28.75
- PO1004: Innova Inc, SKU999, Qty: 50, Price: $15.00

### Master SKU Data (data/master_sku.csv):
- SKU001: Industrial Widget Pro, Reference Price: $42.00
- SKU002: Premium Component X, Reference Price: $35.00
- SKU004: Standard Assembly Kit, Reference Price: $26.50
- SKU999: NOT FOUND in master data

## Expected Validation Results

### Simple JSON Output (validation_results_simple.json):
```json
[
  {"PO_Number": "PO1001", "Status": "Valid"},
  {"PO_Number": "PO1002", "Status": "Valid"},
  {"PO_Number": "PO1003", "Status": "Valid"},
  {"PO_Number": "PO1004", "Status": "Exception"}
]
```

### Validation Explanations:
- PO1001 passed validation - SKU001 exists in master data with acceptable price deviation of 8.3%
- PO1002 passed validation - SKU002 exists in master data with acceptable price deviation of 8.6%
- PO1003 passed validation - SKU004 exists in master data with acceptable price deviation of 8.5%
- PO1004 failed validation because SKU999 is not in master data

### Price Deviation Analysis:
- PO1001: Order $45.50 vs Reference $42.00 = 8.3% deviation (< 10% threshold) ✓
- PO1002: Order $32.00 vs Reference $35.00 = 8.6% deviation (< 10% threshold) ✓
- PO1003: Order $28.75 vs Reference $26.50 = 8.5% deviation (< 10% threshold) ✓
- PO1004: SKU999 not found in master data ✗

## Validation Agent Features Implemented:

✅ **Task 3.1**: Dual CSV reader for validation
- Reads customer_orders.csv and master_sku.csv
- Cross-references SKUs between datasets
- Implements price comparison with 10% deviation threshold

✅ **Task 3.2**: Validation rule engine
- SKU existence validation against master data
- Price deviation detection (>10% variance)
- Validation status determination (Valid/Exception)

✅ **Task 3.3**: JSON output generation
- Simple format: [{"PO_Number":"PO1001","Status":"Valid"}]
- Detailed format with exception reasons
- Saves results for downstream agent consumption

✅ **Task 3.4**: Kiro reasoning view
- Automatic explanations for validation results
- Displays validation logic and decision rationale
- Shows detailed validation results in reasoning interface