"""
Test Data Generator for creating various test scenarios.
Generates valid orders, invalid orders, master SKU data, and scenario-based datasets.
"""

import csv
import json
import os
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal


class TestDataGenerator:
    """Generates various test data scenarios for comprehensive testing"""
    
    def __init__(self, base_output_dir: str = "test_suite/fixtures"):
        self.base_output_dir = base_output_dir
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """Ensure output directory exists"""
        os.makedirs(self.base_output_dir, exist_ok=True)
        
    def generate_valid_orders(self, count: int) -> List[Dict[str, Any]]:
        """
        Generate valid purchase orders for testing.
        
        Args:
            count: Number of valid orders to generate
            
        Returns:
            List of valid order dictionaries
        """
        valid_orders = []
        
        # Sample valid data
        customers = [
            "Acme Corporation", "Beta Industries", "Gamma LLC", "Delta Systems",
            "Echo Enterprises", "Foxtrot Solutions", "Golf Technologies", "Hotel Services"
        ]
        
        valid_skus = ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"]
        
        for i in range(count):
            order = {
                "PO_Number": f"PO{str(i+1).zfill(3)}",
                "Customer_Name": random.choice(customers),
                "SKU": random.choice(valid_skus),
                "Quantity": random.randint(1, 50),
                "Price": round(random.uniform(5.0, 100.0), 2)
            }
            valid_orders.append(order)
            
        return valid_orders
        
    def generate_invalid_orders(self, error_types: List[str]) -> List[Dict[str, Any]]:
        """
        Generate orders with specific validation errors.
        
        Args:
            error_types: List of error types to generate
                       ('invalid_sku', 'missing_customer', 'negative_quantity', 
                        'zero_quantity', 'high_price_deviation', 'missing_po_number')
                        
        Returns:
            List of invalid order dictionaries
        """
        invalid_orders = []
        
        for i, error_type in enumerate(error_types):
            base_order = {
                "PO_Number": f"PO{str(i+1).zfill(3)}",
                "Customer_Name": "Test Customer",
                "SKU": "SKU001",
                "Quantity": 10,
                "Price": 25.50
            }
            
            if error_type == 'invalid_sku':
                base_order["SKU"] = "INVALID_SKU"
                base_order["Customer_Name"] = "Invalid SKU Corp"
                
            elif error_type == 'missing_customer':
                base_order["Customer_Name"] = ""
                
            elif error_type == 'negative_quantity':
                base_order["Quantity"] = -5
                base_order["Customer_Name"] = "Negative Qty Corp"
                
            elif error_type == 'zero_quantity':
                base_order["Quantity"] = 0
                base_order["Customer_Name"] = "Zero Qty Corp"
                
            elif error_type == 'high_price_deviation':
                base_order["Price"] = 999.99  # Assuming standard price is much lower
                base_order["Customer_Name"] = "High Price Corp"
                
            elif error_type == 'missing_po_number':
                base_order["PO_Number"] = ""
                base_order["Customer_Name"] = "Missing PO Corp"
                
            invalid_orders.append(base_order)
            
        return invalid_orders
        
    def generate_master_sku_data(self, sku_list: List[str]) -> List[Dict[str, Any]]:
        """
        Generate master SKU reference data.
        
        Args:
            sku_list: List of SKU codes to generate data for
            
        Returns:
            List of master SKU dictionaries
        """
        categories = ["Electronics", "Hardware", "Software", "Accessories", "Tools"]
        
        master_sku_data = []
        
        for i, sku in enumerate(sku_list):
            sku_data = {
                "sku": sku,
                "description": f"Product {sku}",
                "standard_price": round(random.uniform(10.0, 80.0), 2),
                "category": random.choice(categories)
            }
            master_sku_data.append(sku_data)
            
        return master_sku_data
        
    def create_scenario_dataset(self, scenario: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create complete datasets for test scenarios.
        
        Args:
            scenario: Scenario name ('normal_flow', 'exception_flow', 'mixed_scenario',
                     'large_dataset', 'empty_dataset', 'performance_test')
                     
        Returns:
            Dictionary containing orders and master SKU data
        """
        if scenario == 'normal_flow':
            return self._create_normal_flow_dataset()
        elif scenario == 'exception_flow':
            return self._create_exception_flow_dataset()
        elif scenario == 'mixed_scenario':
            return self._create_mixed_scenario_dataset()
        elif scenario == 'large_dataset':
            return self._create_large_dataset()
        elif scenario == 'empty_dataset':
            return self._create_empty_dataset()
        elif scenario == 'performance_test':
            return self._create_performance_test_dataset()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
            
    def _create_normal_flow_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create dataset for normal workflow testing"""
        valid_skus = ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"]
        
        return {
            'orders': self.generate_valid_orders(10),
            'master_sku': self.generate_master_sku_data(valid_skus),
            'scenario_info': {
                'name': 'normal_flow',
                'description': 'All valid orders for normal workflow testing',
                'expected_valid_orders': 10,
                'expected_invalid_orders': 0
            }
        }
        
    def _create_exception_flow_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create dataset for exception handling testing"""
        error_types = [
            'invalid_sku', 'missing_customer', 'negative_quantity',
            'zero_quantity', 'high_price_deviation'
        ]
        
        valid_skus = ["SKU001", "SKU002", "SKU003"]
        
        return {
            'orders': self.generate_invalid_orders(error_types),
            'master_sku': self.generate_master_sku_data(valid_skus),
            'scenario_info': {
                'name': 'exception_flow',
                'description': 'All invalid orders for exception handling testing',
                'expected_valid_orders': 0,
                'expected_invalid_orders': len(error_types),
                'error_types': error_types
            }
        }
        
    def _create_mixed_scenario_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create dataset with mix of valid and invalid orders"""
        valid_orders = self.generate_valid_orders(6)
        invalid_orders = self.generate_invalid_orders(['invalid_sku', 'negative_quantity', 'missing_customer'])
        
        # Combine and shuffle orders
        all_orders = valid_orders + invalid_orders
        random.shuffle(all_orders)
        
        # Renumber PO numbers to maintain sequence
        for i, order in enumerate(all_orders):
            order["PO_Number"] = f"PO{str(i+1).zfill(3)}"
            
        valid_skus = ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"]
        
        return {
            'orders': all_orders,
            'master_sku': self.generate_master_sku_data(valid_skus),
            'scenario_info': {
                'name': 'mixed_scenario',
                'description': 'Mix of valid and invalid orders',
                'expected_valid_orders': 6,
                'expected_invalid_orders': 3,
                'total_orders': 9
            }
        }
        
    def _create_large_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create large dataset for performance testing"""
        valid_orders = self.generate_valid_orders(800)
        invalid_orders = self.generate_invalid_orders(['invalid_sku'] * 100 + ['negative_quantity'] * 100)
        
        all_orders = valid_orders + invalid_orders
        random.shuffle(all_orders)
        
        # Renumber PO numbers
        for i, order in enumerate(all_orders):
            order["PO_Number"] = f"PO{str(i+1).zfill(4)}"
            
        # Generate larger SKU master data
        valid_skus = [f"SKU{str(i).zfill(3)}" for i in range(1, 51)]  # 50 SKUs
        
        return {
            'orders': all_orders,
            'master_sku': self.generate_master_sku_data(valid_skus),
            'scenario_info': {
                'name': 'large_dataset',
                'description': 'Large dataset for performance testing',
                'expected_valid_orders': 800,
                'expected_invalid_orders': 200,
                'total_orders': 1000,
                'total_skus': 50
            }
        }
        
    def _create_empty_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create empty dataset for edge case testing"""
        return {
            'orders': [],
            'master_sku': [],
            'scenario_info': {
                'name': 'empty_dataset',
                'description': 'Empty dataset for edge case testing',
                'expected_valid_orders': 0,
                'expected_invalid_orders': 0,
                'total_orders': 0
            }
        }
        
    def _create_performance_test_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """Create dataset specifically for performance benchmarking"""
        # Create 2000 orders for stress testing
        valid_orders = self.generate_valid_orders(1800)
        invalid_orders = self.generate_invalid_orders(['invalid_sku'] * 200)
        
        all_orders = valid_orders + invalid_orders
        random.shuffle(all_orders)
        
        # Renumber PO numbers
        for i, order in enumerate(all_orders):
            order["PO_Number"] = f"PO{str(i+1).zfill(5)}"
            
        # Generate comprehensive SKU master data
        valid_skus = [f"SKU{str(i).zfill(3)}" for i in range(1, 101)]  # 100 SKUs
        
        return {
            'orders': all_orders,
            'master_sku': self.generate_master_sku_data(valid_skus),
            'scenario_info': {
                'name': 'performance_test',
                'description': 'Large dataset for performance benchmarking',
                'expected_valid_orders': 1800,
                'expected_invalid_orders': 200,
                'total_orders': 2000,
                'total_skus': 100
            }
        }
        
    def save_dataset_to_files(self, dataset: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """
        Save dataset to CSV files.
        
        Args:
            dataset: Dataset dictionary from create_scenario_dataset
            output_dir: Directory to save files
            
        Returns:
            Dictionary with file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        
        file_paths = {}
        
        # Save orders to CSV
        orders_file = os.path.join(output_dir, 'customer_orders.csv')
        if dataset['orders']:
            with open(orders_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
                writer.writeheader()
                writer.writerows(dataset['orders'])
        else:
            # Create empty file with headers
            with open(orders_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
                
        file_paths['orders_file'] = orders_file
        
        # Save master SKU to CSV
        sku_file = os.path.join(output_dir, 'master_sku.csv')
        if dataset['master_sku']:
            with open(sku_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['sku', 'description', 'standard_price', 'category'])
                writer.writeheader()
                writer.writerows(dataset['master_sku'])
        else:
            # Create empty file with headers
            with open(sku_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['sku', 'description', 'standard_price', 'category'])
                
        file_paths['sku_file'] = sku_file
        
        # Save scenario info to JSON
        info_file = os.path.join(output_dir, 'scenario_info.json')
        with open(info_file, 'w') as f:
            json.dump(dataset['scenario_info'], f, indent=2)
            
        file_paths['info_file'] = info_file
        
        return file_paths
        
    def generate_corrupted_csv(self, output_file: str, corruption_type: str = 'malformed_headers'):
        """
        Generate corrupted CSV files for error handling testing.
        
        Args:
            output_file: Path to output corrupted CSV file
            corruption_type: Type of corruption ('malformed_headers', 'missing_columns', 
                           'invalid_data_types', 'truncated_file')
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        if corruption_type == 'malformed_headers':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['PO_Number', 'Customer', 'SKU'])  # Missing required columns
                writer.writerow(['PO001', 'Test Corp', 'SKU001'])
                
        elif corruption_type == 'missing_columns':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
                writer.writerow(['PO001', 'Test Corp', 'SKU001'])  # Missing columns
                
        elif corruption_type == 'invalid_data_types':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
                writer.writerow(['PO001', 'Test Corp', 'SKU001', 'invalid_quantity', 'invalid_price'])
                
        elif corruption_type == 'truncated_file':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
                f.write('PO001,Test Corp,SKU001,10,')  # Truncated line
                
    def cleanup_generated_files(self, file_paths: List[str]):
        """
        Clean up generated test files.
        
        Args:
            file_paths: List of file paths to remove
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove file {file_path}: {e}")


class TestDataFixtures:
    """Manages test data fixtures and cleanup operations"""
    
    def __init__(self, fixtures_dir: str = "test_suite/fixtures"):
        self.fixtures_dir = fixtures_dir
        self.backup_dir = os.path.join(fixtures_dir, 'backups')
        self.active_fixtures = []
        
    def setup_test_files(self, scenario: str) -> Dict[str, str]:
        """
        Create CSV files for test scenario.
        
        Args:
            scenario: Test scenario name
            
        Returns:
            Dictionary with created file paths
        """
        generator = TestDataGenerator(self.fixtures_dir)
        dataset = generator.create_scenario_dataset(scenario)
        
        scenario_dir = os.path.join(self.fixtures_dir, scenario)
        file_paths = generator.save_dataset_to_files(dataset, scenario_dir)
        
        # Track active fixtures for cleanup
        self.active_fixtures.extend(file_paths.values())
        
        return file_paths
        
    def cleanup_test_files(self):
        """Remove test files and directories"""
        for file_path in self.active_fixtures:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove fixture file {file_path}: {e}")
                
        # Clean up empty directories
        for root, dirs, files in os.walk(self.fixtures_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Directory is empty
                        os.rmdir(dir_path)
                except Exception:
                    pass  # Ignore errors when removing directories
                    
        self.active_fixtures.clear()
        
    def backup_original_data(self):
        """Backup existing data files"""
        os.makedirs(self.backup_dir, exist_ok=True)
        
        original_data_dir = "data"
        if os.path.exists(original_data_dir):
            for filename in os.listdir(original_data_dir):
                if filename.endswith('.csv'):
                    src = os.path.join(original_data_dir, filename)
                    dst = os.path.join(self.backup_dir, f"{filename}.backup")
                    try:
                        import shutil
                        shutil.copy2(src, dst)
                    except Exception as e:
                        print(f"Warning: Could not backup {filename}: {e}")
                        
    def restore_original_data(self):
        """Restore original data files"""
        original_data_dir = "data"
        
        if os.path.exists(self.backup_dir):
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.backup'):
                    src = os.path.join(self.backup_dir, filename)
                    dst = os.path.join(original_data_dir, filename.replace('.backup', ''))
                    try:
                        import shutil
                        shutil.copy2(src, dst)
                    except Exception as e:
                        print(f"Warning: Could not restore {filename}: {e}")
                        
    def get_fixture_path(self, scenario: str, filename: str) -> str:
        """
        Get path to a fixture file.
        
        Args:
            scenario: Scenario name
            filename: File name
            
        Returns:
            Full path to fixture file
        """
        return os.path.join(self.fixtures_dir, scenario, filename)
        
    def create_temporary_fixture(self, content: str, filename: str) -> str:
        """
        Create a temporary fixture file.
        
        Args:
            content: File content
            filename: File name
            
        Returns:
            Path to created file
        """
        temp_dir = os.path.join(self.fixtures_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
            
        self.active_fixtures.append(file_path)
        return file_path