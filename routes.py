from flask import render_template, jsonify, request
from app import app
from monitor_service import MonitoringService
import logging

# Initialize monitoring service
monitor = MonitoringService()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        # Get system overview data
        system_stats = monitor.get_system_stats()
        alerts = monitor.get_active_alerts()
        
        return render_template('dashboard.html', 
                             system_stats=system_stats,
                             alerts=alerts)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             system_stats={},
                             alerts=[],
                             error="Unable to load monitoring data")

@app.route('/metrics')
def metrics():
    """Detailed metrics page"""
    try:
        performance_data = monitor.get_performance_metrics()
        return render_template('metrics.html', metrics=performance_data)
    except Exception as e:
        logging.error(f"Error loading metrics: {e}")
        return render_template('metrics.html', 
                             metrics={},
                             error="Unable to load metrics data")

@app.route('/otp-services')
def otp_services():
    """OTP Services page"""
    try:
        # Define OTP services like in DELTA PRO
        services = [
            {"name": "Tokopedia", "prefix": "62", "status": "active"},
            {"name": "LionParcel", "prefix": "+62", "status": "active"},
            {"name": "KlikDokter", "prefix": "62", "status": "active"},
            {"name": "Alodokter", "prefix": "62", "status": "active"},
            {"name": "Shopee", "prefix": "62", "status": "maintenance"},
            {"name": "Bukalapak", "prefix": "62", "status": "active"}
        ]
        
        return render_template('otp_services.html', services=services)
    except Exception as e:
        logging.error(f"Error loading OTP services: {e}")
        return render_template('otp_services.html', 
                             services=[],
                             error="Unable to load OTP services")

@app.route('/logs')
def logs():
    """System logs viewer"""
    try:
        page = request.args.get('page', 1, type=int)
        filter_level = request.args.get('level', 'all')
        search_query = request.args.get('search', '')
        
        log_data = monitor.get_system_logs(page=page, 
                                         level=filter_level, 
                                         search=search_query)
        
        return render_template('logs.html', 
                             logs=log_data['logs'],
                             pagination=log_data['pagination'],
                             current_filters={'level': filter_level, 'search': search_query})
    except Exception as e:
        logging.error(f"Error loading logs: {e}")
        return render_template('logs.html', 
                             logs=[],
                             pagination={},
                             current_filters={},
                             error="Unable to load log data")

@app.route('/api/system-stats')
def api_system_stats():
    """API endpoint for real-time system stats"""
    try:
        stats = monitor.get_system_stats()
        return jsonify(stats)
    except Exception as e:
        logging.error(f"API error - system stats: {e}")
        return jsonify({'error': 'Unable to fetch system statistics'}), 500

@app.route('/api/performance-data')
def api_performance_data():
    """API endpoint for performance metrics"""
    try:
        timerange = request.args.get('timerange', '1h')
        data = monitor.get_performance_data(timerange)
        return jsonify(data)
    except Exception as e:
        logging.error(f"API error - performance data: {e}")
        return jsonify({'error': 'Unable to fetch performance data'}), 500

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for active alerts"""
    try:
        alerts = monitor.get_active_alerts()
        return jsonify(alerts)
    except Exception as e:
        logging.error(f"API error - alerts: {e}")
        return jsonify({'error': 'Unable to fetch alerts'}), 500

@app.route('/api/acknowledge-alert/<int:alert_id>', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        result = monitor.acknowledge_alert(alert_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"API error - acknowledge alert: {e}")
        return jsonify({'error': 'Unable to acknowledge alert'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('dashboard.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('dashboard.html', error="Internal server error"), 500
