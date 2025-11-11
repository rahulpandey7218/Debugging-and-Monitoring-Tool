import psutil
import time
import json
import os
from datetime import datetime

class SystemMonitor:
    def __init__(self, log_interval=60, alert_threshold=90):
        self.log_interval = log_interval  # seconds
        self.alert_threshold = alert_threshold  # percentage
        self.alerts = []
        self.system_stats = []
        self.max_stats_history = 100  # Keep last 100 measurements

    def get_system_stats(self):
        """Get current CPU and memory usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        timestamp = datetime.now().isoformat()
        
        stats = {
            "timestamp": timestamp,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2)
        }
        
        # Add to history and maintain max size
        self.system_stats.append(stats)
        if len(self.system_stats) > self.max_stats_history:
            self.system_stats.pop(0)
            
        # Check for alerts
        self._check_alerts(stats)
        
        return stats
    
    def _check_alerts(self, stats):
        """Check if any metrics exceed thresholds and generate alerts"""
        alerts = []
        
        if stats["cpu_percent"] > self.alert_threshold:
            alerts.append({
                "timestamp": stats["timestamp"],
                "type": "CPU_HIGH",
                "message": f"High CPU usage detected: {stats['cpu_percent']}%",
                "severity": "WARNING" if stats["cpu_percent"] < 95 else "CRITICAL"
            })
            
        if stats["memory_percent"] > self.alert_threshold:
            alerts.append({
                "timestamp": stats["timestamp"],
                "type": "MEMORY_HIGH",
                "message": f"High memory usage detected: {stats['memory_percent']}%",
                "severity": "WARNING" if stats["memory_percent"] < 95 else "CRITICAL"
            })
            
        if stats["disk_percent"] > self.alert_threshold:
            alerts.append({
                "timestamp": stats["timestamp"],
                "type": "DISK_HIGH",
                "message": f"High disk usage detected: {stats['disk_percent']}%",
                "severity": "WARNING" if stats["disk_percent"] < 95 else "CRITICAL"
            })
            
        # Add new alerts to the list
        if alerts:
            self.alerts.extend(alerts)
            
        return alerts
    
    def get_alerts(self, limit=10):
        """Get recent alerts"""
        return self.alerts[-limit:] if self.alerts else []
    
    def get_stats_history(self):
        """Get system stats history"""
        return self.system_stats
    
    def start_monitoring(self):
        """Start continuous monitoring in background"""
        # This would typically be run in a separate thread
        # For simplicity, we'll just return the current stats
        return self.get_system_stats()

# Create a singleton instance
system_monitor = SystemMonitor()

# Function to get the monitor instance
def get_monitor():
    return system_monitor