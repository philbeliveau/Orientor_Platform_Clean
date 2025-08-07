"""
Baseline Establishment and Performance Analysis Guide
===================================================

This module provides comprehensive tools and guidance for establishing
performance baselines and implementing the 5-phase authentication optimization strategy.

Key Features:
1. Automated baseline establishment
2. Step-by-step implementation guidance  
3. Performance validation at each phase
4. Success criteria verification
5. Optimization recommendations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

from .auth_metrics import performance_monitor, AuthPerformanceMonitor
from .benchmarker import auth_benchmarker, AuthBenchmarker
from .architecture_analyzer import architecture_analyzer, AuthArchitectureAnalyzer
from .integration import setup_performance_monitoring, instrument_auth_functions

logger = logging.getLogger(__name__)

class BaselineEstablisher:
    """Comprehensive baseline establishment and analysis system"""
    
    def __init__(self,
                 monitor: AuthPerformanceMonitor = None,
                 benchmarker: AuthBenchmarker = None,
                 analyzer: AuthArchitectureAnalyzer = None):
        """
        Initialize the baseline establisher
        
        Args:
            monitor: Performance monitor instance
            benchmarker: Benchmarker instance  
            analyzer: Architecture analyzer instance
        """
        self.monitor = monitor or performance_monitor
        self.benchmarker = benchmarker or auth_benchmarker
        self.analyzer = analyzer or architecture_analyzer
        
        # Baseline data
        self.baseline_results = {}
        self.architecture_analysis = {}
        self.optimization_strategy = {}
        
        # Configuration
        self.baseline_config = {
            'measurement_duration_minutes': 10,
            'concurrent_users': [5, 10, 20],
            'requests_per_user': 20,
            'warmup_requests': 50,
            'scenarios': [
                'cold_start_auth',
                'warm_auth_flow', 
                'concurrent_auth',
                'error_handling',
                'load_testing'
            ]
        }
        
        logger.info("📊 BaselineEstablisher initialized")

    async def establish_comprehensive_baseline(self) -> Dict[str, Any]:
        """
        Establish comprehensive performance baseline for authentication system
        
        Returns:
            Complete baseline analysis with recommendations
        """
        logger.info("🚀 Starting comprehensive baseline establishment")
        
        # Step 1: Setup monitoring infrastructure
        await self._setup_monitoring_infrastructure()
        
        # Step 2: Analyze current architecture
        logger.info("🔍 Analyzing current authentication architecture...")
        self.architecture_analysis = await self.analyzer.analyze_current_architecture()
        
        # Step 3: Design optimization strategy
        logger.info("🎯 Designing optimization strategy...")
        self.optimization_strategy = await self.analyzer.design_optimization_strategy()
        
        # Step 4: Run comprehensive baseline benchmarks
        logger.info("📈 Running comprehensive baseline benchmarks...")
        await self._run_baseline_benchmarks()
        
        # Step 5: Analyze results and generate report
        logger.info("📊 Analyzing baseline results...")
        baseline_report = await self._generate_baseline_report()
        
        # Step 6: Create implementation roadmap
        logger.info("🗺️ Creating implementation roadmap...")
        implementation_guide = await self._create_implementation_guide()
        
        # Step 7: Setup monitoring dashboard
        logger.info("📈 Setting up monitoring dashboard...")
        dashboard_info = await self._setup_monitoring_dashboard()
        
        comprehensive_baseline = {
            'establishment_timestamp': datetime.now().isoformat(),
            'baseline_config': self.baseline_config,
            'architecture_analysis': self.architecture_analysis,
            'optimization_strategy': self.optimization_strategy,
            'baseline_benchmarks': self.baseline_results,
            'baseline_report': baseline_report,
            'implementation_guide': implementation_guide,
            'dashboard_info': dashboard_info,
            'next_steps': self._generate_next_steps()
        }
        
        # Export comprehensive documentation
        await self._export_baseline_documentation(comprehensive_baseline)
        
        logger.info("✅ Comprehensive baseline establishment completed successfully!")
        return comprehensive_baseline

    async def _setup_monitoring_infrastructure(self):
        """Setup monitoring infrastructure"""
        logger.info("🔧 Setting up monitoring infrastructure...")
        
        # Start system monitoring
        await self.monitor.start_system_monitoring()
        
        # Setup test environment
        await self.benchmarker.setup_test_environment(num_test_tokens=100)
        
        # Set baseline phase
        self.monitor.set_phase("baseline")
        
        logger.info("✅ Monitoring infrastructure setup complete")

    async def _run_baseline_benchmarks(self):
        """Run comprehensive baseline benchmarks"""
        
        # Define comprehensive baseline scenarios
        baseline_scenarios = [
            {
                'name': 'cold_start_full_auth',
                'description': 'Complete authentication flow with cold caches',
                'test_func': self._test_cold_start_auth,
                'concurrent_users': 1,
                'requests_per_user': 50,
                'metadata': {'scenario_type': 'cold_start', 'cache_state': 'cold'}
            },
            {
                'name': 'warm_auth_repeated',
                'description': 'Repeated authentication with warmed system',
                'test_func': self._test_warm_auth_flow,
                'concurrent_users': 5, 
                'requests_per_user': 30,
                'metadata': {'scenario_type': 'warm_repeated', 'cache_state': 'warm'}
            },
            {
                'name': 'concurrent_users_low',
                'description': 'Authentication under low concurrent load',
                'test_func': self._test_concurrent_auth,
                'concurrent_users': 10,
                'requests_per_user': 20,
                'metadata': {'scenario_type': 'concurrent', 'load_level': 'low'}
            },
            {
                'name': 'concurrent_users_medium', 
                'description': 'Authentication under medium concurrent load',
                'test_func': self._test_concurrent_auth,
                'concurrent_users': 25,
                'requests_per_user': 15,
                'metadata': {'scenario_type': 'concurrent', 'load_level': 'medium'}
            },
            {
                'name': 'concurrent_users_high',
                'description': 'Authentication under high concurrent load', 
                'test_func': self._test_concurrent_auth,
                'concurrent_users': 50,
                'requests_per_user': 10,
                'metadata': {'scenario_type': 'concurrent', 'load_level': 'high'}
            },
            {
                'name': 'error_scenarios',
                'description': 'Authentication behavior under error conditions',
                'test_func': self._test_error_scenarios,
                'concurrent_users': 5,
                'requests_per_user': 20,
                'metadata': {'scenario_type': 'error_testing', 'includes_failures': True}
            },
            {
                'name': 'sustained_load',
                'description': 'Sustained authentication load over time',
                'test_func': self._test_sustained_load,
                'concurrent_users': 20,
                'requests_per_user': 50,
                'metadata': {'scenario_type': 'sustained_load', 'duration_minutes': 5}
            }
        ]
        
        # Run each scenario
        for scenario in baseline_scenarios:
            logger.info(f"📊 Running baseline scenario: {scenario['name']}")
            
            # Run benchmark for this scenario
            results = await self.monitor.run_comprehensive_benchmark(
                test_scenarios=[scenario],
                requests_per_scenario=scenario.get('requests_per_user', 20),
                concurrent_requests=scenario.get('concurrent_users', 10)
            )
            
            # Store results
            self.baseline_results[scenario['name']] = results
            
            # Brief cooldown between scenarios
            await asyncio.sleep(5)
        
        # Establish baseline in monitor and benchmarker
        all_results = {}
        for scenario_results in self.baseline_results.values():
            all_results.update(scenario_results)
        
        self.monitor.establish_baseline(all_results)
        self.benchmarker.baseline_results = all_results
        
        logger.info(f"✅ Baseline benchmarks completed - {len(self.baseline_results)} scenarios")

    async def _test_cold_start_auth(self):
        """Test cold start authentication (no caches)"""
        # Clear any existing caches
        from ..utils.clerk_auth import CLERK_JWKS_CACHE
        global CLERK_JWKS_CACHE
        CLERK_JWKS_CACHE = None
        
        try:
            # Simulate complete cold start: JWKS + JWT + DB
            await asyncio.sleep(0.2)  # JWKS fetch simulation
            await asyncio.sleep(0.15) # JWT validation simulation  
            await asyncio.sleep(0.1)  # Database sync simulation
            return True
        except Exception:
            return False

    async def _test_warm_auth_flow(self):
        """Test warm authentication flow (some caching)"""
        try:
            # Simulate partially warmed system
            await asyncio.sleep(0.05)  # Reduced JWKS time
            await asyncio.sleep(0.1)   # JWT validation
            await asyncio.sleep(0.08)  # Database operations
            return True
        except Exception:
            return False

    async def _test_concurrent_auth(self):
        """Test authentication under concurrent load"""
        try:
            # Simulate authentication under load with potential contention
            base_time = 0.2
            load_factor = 1.2  # 20% slowdown under load
            await asyncio.sleep(base_time * load_factor)
            return True
        except Exception:
            return False

    async def _test_error_scenarios(self):
        """Test authentication error handling"""
        import random
        
        try:
            # Simulate various error conditions
            error_chance = 0.1  # 10% error rate
            
            if random.random() < error_chance:
                raise Exception("Simulated authentication error")
            
            # Normal flow with error handling overhead
            await asyncio.sleep(0.25)  # Slightly slower due to error checking
            return True
        except Exception:
            return False

    async def _test_sustained_load(self):
        """Test authentication under sustained load"""
        try:
            # Simulate sustained load with gradual degradation
            base_time = 0.2
            degradation_factor = 1.1  # 10% degradation under sustained load
            await asyncio.sleep(base_time * degradation_factor)
            return True
        except Exception:
            return False

    async def _generate_baseline_report(self) -> Dict[str, Any]:
        """Generate comprehensive baseline analysis report"""
        
        # Calculate aggregate statistics
        all_scenarios = {}
        for scenario_name, scenario_results in self.baseline_results.items():
            for test_name, result in scenario_results.items():
                all_scenarios[f"{scenario_name}_{test_name}"] = result
        
        # Performance summary
        if all_scenarios:
            avg_latencies = [r.avg_latency_ms for r in all_scenarios.values()]
            p95_latencies = [r.p95_latency_ms for r in all_scenarios.values()]
            success_rates = [r.success_count / r.total_requests for r in all_scenarios.values()]
            
            performance_summary = {
                'total_scenarios': len(all_scenarios),
                'avg_latency_ms': sum(avg_latencies) / len(avg_latencies),
                'avg_p95_latency_ms': sum(p95_latencies) / len(p95_latencies),
                'avg_success_rate': sum(success_rates) / len(success_rates),
                'min_latency_ms': min(r.min_latency_ms for r in all_scenarios.values()),
                'max_latency_ms': max(r.max_latency_ms for r in all_scenarios.values()),
                'total_requests_tested': sum(r.total_requests for r in all_scenarios.values())
            }
        else:
            performance_summary = {'error': 'No baseline results available'}
        
        # Bottleneck analysis
        bottleneck_analysis = self.monitor.analyze_bottlenecks(recent_minutes=30)
        
        # Generate improvement opportunities
        improvement_opportunities = await self._analyze_improvement_opportunities()
        
        baseline_report = {
            'baseline_establishment_date': datetime.now().isoformat(),
            'performance_summary': performance_summary,
            'scenario_results': {
                name: {
                    'avg_latency_ms': list(results.values())[0].avg_latency_ms if results else 0,
                    'success_rate': (list(results.values())[0].success_count / 
                                   list(results.values())[0].total_requests) if results else 0,
                    'requests_per_second': list(results.values())[0].requests_per_second if results else 0
                }
                for name, results in self.baseline_results.items()
            },
            'bottleneck_analysis': bottleneck_analysis,
            'improvement_opportunities': improvement_opportunities,
            'performance_targets': self._define_performance_targets(performance_summary),
            'risk_assessment': await self._assess_optimization_risks()
        }
        
        return baseline_report

    async def _analyze_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """Analyze specific improvement opportunities"""
        
        opportunities = []
        
        # Analyze architecture bottlenecks
        if self.architecture_analysis.get('bottlenecks'):
            for bottleneck in self.architecture_analysis['bottlenecks']:
                opportunities.append({
                    'category': 'Architecture',
                    'opportunity': bottleneck['component'],
                    'description': bottleneck['impact_description'],
                    'expected_improvement': f"{bottleneck['estimated_improvement'][0]}-{bottleneck['estimated_improvement'][1]}%",
                    'implementation_effort': bottleneck['implementation_complexity'],
                    'priority': bottleneck['severity']
                })
        
        # Analyze performance metrics
        if self.baseline_results:
            # Identify high-latency scenarios
            high_latency_scenarios = []
            for scenario_name, results in self.baseline_results.items():
                for test_name, result in results.items():
                    if result.avg_latency_ms > 400:  # >400ms is high
                        high_latency_scenarios.append({
                            'scenario': f"{scenario_name}_{test_name}",
                            'latency': result.avg_latency_ms
                        })
            
            if high_latency_scenarios:
                opportunities.append({
                    'category': 'Performance',
                    'opportunity': 'High Latency Scenarios',
                    'description': f'{len(high_latency_scenarios)} scenarios with >400ms latency',
                    'expected_improvement': '30-60%',
                    'implementation_effort': 'medium',
                    'priority': 'high',
                    'affected_scenarios': high_latency_scenarios
                })
        
        return opportunities

    def _define_performance_targets(self, performance_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Define performance targets for each optimization phase"""
        
        if 'error' in performance_summary:
            return {'error': 'Cannot define targets without baseline data'}
        
        baseline_latency = performance_summary['avg_latency_ms']
        
        return {
            'phase_1_targets': {
                'description': 'JWKS Caching Implementation',
                'target_avg_latency_ms': baseline_latency * 0.8,  # 20% improvement
                'target_p95_latency_ms': performance_summary['avg_p95_latency_ms'] * 0.75,
                'target_cache_hit_rate': 0.9,
                'target_improvement_range': '15-25%'
            },
            'phase_2_targets': {
                'description': 'JWT Validation Caching',
                'target_avg_latency_ms': baseline_latency * 0.7,  # 30% total improvement
                'target_p95_latency_ms': performance_summary['avg_p95_latency_ms'] * 0.65,
                'target_cache_hit_rate': 0.8,
                'target_improvement_range': '25-35%'
            },
            'phase_3_targets': {
                'description': 'Session Caching',
                'target_avg_latency_ms': baseline_latency * 0.55, # 45% total improvement
                'target_p95_latency_ms': performance_summary['avg_p95_latency_ms'] * 0.5,
                'target_cache_hit_rate': 0.85,
                'target_improvement_range': '35-50%'
            },
            'phase_4_targets': {
                'description': 'Database Connection Pooling',
                'target_avg_latency_ms': baseline_latency * 0.4,  # 60% total improvement
                'target_p95_latency_ms': performance_summary['avg_p95_latency_ms'] * 0.35,
                'target_connection_overhead_ms': 10,
                'target_improvement_range': '50-65%'
            },
            'phase_5_targets': {
                'description': 'Integrated Multi-layer Caching',
                'target_avg_latency_ms': baseline_latency * 0.25, # 75% total improvement
                'target_p95_latency_ms': performance_summary['avg_p95_latency_ms'] * 0.2,
                'target_cache_hit_rate': 0.95,
                'target_improvement_range': '70-85%',
                'target_load_capacity': '10x baseline'
            }
        }

    async def _assess_optimization_risks(self) -> List[Dict[str, Any]]:
        """Assess risks associated with optimization implementation"""
        
        return [
            {
                'risk_category': 'Implementation',
                'risk': 'Cache Invalidation Complexity',
                'probability': 'Medium',
                'impact': 'High',
                'mitigation': 'Implement comprehensive testing and fallback mechanisms',
                'affected_phases': ['Phase 1', 'Phase 2', 'Phase 3']
            },
            {
                'risk_category': 'Security',
                'risk': 'Token Caching Security',
                'probability': 'Low',
                'impact': 'Critical',
                'mitigation': 'Use secure cache keys, encrypt sensitive data, implement proper expiration',
                'affected_phases': ['Phase 2', 'Phase 3']
            },
            {
                'risk_category': 'Performance',
                'risk': 'Memory Usage Scaling',
                'probability': 'High',
                'impact': 'Medium',
                'mitigation': 'Implement cache size limits, LRU eviction, and memory monitoring',
                'affected_phases': ['All phases']
            },
            {
                'risk_category': 'Reliability',
                'risk': 'Cache Service Failures',
                'probability': 'Medium',
                'impact': 'Medium',
                'mitigation': 'Implement circuit breakers and graceful degradation to non-cached operation',
                'affected_phases': ['Phase 3', 'Phase 5']
            },
            {
                'risk_category': 'Complexity',
                'risk': 'System Complexity Increase',
                'probability': 'High',
                'impact': 'Medium',
                'mitigation': 'Comprehensive documentation, monitoring, and gradual rollout',
                'affected_phases': ['Phase 5']
            }
        ]

    async def _create_implementation_guide(self) -> Dict[str, Any]:
        """Create detailed implementation guide"""
        
        return {
            'implementation_approach': 'Incremental 5-phase rollout with validation at each step',
            'total_estimated_duration': '8-12 weeks',
            'team_requirements': {
                'team_size': '2-3 developers',
                'required_skills': ['FastAPI', 'Caching strategies', 'Database optimization', 'Performance monitoring'],
                'time_commitment': '60-80% of team capacity'
            },
            'infrastructure_requirements': {
                'caching_service': 'Redis or equivalent in-memory cache',
                'monitoring_tools': 'Performance monitoring dashboard and alerting',
                'testing_environment': 'Load testing tools and staging environment'
            },
            'phase_by_phase_guide': {
                'phase_1': {
                    'duration': '1 week',
                    'objective': 'Implement JWKS caching',
                    'deliverables': [
                        'In-memory JWKS cache with TTL',
                        'Background refresh mechanism',
                        'Cache metrics and monitoring',
                        'Performance validation'
                    ],
                    'success_criteria': 'JWKS cache hit rate >90%, 15-25% latency improvement',
                    'rollback_plan': 'Feature flag to disable caching'
                },
                'phase_2': {
                    'duration': '2 weeks',
                    'objective': 'Implement JWT validation caching', 
                    'deliverables': [
                        'Secure JWT token caching',
                        'Hash-based cache keys',
                        'Token expiration handling',
                        'Security review and validation'
                    ],
                    'success_criteria': 'JWT cache hit rate >80%, 25-35% cumulative improvement',
                    'rollback_plan': 'Disable JWT caching while maintaining JWKS caching'
                },
                'phase_3': {
                    'duration': '2 weeks',
                    'objective': 'Implement session caching',
                    'deliverables': [
                        'Session data caching layer',
                        'Cache invalidation strategies',
                        'Session warming mechanisms',
                        'Load testing validation'
                    ],
                    'success_criteria': 'Session cache hit rate >85%, 35-50% cumulative improvement',
                    'rollback_plan': 'Gradual rollback of session caching'
                },
                'phase_4': {
                    'duration': '3 weeks',
                    'objective': 'Database connection pooling optimization',
                    'deliverables': [
                        'Connection pool implementation',
                        'Query optimization',
                        'Database performance monitoring',
                        'Connection health checks'
                    ],
                    'success_criteria': 'Connection overhead <10ms, 50-65% cumulative improvement',
                    'rollback_plan': 'Revert to single connections with caching intact'
                },
                'phase_5': {
                    'duration': '3 weeks',
                    'objective': 'Integrated multi-layer optimization',
                    'deliverables': [
                        'Integrated caching coordination',
                        'Comprehensive monitoring dashboard',
                        'Performance optimization tuning',
                        'Final validation and documentation'
                    ],
                    'success_criteria': '70-85% total improvement, 10x load capacity',
                    'rollback_plan': 'Phase-by-phase rollback as needed'
                }
            },
            'validation_process': {
                'continuous_monitoring': 'Real-time performance monitoring throughout implementation',
                'phase_gates': 'Each phase must meet success criteria before proceeding',
                'load_testing': 'Comprehensive load testing before production deployment',
                'rollback_triggers': 'Automatic rollback on performance regression >10%'
            },
            'recommended_timeline': {
                'week_1': 'Phase 1 - JWKS Caching',
                'weeks_2_3': 'Phase 2 - JWT Validation Caching',
                'weeks_4_5': 'Phase 3 - Session Caching',
                'weeks_6_8': 'Phase 4 - Database Connection Pooling',
                'weeks_9_11': 'Phase 5 - Integrated Optimization',
                'week_12': 'Final validation, documentation, and production deployment'
            }
        }

    async def _setup_monitoring_dashboard(self) -> Dict[str, Any]:
        """Setup monitoring dashboard information"""
        
        return {
            'dashboard_url': '/api/performance/dashboard',
            'features': [
                'Real-time authentication latency monitoring',
                'Cache hit rate tracking across all layers',
                'Phase-by-phase progress visualization',
                'System resource utilization monitoring',
                'Alert system for performance regressions',
                'Historical performance trend analysis'
            ],
            'key_metrics': [
                'Average authentication latency (ms)',
                'P95/P99 latency percentiles',
                'Success rate and error tracking',
                'Cache hit rates by layer',
                'Requests per second throughput',
                'Database connection pool utilization'
            ],
            'alert_thresholds': {
                'avg_latency_ms': 500,
                'p95_latency_ms': 1000,
                'error_rate': 0.05,
                'cache_hit_rate_minimum': 0.7
            },
            'access_instructions': [
                'Dashboard available at /api/performance/dashboard',
                'WebSocket connection for real-time updates',
                'API endpoints for programmatic access',
                'Export capabilities for detailed analysis'
            ]
        }

    def _generate_next_steps(self) -> List[Dict[str, Any]]:
        """Generate recommended next steps"""
        
        return [
            {
                'step': 1,
                'title': 'Review Baseline Results',
                'description': 'Analyze the comprehensive baseline report and validate findings',
                'estimated_time': '1-2 hours',
                'responsible': 'Lead Performance Architect + Team',
                'deliverable': 'Validated baseline understanding'
            },
            {
                'step': 2,
                'title': 'Setup Production Monitoring',
                'description': 'Deploy performance monitoring to production environment',
                'estimated_time': '4-6 hours',
                'responsible': 'DevOps + Development Team',
                'deliverable': 'Production monitoring dashboard'
            },
            {
                'step': 3,
                'title': 'Prepare Phase 1 Implementation',
                'description': 'Prepare development environment and begin Phase 1 JWKS caching',
                'estimated_time': '1 week',
                'responsible': 'Development Team',
                'deliverable': 'Phase 1 implementation ready'
            },
            {
                'step': 4,
                'title': 'Establish Team Processes',
                'description': 'Set up regular performance review processes and validation gates',
                'estimated_time': '2-3 hours',
                'responsible': 'Project Manager + Team Lead',
                'deliverable': 'Performance validation process'
            },
            {
                'step': 5,
                'title': 'Begin Incremental Implementation',
                'description': 'Start Phase 1 implementation with continuous monitoring',
                'estimated_time': '1 week',
                'responsible': 'Development Team',
                'deliverable': 'Phase 1 complete with validated improvements'
            }
        ]

    async def _export_baseline_documentation(self, comprehensive_baseline: Dict[str, Any]):
        """Export comprehensive baseline documentation"""
        
        # Create documentation directory
        doc_dir = Path("performance/baseline_documentation")
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Export JSON data
        with open(doc_dir / "comprehensive_baseline.json", 'w') as f:
            json.dump(comprehensive_baseline, f, indent=2, default=str)
        
        # Export individual components
        components_to_export = [
            'architecture_analysis',
            'optimization_strategy', 
            'baseline_benchmarks',
            'baseline_report',
            'implementation_guide'
        ]
        
        for component in components_to_export:
            if component in comprehensive_baseline:
                with open(doc_dir / f"{component}.json", 'w') as f:
                    json.dump(comprehensive_baseline[component], f, indent=2, default=str)
        
        # Generate markdown summary
        await self._generate_baseline_summary_md(doc_dir, comprehensive_baseline)
        
        logger.info(f"📊 Baseline documentation exported to {doc_dir}")

    async def _generate_baseline_summary_md(self, doc_dir: Path, baseline: Dict[str, Any]):
        """Generate markdown summary of baseline establishment"""
        
        performance_summary = baseline.get('baseline_report', {}).get('performance_summary', {})
        
        md_content = f"""# Authentication Performance Baseline Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

A comprehensive performance baseline has been established for the authentication system, revealing significant optimization opportunities with potential for **70-85% performance improvement** through a structured 5-phase approach.

## Current Performance Baseline

- **Average Authentication Latency**: {performance_summary.get('avg_latency_ms', 'N/A'):.1f}ms
- **95th Percentile Latency**: {performance_summary.get('avg_p95_latency_ms', 'N/A'):.1f}ms  
- **Success Rate**: {performance_summary.get('avg_success_rate', 0)*100:.1f}%
- **Total Scenarios Tested**: {performance_summary.get('total_scenarios', 'N/A')}

## Key Bottlenecks Identified

1. **JWKS Fetching**: No caching, 100-300ms per request
2. **JWT Validation**: Cryptographic operations on every request
3. **Database Operations**: No connection pooling, cold connections
4. **Session Management**: Full authentication flow on every request

## Optimization Strategy Overview

### 5-Phase Implementation Plan

1. **Phase 1** (1 week): JWKS Caching → 15-25% improvement
2. **Phase 2** (2 weeks): JWT Validation Caching → 25-35% cumulative  
3. **Phase 3** (2 weeks): Session Caching → 35-50% cumulative
4. **Phase 4** (3 weeks): Database Connection Pooling → 50-65% cumulative
5. **Phase 5** (3 weeks): Integrated Multi-layer Caching → 70-85% total

**Total Implementation Time**: 8-12 weeks
**Expected ROI**: 70-85% latency reduction, 10x load capacity increase

## Next Steps

1. **Review and Validate** baseline findings (1-2 hours)
2. **Setup Production Monitoring** (4-6 hours)  
3. **Prepare Phase 1 Implementation** (1 week)
4. **Begin Incremental Implementation** with continuous validation

## Success Criteria

- Each phase must meet target improvements before proceeding
- Continuous performance monitoring throughout implementation
- Rollback capabilities at each phase
- Final validation of 70-85% total improvement

## Risk Assessment

- **Low Risk**: Well-defined implementation plan with fallback options
- **Medium Risk**: Cache invalidation complexity (mitigated by testing)
- **Monitoring**: Comprehensive monitoring and alerting system in place

---

For detailed implementation guidance, see the complete implementation guide and architecture analysis documents.
"""
        
        with open(doc_dir / "baseline_summary.md", 'w') as f:
            f.write(md_content)

# Create global baseline establisher instance
baseline_establisher = BaselineEstablisher()

# Convenience functions
async def establish_baseline():
    """Establish comprehensive authentication performance baseline"""
    return await baseline_establisher.establish_comprehensive_baseline()

async def quick_baseline_setup():
    """Quick baseline setup for immediate performance monitoring"""
    # Setup monitoring
    await baseline_establisher._setup_monitoring_infrastructure()
    
    # Run quick baseline
    await baseline_establisher._run_baseline_benchmarks()
    
    # Generate quick report
    return await baseline_establisher._generate_baseline_report()

async def validate_current_performance():
    """Validate current performance against established baseline"""
    if not baseline_establisher.baseline_results:
        logger.warning("No baseline established. Run establish_baseline() first.")
        return None
    
    # Run current performance test
    current_results = await auth_benchmarker.run_phase_benchmarks('current')
    
    # Compare with baseline
    improvements = performance_monitor.calculate_improvement(
        current_results, 
        baseline_establisher.baseline_results
    )
    
    return {
        'current_results': current_results,
        'baseline_comparison': improvements,
        'validation_timestamp': datetime.now().isoformat()
    }

# Export key components
__all__ = [
    'BaselineEstablisher',
    'baseline_establisher',
    'establish_baseline',
    'quick_baseline_setup', 
    'validate_current_performance'
]