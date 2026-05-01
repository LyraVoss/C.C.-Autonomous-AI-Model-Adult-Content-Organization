import psutil
import time
from typing import Dict, List
from datetime import datetime, timedelta
import asyncio
from .models import DigitalCreator
from .performance import PerformanceOptimizer

class HealthMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history: List[Dict] = []
        self.alerts: List[Dict] = []

    def get_system_health(self) -> Dict:
        """Get comprehensive system health metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_connections": len(psutil.net_connections()),
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_application_health(self, creator_manager, streaming_manager, performance_optimizer) -> Dict:
        """Get application-specific health metrics"""
        active_streams = len(streaming_manager.active_streams)
        online_creators = len(creator_manager.get_online_creators())
        total_creators = len(creator_manager.creators)

        return {
            "active_streams": active_streams,
            "online_creators": online_creators,
            "total_creators": total_creators,
            "cache_size": len(performance_optimizer.cache),
            "active_threads": performance_optimizer.executor._threads if hasattr(performance_optimizer.executor, '_threads') else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    def check_service_dependencies(self) -> Dict[str, bool]:
        """Check if external services are available"""
        services = {
            "database": self._check_database(),
            "openai_api": self._check_openai_api(),
            "elevenlabs_api": self._check_elevenlabs_api(),
            "stripe_api": self._check_stripe_api(),
            "redis": self._check_redis()
        }
        return services

    def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Placeholder - would check actual DB connection
            return True
        except:
            return False

    def _check_openai_api(self) -> bool:
        """Check OpenAI API availability"""
        try:
            # Placeholder - would make a test API call
            return True
        except:
            return False

    def _check_elevenlabs_api(self) -> bool:
        """Check ElevenLabs API availability"""
        try:
            return True
        except:
            return False

    def _check_stripe_api(self) -> bool:
        """Check Stripe API availability"""
        try:
            return True
        except:
            return False

    def _check_redis(self) -> bool:
        """Check Redis availability"""
        try:
            return True
        except:
            return False

    def record_metrics(self, system_health: Dict, app_health: Dict):
        """Record health metrics for historical analysis"""
        metrics = {
            **system_health,
            **app_health,
            "recorded_at": datetime.utcnow()
        }
        self.metrics_history.append(metrics)

        # Keep only last 1000 records
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]

    def check_thresholds(self, metrics: Dict) -> List[str]:
        """Check if metrics exceed thresholds and return alerts"""
        alerts = []

        if metrics.get('cpu_percent', 0) > 90:
            alerts.append("High CPU usage detected")
        if metrics.get('memory_percent', 0) > 85:
            alerts.append("High memory usage detected")
        if metrics.get('active_streams', 0) > 50:
            alerts.append("High number of active streams")
        if not metrics.get('database', True):
            alerts.append("Database connection failed")

        return alerts

    async def continuous_monitoring(self, interval: int = 60):
        """Run continuous health monitoring"""
        while True:
            try:
                system_health = self.get_system_health()
                # Note: Would need to pass actual managers here
                # app_health = self.get_application_health(creator_manager, streaming_manager, performance_optimizer)
                services = self.check_service_dependencies()

                combined_metrics = {**system_health, **services}
                alerts = self.check_thresholds(combined_metrics)

                if alerts:
                    for alert in alerts:
                        self.alerts.append({
                            "message": alert,
                            "timestamp": datetime.utcnow(),
                            "metrics": combined_metrics
                        })

                self.record_metrics(system_health, {})

                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(interval)

    def get_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        latest_metrics = self.metrics_history[-1] if self.metrics_history else {}
        recent_alerts = self.alerts[-10:] if self.alerts else []

        return {
            "status": "healthy" if not recent_alerts else "warning",
            "latest_metrics": latest_metrics,
            "recent_alerts": recent_alerts,
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "generated_at": datetime.utcnow().isoformat()
        }