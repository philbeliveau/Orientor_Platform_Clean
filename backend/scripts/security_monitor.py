#!/usr/bin/env python3
"""
Security Monitoring and Alerting System
=======================================

Real-time security monitoring for the authentication caching system.
Detects suspicious activities, security violations, and potential attacks.

Features:
- Real-time threat detection
- Anomaly detection algorithms
- Security incident logging
- Automated alerting system
- Performance impact monitoring
- Compliance monitoring
- Security metrics dashboard

Usage:
    python scripts/security_monitor.py --mode continuous
    python scripts/security_monitor.py --mode scan-once
    python scripts/security_monitor.py --mode report
"""

import os
import sys
import json
import time
import asyncio
import logging
import argparse
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/security_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY MONITORING CONFIGURATION
# ============================================================================

@dataclass
class SecurityThreshold:
    """Security monitoring thresholds"""
    failed_auth_rate: float = 10.0  # per minute
    cache_miss_rate: float = 0.8    # 80% miss rate indicates attack
    error_rate: float = 0.1         # 10% error rate threshold
    response_time_ms: float = 1000  # 1 second response time
    concurrent_users: int = 1000    # Max concurrent users
    memory_usage_mb: int = 512      # Memory usage threshold

@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: str
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source: str
    description: str
    details: Dict[str, Any]
    remediation: Optional[str] = None
    affected_users: Optional[List[str]] = None

@dataclass
class AlertConfig:
    """Alert configuration"""
    email_enabled: bool = True
    email_recipients: List[str] = None
    slack_enabled: bool = False
    slack_webhook: Optional[str] = None
    sms_enabled: bool = False
    log_enabled: bool = True

# ============================================================================
# SECURITY METRICS COLLECTOR
# ============================================================================

class SecurityMetricsCollector:
    """Collects security-related metrics from the cache system"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=10000)  # Keep last 10k metrics
        self.current_metrics = {}
        self.lock = threading.Lock()
        
    async def collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect cache system metrics"""
        try:
            # Import cache metrics (this would need to be adapted to actual imports)
            from app.utils.auth_cache import CacheMetrics
            from app.utils.database_session_cache import database_session_manager
            
            # Collect cache statistics
            cache_stats = CacheMetrics.get_all_stats()
            db_stats = database_session_manager.get_comprehensive_stats()
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cache_hit_rate": cache_stats.get("jwt_validation_cache", {}).get("hit_rate", 0),
                "cache_size": cache_stats.get("jwt_validation_cache", {}).get("size", 0),
                "memory_usage_kb": cache_stats.get("jwt_validation_cache", {}).get("memory_usage_kb", 0),
                "database_sync_rate": db_stats.get("sync_statistics", {}).get("sync_rate", 0),
                "total_operations": db_stats.get("total_operations", 0),
                "connection_pool_usage": db_stats.get("connection_pool", {}).get("checked_out", 0)
            }
            
            with self.lock:
                self.current_metrics = metrics
                self.metrics_history.append(metrics)
                
            return metrics
            
        except ImportError:
            logger.warning("Cache metrics modules not available")
            return {}
        except Exception as e:
            logger.error(f"Failed to collect cache metrics: {e}")
            return {}
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level security metrics"""
        import psutil
        
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": (disk.used / disk.total) * 100,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_memory_mb": process_memory.rss / 1024 / 1024,
                "process_cpu_percent": process.cpu_percent()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def get_metrics_trend(self, metric_name: str, window_minutes: int = 5) -> List[float]:
        """Get trend for specific metric"""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            return [m.get(metric_name, 0) for m in recent_metrics if metric_name in m]

# ============================================================================
# ANOMALY DETECTION ENGINE
# ============================================================================

class AnomalyDetector:
    """Detects security anomalies in system behavior"""
    
    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity  # Standard deviations for anomaly detection
        self.baselines = {}
        self.anomaly_history = deque(maxlen=1000)
        
    def update_baseline(self, metric_name: str, values: List[float]):
        """Update baseline statistics for a metric"""
        if not values:
            return
            
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        self.baselines[metric_name] = {
            "mean": mean,
            "std_dev": std_dev,
            "sample_size": len(values),
            "last_updated": datetime.now().isoformat()
        }
        
    def detect_anomaly(self, metric_name: str, current_value: float) -> Optional[Dict[str, Any]]:
        """Detect if current value is anomalous"""
        if metric_name not in self.baselines:
            return None
            
        baseline = self.baselines[metric_name]
        mean = baseline["mean"]
        std_dev = baseline["std_dev"]
        
        if std_dev == 0:  # No variance in baseline
            return None
            
        # Z-score calculation
        z_score = abs(current_value - mean) / std_dev
        
        if z_score > self.sensitivity:
            anomaly = {
                "metric": metric_name,
                "current_value": current_value,
                "baseline_mean": mean,
                "baseline_std": std_dev,
                "z_score": z_score,
                "severity": "HIGH" if z_score > 4.0 else "MEDIUM",
                "timestamp": datetime.now().isoformat()
            }
            
            self.anomaly_history.append(anomaly)
            return anomaly
            
        return None
    
    def detect_pattern_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect pattern-based anomalies"""
        anomalies = []
        
        if len(values) < 10:
            return anomalies
            
        # Check for sudden spikes
        for i in range(1, len(values)):
            if values[i] > values[i-1] * 5:  # 5x increase
                anomalies.append({
                    "type": "spike",
                    "position": i,
                    "value": values[i],
                    "previous": values[i-1],
                    "increase_factor": values[i] / values[i-1] if values[i-1] != 0 else float('inf')
                })
        
        # Check for unusual patterns (e.g., perfect periodicity might indicate attack)
        if len(set(values[-10:])) == 1 and values[-1] != 0:
            anomalies.append({
                "type": "constant_pattern",
                "value": values[-1],
                "duration": 10
            })
            
        return anomalies

# ============================================================================
# THREAT DETECTION ENGINE
# ============================================================================

class ThreatDetector:
    """Detects specific security threats and attack patterns"""
    
    def __init__(self, thresholds: SecurityThreshold):
        self.thresholds = thresholds
        self.threat_patterns = {
            "brute_force": self._detect_brute_force,
            "cache_flooding": self._detect_cache_flooding,
            "timing_attack": self._detect_timing_attack,
            "injection_attempt": self._detect_injection_attempt,
            "privilege_escalation": self._detect_privilege_escalation,
            "dos_attack": self._detect_dos_attack
        }
        
    def detect_threats(self, metrics: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect security threats based on current metrics"""
        threats = []
        
        for threat_name, detector_func in self.threat_patterns.items():
            try:
                threat_events = detector_func(metrics, historical_data)
                if threat_events:
                    threats.extend(threat_events)
            except Exception as e:
                logger.error(f"Error in threat detector {threat_name}: {e}")
                
        return threats
    
    def _detect_brute_force(self, metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect brute force authentication attempts"""
        events = []
        
        # Check for high error rates (indicating failed auth attempts)
        error_rate = metrics.get("error_rate", 0)
        if error_rate > self.thresholds.error_rate:
            events.append(SecurityEvent(
                timestamp=datetime.now().isoformat(),
                event_type="brute_force_detected",
                severity="HIGH",
                source="authentication_system",
                description=f"High error rate detected: {error_rate:.2%}",
                details={
                    "error_rate": error_rate,
                    "threshold": self.thresholds.error_rate,
                    "metrics": metrics
                },
                remediation="Implement account lockout and rate limiting"
            ))
            
        return events
    
    def _detect_cache_flooding(self, metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect cache flooding attacks"""
        events = []
        
        # Check for unusual cache miss rates
        cache_hit_rate = metrics.get("cache_hit_rate", 1.0)
        cache_miss_rate = 1.0 - cache_hit_rate
        
        if cache_miss_rate > self.thresholds.cache_miss_rate:
            events.append(SecurityEvent(
                timestamp=datetime.now().isoformat(),
                event_type="cache_flooding_detected",
                severity="MEDIUM",
                source="cache_system",
                description=f"Unusual cache miss rate: {cache_miss_rate:.2%}",
                details={
                    "cache_hit_rate": cache_hit_rate,
                    "cache_miss_rate": cache_miss_rate,
                    "threshold": self.thresholds.cache_miss_rate
                },
                remediation="Review cache keys for flooding patterns"
            ))
            
        return events
    
    def _detect_timing_attack(self, metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect timing attack patterns"""
        events = []
        
        # Check for consistent response times (might indicate probing)
        response_times = [h.get("response_time_ms", 0) for h in history[-10:]]
        if len(response_times) >= 5:
            # Check if response times are suspiciously consistent
            std_dev = (sum((x - sum(response_times)/len(response_times))**2 for x in response_times) / len(response_times)) ** 0.5
            if std_dev < 1.0 and sum(response_times) > 0:  # Very consistent timing
                events.append(SecurityEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type="timing_attack_suspected",
                    severity="MEDIUM",
                    source="response_timing",
                    description="Suspicious response time consistency detected",
                    details={
                        "response_times": response_times,
                        "std_deviation": std_dev
                    },
                    remediation="Implement constant-time operations"
                ))
                
        return events
    
    def _detect_injection_attempt(self, metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect injection attack attempts"""
        events = []
        
        # This would typically analyze request patterns from logs
        # For now, we check for validation errors which might indicate injection attempts
        validation_errors = metrics.get("validation_failures", 0)
        if validation_errors > 10:  # Threshold for validation errors
            events.append(SecurityEvent(
                timestamp=datetime.now().isoformat(),
                event_type="injection_attempt_detected",
                severity="HIGH",
                source="input_validation",
                description=f"High validation error rate: {validation_errors} failures",
                details={
                    "validation_failures": validation_errors,
                    "timeframe": "last_minute"
                },
                remediation="Review input validation logs for injection patterns"
            ))
            
        return events
    
    def _detect_privilege_escalation(self, metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect privilege escalation attempts"""
        events = []
        
        # Check for access denied events (might indicate privilege escalation attempts)
        access_denied = metrics.get("access_denied", 0)
        if access_denied > 5:  # Threshold for access denied attempts
            events.append(SecurityEvent(
                timestamp=datetime.now().isoformat(),
                event_type="privilege_escalation_attempt",
                severity="HIGH",
                source="access_control",
                description=f"Multiple access denied events: {access_denied}",
                details={
                    "access_denied_count": access_denied,
                    "timeframe": "last_minute"
                },
                remediation="Review access control logs for escalation patterns"
            ))
            
        return events
    
    def _detect_dos_attack(self, metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SecurityEvent]:
        """Detect denial of service attacks"""
        events = []
        
        # Check for resource exhaustion indicators
        memory_usage = metrics.get("process_memory_mb", 0)
        cpu_percent = metrics.get("cpu_percent", 0)
        
        if memory_usage > self.thresholds.memory_usage_mb:
            events.append(SecurityEvent(
                timestamp=datetime.now().isoformat(),
                event_type="memory_exhaustion_detected",
                severity="CRITICAL",
                source="system_resources",
                description=f"High memory usage: {memory_usage:.1f}MB",
                details={
                    "memory_usage_mb": memory_usage,
                    "threshold_mb": self.thresholds.memory_usage_mb,
                    "cpu_percent": cpu_percent
                },
                remediation="Scale resources or implement rate limiting"
            ))
            
        return events

# ============================================================================
# ALERTING SYSTEM
# ============================================================================

class SecurityAlerter:
    """Handles security alert notifications"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.alert_history = deque(maxlen=1000)
        
    async def send_alert(self, event: SecurityEvent):
        """Send security alert through configured channels"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "event": asdict(event),
            "channels_used": []
        }
        
        # Email alerts
        if self.config.email_enabled and self.config.email_recipients:
            try:
                await self._send_email_alert(event)
                alert_data["channels_used"].append("email")
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        # Slack alerts
        if self.config.slack_enabled and self.config.slack_webhook:
            try:
                await self._send_slack_alert(event)
                alert_data["channels_used"].append("slack")
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
        
        # Log alerts (always enabled)
        if self.config.log_enabled:
            self._log_alert(event)
            alert_data["channels_used"].append("log")
        
        self.alert_history.append(alert_data)
        
    async def _send_email_alert(self, event: SecurityEvent):
        """Send email alert"""
        if not self.config.email_recipients:
            return
            
        smtp_server = os.getenv("SMTP_SERVER", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        msg = MIMEMultipart()
        msg['From'] = smtp_user or "security-monitor@orientor.com"
        msg['To'] = ", ".join(self.config.email_recipients)
        msg['Subject'] = f"SECURITY ALERT [{event.severity}]: {event.event_type}"
        
        body = f"""
Security Alert Detected

Event Type: {event.event_type}
Severity: {event.severity}
Source: {event.source}
Timestamp: {event.timestamp}

Description:
{event.description}

Details:
{json.dumps(event.details, indent=2)}

Recommended Action:
{event.remediation or 'Review security logs and investigate'}

--
Orientor Security Monitoring System
        """.strip()
        
        msg.attach(MIMEText(body, 'plain'))
        
        if smtp_user and smtp_password:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_user, self.config.email_recipients, text)
            server.quit()
        else:
            logger.warning("SMTP credentials not configured, email alert not sent")
    
    async def _send_slack_alert(self, event: SecurityEvent):
        """Send Slack alert"""
        import aiohttp
        
        if not self.config.slack_webhook:
            return
            
        severity_colors = {
            "LOW": "good",
            "MEDIUM": "warning", 
            "HIGH": "danger",
            "CRITICAL": "danger"
        }
        
        payload = {
            "username": "Security Monitor",
            "icon_emoji": ":warning:",
            "attachments": [{
                "color": severity_colors.get(event.severity, "warning"),
                "title": f"Security Alert: {event.event_type}",
                "text": event.description,
                "fields": [
                    {"title": "Severity", "value": event.severity, "short": True},
                    {"title": "Source", "value": event.source, "short": True},
                    {"title": "Timestamp", "value": event.timestamp, "short": False}
                ],
                "footer": "Orientor Security Monitor"
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.config.slack_webhook, json=payload) as response:
                if response.status != 200:
                    logger.error(f"Slack alert failed: {response.status}")
    
    def _log_alert(self, event: SecurityEvent):
        """Log security alert"""
        log_level = {
            "LOW": logging.INFO,
            "MEDIUM": logging.WARNING,
            "HIGH": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }.get(event.severity, logging.WARNING)
        
        logger.log(log_level, f"SECURITY ALERT [{event.event_type}]: {event.description}")

# ============================================================================
# MAIN SECURITY MONITOR
# ============================================================================

class SecurityMonitor:
    """Main security monitoring orchestrator"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.thresholds = SecurityThreshold()
        self.metrics_collector = SecurityMetricsCollector()
        self.anomaly_detector = AnomalyDetector()
        self.threat_detector = ThreatDetector(self.thresholds)
        self.alerter = SecurityAlerter(AlertConfig())
        
        self.running = False
        self.monitor_task = None
        
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "monitoring_interval": 30,  # seconds
            "baseline_window_hours": 24,
            "alert_cooldown_minutes": 15,
            "enable_anomaly_detection": True,
            "enable_threat_detection": True
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
            except Exception as e:
                logger.error(f"Failed to load config file {config_file}: {e}")
                
        return default_config
    
    async def start_monitoring(self):
        """Start continuous security monitoring"""
        if self.running:
            logger.warning("Security monitor is already running")
            return
            
        self.running = True
        logger.info("Starting security monitoring...")
        
        try:
            while self.running:
                await self._monitoring_cycle()
                await asyncio.sleep(self.config["monitoring_interval"])
        except Exception as e:
            logger.error(f"Security monitoring error: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.running = False
        logger.info("Stopping security monitoring...")
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        try:
            # Collect current metrics
            cache_metrics = await self.metrics_collector.collect_cache_metrics()
            system_metrics = await self.metrics_collector.collect_system_metrics()
            
            combined_metrics = {**cache_metrics, **system_metrics}
            
            # Update anomaly detection baselines
            if self.config["enable_anomaly_detection"]:
                await self._update_baselines()
            
            # Detect anomalies
            anomalies = []
            if self.config["enable_anomaly_detection"]:
                anomalies = await self._detect_anomalies(combined_metrics)
            
            # Detect threats
            threats = []
            if self.config["enable_threat_detection"]:
                historical_data = list(self.metrics_collector.metrics_history)[-100:]  # Last 100 data points
                threats = self.threat_detector.detect_threats(combined_metrics, historical_data)
            
            # Send alerts for high-severity events
            all_events = anomalies + threats
            for event in all_events:
                if event.severity in ["HIGH", "CRITICAL"]:
                    await self.alerter.send_alert(event)
            
            # Log summary
            if all_events:
                logger.info(f"Security monitoring cycle: {len(anomalies)} anomalies, {len(threats)} threats detected")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    async def _update_baselines(self):
        """Update anomaly detection baselines"""
        cutoff_time = datetime.now() - timedelta(hours=self.config["baseline_window_hours"])
        
        baseline_metrics = [
            m for m in self.metrics_collector.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if len(baseline_metrics) < 10:  # Need minimum data for baseline
            return
            
        # Update baselines for key metrics
        key_metrics = [
            "cache_hit_rate", "memory_usage_kb", "cpu_percent", 
            "total_operations", "connection_pool_usage"
        ]
        
        for metric_name in key_metrics:
            values = [m.get(metric_name, 0) for m in baseline_metrics if metric_name in m]
            if values:
                self.anomaly_detector.update_baseline(metric_name, values)
    
    async def _detect_anomalies(self, current_metrics: Dict[str, Any]) -> List[SecurityEvent]:
        """Detect anomalies in current metrics"""
        anomaly_events = []
        
        for metric_name, value in current_metrics.items():
            if isinstance(value, (int, float)):
                anomaly = self.anomaly_detector.detect_anomaly(metric_name, value)
                if anomaly:
                    event = SecurityEvent(
                        timestamp=datetime.now().isoformat(),
                        event_type="metric_anomaly",
                        severity=anomaly["severity"],
                        source="anomaly_detector",
                        description=f"Anomalous {metric_name}: {value} (z-score: {anomaly['z_score']:.2f})",
                        details=anomaly,
                        remediation="Investigate metric anomaly for potential security issues"
                    )
                    anomaly_events.append(event)
        
        return anomaly_events
    
    async def scan_once(self) -> Dict[str, Any]:
        """Perform single security scan"""
        logger.info("Performing one-time security scan...")
        
        # Collect metrics
        cache_metrics = await self.metrics_collector.collect_cache_metrics()
        system_metrics = await self.metrics_collector.collect_system_metrics()
        combined_metrics = {**cache_metrics, **system_metrics}
        
        # Detect threats
        historical_data = list(self.metrics_collector.metrics_history)[-100:]
        threats = self.threat_detector.detect_threats(combined_metrics, historical_data)
        
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "metrics": combined_metrics,
            "threats_detected": len(threats),
            "threats": [asdict(t) for t in threats],
            "status": "CLEAN" if not threats else "THREATS_DETECTED"
        }
        
        logger.info(f"Security scan complete: {len(threats)} threats detected")
        return scan_result
    
    def generate_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate security monitoring report"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get recent metrics
        recent_metrics = [
            m for m in self.metrics_collector.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        # Get recent alerts
        recent_alerts = [
            a for a in self.alerter.alert_history
            if datetime.fromisoformat(a["timestamp"]) > cutoff_time
        ]
        
        # Calculate statistics
        if recent_metrics:
            avg_cpu = sum(m.get("cpu_percent", 0) for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.get("memory_percent", 0) for m in recent_metrics) / len(recent_metrics)
            avg_cache_hit_rate = sum(m.get("cache_hit_rate", 0) for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = avg_cache_hit_rate = 0
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "metrics_collected": len(recent_metrics),
            "alerts_generated": len(recent_alerts),
            "performance_summary": {
                "avg_cpu_percent": round(avg_cpu, 2),
                "avg_memory_percent": round(avg_memory, 2),
                "avg_cache_hit_rate": round(avg_cache_hit_rate, 3)
            },
            "alert_summary": {
                "total_alerts": len(recent_alerts),
                "by_severity": self._count_alerts_by_severity(recent_alerts)
            },
            "security_status": "GOOD" if len(recent_alerts) == 0 else "MONITORING",
            "recommendations": self._generate_recommendations(recent_alerts, recent_metrics)
        }
        
        return report
    
    def _count_alerts_by_severity(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count alerts by severity level"""
        severity_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        for alert in alerts:
            severity = alert.get("event", {}).get("severity", "LOW")
            if severity in severity_counts:
                severity_counts[severity] += 1
                
        return severity_counts
    
    def _generate_recommendations(self, alerts: List[Dict[str, Any]], metrics: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on recent activity"""
        recommendations = []
        
        if len(alerts) > 10:
            recommendations.append("High alert volume detected - review security configurations")
        
        if metrics:
            avg_cache_hit_rate = sum(m.get("cache_hit_rate", 0) for m in metrics) / len(metrics)
            if avg_cache_hit_rate < 0.5:
                recommendations.append("Low cache hit rate - investigate potential cache flooding")
        
        # Check for specific threat types in alerts
        threat_types = set()
        for alert in alerts:
            event_type = alert.get("event", {}).get("event_type", "")
            if "brute_force" in event_type:
                threat_types.add("brute_force")
            elif "injection" in event_type:
                threat_types.add("injection")
            elif "dos" in event_type:
                threat_types.add("dos")
        
        for threat in threat_types:
            if threat == "brute_force":
                recommendations.append("Implement account lockout policies and rate limiting")
            elif threat == "injection":
                recommendations.append("Review input validation and sanitization")
            elif threat == "dos":
                recommendations.append("Scale resources and implement DDoS protection")
        
        if not recommendations:
            recommendations.append("System operating within normal security parameters")
        
        return recommendations

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Security Monitoring System")
    parser.add_argument("--mode", choices=["continuous", "scan-once", "report"], 
                        default="scan-once", help="Monitoring mode")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", help="Output file for reports")
    parser.add_argument("--hours", type=int, default=24, help="Report period in hours")
    
    args = parser.parse_args()
    
    # Initialize security monitor
    monitor = SecurityMonitor(args.config)
    
    try:
        if args.mode == "continuous":
            logger.info("Starting continuous security monitoring (Ctrl+C to stop)")
            await monitor.start_monitoring()
            
        elif args.mode == "scan-once":
            result = await monitor.scan_once()
            print(json.dumps(result, indent=2))
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to {args.output}")
            
        elif args.mode == "report":
            report = monitor.generate_report(args.hours)
            print(json.dumps(report, indent=2))
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Report saved to {args.output}")
                
    except KeyboardInterrupt:
        logger.info("Security monitoring stopped by user")
        monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"Security monitoring failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)