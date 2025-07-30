"""
Health Monitoring System for application health checks and metrics.
"""

import psutil
import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import threading


class HealthMonitor:
    """Monitors system health and application performance."""

    def __init__(self, alert_thresholds: Dict[str, float] = None):
        self.logger = logging.getLogger(__name__)
        self.alert_thresholds = alert_thresholds or {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "latency_ms": 200.0,
        }
        self.metrics = []
        self.monitoring = False
        self.monitor_thread = None

    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "process_count": len(psutil.pids()),
        }

    def check_health_status(self) -> Dict[str, Any]:
        """Check overall health status."""
        metrics = self.get_system_metrics()
        alerts = []

        # Check CPU usage
        if metrics["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']}%")

        # Check memory usage
        if metrics["memory_percent"] > self.alert_thresholds["memory_percent"]:
            alerts.append(f"High memory usage: {metrics['memory_percent']}%")

        # Check disk usage
        if metrics["disk_percent"] > self.alert_thresholds["disk_percent"]:
            alerts.append(f"High disk usage: {metrics['disk_percent']}%")

        health_status = {
            "status": "healthy" if not alerts else "warning",
            "metrics": metrics,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
        }

        return health_status

    def check_connection_health(self, connections: Dict[str, bool]) -> Dict[str, Any]:
        """Check health of all connections."""
        connection_status = {
            "mt5_connections": sum(1 for connected in connections.get("mt5", {}).values() if connected),
            "match_trader_connections": sum(
                1 for connected in connections.get("match_trader", {}).values() if connected
            ),
            "total_expected": len(connections.get("mt5", {})) + len(connections.get("match_trader", {})),
        }

        connection_status["health_percentage"] = (
            (connection_status["mt5_connections"] + connection_status["match_trader_connections"])
            / connection_status["total_expected"]
            * 100
            if connection_status["total_expected"] > 0
            else 0
        )

        return connection_status

    def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous health monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval_seconds,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info(f"Health monitoring started with {interval_seconds}s interval")

    def _monitor_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                health_status = self.check_health_status()
                self.metrics.append(health_status)

                # Keep only last 24 hours of metrics
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics = [m for m in self.metrics if datetime.fromisoformat(m["timestamp"]) > cutoff_time]

                # Log alerts
                if health_status["alerts"]:
                    for alert in health_status["alerts"]:
                        self.logger.warning(f"Health Alert: {alert}")

            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")

            time.sleep(interval_seconds)

    def stop_monitoring(self):
        """Stop health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Health monitoring stopped")

    def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        if not self.metrics:
            return {"status": "no_data", "message": "No health metrics available"}

        recent_metrics = self.metrics[-10:]  # Last 10 readings

        avg_cpu = sum(m["metrics"]["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["metrics"]["memory_percent"] for m in recent_metrics) / len(recent_metrics)

        return {
            "current_status": self.check_health_status(),
            "average_metrics": {"cpu_percent": round(avg_cpu, 2), "memory_percent": round(avg_memory, 2)},
            "total_alerts": sum(len(m["alerts"]) for m in self.metrics),
            "uptime_hours": len(self.metrics) / 60 if self.metrics else 0,
        }
