import json
import os
from datetime import datetime

class JSONDatabaseManager:
    """Simple JSON-based database manager for lightweight storage"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.logs_file = os.path.join(data_dir, 'logs.json')
        self.stats_file = os.path.join(data_dir, 'system_stats.json')
        self.alerts_file = os.path.join(data_dir, 'alerts.json')
        self.initialized = True
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_json_data(self, filename):
        """Load data from JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_json_data(self, filename, data):
        """Save data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")
            return False
    
    def add_log(self, log_data):
        """Add a log entry to JSON storage"""
        try:
            logs = self._load_json_data(self.logs_file)
            log_entry = {
                'id': len(logs) + 1,
                'timestamp': log_data.get('timestamp', datetime.now().isoformat()),
                'severity': log_data.get('severity', 'INFO'),
                'service': log_data.get('service', 'unknown'),
                'message': log_data.get('message', ''),
                'details': log_data.get('details', ''),
                'stack_trace': log_data.get('stack_trace', '')
            }
            logs.insert(0, log_entry)
            self._save_json_data(self.logs_file, logs)
            return log_entry['id']
        except Exception as e:
            print(f"Error adding log: {e}")
            return None
    
    def get_logs(self, limit=100, severity=None, service=None):
        """Get logs with optional filtering"""
        try:
            logs = self._load_json_data(self.logs_file)
            
            # Apply filters
            if severity:
                logs = [log for log in logs if log['severity'] == severity]
            if service:
                logs = [log for log in logs if log['service'] == service]
            
            return logs[:limit]
        except Exception as e:
            print(f"Error getting logs: {e}")
            return []

    # Add ability to clear persisted logs
    def clear_logs(self) -> bool:
        try:
            return self._save_json_data(self.logs_file, [])
        except Exception as e:
            print(f"Error clearing logs: {e}")
            return False

    def get_log_by_id(self, log_id):
        """Get a single log by ID"""
        try:
            logs = self._load_json_data(self.logs_file)
            for log in logs:
                if log.get('id') == log_id:
                    return log
            return None
        except Exception as e:
            print(f"Error getting log by id: {e}")
            return None
    
    def add_system_stat(self, stat_data):
        """Add system statistics to JSON storage"""
        try:
            stats = self._load_json_data(self.stats_file)
            stat_entry = {
                'id': len(stats) + 1,
                'timestamp': stat_data.get('timestamp', datetime.now().isoformat()),
                'cpu_percent': stat_data.get('cpu_percent', 0),
                'memory_percent': stat_data.get('memory_percent', 0),
                'disk_percent': stat_data.get('disk_percent', 0),
                'memory_total_gb': stat_data.get('memory_total_gb', 0),
                'memory_used_gb': stat_data.get('memory_used_gb', 0)
            }
            stats.insert(0, stat_entry)
            
            # Keep only last 1000 entries
            if len(stats) > 1000:
                stats = stats[:1000]
            
            self._save_json_data(self.stats_file, stats)
            return stat_entry['id']
        except Exception as e:
            print(f"Error adding system stat: {e}")
            return None
    
    def get_system_stats(self, limit=100):
        """Get system statistics"""
        try:
            stats = self._load_json_data(self.stats_file)
            return stats[:limit]
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return []
    
    def add_alert(self, alert_data):
        """Add an alert to JSON storage"""
        try:
            alerts = self._load_json_data(self.alerts_file)
            alert_entry = {
                'id': len(alerts) + 1,
                'timestamp': alert_data.get('timestamp', datetime.now().isoformat()),
                'type': alert_data.get('type', 'system'),
                'message': alert_data.get('message', ''),
                'severity': alert_data.get('severity', 'WARNING'),
                'data': alert_data.get('data', {}),
                'acknowledged': alert_data.get('acknowledged', False),
                'acknowledged_at': alert_data.get('acknowledged_at')
            }
            alerts.insert(0, alert_entry)
            self._save_json_data(self.alerts_file, alerts)
            return alert_entry['id']
        except Exception as e:
            print(f"Error adding alert: {e}")
            return None
    
    def get_alerts(self, limit=100, acknowledged=None):
        """Get alerts with optional filtering"""
        try:
            alerts = self._load_json_data(self.alerts_file)
            
            # Apply filters
            if acknowledged is not None:
                alerts = [alert for alert in alerts if alert['acknowledged'] == acknowledged]
            
            return alerts[:limit]
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Mark an alert as acknowledged in JSON storage"""
        try:
            alerts = self._load_json_data(self.alerts_file)
            updated = False
            for alert in alerts:
                if alert.get('id') == alert_id:
                    alert['acknowledged'] = True
                    alert['acknowledged_at'] = datetime.now().isoformat()
                    updated = True
                    break
            if updated:
                return self._save_json_data(self.alerts_file, alerts)
            return False
        except Exception as e:
            print(f"Error acknowledging alert: {e}")
            return False

# Global JSON database manager instance
db_manager = None

def get_db_manager(data_dir='data'):
    """Get or create the JSON database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = JSONDatabaseManager(data_dir)
    return db_manager