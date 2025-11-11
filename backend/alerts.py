import json
import os
from datetime import datetime
import time

class AlertManager:
    def __init__(self):
        self.alerts = []
        self.subscribers = []
        self.alert_history_file = os.path.join(os.path.dirname(__file__), 'logs', 'alerts.json')
        self._load_alerts()
    
    def _load_alerts(self):
        """Load alerts from file if it exists"""
        if os.path.exists(self.alert_history_file):
            try:
                with open(self.alert_history_file, 'r') as f:
                    self.alerts = json.load(f)
            except:
                self.alerts = []
    
    def _save_alerts(self):
        """Save alerts to file"""
        os.makedirs(os.path.dirname(self.alert_history_file), exist_ok=True)
        with open(self.alert_history_file, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def add_alert(self, alert_type, message, severity="WARNING", data=None):
        """Add a new alert"""
        alert = {
            "id": len(self.alerts) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity,
            "data": data or {},
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        self._save_alerts()
        
        # Notify subscribers
        self._notify_subscribers(alert)
        
        return alert
    
    def get_alerts(self, limit=10, include_acknowledged=False):
        """Get recent alerts"""
        filtered = [a for a in self.alerts if include_acknowledged or not a.get("acknowledged")]
        return filtered[-limit:] if filtered else []
    
    def acknowledge_alert(self, alert_id):
        """Mark an alert as acknowledged"""
        for alert in self.alerts:
            if alert.get("id") == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                self._save_alerts()
                return True
        return False
    
    def subscribe(self, callback):
        """Subscribe to alerts"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)
    
    def unsubscribe(self, callback):
        """Unsubscribe from alerts"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _notify_subscribers(self, alert):
        """Notify all subscribers of a new alert"""
        for callback in self.subscribers:
            try:
                callback(alert)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")

# Create a singleton instance
alert_manager = AlertManager()

# Function to get the alert manager instance
def get_alert_manager():
    return alert_manager