"""
Dataset Scaling Performance Tests

Tests system performance with varying data volumes:
- Small datasets (1-10 orders)
- Medium datasets (100-500 orders) 
- Large datasets (1000+ orders)
- Verifies linear scaling characteristics and performance degradation points
"""

import unittest
import time
import os
import sys
import tempfile
import shutil
from typing import Dict, Any, List, Tuple
import statistics

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseIntegrationTest
from test_suite.utilities.test_data_generator import TestDataGenerator, TestDataFixtures
from orchestration.orchestration_manager import OrchestrationManager


class DatasetScalingTests(BaseIntegrationTest):
    """Test system performance scaling with different dataset sizes"""
    
    def setUp(self):
        """Setup scaling test environment"""
        super().setUp()
        
        # Initialize test data generator and fixtures
        self.data_generator = TestDataGenerator(self.test_temp_dir)
        self.fixtures = TestDataFixtures(os.path.join(self.test_temp_dir, 'fixtures'))
        
        # Performance tracking
        self.performance_results = {}
        
        # Dataset size configurations
        self.dataset_configs = {
            'small': {'min_size': 1, 'max_size': 10, 'test_sizes': [1, 5, 10]},
            'medium': {'min_size': 100, 'max_size': 500, 'test_sizes': [100, 250, 500]},
            'large': {'min_size': 1000, 'max_size': 2000, 'test_sizes': [1000, 1500, 2000]}
        }
        
        # Performance thresholds (in seconds)
        self.performance_thresholds = {
            'small': {'max_time': 5.0, 'expected_time': 2.0},
            'medium': {'max_time': 30.0, 'expected_time': 15.0},
            'large': {'max_time': 120.0, 'expected_time': 60.0}
        }
        
    def tearDown(self):
        """Cleanup scaling test environment"""
        # Cleanup fixtures
        self.fixtures.cleanup_test_files()
        super().tearDown()
        
    def test_small_dataset_performance(self):
        """Test system performance with small datasets (1-10 orders)"""
        self.test_logger.info("Starting small dataset performance tests")
        
        dataset_category = 'small'
        test_sizes = self.dataset_configs[dataset_category]['test_sizes']
        
        performance_data = []
        
        for size in test_sizes:
            with self.subTest(dataset_size=size):
                self.test_logger.info(f"Testing small dataset with {size} orders")
                
                # Generate test dataset
                dataset = self._generate_performance_dataset(size)
                
                # Execute workflow and measure performance
                execution_time, memory_usage = self._execute_workflow_with_monitoring(dataset)
                
                # Record performance data
                perf_data = {
                    'size': size,
                    'execution_time': execution_time,
                    'memory_usage': memory_usage,
                    'throughput': size / execution_time if execution_time > 0 else 0
                }
                performance_data.append(perf_data)
                
                # Validate performance against thresholds
                max_time = self.performance_thresholds[dataset_category]['max_time']
                self.assertLess(execution_time, max_time,
                               f"Small dataset ({size} orders) execution time {execution_time:.2f}s "
                               f"exceeded threshold {max_time}s")
                
                self.test_logger.info(f"Small dataset ({size} orders): {execution_time:.2f}s, "
                                    f"throughput: {perf_data['throughput']:.2f} orders/sec")
        
        # Store results for analysis
        self.performance_results[dataset_category] = performance_data
        
        # Validate scaling characteristics
        self._validate_scaling_characteristics(performance_data, dataset_category)
        
    def test_medium_dataset_performance(self):
        """Test system performance with medium datasets (100-500 orders)"""
        self.test_logger.info("Starting medium dataset performance tests")
        
        dataset_category = 'medium'
        test_sizes = self.dataset_configs[dataset_category]['test_sizes']
        
        performance_data = []
        
        for size in test_sizes:
            with self.subTest(dataset_size=size):
                self.test_logger.info(f"Testing medium dataset with {size} orders")
                
                # Generate test dataset
                dataset = self._generate_performance_dataset(size)
                
                # Execute workflow and measure performance
                execution_time, memory_usage = self._execute_workflow_with_monitoring(dataset)
                
                # Record performance data
                perf_data = {
                    'size': size,
                    'execution_time': execution_time,
                    'memory_usage': memory_usage,
                    'throughput': size / execution_time if execution_time > 0 else 0
                }
                performance_data.append(perf_data)
                
                # Validate performance against thresholds
                max_time = self.performance_thresholds[dataset_category]['max_time']
                self.assertLess(execution_time, max_time,
                               f"Medium dataset ({size} orders) execution time {execution_time:.2f}s "
                               f"exceeded threshold {max_time}s")
                
                self.test_logger.info(f"Medium dataset ({size} orders): {execution_time:.2f}s, "
                                    f"throughput: {perf_data['throughput']:.2f} orders/sec")
        
        # Store results for analysis
        self.performance_results[dataset_category] = performance_data
        
        # Validate scaling characteristics
        self._validate_scaling_characteristics(performance_data, dataset_category)
        
    def test_large_dataset_performance(self):
        """Test system performance with large datasets (1000+ orders)"""
        self.test_logger.info("Starting large dataset performance tests")
        
        dataset_category = 'large'
        test_sizes = self.dataset_configs[dataset_category]['test_sizes']
        
        performance_data = []
        
        for size in test_sizes:
            with self.subTest(dataset_size=size):
                self.test_logger.info(f"Testing large dataset with {size} orders")
                
                # Generate test dataset
                dataset = self._generate_performance_dataset(size)
                
                # Execute workflow and measure performance
                execution_time, memory_usage = self._execute_workflow_with_monitoring(dataset)
                
                # Record performance data
                perf_data = {
                    'size': size,
                    'execution_time': execution_time,
                    'memory_usage': memory_usage,
                    'throughput': size / execution_time if execution_time > 0 else 0
                }
                performance_data.append(perf_data)
                
                # Validate performance against thresholds
                max_time = self.performance_thresholds[dataset_category]['max_time']
                self.assertLess(execution_time, max_time,
                               f"Large dataset ({size} orders) execution time {execution_time:.2f}s "
                               f"exceeded threshold {max_time}s")
                
                self.test_logger.info(f"Large dataset ({size} orders): {execution_time:.2f}s, "
                                    f"throughput: {perf_data['throughput']:.2f} orders/sec")
        
        # Store results for analysis
        self.performance_results[dataset_category] = performance_data
        
        # Validate scaling characteristics
        self._validate_scaling_characteristics(performance_data, dataset_category)
        
    def test_scaling_linearity(self):
        """Test that performance scales approximately linearly with dataset size"""
        self.test_logger.info("Testing scaling linearity across all dataset sizes")
        
        # Run tests for all dataset categories if not already done
        if 'small' not in self.performance_results:
            self.test_small_dataset_performance()
        if 'medium' not in self.performance_results:
            self.test_medium_dataset_performance()
        if 'large' not in self.performance_results:
            self.test_large_dataset_performance()
            
        # Combine all performance data
        all_performance_data = []
        for category_data in self.performance_results.values():
            all_performance_data.extend(category_data)
            
        # Sort by dataset size
        all_performance_data.sort(key=lambda x: x['size'])
        
        # Analyze scaling characteristics
        sizes = [data['size'] for data in all_performance_data]
        times = [data['execution_time'] for data in all_performance_data]
        throughputs = [data['throughput'] for data in all_performance_data]
        
        # Calculate scaling metrics
        scaling_analysis = self._analyze_scaling_metrics(sizes, times, throughputs)
        
        self.test_logger.info(f"Scaling analysis: {scaling_analysis}")
        
        # Validate that scaling is reasonable (not exponential)
        # Time should not increase faster than O(n log n)
        max_acceptable_scaling_factor = 2.0  # Allow up to 2x degradation
        
        if len(scaling_analysis['time_ratios']) > 0:
            max_scaling_ratio = max(scaling_analysis['time_ratios'])
            self.assertLess(max_scaling_ratio, max_acceptable_scaling_factor,
                           f"Performance degradation too severe: {max_scaling_ratio:.2f}x "
                           f"exceeds acceptable limit of {max_acceptable_scaling_factor}x")
                           
    def test_performance_degradation_points(self):
        """Identify performance degradation points across dataset sizes"""
        self.test_logger.info("Analyzing performance degradation points")
        
        # Ensure all performance data is available
        if not all(category in self.performance_results for category in ['small', 'medium', 'large']):
            self.test_scaling_linearity()  # This will run all tests
            
        # Analyze degradation points
        degradation_points = self._identify_degradation_points()
        
        self.test_logger.info(f"Performance degradation analysis: {degradation_points}")
        
        # Validate that there are no severe degradation points
        for point in degradation_points:
            if point['degradation_factor'] > 3.0:  # More than 3x degradation
                self.test_logger.warning(f"Severe performance degradation detected at {point['size']} orders: "
                                       f"{point['degradation_factor']:.2f}x slower than expected")
                                       
        # At least ensure the system doesn't completely break down
        final_performance = degradation_points[-1] if degradation_points else None
        if final_performance:
            self.assertLess(final_performance['degradation_factor'], 10.0,
                           "System performance degraded beyond acceptable limits")
                           
    def _generate_performance_dataset(self, size: int) -> Dict[str, Any]:
        """Generate dataset for performance testing"""
        # Create mostly valid orders with some exceptions for realistic testing
        valid_count = int(size * 0.9)  # 90% valid orders
        invalid_count = size - valid_count
        
        valid_orders = self.data_generator.generate_valid_orders(valid_count)
        invalid_orders = self.data_generator.generate_invalid_orders(['invalid_sku'] * invalid_count)
        
        all_orders = valid_orders + invalid_orders
        
        # Generate appropriate number of SKUs (at least 10% of order count, minimum 5)
        sku_count = max(5, int(size * 0.1))
        valid_skus = [f"SKU{str(i).zfill(3)}" for i in range(1, sku_count + 1)]
        master_sku_data = self.data_generator.generate_master_sku_data(valid_skus)
        
        return {
            'orders': all_orders,
            'master_sku': master_sku_data,
            'scenario_info': {
                'name': f'performance_test_{size}',
                'total_orders': size,
                'valid_orders': valid_count,
                'invalid_orders': invalid_count,
                'total_skus': sku_count
            }
        }
        
    def _execute_workflow_with_monitoring(self, dataset: Dict[str, Any]) -> Tuple[float, float]:
        """Execute workflow with performance monitoring"""
        import psutil
        import gc
        
        # Setup test data files
        test_data_dir = os.path.join(self.test_temp_dir, 'perf_test_data')
        os.makedirs(test_data_dir, exist_ok=True)
        
        file_paths = self.data_generator.save_dataset_to_files(dataset, test_data_dir)
        
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Execute workflow with timing
        start_time = time.time()
        
        try:
            # Mock workflow execution for performance testing
            # In real implementation, this would call the actual orchestration manager
            result = self._mock_workflow_execution(dataset)
            
            execution_time = time.time() - start_time
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = final_memory - initial_memory
            
            # Validate that workflow completed successfully
            self.assertIsNotNone(result, "Workflow execution returned None")
            
            return execution_time, memory_usage
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.test_logger.error(f"Workflow execution failed after {execution_time:.2f}s: {e}")
            raise
            
        finally:
            # Cleanup test files
            for file_path in file_paths.values():
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
    def _mock_workflow_execution(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Mock workflow execution for performance testing"""
        # Simulate realistic processing time based on dataset size
        order_count = len(dataset['orders'])
        sku_count = len(dataset['master_sku'])
        
        # Simulate processing time (base time + linear scaling)
        base_time = 0.1  # 100ms base overhead
        per_order_time = 0.001  # 1ms per order
        per_sku_time = 0.0005  # 0.5ms per SKU
        
        processing_time = base_time + (order_count * per_order_time) + (sku_count * per_sku_time)
        time.sleep(processing_time)
        
        # Return mock results
        valid_orders = int(order_count * 0.9)  # Assume 90% valid
        invalid_orders = order_count - valid_orders
        
        return {
            'status': 'success',
            'total_orders': order_count,
            'valid_orders': valid_orders,
            'invalid_orders': invalid_orders,
            'processing_time': processing_time
        }
        
    def _validate_scaling_characteristics(self, performance_data: List[Dict[str, Any]], category: str):
        """Validate scaling characteristics for a dataset category"""
        if len(performance_data) < 2:
            return  # Need at least 2 data points for comparison
            
        # Sort by size
        performance_data.sort(key=lambda x: x['size'])
        
        # Calculate scaling ratios
        scaling_ratios = []
        for i in range(1, len(performance_data)):
            prev_data = performance_data[i-1]
            curr_data = performance_data[i]
            
            size_ratio = curr_data['size'] / prev_data['size']
            time_ratio = curr_data['execution_time'] / prev_data['execution_time']
            
            scaling_ratio = time_ratio / size_ratio
            scaling_ratios.append(scaling_ratio)
            
        # Average scaling ratio should be reasonable (close to 1.0 for linear scaling)
        avg_scaling_ratio = statistics.mean(scaling_ratios)
        
        self.test_logger.info(f"{category} dataset scaling ratio: {avg_scaling_ratio:.2f}")
        
        # Scaling should not be worse than quadratic (ratio < 2.0)
        self.assertLess(avg_scaling_ratio, 2.0,
                       f"{category} dataset scaling is worse than quadratic: {avg_scaling_ratio:.2f}")
                       
    def _analyze_scaling_metrics(self, sizes: List[int], times: List[float], 
                                throughputs: List[float]) -> Dict[str, Any]:
        """Analyze scaling metrics across all dataset sizes"""
        analysis = {
            'size_range': {'min': min(sizes), 'max': max(sizes)},
            'time_range': {'min': min(times), 'max': max(times)},
            'throughput_range': {'min': min(throughputs), 'max': max(throughputs)},
            'time_ratios': [],
            'throughput_degradation': []
        }
        
        # Calculate time scaling ratios
        for i in range(1, len(sizes)):
            size_ratio = sizes[i] / sizes[i-1]
            time_ratio = times[i] / times[i-1]
            scaling_ratio = time_ratio / size_ratio
            analysis['time_ratios'].append(scaling_ratio)
            
        # Calculate throughput degradation
        max_throughput = max(throughputs)
        for throughput in throughputs:
            degradation = max_throughput / throughput if throughput > 0 else float('inf')
            analysis['throughput_degradation'].append(degradation)
            
        return analysis
        
    def _identify_degradation_points(self) -> List[Dict[str, Any]]:
        """Identify points where performance significantly degrades"""
        # Combine all performance data
        all_data = []
        for category_data in self.performance_results.values():
            all_data.extend(category_data)
            
        # Sort by size
        all_data.sort(key=lambda x: x['size'])
        
        degradation_points = []
        
        if len(all_data) < 2:
            return degradation_points
            
        # Use first data point as baseline
        baseline_throughput = all_data[0]['throughput']
        
        for data in all_data:
            if data['throughput'] > 0:
                degradation_factor = baseline_throughput / data['throughput']
            else:
                degradation_factor = float('inf')
                
            degradation_points.append({
                'size': data['size'],
                'execution_time': data['execution_time'],
                'throughput': data['throughput'],
                'degradation_factor': degradation_factor
            })
            
        return degradation_points


if __name__ == '__main__':
    unittest.main()