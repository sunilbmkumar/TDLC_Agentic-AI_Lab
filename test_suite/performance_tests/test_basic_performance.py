"""
Basic Performance Test (No External Dependencies)

Simple performance test that validates the test structure and basic functionality
without requiring external dependencies like psutil.
"""

import unittest
import time
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseIntegrationTest
from test_suite.utilities.test_data_generator import TestDataGenerator


class BasicPerformanceTests(BaseIntegrationTest):
    """Basic performance tests without external dependencies"""
    
    def setUp(self):
        """Setup basic performance test environment"""
        super().setUp()
        self.data_generator = TestDataGenerator(self.test_temp_dir)
        
    def test_basic_dataset_generation(self):
        """Test that dataset generation works correctly"""
        self.test_logger.info("Testing basic dataset generation")
        
        # Test different dataset sizes
        test_sizes = [10, 50, 100]
        
        for size in test_sizes:
            with self.subTest(dataset_size=size):
                # Generate test dataset
                dataset = self._generate_test_dataset(size)
                
                # Validate dataset structure
                self.assertIn('orders', dataset)
                self.assertIn('master_sku', dataset)
                self.assertIn('scenario_info', dataset)
                
                # Validate dataset size
                self.assertEqual(len(dataset['orders']), size)
                self.assertGreater(len(dataset['master_sku']), 0)
                
                # Validate scenario info
                scenario_info = dataset['scenario_info']
                self.assertEqual(scenario_info['total_orders'], size)
                
                self.test_logger.info(f"Dataset generation successful for {size} orders")
                
    def test_basic_execution_timing(self):
        """Test basic execution timing without external monitoring"""
        self.test_logger.info("Testing basic execution timing")
        
        test_sizes = [10, 50, 100]
        execution_times = []
        
        for size in test_sizes:
            with self.subTest(dataset_size=size):
                # Generate test dataset
                dataset = self._generate_test_dataset(size)
                
                # Measure execution time
                start_time = time.time()
                result = self._mock_workflow_execution(dataset)
                execution_time = time.time() - start_time
                
                execution_times.append({
                    'size': size,
                    'time': execution_time,
                    'throughput': size / execution_time if execution_time > 0 else 0
                })
                
                # Basic validation
                self.assertIsNotNone(result)
                self.assertGreater(execution_time, 0)
                
                self.test_logger.info(f"Execution time for {size} orders: {execution_time:.4f}s")
                
        # Validate that execution time scales reasonably
        if len(execution_times) >= 2:
            # Check that larger datasets don't take exponentially longer
            first_time = execution_times[0]['time']
            last_time = execution_times[-1]['time']
            size_ratio = execution_times[-1]['size'] / execution_times[0]['size']
            time_ratio = last_time / first_time if first_time > 0 else 1
            
            # Time should not increase faster than size squared
            self.assertLess(time_ratio, size_ratio ** 2,
                           f"Execution time scaling too poor: {time_ratio:.2f}x time for {size_ratio:.2f}x data")
                           
    def test_basic_resource_cleanup(self):
        """Test basic resource cleanup without external monitoring"""
        self.test_logger.info("Testing basic resource cleanup")
        
        # Track temporary files created
        initial_temp_files = len(os.listdir(self.test_temp_dir))
        
        # Generate and process multiple datasets
        for i in range(3):
            dataset = self._generate_test_dataset(20)
            result = self._mock_workflow_execution(dataset)
            
            # Simulate some temporary file creation and cleanup
            temp_file = os.path.join(self.test_temp_dir, f'temp_test_{i}.txt')
            with open(temp_file, 'w') as f:
                f.write(f"Temporary data {i}")
                
            # Cleanup
            os.remove(temp_file)
            
        # Verify no extra files remain
        final_temp_files = len(os.listdir(self.test_temp_dir))
        
        # Should be same or fewer files (allowing for test framework files)
        self.assertLessEqual(final_temp_files, initial_temp_files + 5,
                            "Too many temporary files remain after cleanup")
                            
        self.test_logger.info(f"Resource cleanup test passed: {initial_temp_files} -> {final_temp_files} files")
        
    def test_concurrent_execution_basic(self):
        """Test basic concurrent execution without external monitoring"""
        self.test_logger.info("Testing basic concurrent execution")
        
        import concurrent.futures
        
        # Prepare datasets for concurrent execution
        datasets = []
        for i in range(3):
            dataset = self._generate_test_dataset(30)
            datasets.append(dataset)
            
        # Execute concurrently
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i, dataset in enumerate(datasets):
                future = executor.submit(self._mock_workflow_execution_with_id, dataset, i)
                futures.append(future)
                
            # Collect results
            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                
        total_time = time.time() - start_time
        
        # Validate results
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIn('workflow_id', result)
            self.assertIn('status', result)
            
        # Concurrent execution should be faster than sequential
        # (This is a basic check - real performance tests would be more sophisticated)
        expected_sequential_time = sum(0.1 for _ in datasets)  # Rough estimate
        self.assertLess(total_time, expected_sequential_time * 1.5,
                       f"Concurrent execution not showing expected performance benefit")
                       
        self.test_logger.info(f"Concurrent execution completed in {total_time:.4f}s")
        
    def _generate_test_dataset(self, size: int):
        """Generate test dataset for performance testing"""
        valid_count = int(size * 0.8)
        invalid_count = size - valid_count
        
        valid_orders = self.data_generator.generate_valid_orders(valid_count)
        invalid_orders = self.data_generator.generate_invalid_orders(['invalid_sku'] * invalid_count)
        
        all_orders = valid_orders + invalid_orders
        
        sku_count = max(5, int(size * 0.2))
        valid_skus = [f"SKU{str(i).zfill(3)}" for i in range(1, sku_count + 1)]
        master_sku_data = self.data_generator.generate_master_sku_data(valid_skus)
        
        return {
            'orders': all_orders,
            'master_sku': master_sku_data,
            'scenario_info': {
                'name': f'basic_test_{size}',
                'total_orders': size,
                'valid_orders': valid_count,
                'invalid_orders': invalid_count,
                'total_skus': sku_count
            }
        }
        
    def _mock_workflow_execution(self, dataset):
        """Mock workflow execution for basic testing"""
        order_count = len(dataset['orders'])
        
        # Simulate realistic processing time
        base_time = 0.01
        per_order_time = 0.001
        processing_time = base_time + (order_count * per_order_time)
        
        time.sleep(processing_time)
        
        return {
            'status': 'success',
            'processed_orders': order_count,
            'processing_time': processing_time
        }
        
    def _mock_workflow_execution_with_id(self, dataset, workflow_id):
        """Mock workflow execution with ID for concurrent testing"""
        result = self._mock_workflow_execution(dataset)
        result['workflow_id'] = workflow_id
        return result


if __name__ == '__main__':
    unittest.main()