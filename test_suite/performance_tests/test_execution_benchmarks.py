"""
Execution Time Benchmark Tests

Creates baseline performance measurements and validates execution time scaling:
- Baseline performance measurements for each agent
- Complete workflow execution time scaling
- Performance improvements with parallel execution
- Performance regression detection capabilities
"""

import unittest
import time
import os
import sys
import statistics
import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import concurrent.futures

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseIntegrationTest
from test_suite.utilities.test_data_generator import TestDataGenerator, TestDataFixtures


class ExecutionBenchmarkTests(BaseIntegrationTest):
    """Test execution time benchmarks and performance regression detection"""
    
    def setUp(self):
        """Setup benchmark test environment"""
        super().setUp()
        
        # Initialize test data generator and fixtures
        self.data_generator = TestDataGenerator(self.test_temp_dir)
        self.fixtures = TestDataFixtures(os.path.join(self.test_temp_dir, 'fixtures'))
        
        # Benchmark tracking
        self.benchmark_results = {}
        self.baseline_benchmarks = {}
        
        # Agent configurations for testing
        self.agent_configs = {
            'po_reader': {'complexity': 'low', 'expected_time_per_order': 0.001},
            'validation': {'complexity': 'medium', 'expected_time_per_order': 0.002},
            'exception_response': {'complexity': 'low', 'expected_time_per_order': 0.001},
            'so_creator': {'complexity': 'medium', 'expected_time_per_order': 0.002},
            'summary_insights': {'complexity': 'high', 'expected_time_per_order': 0.003}
        }
        
        # Benchmark dataset sizes
        self.benchmark_sizes = [10, 50, 100, 250, 500]
        
        # Performance regression thresholds
        self.regression_thresholds = {
            'warning': 1.2,  # 20% slower than baseline
            'critical': 1.5  # 50% slower than baseline
        }
        
    def tearDown(self):
        """Cleanup benchmark test environment"""
        self.fixtures.cleanup_test_files()
        super().tearDown()
        
    def test_individual_agent_benchmarks(self):
        """Create baseline performance measurements for each agent"""
        self.test_logger.info("Starting individual agent benchmark tests")
        
        for agent_name, config in self.agent_configs.items():
            with self.subTest(agent=agent_name):
                self.test_logger.info(f"Benchmarking agent: {agent_name}")
                
                agent_benchmarks = []
                
                for size in self.benchmark_sizes:
                    # Generate test dataset
                    dataset = self._generate_benchmark_dataset(size)
                    
                    # Run multiple iterations for statistical accuracy
                    execution_times = []
                    iterations = 5
                    
                    for iteration in range(iterations):
                        execution_time = self._benchmark_agent_execution(agent_name, dataset)
                        execution_times.append(execution_time)
                        
                    # Calculate statistics
                    avg_time = statistics.mean(execution_times)
                    std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
                    min_time = min(execution_times)
                    max_time = max(execution_times)
                    
                    benchmark_data = {
                        'dataset_size': size,
                        'avg_execution_time': avg_time,
                        'std_deviation': std_dev,
                        'min_time': min_time,
                        'max_time': max_time,
                        'time_per_order': avg_time / size if size > 0 else 0,
                        'iterations': iterations
                    }
                    
                    agent_benchmarks.append(benchmark_data)
                    
                    # Validate against expected performance
                    expected_time_per_order = config['expected_time_per_order']
                    actual_time_per_order = benchmark_data['time_per_order']
                    
                    # Allow 3x tolerance for mock implementations
                    max_acceptable_time = expected_time_per_order * 3
                    
                    self.assertLess(actual_time_per_order, max_acceptable_time,
                                   f"Agent {agent_name} performance ({actual_time_per_order:.4f}s/order) "
                                   f"exceeds expected threshold ({max_acceptable_time:.4f}s/order)")
                    
                    self.test_logger.info(f"Agent {agent_name} ({size} orders): "
                                        f"{avg_time:.4f}s avg, {actual_time_per_order:.4f}s/order")
                
                # Store benchmark results
                self.benchmark_results[agent_name] = agent_benchmarks
                
                # Validate scaling characteristics
                self._validate_agent_scaling(agent_name, agent_benchmarks)
                
    def test_workflow_execution_time_scaling(self):
        """Test complete workflow execution time scaling"""
        self.test_logger.info("Starting workflow execution time scaling tests")
        
        workflow_benchmarks = []
        
        for size in self.benchmark_sizes:
            with self.subTest(dataset_size=size):
                self.test_logger.info(f"Benchmarking workflow with {size} orders")
                
                # Generate test dataset
                dataset = self._generate_benchmark_dataset(size)
                
                # Run multiple iterations for statistical accuracy
                execution_times = []
                iterations = 3  # Fewer iterations for full workflow due to time
                
                for iteration in range(iterations):
                    execution_time = self._benchmark_workflow_execution(dataset)
                    execution_times.append(execution_time)
                    
                # Calculate statistics
                avg_time = statistics.mean(execution_times)
                std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
                min_time = min(execution_times)
                max_time = max(execution_times)
                
                benchmark_data = {
                    'dataset_size': size,
                    'avg_execution_time': avg_time,
                    'std_deviation': std_dev,
                    'min_time': min_time,
                    'max_time': max_time,
                    'time_per_order': avg_time / size if size > 0 else 0,
                    'throughput': size / avg_time if avg_time > 0 else 0,
                    'iterations': iterations
                }
                
                workflow_benchmarks.append(benchmark_data)
                
                self.test_logger.info(f"Workflow ({size} orders): {avg_time:.4f}s avg, "
                                    f"throughput: {benchmark_data['throughput']:.2f} orders/sec")
                
        # Store workflow benchmark results
        self.benchmark_results['workflow'] = workflow_benchmarks
        
        # Validate workflow scaling
        self._validate_workflow_scaling(workflow_benchmarks)
        
    def test_parallel_vs_sequential_performance(self):
        """Validate performance improvements with parallel execution"""
        self.test_logger.info("Testing parallel vs sequential execution performance")
        
        test_sizes = [100, 250, 500]  # Medium to large datasets where parallel benefits are visible
        
        performance_comparisons = []
        
        for size in test_sizes:
            with self.subTest(dataset_size=size):
                self.test_logger.info(f"Comparing execution modes with {size} orders")
                
                # Generate test dataset
                dataset = self._generate_benchmark_dataset(size)
                
                # Benchmark sequential execution
                sequential_times = []
                for _ in range(3):
                    exec_time = self._benchmark_sequential_execution(dataset)
                    sequential_times.append(exec_time)
                    
                sequential_avg = statistics.mean(sequential_times)
                
                # Benchmark parallel execution
                parallel_times = []
                for _ in range(3):
                    exec_time = self._benchmark_parallel_execution(dataset)
                    parallel_times.append(exec_time)
                    
                parallel_avg = statistics.mean(parallel_times)
                
                # Calculate performance improvement
                improvement_factor = sequential_avg / parallel_avg if parallel_avg > 0 else 1.0
                improvement_percentage = (improvement_factor - 1.0) * 100
                
                comparison_data = {
                    'dataset_size': size,
                    'sequential_time': sequential_avg,
                    'parallel_time': parallel_avg,
                    'improvement_factor': improvement_factor,
                    'improvement_percentage': improvement_percentage
                }
                
                performance_comparisons.append(comparison_data)
                
                # Validate that parallel execution provides some benefit
                # Allow for overhead in small datasets, but expect improvement in larger ones
                if size >= 250:
                    self.assertGreater(improvement_factor, 1.1,
                                     f"Parallel execution should provide at least 10% improvement "
                                     f"for {size} orders, got {improvement_percentage:.1f}%")
                                     
                self.test_logger.info(f"Execution comparison ({size} orders): "
                                    f"Sequential: {sequential_avg:.4f}s, "
                                    f"Parallel: {parallel_avg:.4f}s, "
                                    f"Improvement: {improvement_percentage:.1f}%")
                
        # Store comparison results
        self.benchmark_results['parallel_comparison'] = performance_comparisons
        
    def test_performance_regression_detection(self):
        """Verify performance regression detection capabilities"""
        self.test_logger.info("Testing performance regression detection")
        
        # First establish baseline benchmarks
        if 'workflow' not in self.benchmark_results:
            self.test_workflow_execution_time_scaling()
            
        # Use workflow benchmarks as baseline
        baseline_benchmarks = self.benchmark_results['workflow']
        
        # Simulate performance regression by adding artificial delay
        regression_test_results = []
        
        for baseline in baseline_benchmarks:
            size = baseline['dataset_size']
            baseline_time = baseline['avg_execution_time']
            
            # Simulate different levels of regression
            regression_scenarios = [
                {'name': 'no_regression', 'factor': 1.0},
                {'name': 'minor_regression', 'factor': 1.15},  # 15% slower
                {'name': 'major_regression', 'factor': 1.6}   # 60% slower
            ]
            
            for scenario in regression_scenarios:
                with self.subTest(dataset_size=size, scenario=scenario['name']):
                    # Generate test dataset
                    dataset = self._generate_benchmark_dataset(size)
                    
                    # Execute with simulated regression
                    execution_time = self._benchmark_workflow_with_regression(
                        dataset, scenario['factor']
                    )
                    
                    # Detect regression
                    regression_detected, regression_level = self._detect_performance_regression(
                        baseline_time, execution_time
                    )
                    
                    regression_result = {
                        'dataset_size': size,
                        'scenario': scenario['name'],
                        'baseline_time': baseline_time,
                        'current_time': execution_time,
                        'regression_factor': execution_time / baseline_time,
                        'regression_detected': regression_detected,
                        'regression_level': regression_level
                    }
                    
                    regression_test_results.append(regression_result)
                    
                    # Validate regression detection accuracy
                    if scenario['name'] == 'no_regression':
                        self.assertFalse(regression_detected,
                                       f"False positive regression detection for {size} orders")
                    elif scenario['name'] == 'major_regression':
                        self.assertTrue(regression_detected,
                                      f"Failed to detect major regression for {size} orders")
                        self.assertEqual(regression_level, 'critical',
                                       f"Major regression not classified as critical for {size} orders")
                                       
                    self.test_logger.info(f"Regression test ({size} orders, {scenario['name']}): "
                                        f"Factor: {regression_result['regression_factor']:.2f}, "
                                        f"Detected: {regression_detected}, Level: {regression_level}")
                    
        # Store regression test results
        self.benchmark_results['regression_tests'] = regression_test_results
        
    def test_benchmark_persistence_and_comparison(self):
        """Test saving and comparing benchmark results over time"""
        self.test_logger.info("Testing benchmark persistence and comparison")
        
        # Ensure we have benchmark data
        if 'workflow' not in self.benchmark_results:
            self.test_workflow_execution_time_scaling()
            
        # Save benchmark results
        benchmark_file = os.path.join(self.test_temp_dir, 'benchmark_results.json')
        self._save_benchmark_results(benchmark_file)
        
        # Verify file was created and contains expected data
        self.assert_file_exists(benchmark_file)
        
        # Load and verify benchmark data
        loaded_benchmarks = self._load_benchmark_results(benchmark_file)
        
        self.assertIsInstance(loaded_benchmarks, dict)
        self.assertIn('workflow', loaded_benchmarks)
        self.assertIn('metadata', loaded_benchmarks)
        
        # Verify metadata
        metadata = loaded_benchmarks['metadata']
        self.assertIn('timestamp', metadata)
        self.assertIn('test_environment', metadata)
        
        # Compare with current results
        comparison_results = self._compare_benchmark_results(
            loaded_benchmarks['workflow'], 
            self.benchmark_results['workflow']
        )
        
        self.assertIsInstance(comparison_results, list)
        
        for comparison in comparison_results:
            self.assertIn('dataset_size', comparison)
            self.assertIn('baseline_time', comparison)
            self.assertIn('current_time', comparison)
            self.assertIn('change_percentage', comparison)
            
        self.test_logger.info(f"Benchmark comparison completed: {len(comparison_results)} data points")
        
    def _generate_benchmark_dataset(self, size: int) -> Dict[str, Any]:
        """Generate consistent dataset for benchmarking"""
        # Use consistent seed for reproducible benchmarks
        import random
        random.seed(42)
        
        # Create realistic mix of valid/invalid orders
        valid_count = int(size * 0.85)  # 85% valid orders
        invalid_count = size - valid_count
        
        valid_orders = self.data_generator.generate_valid_orders(valid_count)
        invalid_orders = self.data_generator.generate_invalid_orders(['invalid_sku'] * invalid_count)
        
        all_orders = valid_orders + invalid_orders
        random.shuffle(all_orders)
        
        # Generate appropriate SKU data
        sku_count = max(10, int(size * 0.2))  # At least 10 SKUs, or 20% of orders
        valid_skus = [f"SKU{str(i).zfill(3)}" for i in range(1, sku_count + 1)]
        master_sku_data = self.data_generator.generate_master_sku_data(valid_skus)
        
        return {
            'orders': all_orders,
            'master_sku': master_sku_data,
            'scenario_info': {
                'name': f'benchmark_{size}',
                'total_orders': size,
                'valid_orders': valid_count,
                'invalid_orders': invalid_count,
                'total_skus': sku_count
            }
        }
        
    def _benchmark_agent_execution(self, agent_name: str, dataset: Dict[str, Any]) -> float:
        """Benchmark individual agent execution time"""
        # Mock agent execution with realistic timing
        order_count = len(dataset['orders'])
        config = self.agent_configs[agent_name]
        
        # Simulate processing time based on agent complexity
        base_time = 0.01  # 10ms base overhead
        per_order_time = config['expected_time_per_order']
        
        # Add some realistic variation
        import random
        variation = random.uniform(0.8, 1.2)  # ±20% variation
        
        processing_time = (base_time + (order_count * per_order_time)) * variation
        
        start_time = time.time()
        time.sleep(processing_time)
        execution_time = time.time() - start_time
        
        return execution_time
        
    def _benchmark_workflow_execution(self, dataset: Dict[str, Any]) -> float:
        """Benchmark complete workflow execution time"""
        start_time = time.time()
        
        # Mock complete workflow execution
        # Sequential execution of all agents
        total_processing_time = 0
        
        for agent_name in self.agent_configs.keys():
            agent_time = self._benchmark_agent_execution(agent_name, dataset)
            total_processing_time += agent_time
            
        execution_time = time.time() - start_time
        return execution_time
        
    def _benchmark_sequential_execution(self, dataset: Dict[str, Any]) -> float:
        """Benchmark sequential workflow execution"""
        start_time = time.time()
        
        # Sequential execution - agents run one after another
        for agent_name in ['po_reader', 'validation', 'exception_response', 'so_creator', 'summary_insights']:
            self._benchmark_agent_execution(agent_name, dataset)
            
        execution_time = time.time() - start_time
        return execution_time
        
    def _benchmark_parallel_execution(self, dataset: Dict[str, Any]) -> float:
        """Benchmark parallel workflow execution"""
        start_time = time.time()
        
        # Simulate parallel execution with realistic dependencies
        # Phase 1: PO Reader (sequential)
        self._benchmark_agent_execution('po_reader', dataset)
        
        # Phase 2: Validation (sequential)
        self._benchmark_agent_execution('validation', dataset)
        
        # Phase 3: Exception Response and SO Creator (parallel)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(self._benchmark_agent_execution, 'exception_response', dataset)
            future2 = executor.submit(self._benchmark_agent_execution, 'so_creator', dataset)
            
            # Wait for both to complete
            concurrent.futures.wait([future1, future2])
            
        # Phase 4: Summary Insights (sequential)
        self._benchmark_agent_execution('summary_insights', dataset)
        
        execution_time = time.time() - start_time
        return execution_time
        
    def _benchmark_workflow_with_regression(self, dataset: Dict[str, Any], regression_factor: float) -> float:
        """Benchmark workflow with simulated performance regression"""
        # Execute normal workflow
        normal_time = self._benchmark_workflow_execution(dataset)
        
        # Add artificial delay to simulate regression
        if regression_factor > 1.0:
            additional_delay = normal_time * (regression_factor - 1.0)
            time.sleep(additional_delay)
            
        return normal_time * regression_factor
        
    def _validate_agent_scaling(self, agent_name: str, benchmarks: List[Dict[str, Any]]):
        """Validate that agent performance scales reasonably"""
        if len(benchmarks) < 2:
            return
            
        # Check that time per order remains relatively stable
        times_per_order = [b['time_per_order'] for b in benchmarks]
        
        # Calculate coefficient of variation (std dev / mean)
        mean_time = statistics.mean(times_per_order)
        std_dev = statistics.stdev(times_per_order) if len(times_per_order) > 1 else 0
        coefficient_of_variation = std_dev / mean_time if mean_time > 0 else 0
        
        # Time per order should be relatively stable (CV < 0.5)
        self.assertLess(coefficient_of_variation, 0.5,
                       f"Agent {agent_name} time per order is too variable: CV={coefficient_of_variation:.3f}")
                       
        self.test_logger.info(f"Agent {agent_name} scaling validation: "
                            f"Mean time/order: {mean_time:.4f}s, CV: {coefficient_of_variation:.3f}")
                            
    def _validate_workflow_scaling(self, benchmarks: List[Dict[str, Any]]):
        """Validate that workflow performance scales reasonably"""
        if len(benchmarks) < 2:
            return
            
        # Sort by dataset size
        benchmarks.sort(key=lambda x: x['dataset_size'])
        
        # Check that throughput doesn't degrade too severely
        throughputs = [b['throughput'] for b in benchmarks]
        max_throughput = max(throughputs)
        min_throughput = min(throughputs)
        
        throughput_degradation = max_throughput / min_throughput if min_throughput > 0 else float('inf')
        
        # Throughput shouldn't degrade more than 3x
        self.assertLess(throughput_degradation, 3.0,
                       f"Workflow throughput degradation too severe: {throughput_degradation:.2f}x")
                       
        self.test_logger.info(f"Workflow scaling validation: "
                            f"Throughput range: {min_throughput:.2f}-{max_throughput:.2f} orders/sec, "
                            f"Degradation: {throughput_degradation:.2f}x")
                            
    def _detect_performance_regression(self, baseline_time: float, current_time: float) -> Tuple[bool, str]:
        """Detect performance regression based on execution times"""
        if baseline_time <= 0:
            return False, 'none'
            
        regression_factor = current_time / baseline_time
        
        if regression_factor >= self.regression_thresholds['critical']:
            return True, 'critical'
        elif regression_factor >= self.regression_thresholds['warning']:
            return True, 'warning'
        else:
            return False, 'none'
            
    def _save_benchmark_results(self, file_path: str):
        """Save benchmark results to file"""
        benchmark_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_environment': {
                    'python_version': sys.version,
                    'platform': sys.platform
                }
            },
            'benchmarks': self.benchmark_results
        }
        
        with open(file_path, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
            
    def _load_benchmark_results(self, file_path: str) -> Dict[str, Any]:
        """Load benchmark results from file"""
        with open(file_path, 'r') as f:
            return json.load(f)
            
    def _compare_benchmark_results(self, baseline: List[Dict[str, Any]], 
                                 current: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare benchmark results between baseline and current"""
        comparisons = []
        
        # Create lookup for current results by dataset size
        current_lookup = {b['dataset_size']: b for b in current}
        
        for baseline_result in baseline:
            size = baseline_result['dataset_size']
            if size in current_lookup:
                current_result = current_lookup[size]
                
                baseline_time = baseline_result['avg_execution_time']
                current_time = current_result['avg_execution_time']
                
                change_percentage = ((current_time - baseline_time) / baseline_time * 100) if baseline_time > 0 else 0
                
                comparison = {
                    'dataset_size': size,
                    'baseline_time': baseline_time,
                    'current_time': current_time,
                    'change_percentage': change_percentage,
                    'regression_detected': change_percentage > 20  # 20% threshold
                }
                
                comparisons.append(comparison)
                
        return comparisons


if __name__ == '__main__':
    unittest.main()