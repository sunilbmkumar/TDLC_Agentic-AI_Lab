"""
Unit tests for Agent Performance.
Tests individual agent execution times, memory usage patterns, resource constraints, and timeout handling.
"""

import unittest
import os
import sys
import time
import threading
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Try to import psutil, use fallback if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseAgentTest
from test_suite.utilities.test_data_generator import TestDataGenerator
from agents.po_reader.agent import POReaderAgent
from agents.validation.agent import ValidationAgent
from agents.exception_response.agent import ExceptionResponseAgent
from agents.so_creator.agent import SalesOrderCreatorAgent
from agents.summary_insights.agent import SummaryInsightsAgent


class TestAgentPerformance(BaseAgentTest):
    """Unit tests for individual agent performance characteristics"""
    
    def setUp(self):
        """Setup test environment for performance testing"""
        super().setUp()
        self.data_generator = TestDataGenerator(self.test_data_dir)
        self.performance_results = {}
        
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
        
    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage during function execution"""
        if HAS_PSUTIL:
            process = psutil.Process()
            
            # Get initial memory usage
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Execute function
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = final_memory - initial_memory
            execution_time = end_time - start_time
            
            return result, execution_time, memory_delta, final_memory
        else:
            # Fallback without memory measurement
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Return dummy memory values
            return result, execution_time, 0.0, 0.0
        
    def test_po_reader_performance_small_dataset(self):
        """Test PO Reader Agent performance with small dataset (1-10 orders)"""
        # Generate small dataset
        dataset = self.data_generator.create_scenario_dataset('normal_flow')
        file_paths = self.data_generator.save_dataset_to_files(dataset, self.test_data_dir)
        
        agent = POReaderAgent(data_path=file_paths['orders_file'])
        
        # Measure execution time and memory
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(agent.read_orders)
        
        # Performance assertions
        self.assertLess(exec_time, 1.0, "PO Reader should process small dataset in under 1 second")
        self.assertLess(memory_delta, 10.0, "Memory usage should be under 10MB for small dataset")
        self.assertGreater(len(result), 0, "Should successfully process orders")
        
        # Store results for comparison
        self.performance_results['po_reader_small'] = {
            'execution_time': exec_time,
            'memory_delta': memory_delta,
            'orders_processed': len(result)
        }
        
    def test_po_reader_performance_medium_dataset(self):
        """Test PO Reader Agent performance with medium dataset (100-500 orders)"""
        # Generate medium dataset
        dataset = self.data_generator.create_scenario_dataset('large_dataset')
        # Reduce to medium size for this test
        dataset['orders'] = dataset['orders'][:100]  # Take first 100 orders
        file_paths = self.data_generator.save_dataset_to_files(dataset, self.test_data_dir)
        
        agent = POReaderAgent(data_path=file_paths['orders_file'])
        
        # Measure execution time and memory
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(agent.read_orders)
        
        # Performance assertions
        self.assertLess(exec_time, 5.0, "PO Reader should process medium dataset in under 5 seconds")
        self.assertLess(memory_delta, 50.0, "Memory usage should be under 50MB for medium dataset")
        self.assertEqual(len(result), 100, "Should process all 100 orders")
        
        # Store results for comparison
        self.performance_results['po_reader_medium'] = {
            'execution_time': exec_time,
            'memory_delta': memory_delta,
            'orders_processed': len(result)
        }
        
    def test_po_reader_performance_large_dataset(self):
        """Test PO Reader Agent performance with large dataset (1000+ orders)"""
        # Generate large dataset
        dataset = self.data_generator.create_scenario_dataset('performance_test')
        file_paths = self.data_generator.save_dataset_to_files(dataset, self.test_data_dir)
        
        agent = POReaderAgent(data_path=file_paths['orders_file'])
        
        # Measure execution time and memory
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(agent.read_orders)
        
        # Performance assertions
        self.assertLess(exec_time, 15.0, "PO Reader should process large dataset in under 15 seconds")
        self.assertLess(memory_delta, 100.0, "Memory usage should be under 100MB for large dataset")
        self.assertEqual(len(result), 2000, "Should process all 2000 orders")
        
        # Store results for comparison
        self.performance_results['po_reader_large'] = {
            'execution_time': exec_time,
            'memory_delta': memory_delta,
            'orders_processed': len(result)
        }
        
    def test_validation_agent_performance_scaling(self):
        """Test Validation Agent performance scaling with different data sizes"""
        # Test with different dataset sizes
        sizes = [10, 100, 500]
        results = {}
        
        for size in sizes:
            # Generate dataset of specific size
            orders = self.data_generator.generate_valid_orders(size)
            skus = self.data_generator.generate_master_sku_data(['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'])
            
            # Create temporary files
            orders_file = os.path.join(self.test_data_dir, f'orders_{size}.csv')
            sku_file = os.path.join(self.test_data_dir, f'skus_{size}.csv')
            
            # Save test data
            import csv
            with open(orders_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
                writer.writeheader()
                writer.writerows(orders)
                
            with open(sku_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['sku', 'description', 'standard_price', 'category'])
                writer.writeheader()
                writer.writerows(skus)
            
            # Test validation agent
            agent = ValidationAgent()
            
            def run_validation():
                agent.read_customer_orders(orders_file)
                agent.read_master_skus(sku_file)
                return agent.run_validation_engine()
            
            # Measure performance
            result, exec_time, memory_delta, final_memory = self.measure_memory_usage(run_validation)
            
            results[size] = {
                'execution_time': exec_time,
                'memory_delta': memory_delta,
                'orders_processed': len(result)
            }
            
            # Performance assertions based on size
            if size == 10:
                self.assertLess(exec_time, 2.0, f"Validation should complete in under 2s for {size} orders")
            elif size == 100:
                self.assertLess(exec_time, 10.0, f"Validation should complete in under 10s for {size} orders")
            elif size == 500:
                self.assertLess(exec_time, 30.0, f"Validation should complete in under 30s for {size} orders")
                
        # Verify scaling characteristics
        self.assertLess(results[100]['execution_time'], results[500]['execution_time'], 
                       "Execution time should increase with dataset size")
        
        self.performance_results['validation_scaling'] = results
        
    def test_exception_response_agent_performance(self):
        """Test Exception Response Agent performance with various exception counts"""
        # Create test validation results with exceptions
        validation_results = []
        for i in range(50):  # 50 exceptions
            validation_results.append({
                'PO_Number': f'PO{str(i+1).zfill(3)}',
                'SKU': f'INVALID_SKU_{i}',
                'Status': 'Exception',
                'Reasons': [f'SKU INVALID_SKU_{i} not found in master data'],
                'Details': {'order_price': 25.50, 'reference_price': None}
            })
            
        # Create test file
        results_file = os.path.join(self.test_output_dir, 'validation_results_detailed.json')
        import json
        with open(results_file, 'w') as f:
            json.dump(validation_results, f)
            
        agent = ExceptionResponseAgent()
        
        def run_exception_processing():
            agent.load_validation_results(results_file)
            return agent.generate_automated_email_responses()
            
        # Measure performance
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(run_exception_processing)
        
        # Performance assertions
        self.assertLess(exec_time, 10.0, "Exception processing should complete in under 10 seconds")
        self.assertLess(memory_delta, 30.0, "Memory usage should be under 30MB")
        self.assertEqual(len(result), 50, "Should generate 50 exception emails")
        
        self.performance_results['exception_response'] = {
            'execution_time': exec_time,
            'memory_delta': memory_delta,
            'exceptions_processed': len(result)
        }
        
    def test_so_creator_agent_performance(self):
        """Test SO Creator Agent performance with various order counts"""
        # Create test validation results (all valid)
        validation_results = []
        customer_orders = []
        
        for i in range(200):  # 200 valid orders
            po_number = f'PO{str(i+1).zfill(3)}'
            validation_results.append({'PO_Number': po_number, 'Status': 'Valid'})
            customer_orders.append({
                'PO_Number': po_number,
                'Customer_Name': f'Customer_{i+1}',
                'SKU': f'SKU{str((i % 10) + 1).zfill(3)}',
                'Quantity': (i % 20) + 1,
                'Price': round((i + 1) * 1.5, 2)
            })
            
        # Create test files
        validation_file = os.path.join(self.test_output_dir, 'validation_results_simple.json')
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        
        import json
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f)
            
        import csv
        with open(orders_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writeheader()
            writer.writerows(customer_orders)
            
        agent = SalesOrderCreatorAgent()
        
        def run_so_creation():
            agent.read_validation_results(validation_file)
            agent.read_customer_orders(orders_file)
            return agent.process_validated_orders()
            
        # Measure performance
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(run_so_creation)
        
        # Performance assertions
        self.assertLess(exec_time, 15.0, "SO creation should complete in under 15 seconds")
        self.assertLess(memory_delta, 50.0, "Memory usage should be under 50MB")
        self.assertEqual(len(result), 200, "Should create 200 sales orders")
        
        self.performance_results['so_creator'] = {
            'execution_time': exec_time,
            'memory_delta': memory_delta,
            'orders_processed': len(result)
        }
        
    def test_summary_insights_agent_performance(self):
        """Test Summary Insights Agent performance with comprehensive data"""
        # Create comprehensive test data
        customer_orders = []
        validation_results = []
        sales_orders = []
        
        for i in range(100):
            po_number = f'PO{str(i+1).zfill(3)}'
            so_number = f'SO{str(i+2001).zfill(4)}'
            
            customer_orders.append({
                'PO_Number': po_number,
                'Customer_Name': f'Customer_{(i % 5) + 1}',
                'SKU': f'SKU{str((i % 10) + 1).zfill(3)}',
                'Quantity': (i % 20) + 1,
                'Price': round((i + 1) * 1.5, 2)
            })
            
            status = 'Valid' if i % 4 != 0 else 'Exception'  # 25% exceptions
            validation_results.append({'PO_Number': po_number, 'Status': status})
            
            if status == 'Valid':
                sales_orders.append({
                    'SO_Number': so_number,
                    'Customer': f'Customer_{(i % 5) + 1}',
                    'Material': f'SKU{str((i % 10) + 1).zfill(3)}',
                    'Quantity': (i % 20) + 1,
                    'Price': round((i + 1) * 1.5, 2),
                    'Total': round(((i % 20) + 1) * (i + 1) * 1.5, 2)
                })
                
        # Create test files
        orders_file = os.path.join(self.test_data_dir, 'customer_orders.csv')
        validation_file = os.path.join(self.test_output_dir, 'validation_results_detailed.json')
        sales_file = os.path.join(self.test_output_dir, 'sales_order_output.csv')
        
        # Save test data
        import csv, json
        
        with open(orders_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['PO_Number', 'Customer_Name', 'SKU', 'Quantity', 'Price'])
            writer.writeheader()
            writer.writerows(customer_orders)
            
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f)
            
        with open(sales_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['SO_Number', 'Customer', 'Material', 'Quantity', 'Price', 'Total'])
            writer.writeheader()
            writer.writerows(sales_orders)
            
        agent = SummaryInsightsAgent()
        
        def run_summary_generation():
            agent.load_customer_orders(orders_file)
            agent.load_validation_results(validation_file)
            agent.load_sales_orders(sales_file)
            return agent.generate_comprehensive_summary()
            
        # Measure performance
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(run_summary_generation)
        
        # Performance assertions
        self.assertLess(exec_time, 10.0, "Summary generation should complete in under 10 seconds")
        self.assertLess(memory_delta, 40.0, "Memory usage should be under 40MB")
        self.assertIn('total_orders', result, "Should generate comprehensive summary")
        
        self.performance_results['summary_insights'] = {
            'execution_time': exec_time,
            'memory_delta': memory_delta,
            'orders_analyzed': result['total_orders']
        }
        
    def test_agent_timeout_handling(self):
        """Test agent behavior under timeout scenarios"""
        def timeout_test_function():
            """Function that simulates long-running operation"""
            time.sleep(3)  # Simulate 3-second operation
            return "completed"
            
        def run_with_timeout(func, timeout_seconds):
            """Run function with timeout"""
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func()
                except Exception as e:
                    exception[0] = e
                    
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_seconds)
            
            if thread.is_alive():
                # Timeout occurred
                return None, "timeout"
            elif exception[0]:
                return None, str(exception[0])
            else:
                return result[0], "success"
                
        # Test with sufficient timeout
        result, status = run_with_timeout(timeout_test_function, 5.0)
        self.assertEqual(status, "success", "Should complete within sufficient timeout")
        self.assertEqual(result, "completed")
        
        # Test with insufficient timeout
        result, status = run_with_timeout(timeout_test_function, 1.0)
        self.assertEqual(status, "timeout", "Should timeout with insufficient time")
        self.assertIsNone(result)
        
    def test_agent_resource_constraints(self):
        """Test agent behavior under resource constraints"""
        # Test memory constraint simulation
        def memory_intensive_operation():
            """Simulate memory-intensive operation"""
            # Create large data structure
            large_data = []
            for i in range(10000):
                large_data.append({
                    'id': i,
                    'data': 'x' * 100,  # 100 characters per item
                    'timestamp': datetime.now().isoformat()
                })
            return len(large_data)
            
        # Measure memory usage during intensive operation
        result, exec_time, memory_delta, final_memory = self.measure_memory_usage(memory_intensive_operation)
        
        # Verify operation completed successfully
        self.assertEqual(result, 10000, "Should complete memory-intensive operation")
        self.assertGreater(memory_delta, 0, "Should show memory usage increase")
        
        # Test CPU constraint simulation
        def cpu_intensive_operation():
            """Simulate CPU-intensive operation"""
            total = 0
            for i in range(100000):
                total += i * i
            return total
            
        # Measure execution time for CPU-intensive operation
        result, exec_time = self.measure_execution_time(cpu_intensive_operation)
        
        # Verify operation completed
        self.assertGreater(result, 0, "Should complete CPU-intensive operation")
        self.assertLess(exec_time, 5.0, "Should complete within reasonable time")
        
    def test_concurrent_agent_execution(self):
        """Test performance when multiple agents run concurrently"""
        # Create test data
        dataset = self.data_generator.create_scenario_dataset('normal_flow')
        file_paths = self.data_generator.save_dataset_to_files(dataset, self.test_data_dir)
        
        def run_po_reader():
            agent = POReaderAgent(data_path=file_paths['orders_file'])
            return agent.read_orders()
            
        def run_validation():
            agent = ValidationAgent()
            agent.read_customer_orders(file_paths['orders_file'])
            agent.read_master_skus(file_paths['sku_file'])
            return agent.run_validation_engine()
            
        # Test sequential execution
        start_time = time.time()
        po_result = run_po_reader()
        validation_result = run_validation()
        sequential_time = time.time() - start_time
        
        # Test concurrent execution
        results = [None, None]
        exceptions = [None, None]
        
        def po_target():
            try:
                results[0] = run_po_reader()
            except Exception as e:
                exceptions[0] = e
                
        def validation_target():
            try:
                results[1] = run_validation()
            except Exception as e:
                exceptions[1] = e
                
        start_time = time.time()
        po_thread = threading.Thread(target=po_target)
        validation_thread = threading.Thread(target=validation_target)
        
        po_thread.start()
        validation_thread.start()
        
        po_thread.join()
        validation_thread.join()
        
        concurrent_time = time.time() - start_time
        
        # Verify both operations completed successfully
        self.assertIsNone(exceptions[0], "PO Reader should complete without errors")
        self.assertIsNone(exceptions[1], "Validation should complete without errors")
        self.assertIsNotNone(results[0], "PO Reader should return results")
        self.assertIsNotNone(results[1], "Validation should return results")
        
        # Concurrent execution should be faster than sequential
        self.assertLess(concurrent_time, sequential_time, 
                       "Concurrent execution should be faster than sequential")
        
        self.performance_results['concurrent_execution'] = {
            'sequential_time': sequential_time,
            'concurrent_time': concurrent_time,
            'improvement': (sequential_time - concurrent_time) / sequential_time * 100
        }
        
    def test_performance_regression_detection(self):
        """Test performance regression detection capabilities"""
        # Baseline performance measurement
        dataset = self.data_generator.create_scenario_dataset('normal_flow')
        file_paths = self.data_generator.save_dataset_to_files(dataset, self.test_data_dir)
        
        agent = POReaderAgent(data_path=file_paths['orders_file'])
        
        # Run multiple iterations to get baseline
        execution_times = []
        for i in range(5):
            result, exec_time = self.measure_execution_time(agent.read_orders)
            execution_times.append(exec_time)
            
        # Calculate baseline statistics
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        # Performance assertions
        self.assertLess(avg_time, 1.0, "Average execution time should be under 1 second")
        self.assertLess(max_time - min_time, 0.5, "Execution time variance should be low")
        
        # Store baseline for regression detection
        self.performance_results['baseline_performance'] = {
            'average_time': avg_time,
            'max_time': max_time,
            'min_time': min_time,
            'variance': max_time - min_time
        }
        
    def tearDown(self):
        """Cleanup and report performance results"""
        super().tearDown()
        
        # Print performance summary
        if self.performance_results:
            print("\n=== PERFORMANCE TEST RESULTS ===")
            for test_name, results in self.performance_results.items():
                print(f"\n{test_name.upper()}:")
                for metric, value in results.items():
                    if isinstance(value, float):
                        print(f"  {metric}: {value:.3f}")
                    else:
                        print(f"  {metric}: {value}")
            print("=== END PERFORMANCE RESULTS ===\n")


if __name__ == '__main__':
    unittest.main()