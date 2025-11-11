from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import os
import datetime
import random
import threading
import time
from backend.ai_module import AIDebugger

app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app)  # Enable CORS for all routes

# Create logs directory if it doesn't exist
if not os.path.exists('backend/logs'):
    os.makedirs('backend/logs')

# Sample log data (in a real app, this would be stored in a database)
sample_logs = []
alerts = []
ai_debugger = AIDebugger()

# Load sample log data from file
def load_sample_logs():
    global sample_logs
    try:
        with open('backend/logs/sample_logs.json', 'r') as f:
            sample_logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Generate some sample logs if file doesn't exist
        generate_sample_logs()
        save_sample_logs()

# Save sample logs to file
def save_sample_logs():
    with open('backend/logs/sample_logs.json', 'w') as f:
        json.dump(sample_logs, f, indent=2)
        
# Reset logs - clear all logs
def reset_logs():
    global sample_logs
    sample_logs = []
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
            log_entry['stack_trace'] = 'Exception in thread "main" java.lang.NullPointerException\\n    at com.example.myproject.Book.getTitle(Book.java:16)\\n    at com.example.myproject.Author.getBookTitles(Author.java:25)\\n    at com.example.myproject.Bootstrap.main(Bootstrap.java:14)'
        
        sample_logs.append(log_entry)

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
            new_log['stack_trace'] = 'Exception in thread "main" java.lang.NullPointerException\\n    at com.example.myproject.Book.getTitle(Book.java:16)\\n    at com.example.myproject.Author.getBookTitles(Author.java:25)\\n    at com.example.myproject.Bootstrap.main(Bootstrap.java:14)'
        
        # Add to logs
        sample_logs.insert(0, new_log)
        
        # Generate alert if needed
        if new_log['severity'] in ['ERROR', 'CRITICAL']:
            generate_alert(new_log)
        
        # Save logs
        save_sample_logs()

# Frontend route - serve the main page
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

# Serve static files (CSS, JS)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

# API Routes
@app.route('/api/logs', methods=['GET'])
def get_logs():
    severity_filter = request.args.get('severity')
    service_filter = request.args.get('service')
    
    filtered_logs = sample_logs
    
    if severity_filter:
        filtered_logs = [log for log in filtered_logs if log['severity'] == severity_filter]
    
    if service_filter:
        filtered_logs = [log for log in filtered_logs if log['service'] == service_filter]
    
    return jsonify(filtered_logs)

@app.route('/api/logs/reset', methods=['POST'])
def reset_logs_endpoint():
    reset_logs()
    return jsonify({"status": "success", "message": "All logs have been reset"})

@app.route('/api/logs/<int:log_id>', methods=['GET'])
def get_log(log_id):
    for log in sample_logs:
        if log['id'] == log_id:
            return jsonify(log)
    
    return jsonify({'error': 'Log not found'}), 404

@app.route('/api/analyze/<int:log_id>', methods=['GET'])
def analyze_log(log_id):
    for log in sample_logs:
        if log['id'] == log_id:
            analysis = analyze_error(log)
            return jsonify({
                'log': log,
                'analysis': analysis
            })
    
    return jsonify({'error': 'Log not found'}), 404

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
    """Get all alerts"""
    return jsonify(alerts)

@app.route('/api/alerts/<int:alert_id>/mark-read', methods=['POST'])
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    for alert in alerts:
        if alert['id'] == alert_id:
            alert['is_read'] = True
            return jsonify({'success': True})
    
    return jsonify({'error': 'Alert not found'}), 404

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
    
    # Generate alert if needed
    if new_log['severity'] in ['ERROR', 'CRITICAL']:
        generate_alert(new_log)
    
    # Save logs
    save_sample_logs()
    
    return jsonify(new_log)

# Initialize data and start background processes
load_sample_logs()

# Start background log generator thread
log_generator_thread = threading.Thread(target=log_generator, daemon=True)
log_generator_thread.start()

if __name__ == '__main__':
    print("Starting unified server...")
    print("Frontend will be available at: http://localhost:5001")
    print("API endpoints available at: http://localhost:5001/api/")
    app.run(debug=True, port=5001, host='0.0.0.0')