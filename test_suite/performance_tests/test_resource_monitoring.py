"""
Resource Monitoring Performance Tests

Tests memory usage patterns, CPU utilization, file system I/O performance,
and resource cleanup during workflow execution:
- Memory usage patterns during workflow execution
- CPU utilization and processing efficiency
- File system I/O performance and disk usage
- Resource cleanup and memory leak detection
"""

import unittest
import time
import os
import sys
import psutil
import gc
import threading
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import tempfile
import shutil

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from test_suite.utilities.base_test import BaseIntegrationTest
from test_suite.utilities.test_data_generator import TestDataGenerator, TestDataFixtures


class ResourceMonitoringTests(BaseIntegrationTest):
    """Test resource usage patterns and cleanup during workflow execution"""
    
    def setUp(self):
        """Setup resource monitoring test environment"""
        super().setUp()
        
        # Initialize test data generator and fixtures
        self.data_generator = TestDataGenerator(self.test_temp_dir)
        self.fixtures = TestDataFixtures(os.path.join(self.test_temp_dir, 'fixtures'))
        
        # Resource monitoring data
        self.resource_data = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Get initial system state
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.initial_cpu_percent = self.process.cpu_percent()
        
        # Resource thresholds
        self.memory_thresholds = {
            'small_dataset': 50,    # MB
            'medium_dataset': 150,  # MB
            'large_dataset': 300    # MB
        }
        
        self.cpu_thresholds = {
            'max_sustained_cpu': 80,  # % CPU usage
            'max_peak_cpu': 95        # % CPU usage
        }
        
        # I/O monitoring
        self.io_counters_start = None
        self.temp_files_created = []
        
    def tearDown(self):
        """Cleanup resource monitoring test environment"""
        # Stop monitoring if active
        self._stop_resource_monitoring()
        
        # Cleanup temporary files
        for temp_file in self.temp_files_created:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
                
        self.fixtures.cleanup_test_files()
        super().tearDown()
        
    def test_memory_usage_patterns(self):
        """Test memory usage patterns during workflow execution"""
        self.test_logger.info("Starting memory usage pattern tests")
        
        test_scenarios = [
            {'name': 'small_dataset', 'size': 50},
            {'name': 'medium_dataset', 'size': 250},
            {'name': 'large_dataset', 'size': 1000}
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario['name']):
                self.test_logger.info(f"Testing memory usage with {scenario['name']} ({scenario['size']} orders)")
                
                # Force garbage collection before test
                gc.collect()
                
                # Get baseline memory
                baseline_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                
                # Generate test dataset
                dataset = self._generate_resource_test_dataset(scenario['size'])
                
                # Start memory monitoring
                memory_samples = []
                self._start_memory_monitoring(memory_samples)
                
                try:
                    # Execute workflow with memory monitoring
                    execution_result = self._execute_workflow_with_memory_monitoring(dataset)
                    
                    # Stop monitoring
                    self._stop_resource_monitoring()
                    
                    # Analyze memory usage
                    memory_analysis = self._analyze_memory_usage(memory_samples, baseline_memory)
                    
                    # Validate memory usage
                    max_threshold = self.memory_thresholds[scenario['name']]
                    peak_memory_usage = memory_analysis['peak_usage']
                    
                    self.assertLess(peak_memory_usage, max_threshold,
                                   f"Peak memory usage ({peak_memory_usage:.1f} MB) exceeded "
                                   f"threshold ({max_threshold} MB) for {scenario['name']}")
                    
                    # Check for memory leaks
                    final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
                    memory_growth = final_memory - baseline_memory
                    
                    # Allow some growth but not excessive
                    max_acceptable_growth = 20  # MB
                    self.assertLess(memory_growth, max_acceptable_growth,
                                   f"Potential memory leak detected: {memory_growth:.1f} MB growth "
                                   f"after {scenario['name']} execution")
                    
                    self.test_logger.info(f"Memory analysis for {scenario['name']}: "
                                        f"Peak: {peak_memory_usage:.1f} MB, "
                                        f"Average: {memory_analysis['avg_usage']:.1f} MB, "
                                        f"Growth: {memory_growth:.1f} MB")
                    
                    # Store results
                    self.resource_data[f"memory_{scenario['name']}"] = {
                        'baseline_memory': baseline_memory,
                        'peak_memory': peak_memory_usage,
                        'avg_memory': memory_analysis['avg_usage'],
                        'memory_growth': memory_growth,
                        'samples': len(memory_samples)
                    }
                    
                finally:
                    # Ensure monitoring is stopped
                    self._stop_resource_monitoring()
                    
    def test_cpu_utilization_efficiency(self):
        """Test CPU utilization and processing efficiency"""
        self.test_logger.info("Starting CPU utilization efficiency tests")
        
        test_scenarios = [
            {'name': 'sequential_execution', 'size': 200, 'mode': 'sequential'},
            {'name': 'parallel_execution', 'size': 200, 'mode': 'parallel'}
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario['name']):
                self.test_logger.info(f"Testing CPU utilization with {scenario['name']}")
                
                # Generate test dataset
                dataset = self._generate_resource_test_dataset(scenario['size'])
                
                # Start CPU monitoring
                cpu_samples = []
                self._start_cpu_monitoring(cpu_samples)
                
                try:
                    # Execute workflow with CPU monitoring
                    start_time = time.time()
                    
                    if scenario['mode'] == 'sequential':
                        execution_result = self._execute_sequential_workflow(dataset)
                    else:
                        execution_result = self._execute_parallel_workflow(dataset)
                        
                    execution_time = time.time() - start_time
                    
                    # Stop monitoring
                    self._stop_resource_monitoring()
                    
                    # Analyze CPU usage
                    cpu_analysis = self._analyze_cpu_usage(cpu_samples)
                    
                    # Validate CPU usage
                    peak_cpu = cpu_analysis['peak_usage']
                    avg_cpu = cpu_analysis['avg_usage']
                    
                    self.assertLess(peak_cpu, self.cpu_thresholds['max_peak_cpu'],
                                   f"Peak CPU usage ({peak_cpu:.1f}%) exceeded threshold "
                                   f"({self.cpu_thresholds['max_peak_cpu']}%) for {scenario['name']}")
                    
                    # For parallel execution, expect higher CPU utilization
                    if scenario['mode'] == 'parallel':
                        self.assertGreater(avg_cpu, 10,
                                         f"Parallel execution should show higher CPU utilization, "
                                         f"got {avg_cpu:.1f}%")
                    
                    # Calculate processing efficiency (orders per second per CPU%)
                    efficiency = (scenario['size'] / execution_time) / avg_cpu if avg_cpu > 0 else 0
                    
                    self.test_logger.info(f"CPU analysis for {scenario['name']}: "
                                        f"Peak: {peak_cpu:.1f}%, Average: {avg_cpu:.1f}%, "
                                        f"Efficiency: {efficiency:.2f} orders/sec/%CPU")
                    
                    # Store results
                    self.resource_data[f"cpu_{scenario['name']}"] = {
                        'peak_cpu': peak_cpu,
                        'avg_cpu': avg_cpu,
                        'execution_time': execution_time,
                        'efficiency': efficiency,
                        'samples': len(cpu_samples)
                    }
                    
                finally:
                    # Ensure monitoring is stopped
                    self._stop_resource_monitoring()
                    
    def test_file_system_io_performance(self):
        """Test file system I/O performance and disk usage"""
        self.test_logger.info("Starting file system I/O performance tests")
        
        test_scenarios = [
            {'name': 'small_io', 'size': 50, 'expected_files': 5},
            {'name': 'medium_io', 'size': 250, 'expected_files': 10},
            {'name': 'large_io', 'size': 1000, 'expected_files': 15}
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario['name']):
                self.test_logger.info(f"Testing I/O performance with {scenario['name']}")
                
                # Get initial I/O counters
                initial_io = self.process.io_counters()
                initial_disk_usage = shutil.disk_usage(self.test_temp_dir)
                
                # Generate test dataset
                dataset = self._generate_resource_test_dataset(scenario['size'])
                
                # Execute workflow with I/O monitoring
                start_time = time.time()
                execution_result = self._execute_workflow_with_io_monitoring(dataset, scenario)
                execution_time = time.time() - start_time
                
                # Get final I/O counters
                final_io = self.process.io_counters()
                final_disk_usage = shutil.disk_usage(self.test_temp_dir)
                
                # Calculate I/O metrics
                bytes_read = final_io.read_bytes - initial_io.read_bytes
                bytes_written = final_io.write_bytes - initial_io.write_bytes
                read_operations = final_io.read_count - initial_io.read_count
                write_operations = final_io.write_count - initial_io.write_count
                
                disk_space_used = initial_disk_usage.free - final_disk_usage.free
                
                # Calculate I/O efficiency
                read_throughput = bytes_read / execution_time if execution_time > 0 else 0
                write_throughput = bytes_written / execution_time if execution_time > 0 else 0
                
                io_analysis = {
                    'bytes_read': bytes_read,
                    'bytes_written': bytes_written,
                    'read_operations': read_operations,
                    'write_operations': write_operations,
                    'read_throughput': read_throughput / 1024 / 1024,  # MB/s
                    'write_throughput': write_throughput / 1024 / 1024,  # MB/s
                    'disk_space_used': disk_space_used,
                    'execution_time': execution_time
                }
                
                # Validate I/O performance
                # Read throughput should be reasonable (at least 1 MB/s for large datasets)
                if scenario['size'] >= 1000:
                    self.assertGreater(io_analysis['read_throughput'], 1.0,
                                     f"Read throughput too low for {scenario['name']}: "
                                     f"{io_analysis['read_throughput']:.2f} MB/s")
                
                # Write throughput should be reasonable
                if bytes_written > 0:
                    self.assertGreater(io_analysis['write_throughput'], 0.5,
                                     f"Write throughput too low for {scenario['name']}: "
                                     f"{io_analysis['write_throughput']:.2f} MB/s")
                
                self.test_logger.info(f"I/O analysis for {scenario['name']}: "
                                    f"Read: {io_analysis['read_throughput']:.2f} MB/s, "
                                    f"Write: {io_analysis['write_throughput']:.2f} MB/s, "
                                    f"Disk used: {disk_space_used} bytes")
                
                # Store results
                self.resource_data[f"io_{scenario['name']}"] = io_analysis
                
    def test_resource_cleanup_and_leak_detection(self):
        """Test resource cleanup and memory leak detection"""
        self.test_logger.info("Starting resource cleanup and leak detection tests")
        
        # Run multiple iterations to detect leaks
        iterations = 5
        memory_samples = []
        file_handle_samples = []
        
        for iteration in range(iterations):
            with self.subTest(iteration=iteration):
                self.test_logger.info(f"Leak detection iteration {iteration + 1}/{iterations}")
                
                # Force garbage collection
                gc.collect()
                
                # Sample resource usage before execution
                memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
                
                try:
                    open_files_before = len(self.process.open_files())
                except (psutil.AccessDenied, AttributeError):
                    open_files_before = 0
                
                # Generate and execute test
                dataset = self._generate_resource_test_dataset(100)
                execution_result = self._execute_workflow_with_cleanup_monitoring(dataset)
                
                # Force garbage collection after execution
                gc.collect()
                time.sleep(0.1)  # Allow cleanup to complete
                
                # Sample resource usage after execution
                memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
                
                try:
                    open_files_after = len(self.process.open_files())
                except (psutil.AccessDenied, AttributeError):
                    open_files_after = 0
                
                # Record samples
                memory_samples.append({
                    'iteration': iteration,
                    'memory_before': memory_before,
                    'memory_after': memory_after,
                    'memory_growth': memory_after - memory_before
                })
                
                file_handle_samples.append({
                    'iteration': iteration,
                    'files_before': open_files_before,
                    'files_after': open_files_after,
                    'file_growth': open_files_after - open_files_before
                })
                
                self.test_logger.info(f"Iteration {iteration + 1}: "
                                    f"Memory growth: {memory_after - memory_before:.1f} MB, "
                                    f"File handle growth: {open_files_after - open_files_before}")
        
        # Analyze leak patterns
        leak_analysis = self._analyze_leak_patterns(memory_samples, file_handle_samples)
        
        # Validate no significant leaks
        avg_memory_growth = leak_analysis['avg_memory_growth']
        max_memory_growth = leak_analysis['max_memory_growth']
        total_memory_growth = leak_analysis['total_memory_growth']
        
        # Memory growth per iteration should be minimal
        self.assertLess(avg_memory_growth, 5.0,
                       f"Average memory growth per iteration too high: {avg_memory_growth:.1f} MB")
        
        # Total memory growth should be reasonable
        self.assertLess(total_memory_growth, 25.0,
                       f"Total memory growth across iterations too high: {total_memory_growth:.1f} MB")
        
        # File handle growth should be zero (no leaks)
        avg_file_growth = leak_analysis['avg_file_growth']
        self.assertEqual(avg_file_growth, 0,
                        f"File handle leak detected: {avg_file_growth} handles per iteration")
        
        self.test_logger.info(f"Leak analysis: "
                            f"Avg memory growth: {avg_memory_growth:.1f} MB/iteration, "
                            f"Total memory growth: {total_memory_growth:.1f} MB, "
                            f"Avg file growth: {avg_file_growth} handles/iteration")
        
        # Store results
        self.resource_data['leak_detection'] = {
            'memory_samples': memory_samples,
            'file_handle_samples': file_handle_samples,
            'analysis': leak_analysis
        }
        
    def test_concurrent_resource_usage(self):
        """Test resource usage under concurrent workflow executions"""
        self.test_logger.info("Starting concurrent resource usage tests")
        
        # Test with multiple concurrent workflows
        concurrent_workflows = 3
        dataset_size = 100
        
        # Generate datasets for concurrent execution
        datasets = []
        for i in range(concurrent_workflows):
            dataset = self._generate_resource_test_dataset(dataset_size)
            datasets.append(dataset)
        
        # Monitor resources during concurrent execution
        memory_samples = []
        cpu_samples = []
        
        self._start_memory_monitoring(memory_samples)
        self._start_cpu_monitoring(cpu_samples)
        
        try:
            # Execute workflows concurrently
            import concurrent.futures
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_workflows) as executor:
                futures = []
                for i, dataset in enumerate(datasets):
                    future = executor.submit(self._execute_workflow_with_resource_tracking, dataset, i)
                    futures.append(future)
                
                # Wait for all to complete
                results = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results.append(result)
            
            execution_time = time.time() - start_time
            
            # Stop monitoring
            self._stop_resource_monitoring()
            
            # Analyze concurrent resource usage
            memory_analysis = self._analyze_memory_usage(memory_samples, self.initial_memory)
            cpu_analysis = self._analyze_cpu_usage(cpu_samples)
            
            # Validate concurrent execution didn't exceed limits
            peak_memory = memory_analysis['peak_usage']
            peak_cpu = cpu_analysis['peak_usage']
            
            # Memory usage should scale reasonably with concurrency
            expected_max_memory = self.memory_thresholds['medium_dataset'] * 1.5  # Allow 50% overhead
            self.assertLess(peak_memory, expected_max_memory,
                           f"Concurrent execution peak memory ({peak_memory:.1f} MB) "
                           f"exceeded expected limit ({expected_max_memory:.1f} MB)")
            
            # CPU usage should be higher but not excessive
            self.assertLess(peak_cpu, self.cpu_thresholds['max_peak_cpu'],
                           f"Concurrent execution peak CPU ({peak_cpu:.1f}%) "
                           f"exceeded threshold ({self.cpu_thresholds['max_peak_cpu']}%)")
            
            self.test_logger.info(f"Concurrent execution analysis: "
                                f"Peak memory: {peak_memory:.1f} MB, "
                                f"Peak CPU: {peak_cpu:.1f}%, "
                                f"Total time: {execution_time:.2f}s")
            
            # Store results
            self.resource_data['concurrent_execution'] = {
                'workflows': concurrent_workflows,
                'peak_memory': peak_memory,
                'peak_cpu': peak_cpu,
                'execution_time': execution_time,
                'results': results
            }
            
        finally:
            # Ensure monitoring is stopped
            self._stop_resource_monitoring()   
    def _generate_resource_test_dataset(self, size: int) -> Dict[str, Any]:
            """Generate dataset for resource testing"""
            # Create realistic dataset for resource monitoring
            valid_count = int(size * 0.8)  # 80% valid orders
            invalid_count = size - valid_count
            
            valid_orders = self.data_generator.generate_valid_orders(valid_count)
            invalid_orders = self.data_generator.generate_invalid_orders(['invalid_sku'] * invalid_count)
            
            all_orders = valid_orders + invalid_orders
            
            # Generate SKU data
            sku_count = max(5, int(size * 0.15))
            valid_skus = [f"SKU{str(i).zfill(3)}" for i in range(1, sku_count + 1)]
            master_sku_data = self.data_generator.generate_master_sku_data(valid_skus)
            
            return {
                'orders': all_orders,
                'master_sku': master_sku_data,
                'scenario_info': {
                    'name': f'resource_test_{size}',
                    'total_orders': size,
                    'valid_orders': valid_count,
                    'invalid_orders': invalid_count,
                    'total_skus': sku_count
                }
            }
        
    def _start_memory_monitoring(self, memory_samples: List[Dict[str, Any]]):
        """Start memory usage monitoring in background thread"""
        self.monitoring_active = True
        
        def monitor_memory():
            while self.monitoring_active:
                try:
                    memory_info = self.process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    
                    sample = {
                        'timestamp': time.time(),
                        'memory_mb': memory_mb,
                        'memory_percent': self.process.memory_percent()
                    }
                    memory_samples.append(sample)
                    
                    time.sleep(0.1)  # Sample every 100ms
                except Exception as e:
                    self.test_logger.warning(f"Memory monitoring error: {e}")
                    break
                    
        self.monitoring_thread = threading.Thread(target=monitor_memory, daemon=True)
        self.monitoring_thread.start()
        
    def _start_cpu_monitoring(self, cpu_samples: List[Dict[str, Any]]):
        """Start CPU usage monitoring in background thread"""
        self.monitoring_active = True
        
        def monitor_cpu():
            # Initial CPU reading (psutil needs this)
            self.process.cpu_percent()
            time.sleep(0.1)
            
            while self.monitoring_active:
                try:
                    cpu_percent = self.process.cpu_percent()
                    
                    sample = {
                        'timestamp': time.time(),
                        'cpu_percent': cpu_percent
                    }
                    cpu_samples.append(sample)
                    
                    time.sleep(0.1)  # Sample every 100ms
                except Exception as e:
                    self.test_logger.warning(f"CPU monitoring error: {e}")
                    break
                    
        self.monitoring_thread = threading.Thread(target=monitor_cpu, daemon=True)
        self.monitoring_thread.start()
        
    def _stop_resource_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1.0)
            
    def _execute_workflow_with_memory_monitoring(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with memory monitoring"""
        # Mock workflow execution with realistic memory usage patterns
        order_count = len(dataset['orders'])
        
        # Simulate memory allocation patterns
        # Phase 1: Load data (memory increases)
        data_buffer = []
        for order in dataset['orders']:
            # Simulate data processing
            processed_order = dict(order)
            processed_order['processed'] = True
            data_buffer.append(processed_order)
            
            # Add small delay to allow monitoring
            if len(data_buffer) % 50 == 0:
                time.sleep(0.01)
        
        # Phase 2: Process data (peak memory usage)
        results = []
        for order in data_buffer:
            # Simulate processing
            result = {
                'order_id': order.get('PO_Number'),
                'status': 'processed',
                'timestamp': time.time()
            }
            results.append(result)
            
            # Add delay for monitoring
            if len(results) % 25 == 0:
                time.sleep(0.01)
        
        # Phase 3: Cleanup (memory should decrease)
        data_buffer.clear()
        
        return {
            'status': 'success',
            'processed_orders': len(results),
            'results': results
        }
        
    def _execute_sequential_workflow(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow in sequential mode"""
        # Simulate sequential agent execution
        agents = ['po_reader', 'validation', 'exception_response', 'so_creator', 'summary_insights']
        
        shared_data = {}
        
        for agent in agents:
            # Simulate agent processing
            processing_time = 0.1 + (len(dataset['orders']) * 0.001)
            time.sleep(processing_time)
            
            # Update shared data
            shared_data[agent] = {
                'processed_orders': len(dataset['orders']),
                'timestamp': time.time()
            }
            
        return {
            'status': 'success',
            'execution_mode': 'sequential',
            'agents_executed': agents,
            'shared_data': shared_data
        }
        
    def _execute_parallel_workflow(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow in parallel mode"""
        import concurrent.futures
        
        # Simulate parallel execution with dependencies
        shared_data = {}
        
        # Phase 1: Sequential (po_reader)
        time.sleep(0.05 + (len(dataset['orders']) * 0.0005))
        shared_data['po_reader'] = {'processed_orders': len(dataset['orders'])}
        
        # Phase 2: Sequential (validation)
        time.sleep(0.1 + (len(dataset['orders']) * 0.001))
        shared_data['validation'] = {'processed_orders': len(dataset['orders'])}
        
        # Phase 3: Parallel (exception_response, so_creator)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            def process_exceptions():
                time.sleep(0.05 + (len(dataset['orders']) * 0.0005))
                return {'processed_orders': len(dataset['orders'])}
                
            def create_sales_orders():
                time.sleep(0.08 + (len(dataset['orders']) * 0.0008))
                return {'processed_orders': len(dataset['orders'])}
            
            future1 = executor.submit(process_exceptions)
            future2 = executor.submit(create_sales_orders)
            
            shared_data['exception_response'] = future1.result()
            shared_data['so_creator'] = future2.result()
        
        # Phase 4: Sequential (summary_insights)
        time.sleep(0.15 + (len(dataset['orders']) * 0.0015))
        shared_data['summary_insights'] = {'processed_orders': len(dataset['orders'])}
        
        return {
            'status': 'success',
            'execution_mode': 'parallel',
            'agents_executed': ['po_reader', 'validation', 'exception_response', 'so_creator', 'summary_insights'],
            'shared_data': shared_data
        }
        
    def _execute_workflow_with_io_monitoring(self, dataset: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with I/O monitoring"""
        # Create temporary files to simulate I/O operations
        temp_files = []
        
        try:
            # Simulate input file reading
            input_file = os.path.join(self.test_temp_dir, 'input_orders.csv')
            file_paths = self.data_generator.save_dataset_to_files(dataset, self.test_temp_dir)
            temp_files.extend(file_paths.values())
            
            # Simulate processing with intermediate files
            for i in range(scenario['expected_files']):
                temp_file = os.path.join(self.test_temp_dir, f'temp_processing_{i}.txt')
                with open(temp_file, 'w') as f:
                    # Write some data to simulate processing
                    for j in range(100):
                        f.write(f"Processing data line {j} for file {i}\n")
                temp_files.append(temp_file)
                self.temp_files_created.append(temp_file)
                
                # Add delay to spread I/O operations
                time.sleep(0.01)
            
            # Simulate output file creation
            output_file = os.path.join(self.test_temp_dir, 'output_results.json')
            with open(output_file, 'w') as f:
                import json
                result_data = {
                    'processed_orders': len(dataset['orders']),
                    'timestamp': datetime.now().isoformat(),
                    'scenario': scenario['name']
                }
                json.dump(result_data, f, indent=2)
            temp_files.append(output_file)
            self.temp_files_created.append(output_file)
            
            return {
                'status': 'success',
                'files_created': len(temp_files),
                'processed_orders': len(dataset['orders'])
            }
            
        except Exception as e:
            self.test_logger.error(f"I/O monitoring execution error: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
            
    def _execute_workflow_with_cleanup_monitoring(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with cleanup monitoring"""
        # Create temporary resources that should be cleaned up
        temp_resources = []
        
        try:
            # Create temporary files
            for i in range(5):
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                                      dir=self.test_temp_dir, 
                                                      prefix=f'cleanup_test_{i}_')
                temp_file.write(f"Temporary data for cleanup test {i}\n")
                temp_file.close()
                temp_resources.append(temp_file.name)
            
            # Simulate processing
            processing_time = 0.05 + (len(dataset['orders']) * 0.0005)
            time.sleep(processing_time)
            
            # Cleanup temporary resources
            for temp_file in temp_resources:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return {
                'status': 'success',
                'processed_orders': len(dataset['orders']),
                'temp_resources_created': len(temp_resources),
                'temp_resources_cleaned': len(temp_resources)
            }
            
        except Exception as e:
            # Cleanup on error
            for temp_file in temp_resources:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception:
                    pass
                    
            return {
                'status': 'failed',
                'error': str(e)
            }
            
    def _execute_workflow_with_resource_tracking(self, dataset: Dict[str, Any], workflow_id: int) -> Dict[str, Any]:
        """Execute workflow with resource tracking for concurrent testing"""
        start_time = time.time()
        
        # Simulate workflow execution with unique identifier
        processing_time = 0.1 + (len(dataset['orders']) * 0.001)
        time.sleep(processing_time)
        
        execution_time = time.time() - start_time
        
        return {
            'workflow_id': workflow_id,
            'status': 'success',
            'processed_orders': len(dataset['orders']),
            'execution_time': execution_time
        }
        
    def _analyze_memory_usage(self, memory_samples: List[Dict[str, Any]], baseline_memory: float) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        if not memory_samples:
            return {
                'peak_usage': baseline_memory,
                'avg_usage': baseline_memory,
                'min_usage': baseline_memory,
                'growth': 0
            }
            
        memory_values = [sample['memory_mb'] for sample in memory_samples]
        
        return {
            'peak_usage': max(memory_values),
            'avg_usage': sum(memory_values) / len(memory_values),
            'min_usage': min(memory_values),
            'growth': max(memory_values) - baseline_memory,
            'sample_count': len(memory_samples)
        }
        
    def _analyze_cpu_usage(self, cpu_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CPU usage patterns"""
        if not cpu_samples:
            return {
                'peak_usage': 0,
                'avg_usage': 0,
                'min_usage': 0
            }
            
        cpu_values = [sample['cpu_percent'] for sample in cpu_samples]
        
        return {
            'peak_usage': max(cpu_values),
            'avg_usage': sum(cpu_values) / len(cpu_values),
            'min_usage': min(cpu_values),
            'sample_count': len(cpu_samples)
        }
        
    def _analyze_leak_patterns(self, memory_samples: List[Dict[str, Any]], 
                              file_handle_samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze resource leak patterns"""
        memory_growths = [sample['memory_growth'] for sample in memory_samples]
        file_growths = [sample['file_growth'] for sample in file_handle_samples]
        
        return {
            'avg_memory_growth': sum(memory_growths) / len(memory_growths) if memory_growths else 0,
            'max_memory_growth': max(memory_growths) if memory_growths else 0,
            'total_memory_growth': sum(memory_growths) if memory_growths else 0,
            'avg_file_growth': sum(file_growths) / len(file_growths) if file_growths else 0,
            'max_file_growth': max(file_growths) if file_growths else 0,
            'total_file_growth': sum(file_growths) if file_growths else 0,
            'iterations': len(memory_samples)
        }


if __name__ == '__main__':
    unittest.main()