from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import datetime
import random
import threading
import time
from ai_module import AIDebugger
from system_monitor import SystemMonitor
from alerts import AlertManager
from predictive import PredictiveAnalysis
from database import get_db_manager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Initialize components
sample_logs = []
alerts = []  # Initialize alerts list
ai_debugger = AIDebugger()
system_monitor = SystemMonitor()
alert_manager = AlertManager()
predictive_analysis = PredictiveAnalysis()

# Initialize JSON database manager
db_manager = get_db_manager('data')

# System statistics storage (JSON-based)
system_stats = []

# Start system monitoring in background
def monitor_system():
    while True:
        stats = system_monitor.get_system_stats()
        # Store stats in JSON database
        db_manager.add_system_stat(stats)
        
        # Check for alerts and persist to JSON DB (fix)
        alerts_list = system_monitor._check_alerts(stats)
        for alert in alerts_list:
            db_manager.add_alert({
                'timestamp': alert.get('timestamp'),
                'type': 'system',
                'message': alert.get('message'),
                'severity': alert.get('severity', 'WARNING'),
                'data': {'source': alert.get('type')},
                'acknowledged': False
            })
        
        time.sleep(30)  # Check every 30 seconds

# Start monitoring thread
monitor_thread = threading.Thread(target=monitor_system, daemon=True)
monitor_thread.start()

# Load sample log data from file
def load_sample_logs():
    global sample_logs
    try:
        with open('logs/sample_logs.json', 'r') as f:
            sample_logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Generate some sample logs if file doesn't exist
        generate_sample_logs()
        save_sample_logs()

# Save sample logs to file
def save_sample_logs():
    with open('logs/sample_logs.json', 'w') as f:
        json.dump(sample_logs, f, indent=2)
        
# Reset logs - clear all logs
def reset_logs():
    global sample_logs
    sample_logs = []
    # Clear persisted logs in JSON database
    try:
        db_manager.clear_logs()
    except Exception:
        pass
    save_sample_logs()

# Generate sample log data
def generate_sample_logs():
    global sample_logs
    log_types = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    services = ['auth-service', 'user-service', 'payment-service', 'api-gateway']
    messages = [
        'Application started successfully',
        'Database connection established',
        'Failed to connect to database',
        'User authentication failed',
        'Payment processing error',
        'Memory usage exceeds threshold',
        'CPU usage high',
        'Network timeout',
        'Invalid request parameters',
        'Unauthorized access attempt'
    ]
    
    # Generate 50 sample logs
    for i in range(50):
        severity = random.choice(log_types)
        timestamp = (datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )).isoformat()
        
        log_entry = {
            'id': i + 1,
            'timestamp': timestamp,
            'severity': severity,
            'service': random.choice(services),
            'message': random.choice(messages),
            'details': f'Log details for event {i+1}'
        }
        
        # Add stack trace for errors
        if severity in ['ERROR', 'CRITICAL']:
            log_entry['stack_trace'] = f"Exception in thread \"main\" java.lang.NullPointerException\n    at com.example.myproject.Book.getTitle(Book.java:16)\n    at com.example.myproject.Author.getBookTitles(Author.java:25)\n    at com.example.myproject.Bootstrap.main(Bootstrap.java:14)"
        
        sample_logs.append(log_entry)
    
    # Sort logs by timestamp (newest first)
    sample_logs.sort(key=lambda x: x['timestamp'], reverse=True)

# AI-based error analysis using the AIDebugger class
def analyze_error(log_entry):
    return ai_debugger.analyze_error(log_entry)

# Alert system
def generate_alert(log_entry):
    """Generate an alert for critical or error logs"""
    if log_entry['severity'] in ['ERROR', 'CRITICAL']:
        alert = {
            'id': len(alerts) + 1,
            'log_id': log_entry['id'],
            'timestamp': datetime.datetime.now().isoformat(),
            'severity': log_entry['severity'],
            'service': log_entry['service'],
            'message': f"Alert: {log_entry['message']}",
            'is_read': False
        }
        alerts.append(alert)
        
        # Save alert to JSON database
        db_manager.add_alert({
            'timestamp': alert['timestamp'],
            'type': 'system',
            'message': alert['message'],
            'severity': alert['severity'],
            'data': {
                'log_id': alert['log_id'],
                'service': alert['service'],
                'is_read': alert['is_read']
            },
            'acknowledged': alert['is_read']
        })
        
        return alert
    return None

# Simulate real-time log generation
def log_generator():
    """Background thread to generate new logs periodically"""
    global sample_logs
    
    log_types = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    services = ['auth-service', 'user-service', 'payment-service', 'api-gateway']
    messages = [
        'Application started successfully',
        'Database connection established',
        'Failed to connect to database',
        'User authentication failed',
        'Payment processing error',
        'Memory usage exceeds threshold',
        'CPU usage high',
        'Network timeout',
        'Invalid request parameters',
        'Unauthorized access attempt'
    ]
    
    while True:
        # Sleep for a random interval (5-15 seconds)
        time.sleep(random.randint(5, 15))
        
        # Generate a new log
        severity = random.choice(log_types)
        timestamp = datetime.datetime.now().isoformat()
        
        new_log = {
            'id': max([log['id'] for log in sample_logs]) + 1 if sample_logs else 1,
            'timestamp': timestamp,
            'severity': severity,
            'service': random.choice(services),
            'message': random.choice(messages),
            'details': f'Log details for event generated at {timestamp}'
        }
        
        # Add stack trace for errors
        if severity in ['ERROR', 'CRITICAL']:
            new_log['stack_trace'] = f"Exception in thread \"main\" java.lang.NullPointerException\n    at com.example.myproject.Book.getTitle(Book.java:16)\n    at com.example.myproject.Author.getBookTitles(Author.java:25)\n    at com.example.myproject.Bootstrap.main(Bootstrap.java:14)"
        
        # Add to logs
        sample_logs.insert(0, new_log)
        
        # Save log to JSON database
        db_manager.add_log(new_log)
        
        # Generate alert if needed
        if severity in ['ERROR', 'CRITICAL']:
            generate_alert(new_log)
        
        # Save logs periodically to file (legacy backup)
        if random.random() < 0.2:  # 20% chance to save
            save_sample_logs()

# API Routes
@app.route('/api/logs', methods=['GET'])
def get_logs():
    severity = request.args.get('severity')
    service = request.args.get('service')
    limit = request.args.get('limit', 100, type=int)
    
    # Try to get logs from JSON database first
    logs = db_manager.get_logs(limit=limit, severity=severity, service=service)
    if logs:
        return jsonify(logs)
    
    # Fall back to file-based logs if database is empty
    filtered_logs = sample_logs
    
    if severity:
        filtered_logs = [log for log in filtered_logs if log['severity'] == severity]
    
    if service:
        filtered_logs = [log for log in filtered_logs if log['service'] == service]
    
    return jsonify(filtered_logs[:limit])

@app.route('/api/logs/reset', methods=['POST'])
def reset_logs_endpoint():
    reset_logs()
    return jsonify({"status": "success", "message": "All logs have been reset"})

@app.route('/api/logs/<int:log_id>', methods=['GET'])
def get_log(log_id):
    # Prefer JSON database lookup
    log = db_manager.get_log_by_id(log_id)
    if log:
        return jsonify(log)
    
    # Fallback to in-memory logs
    for log_item in sample_logs:
        if log_item['id'] == log_id:
            return jsonify(log_item)
    
    return jsonify({'error': 'Log not found'}), 404

@app.route('/api/analyze/<int:log_id>', methods=['GET'])
def analyze_log(log_id):
    # Prefer JSON database lookup
    log = db_manager.get_log_by_id(log_id)
    if log:
        analysis = analyze_error(log)
        return jsonify({'log': log, 'analysis': analysis})
    
    # Fallback to in-memory logs
    for log_item in sample_logs:
        if log_item['id'] == log_id:
            analysis = analyze_error(log_item)
            return jsonify({'log': log_item, 'analysis': analysis})
    
    return jsonify({'error': 'Log not found'}), 404

@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    limit = request.args.get('limit', 20, type=int)
    
    # Get stats from JSON database
    stats = db_manager.get_system_stats(limit=limit)
    if stats:
        return jsonify(stats)
    
    # Fallback to current stats if database is empty
    current_stats = system_monitor.get_system_stats()
    return jsonify([current_stats])

@app.route('/api/database/status', methods=['GET'])
def get_database_status():
    return jsonify({
        "initialized": True,
        "connection_type": "JSON Files"
    })

@app.route('/api/database/connect', methods=['POST'])
def connect_database():
    # Return success message for JSON-based storage
    return jsonify({"message": "Using JSON file storage - no database connection needed"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # Calculate statistics
    total_logs = len(sample_logs)
    severity_counts = {}
    service_counts = {}
    
    for log in sample_logs:
        severity = log['severity']
        service = log['service']
        
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        service_counts[service] = service_counts.get(service, 0) + 1
    
    return jsonify({
        'total_logs': total_logs,
        'by_severity': severity_counts,
        'by_service': service_counts
    })

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts, with option to filter by read status"""
    is_read = request.args.get('is_read')
    limit = request.args.get('limit', 50, type=int)

    # Prefer JSON database alerts
    acknowledged = None
    if is_read is not None:
        acknowledged = is_read.lower() == 'true'
    alerts_data = db_manager.get_alerts(limit=limit, acknowledged=acknowledged)
    if alerts_data:
        # Normalize fields to match previous API
        normalized = []
        for a in alerts_data:
            normalized.append({
                'id': a.get('id'),
                'log_id': a.get('data', {}).get('log_id'),
                'timestamp': a.get('timestamp'),
                'severity': a.get('severity'),
                'service': a.get('data', {}).get('service'),
                'message': a.get('message'),
                'type': a.get('type'),
                'is_read': a.get('acknowledged', False)
            })
        return jsonify(normalized)

    # Fallback to in-memory alerts
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        filtered_alerts = [alert for alert in alerts if alert['is_read'] == is_read_bool]
        return jsonify(filtered_alerts[:limit])
    return jsonify(alerts[:limit])

@app.route('/api/alerts/<int:alert_id>/mark-read', methods=['POST'])
def mark_alert_read(alert_id):
    """Mark an alert as read/acknowledged and persist to JSON"""
    # Update JSON database
    persisted = db_manager.acknowledge_alert(alert_id)
    
    # Keep in-memory list in sync (best-effort)
    for alert in alerts:
        if alert['id'] == alert_id:
            alert['is_read'] = True
            break
    
    if persisted:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Alert not found'}), 404

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback on an AI analysis"""
    data = request.json
    
    if not data or 'log_id' not in data or 'was_helpful' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Save feedback using the AI debugger
    success = ai_debugger.save_feedback(
        data['log_id'],
        data.get('analysis_id', 'unknown'),
        data['was_helpful'],
        data.get('comments')
    )
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to save feedback'}), 500

@app.route('/api/add-log', methods=['POST'])
def add_log():
    """Add a new log entry"""
    data = request.json
    
    if not data or 'message' not in data or 'severity' not in data or 'service' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_log = {
        'id': max([log['id'] for log in sample_logs]) + 1 if sample_logs else 1,
        'timestamp': datetime.datetime.now().isoformat(),
        'severity': data['severity'],
        'service': data['service'],
        'message': data['message'],
        'details': data.get('details', 'No additional details')
    }
    
    # Add stack trace for errors
    if new_log['severity'] in ['ERROR', 'CRITICAL']:
        new_log['stack_trace'] = data.get('stack_trace', 'No stack trace provided')
    
    # Add to logs
    sample_logs.insert(0, new_log)

    # Persist to JSON database
    db_manager.add_log(new_log)
    
    # Generate alert if needed
    if new_log['severity'] in ['ERROR', 'CRITICAL']:
        generate_alert(new_log)
    
    # Save logs to file (legacy backup)
    save_sample_logs()
    
    return jsonify({'success': True, 'log': new_log})
    

load_sample_logs()

# Start background log generator thread
log_generator_thread = threading.Thread(target=log_generator, daemon=True)
log_generator_thread.start()

@app.route('/api/predict/logs', methods=['GET'])
def predict_logs():
    """Forecast future error counts using ARIMA over hourly log counts"""
    metric = request.args.get('metric', 'error_count')
    limit = request.args.get('limit', 500, type=int)

    # Pull logs from JSON DB
    logs = db_manager.get_logs(limit=limit)
    result = predictive_analysis.analyze_logs(logs, metric=metric)
    return jsonify(result)

@app.route('/api/ai/fix', methods=['POST'])
def ai_auto_fix():
    """Attempt automated remediation for common issues and broken states"""
    actions = []
    status = {
        'data_dir': os.path.abspath('data'),
        'logs_file': os.path.abspath(os.path.join('data', 'logs.json')),
        'alerts_file': os.path.abspath(os.path.join('data', 'alerts.json')),
        'stats_file': os.path.abspath(os.path.join('data', 'system_stats.json'))
    }

    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        actions.append('Created data directory')

    # Ensure JSON files exist and are valid lists
    for fname, key in [(status['logs_file'], 'logs'), (status['alerts_file'], 'alerts'), (status['stats_file'], 'stats')]:
        try:
            if not os.path.exists(fname):
                with open(fname, 'w') as f:
                    json.dump([], f)
                actions.append(f'Initialized missing {os.path.basename(fname)}')
            else:
                with open(fname, 'r') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError('Not a list')
        except Exception:
            with open(fname, 'w') as f:
                json.dump([], f)
            actions.append(f'Reset corrupted {os.path.basename(fname)} to empty list')

    # Capture a fresh system stat to verify monitor
    current_stats = system_monitor.get_system_stats()
    db_manager.add_system_stat(current_stats)
    actions.append('Captured and persisted fresh system stats')

    # Generate and persist alerts from current stats
    alerts_generated = system_monitor._check_alerts(current_stats)
    for alert in alerts_generated:
        db_manager.add_alert({
            'timestamp': alert.get('timestamp'),
            'type': 'system',
            'message': alert.get('message'),
            'severity': alert.get('severity', 'WARNING'),
            'data': {'source': alert.get('type')},
            'acknowledged': False
        })
    if alerts_generated:
        actions.append('Generated alerts from current system stats')

    # Quick health check of endpoints
    health = {
        'logs_count': len(db_manager.get_logs(limit=5)),
        'alerts_count': len(db_manager.get_alerts(limit=5)),
        'stats_count': len(db_manager.get_system_stats(limit=5))
    }

    return jsonify({'status': 'ok', 'actions': actions, 'health': health, 'current_stats': current_stats})

# Helper to fetch alert by ID from JSON DB
def _get_alert_by_id(alert_id: int):
    alert_list = db_manager.get_alerts(limit=1000)
    for a in alert_list:
        if a.get('id') == alert_id:
            return a
    return None

# Helper to attempt auto-remediation for a single alert
def _auto_remediate_alert(alert: dict):
    actions = []
    msg = alert.get('message', '') or ''
    source = (alert.get('data') or {}).get('source') or alert.get('type')

    # Ensure JSON storage is healthy (stand-in for DB/network checks)
    data_dir = 'data'
    files = [
        os.path.join(data_dir, 'logs.json'),
        os.path.join(data_dir, 'alerts.json'),
        os.path.join(data_dir, 'system_stats.json'),
    ]
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        actions.append('Created data directory')
    for fname in files:
        try:
            if not os.path.exists(fname):
                with open(fname, 'w') as f:
                    json.dump([], f)
                actions.append(f'Initialized missing {os.path.basename(fname)}')
            else:
                with open(fname, 'r') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError('Not a list')
        except Exception:
            with open(fname, 'w') as f:
                json.dump([], f)
            actions.append(f'Reset corrupted {os.path.basename(fname)} to empty list')

    # Capture a fresh system stat to validate runtime
    current_stats = system_monitor.get_system_stats()
    db_manager.add_system_stat(current_stats)
    actions.append('Captured fresh system stats')

    # Tailored remediation notes per alert type/message
    if 'Failed to connect to database' in msg:
        actions.append('Validated JSON storage in place of DB; acknowledge alert')
    elif 'Network timeout' in msg:
        actions.append('No network layer; recorded stats; acknowledge alert')
    elif source in ('CPU_HIGH', 'MEMORY_HIGH', 'DISK_HIGH'):
        actions.append('Threshold exceeded; recorded stats; suggest reviewing load')
    else:
        actions.append('No specific remediation available; acknowledge alert')

    # Write an audit alert about remediation
    db_manager.add_alert({
        'timestamp': datetime.datetime.now().isoformat(),
        'type': 'system',
        'message': f"Auto-fix applied to alert {alert.get('id')}",
        'severity': 'INFO',
        'data': {'remediated_alert_id': alert.get('id')},
        'acknowledged': False
    })

    return {'actions': actions}

@app.route('/api/alerts/<int:alert_id>/auto-fix', methods=['POST'])
def auto_fix_alert(alert_id):
    """Attempt to auto-remediate a single alert and acknowledge it"""
    alert = _get_alert_by_id(alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    result = _auto_remediate_alert(alert)

    # Acknowledge the alert after remediation attempt
    db_manager.acknowledge_alert(alert_id)

    return jsonify({'success': True, 'actions': result['actions']})

@app.route('/api/alerts/auto-fix-all', methods=['POST'])
def auto_fix_all_alerts():
    """Attempt to auto-remediate all active (unacknowledged) alerts"""
    active_alerts = db_manager.get_alerts(limit=1000, acknowledged=False)
    results = []
    for alert in active_alerts:
        res = _auto_remediate_alert(alert)
        db_manager.acknowledge_alert(alert.get('id'))
        results.append({'alert_id': alert.get('id'), 'actions': res['actions']})

    return jsonify({'success': True, 'count': len(results), 'results': results})

# Duplicate add_log block removed to avoid endpoint conflicts.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True, use_reloader=False)