// Global variables
const API_URL = 'http://localhost:5001/api';
let logsData = [];
let systemStats = [];
let alerts = [];

// DOM Elements
const logsTable = document.getElementById('logs-body');
const refreshBtn = document.getElementById('refresh-btn');
const resetBtn = document.getElementById('reset-btn');
const severityFilter = document.getElementById('severity-filter');
const serviceFilter = document.getElementById('service-filter');
const modal = document.getElementById('log-details-modal');
const closeModal = document.querySelector('.close');
const totalLogsElement = document.querySelector('#total-logs .stat-value');
const errorLogsElement = document.querySelector('#error-logs .stat-value');
const criticalLogsElement = document.querySelector('#critical-logs .stat-value');
const systemStatsContainer = document.getElementById('system-stats') || document.createElement('div');
const alertsContainer = document.getElementById('alerts-list') || document.createElement('div');
const aiFixBtn = document.getElementById('ai-fix-btn');
// Alerts dropdown elements
const alertsToggle = document.getElementById('alerts-toggle');
const alertsPanel = document.getElementById('alerts-panel');
const alertsBadge = document.getElementById('alerts-badge');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchLogs();
    fetchStats();
    fetchSystemStats();
    fetchAlerts();
    
    // Refresh system stats and alerts every 30 seconds
    setInterval(() => {
        fetchSystemStats();
        fetchAlerts();
    }, 30000);
});

// Dropdown toggle
alertsToggle && alertsToggle.addEventListener('click', (e) => {
  e.stopPropagation();
  fetchAlerts();
  alertsPanel && alertsPanel.classList.toggle('open');
  if (alertsToggle) alertsToggle.setAttribute('aria-expanded', alertsPanel && alertsPanel.classList.contains('open') ? 'true' : 'false');
});
// Close button inside dropdown
const alertsClose = document.getElementById('alerts-close');
alertsClose && alertsClose.addEventListener('click', () => {
  alertsPanel && alertsPanel.classList.remove('open');
  if (alertsToggle) alertsToggle.setAttribute('aria-expanded', 'false');
});
// Click outside to close
window.addEventListener('click', (e) => {
  if (alertsPanel && alertsPanel.classList.contains('open')) {
    const within = alertsPanel.contains(e.target) || (alertsToggle && alertsToggle.contains(e.target));
    if (!within) {
      alertsPanel.classList.remove('open');
      if (alertsToggle) alertsToggle.setAttribute('aria-expanded', 'false');
    }
  }
});

refreshBtn.addEventListener('click', () => {
    fetchLogs();
    fetchStats();
    fetchPredictive();
});

resetBtn.addEventListener('click', () => {
  resetLogs();
  autoFixAllAlerts();
});

async function autoFixAllAlerts() {
  try {
    const response = await fetch(`${API_URL}/alerts/auto-fix-all`, { method: 'POST' });
    const result = await response.json();
    alert(`Alerts auto-fixed: ${result.count}`);
    // Refresh alerts/UI state
    fetchAlerts();
  } catch (error) {
    console.error('Error auto-fixing alerts:', error);
    alert('Failed to auto-fix alerts.');
  }
}
aiFixBtn && aiFixBtn.addEventListener('click', () => {
    runAIFix();
});
severityFilter.addEventListener('change', fetchLogs);
serviceFilter.addEventListener('change', fetchLogs);

closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

// Fetch logs from API
async function fetchLogs() {
    try {
        const severity = severityFilter.value;
        const service = serviceFilter.value;
        
        let url = `${API_URL}/logs`;
        const params = [];
        
        if (severity) params.push(`severity=${severity}`);
        if (service) params.push(`service=${service}`);
        
        if (params.length > 0) {
            url += `?${params.join('&')}`;
        }
        
        const response = await fetch(url);
        logsData = await response.json();
        
        renderLogs();
    } catch (error) {
        console.error('Error fetching logs:', error);
        alert('Failed to fetch logs. Please try again later.');
    }
}

// Fetch statistics from API
async function fetchStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const stats = await response.json();
        
        // Update stats cards
        totalLogsElement.textContent = stats.total_logs;
        errorLogsElement.textContent = stats.by_severity.ERROR || 0;
        criticalLogsElement.textContent = stats.by_severity.CRITICAL || 0;
        
        // Update charts
        updateSeverityChart(stats.by_severity);
        updateServiceChart(stats.by_service);
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// Render logs in the table
function renderLogs() {
    logsTable.innerHTML = '';
    
    if (logsData.length === 0) {
        logsTable.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center;">No logs found</td>
            </tr>
        `;
        return;
    }
    
    logsData.forEach(log => {
        const row = document.createElement('tr');
        
        // Format date
        const date = new Date(log.timestamp);
        const formattedDate = date.toLocaleString();
        
        // Determine severity class
        const severityClass = `severity-${log.severity.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${log.id}</td>
            <td>${formattedDate}</td>
            <td class="${severityClass}">${log.severity}</td>
            <td>${log.service}</td>
            <td>${log.message}</td>
            <td>
                <button class="action-btn" onclick="viewLogDetails(${log.id})">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn" onclick="analyzeLog(${log.id})">
                    <i class="fas fa-brain"></i>
                </button>
            </td>
        `;
        
        logsTable.appendChild(row);
    });
}

// View log details
async function viewLogDetails(logId) {
    try {
        const response = await fetch(`${API_URL}/logs/${logId}`);
        const log = await response.json();
        
        const detailsContent = document.getElementById('log-details-content');
        
        // Format date
        const date = new Date(log.timestamp);
        const formattedDate = date.toLocaleString();
        
        let html = `
            <div class="log-detail-item">
                <span class="log-detail-label">ID:</span> ${log.id}
            </div>
            <div class="log-detail-item">
                <span class="log-detail-label">Timestamp:</span> ${formattedDate}
            </div>
            <div class="log-detail-item">
                <span class="log-detail-label">Severity:</span> 
                <span class="severity-${log.severity.toLowerCase()}">${log.severity}</span>
            </div>
            <div class="log-detail-item">
                <span class="log-detail-label">Service:</span> ${log.service}
            </div>
            <div class="log-detail-item">
                <span class="log-detail-label">Message:</span> ${log.message}
            </div>
            <div class="log-detail-item">
                <span class="log-detail-label">Details:</span> ${log.details}
            </div>
        `;
        
        // Add stack trace if available
        if (log.stack_trace) {
            html += `
                <div class="log-detail-item">
                    <span class="log-detail-label">Stack Trace:</span>
                    <div class="stack-trace">${log.stack_trace}</div>
                </div>
            `;
        }
        
        detailsContent.innerHTML = html;
        
        // Hide analysis section initially
        document.getElementById('ai-analysis').style.display = 'none';
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error fetching log details:', error);
        alert('Failed to fetch log details. Please try again later.');
    }
}

// Reset logs
async function resetLogs() {
    try {
        const response = await fetch(`${API_URL}/logs/reset`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('Logs have been reset successfully');
            fetchLogs();
            fetchStats();
        } else {
            alert('Failed to reset logs. Please try again.');
        }
    } catch (error) {
        console.error('Error resetting logs:', error);
        alert('Failed to reset logs. Please try again later.');
    }
}

// Analyze log with AI
async function analyzeLog(logId) {
    try {
        const response = await fetch(`${API_URL}/analyze/${logId}`);
        const data = await response.json();
        
        // First show the log details
        await viewLogDetails(logId);
        
        // Then show the analysis
        const analysisContent = document.getElementById('analysis-content');
        const analysisSection = document.getElementById('ai-analysis');
        
        let html = `
            <div class="analysis-item">
                <span class="log-detail-label">Probable Cause:</span> 
                ${data.analysis.probable_cause}
            </div>
            <div class="analysis-item">
                <span class="log-detail-label">Suggestion:</span>
                <div class="suggestion">${data.analysis.suggestion}</div>
            </div>
        `;
        
        analysisContent.innerHTML = html;
        analysisSection.style.display = 'block';
    } catch (error) {
        console.error('Error analyzing log:', error);
        alert('Failed to analyze log. Please try again later.');
    }
}

// Update severity chart
function updateSeverityChart(severityData) {
    const chartContainer = document.querySelector('#severity-chart .chart-placeholder');
    chartContainer.innerHTML = '';
    
    const total = Object.values(severityData).reduce((sum, count) => sum + count, 0);
    
    const severityColors = {
        'INFO': '#4CAF50',
        'WARNING': '#FFC107',
        'ERROR': '#F44336',
        'CRITICAL': '#9C27B0'
    };
    
    Object.entries(severityData).forEach(([severity, count]) => {
        const percentage = (count / total) * 100;
        const bar = document.createElement('div');
        
        bar.className = 'chart-bar';
        bar.style.height = `${percentage}%`;
        bar.style.backgroundColor = severityColors[severity] || '#999';
        
        const label = document.createElement('span');
        label.className = 'chart-label';
        label.textContent = severity;
        
        bar.appendChild(label);
        chartContainer.appendChild(bar);
    });
}

// Update service chart
function updateServiceChart(serviceData) {
    const chartContainer = document.querySelector('#service-chart .chart-placeholder');
    chartContainer.innerHTML = '';
    
    const total = Object.values(serviceData).reduce((sum, count) => sum + count, 0);
    
    const serviceColors = {
        'auth-service': '#2196F3',
        'user-service': '#009688',
        'payment-service': '#FF5722',
        'api-gateway': '#607D8B'
    };
    
    Object.entries(serviceData).forEach(([service, count]) => {
        const percentage = (count / total) * 100;
        const bar = document.createElement('div');
        
        bar.className = 'chart-bar';
        bar.style.height = `${percentage}%`;
        bar.style.backgroundColor = serviceColors[service] || '#999';
        
        const label = document.createElement('span');
        label.className = 'chart-label';
        label.textContent = service.replace('-service', '').replace('-gateway', '');
        
        bar.appendChild(label);
        chartContainer.appendChild(bar);
    });
}

// Fetch system stats from API
function fetchSystemStats() {
    fetch(`${API_URL}/system/stats`)
        .then(response => response.json())
        .then(data => {
            systemStats = data;
            updateSystemStatsDisplay();
        })
        .catch(error => console.error('Error fetching system stats:', error));
}

// Update system stats display
function updateSystemStatsDisplay() {
    if (systemStats && systemStats.length > 0) {
        const latestStats = systemStats[0];
        const cpuPercent = latestStats.cpu_percent || 0;
        const memoryPercent = latestStats.memory_percent || 0;

        const cpuEl = document.getElementById('cpu-value');
        const memEl = document.getElementById('mem-value');
        if (cpuEl) cpuEl.textContent = `${cpuPercent.toFixed(1)}%`;
        if (memEl) memEl.textContent = `${memoryPercent.toFixed(1)}%`;
    }
}

// Fetch alerts from API
async function fetchAlerts() {
    try {
        const response = await fetch(`${API_URL}/alerts`);
        const allAlerts = await response.json();
        const activeAlerts = (allAlerts || []).filter(a => {
            const severity = (a?.severity || '').toUpperCase();
            const isInformational = severity === 'INFO';
            const isUnacked = a?.acknowledged === false || a?.is_read === false;
            return isUnacked && !isInformational;
        });
        renderAlerts(activeAlerts);
    } catch (error) {
        console.error('Error fetching alerts:', error);
    }
}

// Enhance alert rendering with class names based on type
function renderAlerts(alerts) {
  const container = document.getElementById('alerts-list');
  if (!container) return;
  container.innerHTML = '';
  // Update badge
  if (alertsBadge) {
    const count = alerts.length;
    if (count > 0) {
      alertsBadge.textContent = count;
      alertsBadge.style.display = 'inline-block';
    } else {
      alertsBadge.textContent = '0';
      alertsBadge.style.display = 'none';
    }
  }
  if (!alerts.length) {
    container.innerHTML = '<div class="alerts-empty">No active alerts</div>';
    return;
  }
  alerts.forEach(alert => {
    const item = document.createElement('div');
    const typeClass = (alert.severity || alert.type || '').toLowerCase();
    item.className = `alert-item ${typeClass}`;
    const ts = alert.timestamp ? new Date(alert.timestamp) : new Date();
    item.innerHTML = `
      <div class="alert-header">
        <span class="alert-type">${(alert.type || alert.severity || 'Alert')}</span>
        <span class="alert-time">${ts.toLocaleString()}</span>
      </div>
      <div class="alert-message">${alert.message || ''}</div>
    `;
    container.appendChild(item);
  });
}
async function runAIFix() {
    try {
        const response = await fetch(`${API_URL}/ai/fix`, { method: 'POST' });
        const result = await response.json();
        alert(`AI Fix applied:\n- ${result.actions.join('\n- ')}`);
        // Refresh key data
        fetchSystemStats();
        fetchLogs();
        fetchStats();
        fetchAlerts();
        fetchPredictive();
    } catch (error) {
        console.error('Error running AI fix:', error);
        alert('Failed to run AI Fix.');
    }
}
async function fetchPredictive() {
    try {
        const response = await fetch(`${API_URL}/predict/logs?metric=error_count&limit=500`);
        const data = await response.json();
        renderPrediction(data.forecast || []);
    } catch (error) {
        console.error('Error fetching predictions:', error);
    }
}

function renderPrediction(forecast) {
    const bars = document.getElementById('predict-bars');
    if (!bars) return;
    bars.innerHTML = '';
    if (!forecast.length) {
        bars.innerHTML = '<div style="text-align:center;width:100%">No prediction available</div>';
        return;
    }
    const maxVal = Math.max(...forecast.map(f => f.predicted_value));
    forecast.forEach(item => {
        const percent = maxVal ? (item.predicted_value / maxVal) * 100 : 0;
        const bar = document.createElement('div');
        bar.className = 'chart-bar';
        bar.style.height = `${percent}%`;
        bar.style.backgroundColor = '#8e44ad';
        const label = document.createElement('span');
        label.className = 'chart-label';
        label.textContent = new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        bar.appendChild(label);
        bars.appendChild(bar);
    });
}

// Initial predictive fetch on load
document.addEventListener('DOMContentLoaded', fetchPredictive);

// Wire format classes to control buttons
function applyButtonStyles() {
  const refreshBtn = document.getElementById('refresh-btn');
  const resetBtn = document.getElementById('reset-btn');
  const aiFixBtn = document.getElementById('ai-fix-btn');
  if (refreshBtn) refreshBtn.classList.add('btn');
  if (resetBtn) resetBtn.classList.add('btn', 'btn-danger');
  if (aiFixBtn) aiFixBtn.classList.add('btn');
}

// Run once on DOM ready
window.addEventListener('DOMContentLoaded', () => {
  applyButtonStyles();
});