"""
Authentication Performance Monitoring Package
===========================================

This package provides comprehensive performance monitoring, benchmarking, and
architecture analysis tools for the authentication optimization project.

Key Components:
1. AuthPerformanceMonitor - Real-time performance metrics collection
2. AuthBenchmarker - Comprehensive benchmarking and validation
3. AuthArchitectureAnalyzer - Architecture analysis and optimization strategy
4. Performance Dashboard - Monitoring and reporting utilities

Usage:
    from backend.app.performance import (
        performance_monitor,
        auth_benchmarker, 
        architecture_analyzer,
        measure_auth_operation,
        get_performance_summary,
        run_quick_baseline
    )
    
    # Start monitoring
    await performance_monitor.start_system_monitoring()
    
    # Run baseline benchmarks
    baseline = await run_quick_baseline()
    
    # Measure specific operations
    result, metric = await measure_auth_operation(
        'jwt_validation',
        your_jwt_validation_function,
        token=jwt_token
    )
    
    # Get performance summary
    summary = get_performance_summary()
"""

from .auth_metrics import (
    AuthPerformanceMonitor,
    PerformanceMetric,
    BenchmarkResult,
    performance_monitor,
    measure_auth_operation,
    get_performance_summary,
    measure_performance
)

from .benchmarker import (
    AuthBenchmarker,
    BenchmarkScenario,
    auth_benchmarker,
    run_quick_baseline,
    benchmark_phase,
    validate_phase_performance
)

from .architecture_analyzer import (
    AuthArchitectureAnalyzer,
    ArchitectureComponent,
    OptimizationPhase,
    BottleneckAnalysis,
    architecture_analyzer,
    analyze_architecture,
    design_optimization,
    export_documentation
)

# Package version
__version__ = "1.0.0"

# Export main classes and functions
__all__ = [
    # Core classes
    'AuthPerformanceMonitor',
    'AuthBenchmarker', 
    'AuthArchitectureAnalyzer',
    
    # Data classes
    'PerformanceMetric',
    'BenchmarkResult',
    'BenchmarkScenario',
    'ArchitectureComponent',
    'OptimizationPhase',
    'BottleneckAnalysis',
    
    # Global instances
    'performance_monitor',
    'auth_benchmarker',
    'architecture_analyzer',
    
    # Utility functions
    'measure_auth_operation',
    'get_performance_summary',
    'measure_performance',
    'run_quick_baseline',
    'benchmark_phase',
    'validate_phase_performance',
    'analyze_architecture',
    'design_optimization',
    'export_documentation',
]

# Package metadata
__author__ = "Lead Performance Architect"
__description__ = "Authentication Performance Monitoring and Optimization Tools"
__license__ = "MIT"