"""
Authentication Performance Metrics and Monitoring System
======================================================

This module provides comprehensive performance monitoring for the Clerk authentication system,
including benchmarking tools, baseline measurements, and bottleneck analysis.

Key Responsibilities:
1. Monitor authentication latency at each caching layer
2. Track JWT validation, JWKS fetch, and database sync performance  
3. Provide before/after comparison benchmarks
4. Identify performance bottlenecks and optimization opportunities
5. Generate performance reports and recommendations

Performance Targets:
- Phase 1 (JWKS Caching): 15-25% improvement
- Phase 2 (JWT Validation Cache): 25-35% improvement  
- Phase 3 (User Session Cache): 35-50% improvement
- Phase 4 (Database Connection Pool): 50-65% improvement
- Phase 5 (Multi-layer Integration): 70-85% improvement
"""

import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from collections import defaultdict
import logging
import json
import csv
from pathlib import Path

import httpx
import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import threading

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Single performance measurement data point"""
    timestamp: datetime
    operation: str
    duration_ms: float
    success: bool
    phase: str = "baseline"
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class BenchmarkResult:
    """Comprehensive benchmark results for a specific test"""
    test_name: str
    phase: str
    total_requests: int
    success_count: int
    failure_count: int
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    requests_per_second: float
    cache_hit_rate: float
    error_rate: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class AuthPerformanceMonitor:
    """Comprehensive authentication performance monitoring system"""
    
    def __init__(self, 
                 store_metrics: bool = True,
                 metrics_file: Optional[str] = None,
                 enable_system_monitoring: bool = True):
        """
        Initialize the performance monitor
        
        Args:
            store_metrics: Whether to store metrics to file
            metrics_file: Optional custom metrics file path
            enable_system_monitoring: Whether to monitor system resources
        """
        self.store_metrics = store_metrics
        self.metrics: List[PerformanceMetric] = []
        self.benchmarks: List[BenchmarkResult] = []
        self.current_phase = "baseline"
        
        # Metrics storage
        if metrics_file:
            self.metrics_file = Path(metrics_file)
        else:
            self.metrics_file = Path("performance/auth_metrics.json")
            
        # System monitoring
        self.enable_system_monitoring = enable_system_monitoring
        self.system_stats = []
        self._monitoring_active = False
        
        # Performance baselines
        self.baseline_metrics = {}
        
        # Create metrics directory
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🔍 AuthPerformanceMonitor initialized - storing to {self.metrics_file}")

    async def measure_operation(self, 
                              operation: str,
                              operation_func,
                              *args, 
                              cache_check_func=None,
                              metadata: Dict[str, Any] = None,
                              **kwargs) -> Tuple[Any, PerformanceMetric]:
        """
        Measure the performance of an authentication operation
        
        Args:
            operation: Name of the operation being measured
            operation_func: Async function to measure
            args: Arguments for the operation function
            cache_check_func: Optional function to check if cache was hit
            metadata: Additional metadata to store
            kwargs: Keyword arguments for the operation function
            
        Returns:
            Tuple of (operation_result, performance_metric)
        """
        start_time = time.perf_counter()
        timestamp = datetime.now()
        success = False
        result = None
        cache_hit = False
        
        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = await operation_func(*args, **kwargs)
            else:
                result = operation_func(*args, **kwargs)
            success = True
            
            # Check if operation hit cache
            if cache_check_func:
                if asyncio.iscoroutinefunction(cache_check_func):
                    cache_hit = await cache_check_func()
                else:
                    cache_hit = cache_check_func()
                    
        except Exception as e:
            logger.error(f"Operation '{operation}' failed: {str(e)}")
            result = e
            success = False
            
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Create performance metric
            metric = PerformanceMetric(
                timestamp=timestamp,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                phase=self.current_phase,
                cache_hit=cache_hit,
                metadata=metadata or {}
            )
            
            # Store metric
            self.metrics.append(metric)
            if self.store_metrics:
                await self._persist_metric(metric)
                
            # Log performance info
            cache_status = "HIT" if cache_hit else "MISS"
            status = "✅" if success else "❌"
            logger.info(f"{status} {operation}: {duration_ms:.2f}ms [CACHE: {cache_status}]")
            
            return result, metric

    async def start_system_monitoring(self, interval_seconds: float = 1.0):
        """Start continuous system resource monitoring"""
        if not self.enable_system_monitoring:
            return
            
        self._monitoring_active = True
        
        async def monitor_loop():
            while self._monitoring_active:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    memory = psutil.virtual_memory()
                    disk_io = psutil.disk_io_counters()
                    net_io = psutil.net_io_counters()
                    
                    system_metric = {
                        'timestamp': datetime.now().isoformat(),
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_used_mb': memory.used / (1024 * 1024),
                        'disk_read_mb': disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                        'disk_write_mb': disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                        'network_sent_mb': net_io.bytes_sent / (1024 * 1024) if net_io else 0,
                        'network_recv_mb': net_io.bytes_recv / (1024 * 1024) if net_io else 0
                    }
                    
                    self.system_stats.append(system_metric)
                    
                    # Keep only last 1000 measurements
                    if len(self.system_stats) > 1000:
                        self.system_stats = self.system_stats[-1000:]
                        
                    await asyncio.sleep(interval_seconds)
                    
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                    await asyncio.sleep(interval_seconds)
        
        # Start monitoring in background
        asyncio.create_task(monitor_loop())
        logger.info("📊 System monitoring started")

    def stop_system_monitoring(self):
        """Stop system resource monitoring"""
        self._monitoring_active = False
        logger.info("📊 System monitoring stopped")

    async def run_comprehensive_benchmark(self,
                                        test_scenarios: List[Dict[str, Any]],
                                        requests_per_scenario: int = 100,
                                        concurrent_requests: int = 10) -> Dict[str, BenchmarkResult]:
        """
        Run comprehensive authentication benchmarks across multiple scenarios
        
        Args:
            test_scenarios: List of test scenarios to run
            requests_per_scenario: Number of requests per scenario
            concurrent_requests: Number of concurrent requests
            
        Returns:
            Dictionary mapping scenario names to benchmark results
        """
        logger.info(f"🚀 Starting comprehensive authentication benchmark")
        logger.info(f"   Scenarios: {len(test_scenarios)}")
        logger.info(f"   Requests per scenario: {requests_per_scenario}")
        logger.info(f"   Concurrent requests: {concurrent_requests}")
        
        # Start system monitoring
        await self.start_system_monitoring()
        
        benchmark_results = {}
        
        try:
            for scenario in test_scenarios:
                scenario_name = scenario.get('name', 'Unknown')
                logger.info(f"🔍 Running benchmark scenario: {scenario_name}")
                
                result = await self._run_scenario_benchmark(
                    scenario=scenario,
                    num_requests=requests_per_scenario,
                    concurrency=concurrent_requests
                )
                
                benchmark_results[scenario_name] = result
                
                # Brief pause between scenarios
                await asyncio.sleep(2)
                
        finally:
            # Stop system monitoring
            self.stop_system_monitoring()
            
        logger.info(f"✅ Comprehensive benchmark completed - {len(benchmark_results)} scenarios")
        return benchmark_results

    async def _run_scenario_benchmark(self,
                                    scenario: Dict[str, Any],
                                    num_requests: int,
                                    concurrency: int) -> BenchmarkResult:
        """Run benchmark for a specific scenario"""
        
        scenario_name = scenario.get('name', 'Unknown')
        test_func = scenario.get('test_func')
        
        if not test_func:
            raise ValueError(f"No test_func provided for scenario {scenario_name}")
        
        # Track metrics for this scenario
        scenario_metrics = []
        start_time = datetime.now()
        
        # Run concurrent requests
        semaphore = asyncio.Semaphore(concurrency)
        
        async def run_single_request():
            async with semaphore:
                try:
                    _, metric = await self.measure_operation(
                        operation=f"benchmark_{scenario_name}",
                        operation_func=test_func,
                        metadata={
                            'scenario': scenario_name,
                            'benchmark': True
                        }
                    )
                    return metric
                except Exception as e:
                    # Create error metric
                    return PerformanceMetric(
                        timestamp=datetime.now(),
                        operation=f"benchmark_{scenario_name}",
                        duration_ms=0,
                        success=False,
                        phase=self.current_phase,
                        metadata={'error': str(e), 'scenario': scenario_name, 'benchmark': True}
                    )
        
        # Execute all requests
        tasks = [run_single_request() for _ in range(num_requests)]
        scenario_metrics = await asyncio.gather(*tasks)
        
        # Calculate benchmark statistics
        successful_metrics = [m for m in scenario_metrics if m.success]
        failed_metrics = [m for m in scenario_metrics if not m.success]
        
        if successful_metrics:
            durations = [m.duration_ms for m in successful_metrics]
            cache_hits = sum(1 for m in successful_metrics if m.cache_hit)
            
            avg_latency = statistics.mean(durations)
            median_latency = statistics.median(durations)
            p95_latency = np.percentile(durations, 95)
            p99_latency = np.percentile(durations, 99) 
            min_latency = min(durations)
            max_latency = max(durations)
            
            # Calculate requests per second
            total_time_seconds = (datetime.now() - start_time).total_seconds()
            rps = len(successful_metrics) / total_time_seconds if total_time_seconds > 0 else 0
            
            cache_hit_rate = cache_hits / len(successful_metrics) if successful_metrics else 0
            error_rate = len(failed_metrics) / num_requests if num_requests > 0 else 0
            
        else:
            # All requests failed
            avg_latency = median_latency = p95_latency = p99_latency = 0
            min_latency = max_latency = rps = cache_hit_rate = 0
            error_rate = 1.0
        
        benchmark_result = BenchmarkResult(
            test_name=scenario_name,
            phase=self.current_phase,
            total_requests=num_requests,
            success_count=len(successful_metrics),
            failure_count=len(failed_metrics),
            avg_latency_ms=avg_latency,
            median_latency_ms=median_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            requests_per_second=rps,
            cache_hit_rate=cache_hit_rate,
            error_rate=error_rate,
            timestamp=start_time,
            metadata=scenario.get('metadata', {})
        )
        
        self.benchmarks.append(benchmark_result)
        await self._persist_benchmark(benchmark_result)
        
        return benchmark_result

    def set_phase(self, phase: str):
        """Set the current testing phase"""
        self.current_phase = phase
        logger.info(f"📍 Performance monitoring phase set to: {phase}")

    def establish_baseline(self, benchmark_results: Dict[str, BenchmarkResult]):
        """Store baseline performance measurements"""
        self.baseline_metrics = {
            scenario: result for scenario, result in benchmark_results.items()
        }
        logger.info(f"📊 Baseline established for {len(benchmark_results)} scenarios")

    def calculate_improvement(self, 
                            current_results: Dict[str, BenchmarkResult],
                            baseline_results: Optional[Dict[str, BenchmarkResult]] = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate performance improvements compared to baseline
        
        Returns:
            Dictionary with improvement percentages for each metric
        """
        if baseline_results is None:
            baseline_results = self.baseline_metrics
            
        if not baseline_results:
            logger.warning("No baseline metrics available for comparison")
            return {}
        
        improvements = {}
        
        for scenario_name in current_results:
            if scenario_name not in baseline_results:
                continue
                
            current = current_results[scenario_name]
            baseline = baseline_results[scenario_name]
            
            scenario_improvements = {}
            
            # Calculate improvements (negative means improvement for latency)
            if baseline.avg_latency_ms > 0:
                scenario_improvements['avg_latency'] = (
                    (baseline.avg_latency_ms - current.avg_latency_ms) / baseline.avg_latency_ms
                ) * 100
            
            if baseline.p95_latency_ms > 0:
                scenario_improvements['p95_latency'] = (
                    (baseline.p95_latency_ms - current.p95_latency_ms) / baseline.p95_latency_ms
                ) * 100
            
            if baseline.requests_per_second > 0:
                scenario_improvements['throughput'] = (
                    (current.requests_per_second - baseline.requests_per_second) / baseline.requests_per_second
                ) * 100
            
            # Error rate improvement (lower is better)
            if baseline.error_rate > 0:
                scenario_improvements['error_rate'] = (
                    (baseline.error_rate - current.error_rate) / baseline.error_rate
                ) * 100
            
            # Cache hit rate improvement
            scenario_improvements['cache_hit_rate'] = (
                current.cache_hit_rate - baseline.cache_hit_rate
            ) * 100
            
            improvements[scenario_name] = scenario_improvements
        
        return improvements

    def analyze_bottlenecks(self, 
                          recent_minutes: int = 30,
                          min_samples: int = 10) -> Dict[str, Any]:
        """
        Analyze recent performance data to identify bottlenecks
        
        Args:
            recent_minutes: How many minutes of recent data to analyze
            min_samples: Minimum number of samples required for analysis
            
        Returns:
            Dictionary containing bottleneck analysis
        """
        cutoff_time = datetime.now() - timedelta(minutes=recent_minutes)
        recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
        
        if len(recent_metrics) < min_samples:
            logger.warning(f"Insufficient data for bottleneck analysis: {len(recent_metrics)} samples")
            return {'warning': 'Insufficient data for analysis'}
        
        # Group metrics by operation
        operation_metrics = defaultdict(list)
        for metric in recent_metrics:
            operation_metrics[metric.operation].append(metric)
        
        bottlenecks = []
        operation_stats = {}
        
        for operation, metrics in operation_metrics.items():
            if len(metrics) < 5:  # Skip operations with too few samples
                continue
            
            successful_metrics = [m for m in metrics if m.success]
            failed_metrics = [m for m in metrics if not m.success]
            
            if successful_metrics:
                durations = [m.duration_ms for m in successful_metrics]
                cache_hits = sum(1 for m in successful_metrics if m.cache_hit)
                
                stats = {
                    'operation': operation,
                    'sample_count': len(metrics),
                    'success_rate': len(successful_metrics) / len(metrics),
                    'avg_duration_ms': statistics.mean(durations),
                    'p95_duration_ms': np.percentile(durations, 95),
                    'max_duration_ms': max(durations),
                    'cache_hit_rate': cache_hits / len(successful_metrics),
                    'error_count': len(failed_metrics)
                }
                
                operation_stats[operation] = stats
                
                # Identify potential bottlenecks
                if stats['avg_duration_ms'] > 500:  # Average > 500ms
                    bottlenecks.append({
                        'type': 'high_latency',
                        'operation': operation,
                        'severity': 'high' if stats['avg_duration_ms'] > 1000 else 'medium',
                        'avg_latency_ms': stats['avg_duration_ms'],
                        'description': f"High average latency: {stats['avg_duration_ms']:.1f}ms"
                    })
                
                if stats['success_rate'] < 0.95:  # Success rate < 95%
                    bottlenecks.append({
                        'type': 'high_error_rate',
                        'operation': operation,
                        'severity': 'high' if stats['success_rate'] < 0.9 else 'medium',
                        'success_rate': stats['success_rate'],
                        'error_count': stats['error_count'],
                        'description': f"High error rate: {(1-stats['success_rate'])*100:.1f}%"
                    })
                
                if stats['cache_hit_rate'] < 0.5 and 'cache' in operation.lower():
                    bottlenecks.append({
                        'type': 'low_cache_hit_rate',
                        'operation': operation,
                        'severity': 'medium',
                        'cache_hit_rate': stats['cache_hit_rate'],
                        'description': f"Low cache hit rate: {stats['cache_hit_rate']*100:.1f}%"
                    })
        
        # System resource analysis
        system_bottlenecks = self._analyze_system_bottlenecks()
        
        return {
            'analysis_period_minutes': recent_minutes,
            'total_samples': len(recent_metrics),
            'operation_stats': operation_stats,
            'bottlenecks': bottlenecks,
            'system_bottlenecks': system_bottlenecks,
            'recommendations': self._generate_recommendations(bottlenecks, operation_stats)
        }

    def _analyze_system_bottlenecks(self) -> List[Dict[str, Any]]:
        """Analyze system resource bottlenecks from monitoring data"""
        if not self.system_stats or len(self.system_stats) < 10:
            return []
        
        recent_stats = self.system_stats[-50:]  # Last 50 measurements
        system_bottlenecks = []
        
        # CPU analysis
        cpu_values = [s['cpu_percent'] for s in recent_stats]
        avg_cpu = statistics.mean(cpu_values)
        max_cpu = max(cpu_values)
        
        if avg_cpu > 80:
            system_bottlenecks.append({
                'type': 'high_cpu',
                'severity': 'high' if avg_cpu > 90 else 'medium',
                'avg_cpu': avg_cpu,
                'max_cpu': max_cpu,
                'description': f"High CPU usage: {avg_cpu:.1f}% average, {max_cpu:.1f}% peak"
            })
        
        # Memory analysis
        memory_values = [s['memory_percent'] for s in recent_stats]
        avg_memory = statistics.mean(memory_values)
        max_memory = max(memory_values)
        
        if avg_memory > 85:
            system_bottlenecks.append({
                'type': 'high_memory',
                'severity': 'high' if avg_memory > 95 else 'medium',
                'avg_memory': avg_memory,
                'max_memory': max_memory,
                'description': f"High memory usage: {avg_memory:.1f}% average, {max_memory:.1f}% peak"
            })
        
        return system_bottlenecks

    def _generate_recommendations(self, 
                                bottlenecks: List[Dict[str, Any]], 
                                operation_stats: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on bottleneck analysis"""
        recommendations = []
        
        # High latency recommendations
        high_latency_ops = [b for b in bottlenecks if b['type'] == 'high_latency']
        if high_latency_ops:
            for bottleneck in high_latency_ops:
                if 'jwks' in bottleneck['operation'].lower():
                    recommendations.append({
                        'priority': 'high',
                        'category': 'caching',
                        'title': 'Implement JWKS Caching',
                        'description': 'JWKS fetching is taking too long. Implement aggressive caching with 5-15 minute TTL.',
                        'expected_improvement': '15-25%',
                        'implementation_effort': 'low'
                    })
                
                if 'jwt' in bottleneck['operation'].lower():
                    recommendations.append({
                        'priority': 'high', 
                        'category': 'caching',
                        'title': 'Implement JWT Validation Caching',
                        'description': 'JWT validation is slow. Cache validated tokens for 2-5 minutes.',
                        'expected_improvement': '25-35%',
                        'implementation_effort': 'medium'
                    })
        
        # Cache hit rate recommendations
        low_cache_ops = [b for b in bottlenecks if b['type'] == 'low_cache_hit_rate']
        if low_cache_ops:
            recommendations.append({
                'priority': 'medium',
                'category': 'caching',
                'title': 'Optimize Cache Strategy',
                'description': 'Cache hit rates are low. Review cache TTL settings and invalidation logic.',
                'expected_improvement': '10-20%',
                'implementation_effort': 'medium'
            })
        
        # Error rate recommendations
        high_error_ops = [b for b in bottlenecks if b['type'] == 'high_error_rate']
        if high_error_ops:
            recommendations.append({
                'priority': 'critical',
                'category': 'reliability',
                'title': 'Investigate Authentication Failures',
                'description': 'High error rates detected. Review logs and implement retry mechanisms.',
                'expected_improvement': 'Improved reliability',
                'implementation_effort': 'high'
            })
        
        # Database connection recommendations
        db_ops = [op for op in operation_stats if 'database' in op.lower() or 'db' in op.lower()]
        if db_ops and any(operation_stats[op]['avg_duration_ms'] > 200 for op in db_ops):
            recommendations.append({
                'priority': 'high',
                'category': 'database',
                'title': 'Implement Database Connection Pooling',
                'description': 'Database operations are slow. Implement connection pooling and query optimization.',
                'expected_improvement': '30-50%',
                'implementation_effort': 'high'
            })
        
        return recommendations

    async def generate_performance_report(self, 
                                        include_system_stats: bool = True,
                                        include_recommendations: bool = True) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        
        # Basic statistics
        total_metrics = len(self.metrics)
        successful_metrics = [m for m in self.metrics if m.success]
        failed_metrics = [m for m in self.metrics if not m.success]
        
        # Recent performance analysis
        bottleneck_analysis = self.analyze_bottlenecks()
        
        # Phase comparison
        phase_stats = self._calculate_phase_statistics()
        
        # Improvement calculations
        improvements = {}
        if self.baseline_metrics and self.benchmarks:
            latest_benchmarks = {b.test_name: b for b in self.benchmarks[-len(self.baseline_metrics):]}
            improvements = self.calculate_improvement(latest_benchmarks)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_measurements': total_metrics,
                'success_rate': len(successful_metrics) / total_metrics if total_metrics > 0 else 0,
                'current_phase': self.current_phase,
                'monitoring_duration_hours': (
                    (datetime.now() - self.metrics[0].timestamp).total_seconds() / 3600
                    if self.metrics else 0
                )
            },
            'phase_statistics': phase_stats,
            'performance_improvements': improvements,
            'bottleneck_analysis': bottleneck_analysis if include_recommendations else None,
            'benchmarks': [
                {
                    'test_name': b.test_name,
                    'phase': b.phase,
                    'avg_latency_ms': b.avg_latency_ms,
                    'p95_latency_ms': b.p95_latency_ms,
                    'requests_per_second': b.requests_per_second,
                    'cache_hit_rate': b.cache_hit_rate,
                    'error_rate': b.error_rate,
                    'timestamp': b.timestamp.isoformat()
                }
                for b in self.benchmarks[-10:]  # Last 10 benchmarks
            ]
        }
        
        if include_system_stats and self.system_stats:
            report['system_statistics'] = self._summarize_system_stats()
        
        return report

    def _calculate_phase_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistics grouped by phase"""
        phase_metrics = defaultdict(list)
        
        for metric in self.metrics:
            if metric.success:
                phase_metrics[metric.phase].append(metric.duration_ms)
        
        phase_stats = {}
        for phase, durations in phase_metrics.items():
            if durations:
                phase_stats[phase] = {
                    'count': len(durations),
                    'avg_latency_ms': statistics.mean(durations),
                    'median_latency_ms': statistics.median(durations),
                    'p95_latency_ms': np.percentile(durations, 95),
                    'min_latency_ms': min(durations),
                    'max_latency_ms': max(durations)
                }
        
        return phase_stats

    def _summarize_system_stats(self) -> Dict[str, Any]:
        """Summarize system monitoring statistics"""
        if not self.system_stats:
            return {}
        
        recent_stats = self.system_stats[-100:]  # Last 100 measurements
        
        return {
            'measurement_count': len(recent_stats),
            'cpu': {
                'avg_percent': statistics.mean(s['cpu_percent'] for s in recent_stats),
                'max_percent': max(s['cpu_percent'] for s in recent_stats),
                'min_percent': min(s['cpu_percent'] for s in recent_stats)
            },
            'memory': {
                'avg_percent': statistics.mean(s['memory_percent'] for s in recent_stats),
                'max_percent': max(s['memory_percent'] for s in recent_stats),
                'avg_used_mb': statistics.mean(s['memory_used_mb'] for s in recent_stats)
            },
            'network': {
                'avg_sent_mb': statistics.mean(s['network_sent_mb'] for s in recent_stats),
                'avg_recv_mb': statistics.mean(s['network_recv_mb'] for s in recent_stats)
            }
        }

    async def _persist_metric(self, metric: PerformanceMetric):
        """Persist a single metric to storage"""
        if not self.store_metrics:
            return
            
        try:
            # Convert metric to dictionary
            metric_dict = {
                'timestamp': metric.timestamp.isoformat(),
                'operation': metric.operation,
                'duration_ms': metric.duration_ms,
                'success': metric.success,
                'phase': metric.phase,
                'cache_hit': metric.cache_hit,
                'metadata': metric.metadata
            }
            
            # Append to metrics file
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metric_dict) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to persist metric: {e}")

    async def _persist_benchmark(self, benchmark: BenchmarkResult):
        """Persist benchmark result to storage"""
        if not self.store_metrics:
            return
            
        try:
            benchmark_file = self.metrics_file.parent / "benchmarks.json"
            
            benchmark_dict = {
                'test_name': benchmark.test_name,
                'phase': benchmark.phase,
                'total_requests': benchmark.total_requests,
                'success_count': benchmark.success_count,
                'failure_count': benchmark.failure_count,
                'avg_latency_ms': benchmark.avg_latency_ms,
                'median_latency_ms': benchmark.median_latency_ms,
                'p95_latency_ms': benchmark.p95_latency_ms,
                'p99_latency_ms': benchmark.p99_latency_ms,
                'min_latency_ms': benchmark.min_latency_ms,
                'max_latency_ms': benchmark.max_latency_ms,
                'requests_per_second': benchmark.requests_per_second,
                'cache_hit_rate': benchmark.cache_hit_rate,
                'error_rate': benchmark.error_rate,
                'timestamp': benchmark.timestamp.isoformat(),
                'metadata': benchmark.metadata
            }
            
            with open(benchmark_file, 'a') as f:
                f.write(json.dumps(benchmark_dict) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to persist benchmark: {e}")

    async def export_metrics_csv(self, output_path: str):
        """Export metrics to CSV for analysis"""
        try:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'timestamp', 'operation', 'duration_ms', 'success', 
                    'phase', 'cache_hit', 'metadata'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for metric in self.metrics:
                    writer.writerow({
                        'timestamp': metric.timestamp.isoformat(),
                        'operation': metric.operation,
                        'duration_ms': metric.duration_ms,
                        'success': metric.success,
                        'phase': metric.phase,
                        'cache_hit': metric.cache_hit,
                        'metadata': json.dumps(metric.metadata)
                    })
            
            logger.info(f"📊 Metrics exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export metrics to CSV: {e}")

# Global monitor instance
performance_monitor = AuthPerformanceMonitor()

# Utility functions for easy integration
async def measure_auth_operation(operation_name: str, operation_func, *args, **kwargs):
    """Convenience function to measure any authentication operation"""
    return await performance_monitor.measure_operation(
        operation=operation_name,
        operation_func=operation_func,
        *args,
        **kwargs
    )

def get_performance_summary() -> Dict[str, Any]:
    """Get quick performance summary"""
    if not performance_monitor.metrics:
        return {"status": "No metrics collected yet"}
    
    recent_metrics = performance_monitor.metrics[-100:]  # Last 100
    successful_metrics = [m for m in recent_metrics if m.success]
    
    if successful_metrics:
        durations = [m.duration_ms for m in successful_metrics]
        return {
            "status": "active",
            "recent_measurements": len(recent_metrics),
            "success_rate": len(successful_metrics) / len(recent_metrics),
            "avg_latency_ms": statistics.mean(durations),
            "p95_latency_ms": np.percentile(durations, 95),
            "current_phase": performance_monitor.current_phase
        }
    
    return {"status": "errors", "recent_failures": len(recent_metrics)}

# Context manager for operation measurement
@asynccontextmanager
async def measure_performance(operation_name: str, metadata: Dict[str, Any] = None):
    """Context manager for measuring operation performance"""
    start_time = time.perf_counter()
    timestamp = datetime.now()
    success = False
    
    try:
        yield
        success = True
    finally:
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        metric = PerformanceMetric(
            timestamp=timestamp,
            operation=operation_name,
            duration_ms=duration_ms,
            success=success,
            phase=performance_monitor.current_phase,
            metadata=metadata or {}
        )
        
        performance_monitor.metrics.append(metric)
        if performance_monitor.store_metrics:
            await performance_monitor._persist_metric(metric)