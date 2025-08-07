"""
Performance Monitoring Dashboard
===============================

Web-based dashboard for monitoring authentication performance in real-time.
Provides visualization of metrics, benchmarks, and optimization progress.

Features:
1. Real-time performance metrics visualization
2. Phase-by-phase progress tracking
3. Bottleneck analysis and alerts
4. Historical performance trends
5. Optimization recommendations
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from .auth_metrics import performance_monitor, AuthPerformanceMonitor
from .benchmarker import auth_benchmarker, AuthBenchmarker
from .architecture_analyzer import architecture_analyzer, AuthArchitectureAnalyzer

logger = logging.getLogger(__name__)

class PerformanceDashboard:
    """Real-time performance monitoring dashboard"""
    
    def __init__(self,
                 monitor: AuthPerformanceMonitor = None,
                 benchmarker: AuthBenchmarker = None,
                 analyzer: AuthArchitectureAnalyzer = None):
        """
        Initialize the performance dashboard
        
        Args:
            monitor: Performance monitor instance
            benchmarker: Benchmarker instance
            analyzer: Architecture analyzer instance
        """
        self.monitor = monitor or performance_monitor
        self.benchmarker = benchmarker or auth_benchmarker
        self.analyzer = analyzer or architecture_analyzer
        
        # WebSocket connections for real-time updates
        self.active_connections: List[WebSocket] = []
        
        # Dashboard state
        self.dashboard_data = {}
        self.alert_thresholds = {
            'avg_latency_ms': 500,
            'p95_latency_ms': 1000,
            'error_rate': 0.05,
            'cache_hit_rate': 0.7
        }
        
        logger.info("📊 PerformanceDashboard initialized")

    async def connect_websocket(self, websocket: WebSocket):
        """Add a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Send initial data
        await self.send_dashboard_update(websocket)
        
        logger.info(f"📡 New WebSocket connection - {len(self.active_connections)} active")

    async def disconnect_websocket(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"📡 WebSocket disconnected - {len(self.active_connections)} active")

    async def send_dashboard_update(self, websocket: WebSocket = None):
        """Send dashboard update to WebSocket connections"""
        dashboard_data = await self.get_dashboard_data()
        
        message = {
            'type': 'dashboard_update',
            'timestamp': datetime.now().isoformat(),
            'data': dashboard_data
        }
        
        if websocket:
            # Send to specific connection
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
        else:
            # Broadcast to all connections
            disconnected = []
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                await self.disconnect_websocket(conn)

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        
        # Current performance summary
        performance_summary = self._get_performance_summary()
        
        # Recent metrics for charts
        metrics_data = await self._get_metrics_data()
        
        # Phase progress
        phase_progress = await self._get_phase_progress()
        
        # Current alerts
        alerts = await self._check_alerts()
        
        # System health
        system_health = await self._get_system_health()
        
        # Recent benchmarks
        recent_benchmarks = await self._get_recent_benchmarks()
        
        dashboard_data = {
            'performance_summary': performance_summary,
            'metrics_data': metrics_data,
            'phase_progress': phase_progress,
            'alerts': alerts,
            'system_health': system_health,
            'recent_benchmarks': recent_benchmarks,
            'last_updated': datetime.now().isoformat()
        }
        
        self.dashboard_data = dashboard_data
        return dashboard_data

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        
        if not self.monitor.metrics:
            return {
                'status': 'no_data',
                'message': 'No performance metrics available'
            }
        
        # Get recent metrics (last 100)
        recent_metrics = self.monitor.metrics[-100:]
        successful_metrics = [m for m in recent_metrics if m.success]
        
        if not successful_metrics:
            return {
                'status': 'errors',
                'total_requests': len(recent_metrics),
                'error_rate': 1.0,
                'message': 'All recent requests failed'
            }
        
        # Calculate summary statistics
        durations = [m.duration_ms for m in successful_metrics]
        cache_hits = sum(1 for m in successful_metrics if m.cache_hit)
        
        import statistics
        import numpy as np
        
        return {
            'status': 'active',
            'current_phase': self.monitor.current_phase,
            'total_requests': len(recent_metrics),
            'success_rate': len(successful_metrics) / len(recent_metrics),
            'error_rate': (len(recent_metrics) - len(successful_metrics)) / len(recent_metrics),
            'avg_latency_ms': statistics.mean(durations),
            'median_latency_ms': statistics.median(durations),
            'p95_latency_ms': np.percentile(durations, 95),
            'p99_latency_ms': np.percentile(durations, 99),
            'min_latency_ms': min(durations),
            'max_latency_ms': max(durations),
            'cache_hit_rate': cache_hits / len(successful_metrics) if successful_metrics else 0,
            'measurements_count': len(recent_metrics)
        }

    async def _get_metrics_data(self) -> Dict[str, Any]:
        """Get metrics data for visualization"""
        
        if not self.monitor.metrics:
            return {}
        
        # Get last 500 metrics for charts
        recent_metrics = self.monitor.metrics[-500:]
        
        # Time series data
        timestamps = [m.timestamp.isoformat() for m in recent_metrics]
        durations = [m.duration_ms if m.success else None for m in recent_metrics]
        success_flags = [m.success for m in recent_metrics]
        cache_hits = [m.cache_hit for m in recent_metrics]
        
        # Group by operation
        operation_data = {}
        for metric in recent_metrics:
            if metric.operation not in operation_data:
                operation_data[metric.operation] = {
                    'timestamps': [],
                    'durations': [],
                    'success_count': 0,
                    'total_count': 0,
                    'cache_hits': 0
                }
            
            op_data = operation_data[metric.operation]
            op_data['timestamps'].append(metric.timestamp.isoformat())
            op_data['durations'].append(metric.duration_ms if metric.success else None)
            op_data['total_count'] += 1
            
            if metric.success:
                op_data['success_count'] += 1
            if metric.cache_hit:
                op_data['cache_hits'] += 1
        
        return {
            'time_series': {
                'timestamps': timestamps,
                'durations': durations,
                'success_flags': success_flags,
                'cache_hits': cache_hits
            },
            'operation_breakdown': operation_data,
            'total_metrics': len(recent_metrics)
        }

    async def _get_phase_progress(self) -> Dict[str, Any]:
        """Get optimization phase progress"""
        
        phase_progress = {
            'current_phase': self.monitor.current_phase,
            'phases': {}
        }
        
        # Get phase statistics from monitor
        phase_stats = self.monitor._calculate_phase_statistics()
        
        # Define expected improvements for each phase
        phase_targets = {
            'baseline': {'target_improvement': 0, 'description': 'Baseline measurements'},
            'phase1': {'target_improvement': 20, 'description': 'JWKS Caching'},
            'phase2': {'target_improvement': 30, 'description': 'JWT Validation Caching'},
            'phase3': {'target_improvement': 42.5, 'description': 'Session Caching'},
            'phase4': {'target_improvement': 57.5, 'description': 'Database Connection Pooling'},
            'phase5': {'target_improvement': 77.5, 'description': 'Integrated Multi-layer Caching'}
        }
        
        baseline_avg = None
        if 'baseline' in phase_stats:
            baseline_avg = phase_stats['baseline']['avg_latency_ms']
        
        for phase, stats in phase_stats.items():
            target_info = phase_targets.get(phase, {'target_improvement': 0, 'description': phase})
            
            # Calculate actual improvement
            actual_improvement = 0
            if baseline_avg and baseline_avg > 0 and phase != 'baseline':
                actual_improvement = ((baseline_avg - stats['avg_latency_ms']) / baseline_avg) * 100
            
            phase_progress['phases'][phase] = {
                'description': target_info['description'],
                'target_improvement': target_info['target_improvement'],
                'actual_improvement': actual_improvement,
                'avg_latency_ms': stats['avg_latency_ms'],
                'measurement_count': stats['count'],
                'status': 'completed' if actual_improvement >= target_info['target_improvement'] * 0.8 else 'in_progress'
            }
        
        return phase_progress

    async def _check_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        
        alerts = []
        summary = self._get_performance_summary()
        
        if summary.get('status') != 'active':
            return alerts
        
        # Latency alerts
        if summary['avg_latency_ms'] > self.alert_thresholds['avg_latency_ms']:
            alerts.append({
                'type': 'latency',
                'severity': 'high' if summary['avg_latency_ms'] > self.alert_thresholds['avg_latency_ms'] * 2 else 'medium',
                'message': f"High average latency: {summary['avg_latency_ms']:.1f}ms (threshold: {self.alert_thresholds['avg_latency_ms']}ms)",
                'current_value': summary['avg_latency_ms'],
                'threshold': self.alert_thresholds['avg_latency_ms']
            })
        
        if summary['p95_latency_ms'] > self.alert_thresholds['p95_latency_ms']:
            alerts.append({
                'type': 'latency_p95',
                'severity': 'medium',
                'message': f"High P95 latency: {summary['p95_latency_ms']:.1f}ms (threshold: {self.alert_thresholds['p95_latency_ms']}ms)",
                'current_value': summary['p95_latency_ms'],
                'threshold': self.alert_thresholds['p95_latency_ms']
            })
        
        # Error rate alerts
        if summary['error_rate'] > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate',
                'severity': 'critical' if summary['error_rate'] > 0.1 else 'high',
                'message': f"High error rate: {summary['error_rate']*100:.1f}% (threshold: {self.alert_thresholds['error_rate']*100:.1f}%)",
                'current_value': summary['error_rate'],
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # Cache hit rate alerts
        if summary['cache_hit_rate'] < self.alert_thresholds['cache_hit_rate']:
            alerts.append({
                'type': 'cache_hit_rate',
                'severity': 'medium',
                'message': f"Low cache hit rate: {summary['cache_hit_rate']*100:.1f}% (threshold: {self.alert_thresholds['cache_hit_rate']*100:.1f}%)",
                'current_value': summary['cache_hit_rate'],
                'threshold': self.alert_thresholds['cache_hit_rate']
            })
        
        return alerts

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health information"""
        
        health = {
            'status': 'unknown',
            'components': {},
            'last_check': datetime.now().isoformat()
        }
        
        # Check monitoring system health
        health['components']['performance_monitor'] = {
            'status': 'healthy' if self.monitor.metrics else 'no_data',
            'metrics_count': len(self.monitor.metrics),
            'last_metric': self.monitor.metrics[-1].timestamp.isoformat() if self.monitor.metrics else None
        }
        
        # Check system resources if available
        if hasattr(self.monitor, 'system_stats') and self.monitor.system_stats:
            recent_stats = self.monitor.system_stats[-10:]  # Last 10 measurements
            
            avg_cpu = sum(s['cpu_percent'] for s in recent_stats) / len(recent_stats)
            avg_memory = sum(s['memory_percent'] for s in recent_stats) / len(recent_stats)
            
            health['components']['system_resources'] = {
                'status': 'healthy' if avg_cpu < 80 and avg_memory < 85 else 'warning',
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'measurements_count': len(recent_stats)
            }
        
        # Overall status
        component_statuses = [comp['status'] for comp in health['components'].values()]
        if all(status == 'healthy' for status in component_statuses):
            health['status'] = 'healthy'
        elif any(status in ['critical', 'error'] for status in component_statuses):
            health['status'] = 'critical'
        elif any(status in ['warning', 'degraded'] for status in component_statuses):
            health['status'] = 'warning'
        else:
            health['status'] = 'unknown'
        
        return health

    async def _get_recent_benchmarks(self) -> List[Dict[str, Any]]:
        """Get recent benchmark results"""
        
        if not hasattr(self.benchmarker, 'benchmarks') or not self.benchmarker.benchmarks:
            return []
        
        # Get last 10 benchmarks
        recent_benchmarks = self.benchmarker.benchmarks[-10:]
        
        benchmark_data = []
        for benchmark in recent_benchmarks:
            benchmark_data.append({
                'test_name': benchmark.test_name,
                'phase': benchmark.phase,
                'timestamp': benchmark.timestamp.isoformat(),
                'success_rate': (benchmark.success_count / benchmark.total_requests) if benchmark.total_requests > 0 else 0,
                'avg_latency_ms': benchmark.avg_latency_ms,
                'p95_latency_ms': benchmark.p95_latency_ms,
                'requests_per_second': benchmark.requests_per_second,
                'cache_hit_rate': benchmark.cache_hit_rate
            })
        
        return benchmark_data

    async def generate_performance_charts(self) -> Dict[str, str]:
        """Generate Plotly charts for performance visualization"""
        
        metrics_data = await self._get_metrics_data()
        
        if not metrics_data.get('time_series'):
            return {}
        
        charts = {}
        
        # Latency trend chart
        fig_latency = go.Figure()
        
        ts_data = metrics_data['time_series']
        fig_latency.add_trace(go.Scatter(
            x=ts_data['timestamps'],
            y=ts_data['durations'],
            mode='lines+markers',
            name='Latency (ms)',
            line=dict(color='blue')
        ))
        
        fig_latency.update_layout(
            title='Authentication Latency Trend',
            xaxis_title='Time',
            yaxis_title='Latency (ms)',
            hovermode='x'
        )
        
        charts['latency_trend'] = json.dumps(fig_latency, cls=PlotlyJSONEncoder)
        
        # Operation breakdown pie chart
        if metrics_data.get('operation_breakdown'):
            operation_counts = {
                op: data['total_count'] 
                for op, data in metrics_data['operation_breakdown'].items()
            }
            
            fig_operations = go.Figure(data=[go.Pie(
                labels=list(operation_counts.keys()),
                values=list(operation_counts.values()),
                hole=0.3
            )])
            
            fig_operations.update_layout(title='Operations Distribution')
            charts['operations_breakdown'] = json.dumps(fig_operations, cls=PlotlyJSONEncoder)
        
        # Cache hit rate chart
        cache_hit_data = []
        timestamps = []
        
        for i, (cache_hit, timestamp) in enumerate(zip(ts_data['cache_hits'], ts_data['timestamps'])):
            if i % 10 == 0:  # Sample every 10th point for readability
                # Calculate rolling cache hit rate
                start_idx = max(0, i - 50)
                recent_cache_hits = ts_data['cache_hits'][start_idx:i+1]
                hit_rate = sum(recent_cache_hits) / len(recent_cache_hits) if recent_cache_hits else 0
                
                cache_hit_data.append(hit_rate * 100)
                timestamps.append(timestamp)
        
        fig_cache = go.Figure()
        fig_cache.add_trace(go.Scatter(
            x=timestamps,
            y=cache_hit_data,
            mode='lines',
            name='Cache Hit Rate (%)',
            line=dict(color='green')
        ))
        
        fig_cache.update_layout(
            title='Cache Hit Rate Over Time',
            xaxis_title='Time',
            yaxis_title='Cache Hit Rate (%)',
            yaxis=dict(range=[0, 100])
        )
        
        charts['cache_hit_rate'] = json.dumps(fig_cache, cls=PlotlyJSONEncoder)
        
        return charts

    def generate_dashboard_html(self) -> str:
        """Generate HTML dashboard page"""
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Performance Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .alert {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        .alert-critical { background-color: #ffebee; border-left: 4px solid #f44336; }
        .alert-high { background-color: #fff3e0; border-left: 4px solid #ff9800; }
        .alert-medium { background-color: #e8f5e8; border-left: 4px solid #4caf50; }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-healthy { background-color: #4caf50; }
        .status-warning { background-color: #ff9800; }
        .status-critical { background-color: #f44336; }
        .status-unknown { background-color: #9e9e9e; }
        .phase-progress {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .phase-item {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            background-color: #f8f9fa;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            transition: width 0.3s ease;
        }
        #connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 10px 15px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
        }
        .connected { background-color: #4caf50; }
        .disconnected { background-color: #f44336; }
    </style>
</head>
<body>
    <div id="connection-status" class="disconnected">Connecting...</div>
    
    <div class="dashboard-header">
        <h1>🚀 Authentication Performance Dashboard</h1>
        <p>Real-time monitoring and optimization tracking</p>
        <div id="last-updated">Last updated: Loading...</div>
    </div>

    <div class="dashboard-grid">
        <div class="metric-card">
            <div class="metric-value" id="avg-latency">--</div>
            <div class="metric-label">Average Latency (ms)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="success-rate">--</div>
            <div class="metric-label">Success Rate (%)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="cache-hit-rate">--</div>
            <div class="metric-label">Cache Hit Rate (%)</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="requests-per-second">--</div>
            <div class="metric-label">Requests/Second</div>
        </div>
    </div>

    <div class="dashboard-grid">
        <div class="phase-progress">
            <h3>Optimization Phase Progress</h3>
            <div id="current-phase">Current Phase: <strong id="phase-name">--</strong></div>
            <div id="phases-container"></div>
        </div>
        
        <div class="metric-card">
            <h3>System Health</h3>
            <div id="system-health">
                <div id="overall-status">
                    <span class="status-indicator status-unknown"></span>
                    <span id="health-status">Checking...</span>
                </div>
                <div id="health-components"></div>
            </div>
        </div>
    </div>

    <div id="alerts-container" style="margin-bottom: 20px;"></div>

    <div class="chart-container">
        <div id="latency-chart"></div>
    </div>
    
    <div class="chart-container">
        <div id="cache-chart"></div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        let ws;
        let reconnectInterval;

        function connectWebSocket() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${location.host}/api/performance/dashboard/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                updateConnectionStatus(true);
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                if (message.type === 'dashboard_update') {
                    updateDashboard(message.data);
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                updateConnectionStatus(false);
                
                // Attempt to reconnect every 5 seconds
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(connectWebSocket, 5000);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        function updateConnectionStatus(connected) {
            const statusEl = document.getElementById('connection-status');
            if (connected) {
                statusEl.textContent = 'Connected';
                statusEl.className = 'connected';
            } else {
                statusEl.textContent = 'Disconnected';
                statusEl.className = 'disconnected';
            }
        }

        function updateDashboard(data) {
            // Update timestamp
            document.getElementById('last-updated').textContent = 
                `Last updated: ${new Date(data.last_updated).toLocaleString()}`;
            
            // Update performance summary
            if (data.performance_summary && data.performance_summary.status === 'active') {
                const summary = data.performance_summary;
                
                document.getElementById('avg-latency').textContent = 
                    Math.round(summary.avg_latency_ms);
                document.getElementById('success-rate').textContent = 
                    (summary.success_rate * 100).toFixed(1);
                document.getElementById('cache-hit-rate').textContent = 
                    (summary.cache_hit_rate * 100).toFixed(1);
                document.getElementById('requests-per-second').textContent = 
                    (60 / (summary.avg_latency_ms / 1000)).toFixed(1);
            }
            
            // Update phase progress
            if (data.phase_progress) {
                document.getElementById('phase-name').textContent = 
                    data.phase_progress.current_phase;
                
                const phasesContainer = document.getElementById('phases-container');
                phasesContainer.innerHTML = '';
                
                Object.entries(data.phase_progress.phases).forEach(([phase, info]) => {
                    const phaseEl = document.createElement('div');
                    phaseEl.className = 'phase-item';
                    
                    const progress = Math.min(100, Math.max(0, info.actual_improvement / info.target_improvement * 100));
                    
                    phaseEl.innerHTML = `
                        <div><strong>${phase}</strong>: ${info.description}</div>
                        <div>Target: ${info.target_improvement}% | Actual: ${info.actual_improvement.toFixed(1)}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                    `;
                    
                    phasesContainer.appendChild(phaseEl);
                });
            }
            
            // Update system health
            if (data.system_health) {
                const health = data.system_health;
                const statusEl = document.getElementById('health-status');
                const indicatorEl = statusEl.previousElementSibling;
                
                statusEl.textContent = health.status.charAt(0).toUpperCase() + health.status.slice(1);
                indicatorEl.className = `status-indicator status-${health.status}`;
            }
            
            // Update alerts
            updateAlerts(data.alerts || []);
            
            // Update charts if available
            if (data.charts) {
                updateCharts(data.charts);
            }
        }

        function updateAlerts(alerts) {
            const alertsContainer = document.getElementById('alerts-container');
            alertsContainer.innerHTML = '';
            
            if (alerts.length === 0) return;
            
            alerts.forEach(alert => {
                const alertEl = document.createElement('div');
                alertEl.className = `alert alert-${alert.severity}`;
                alertEl.innerHTML = `
                    <strong>${alert.type.toUpperCase()}</strong>: ${alert.message}
                `;
                alertsContainer.appendChild(alertEl);
            });
        }

        function updateCharts(charts) {
            if (charts.latency_trend) {
                const data = JSON.parse(charts.latency_trend);
                Plotly.newPlot('latency-chart', data.data, data.layout);
            }
            
            if (charts.cache_hit_rate) {
                const data = JSON.parse(charts.cache_hit_rate);
                Plotly.newPlot('cache-chart', data.data, data.layout);
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
        });
    </script>
</body>
</html>
        """
        
        return html_content

# Create FastAPI router for dashboard endpoints
router = APIRouter(prefix="/api/performance", tags=["performance"])
dashboard = PerformanceDashboard()

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the performance dashboard HTML page"""
    return HTMLResponse(content=dashboard.generate_dashboard_html())

@router.get("/dashboard/data")
async def get_dashboard_data():
    """Get dashboard data as JSON"""
    return await dashboard.get_dashboard_data()

@router.get("/dashboard/charts")
async def get_dashboard_charts():
    """Get performance charts data"""
    return await dashboard.generate_performance_charts()

@router.websocket("/dashboard/ws")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await dashboard.connect_websocket(websocket)
    
    try:
        while True:
            # Wait for any message (keep connection alive)
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        await dashboard.disconnect_websocket(websocket)

@router.post("/dashboard/start-monitoring")
async def start_monitoring():
    """Start performance monitoring"""
    try:
        await dashboard.monitor.start_system_monitoring()
        return {"status": "success", "message": "Performance monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/dashboard/run-baseline")
async def run_baseline_benchmark():
    """Run baseline performance benchmarks"""
    try:
        results = await dashboard.benchmarker.run_baseline_benchmarks()
        return {"status": "success", "results": len(results), "message": "Baseline benchmarks completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run baseline: {str(e)}")

@router.post("/dashboard/run-phase-benchmark/{phase}")
async def run_phase_benchmark(phase: str):
    """Run benchmarks for a specific optimization phase"""
    try:
        results = await dashboard.benchmarker.run_phase_benchmarks(phase)
        return {"status": "success", "results": len(results), "phase": phase, "message": f"Phase {phase} benchmarks completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run phase benchmark: {str(e)}")

# Background task to send periodic updates
async def dashboard_update_task():
    """Background task to send periodic dashboard updates"""
    while True:
        try:
            if dashboard.active_connections:
                await dashboard.send_dashboard_update()
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Dashboard update task error: {e}")
            await asyncio.sleep(10)

# Start the background update task
asyncio.create_task(dashboard_update_task())

# Export router and dashboard instance
__all__ = ['router', 'dashboard', 'PerformanceDashboard']