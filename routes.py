from flask import render_template, jsonify, request
from app import app
from monitor_service import MonitoringService
import logging
import time
from datetime import datetime

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

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to phone number using real OTP services"""
    try:
        import requests
        import json
        import uuid
        
        data = request.get_json()
        service = data.get('service')
        phone = data.get('phone')
        
        if not service or not phone:
            return jsonify({
                'status': 'error',
                'message': 'Service dan nomor telepon harus diisi'
            }), 400
        
        # Log request
        logging.info(f"OTP request - Service: {service}, Phone: {phone}")
        
        # OTP Services configuration
        OTP_SERVICES = {
            "Tokopedia": {
                "url": "https://gql.tokopedia.com/graphql/OTPRequest",
                "headers": {
                    'User-Agent': "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.7103.61 Mobile Safari/537.36",
                    'Content-Type': "application/json",
                    'x-source': "tokopedia-lite",
                    'origin': "https://www.tokopedia.com",
                    'referer': "https://www.tokopedia.com/register",
                },
                "payload": json.dumps([{
                    "operationName": "OTPRequest",
                    "variables": {
                        "msisdn": phone,
                        "otpType": "116",
                        "mode": "whatsapp",
                        "otpDigit": 6
                    },
                    "query": """
                    query OTPRequest($otpType: String!, $mode: String, $msisdn: String, $otpDigit: Int) {
                      OTPRequest: OTPRequestV2(otpType: $otpType, mode: $mode, msisdn: $msisdn, otpDigit: $otpDigit) {
                        success
                        message
                        errorMessage
                      }
                    }
                    """
                }])
            },
            "LionParcel": {
                "url": "https://algo-api.lionparcel.com/v2/account/auth/otp/request",
                "headers": {
                    'User-Agent': "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36",
                    'Accept': "application/json, text/plain, */*",
                    'Content-Type': "application/json",
                    'origin': "https://lionparcel.com",
                    'referer': "https://lionparcel.com/register",
                    'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                },
                "payload": json.dumps({
                    "phone_number": phone,
                    "role": "CUSTOMER",
                    "otp_type": "REGISTER",
                    "messaging_type": "WHATSAPP"
                })
            },
            "KlikDokter": {
                "url": "https://user-api.medkomtek.com/user-svc/api/v1/users/check",
                "headers": {
                    'User-Agent': "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36",
                    'Accept': "application/json",
                    'Content-Type': "application/json",
                    'x-api-platform': "eyJhcHBfdmVyc2lvbiI6IjIuMC4wIiwicGxhdGZvcm0iOiJ3ZWIiLCJtYW51ZmFjdHVyZXIiOiJCbGluayIsInByb2R1Y3QiOiJWMjIwNSIsImRlc2NyaXB0aW9uIjoiQW5kcm9pZCBCcm93c2VyIDQuMCAobGlrZSBDaHJvbWUgMTM2LjAuNzEwMy42MSkgb24gVjIyMDUgKEFuZHJvaWQgMTQpIiwidGltZXpvbmUiOiJBc2lhL01ha2Fzc2FyIn0=",
                    'origin': "https://www.klikdokter.com",
                    'referer': "https://www.klikdokter.com/",
                    'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
                },
                "payload": json.dumps({"phone": phone})
            },
            "Alodokter": {
                "url": "https://www.alodokter.com/resend-otp",
                "headers": {
                    'User-Agent': "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36",
                    'Accept': "application/json",
                    'Content-Type': "application/json",
                    'Origin': "https://www.alodokter.com",
                    'Referer': f"https://www.alodokter.com/otp_phone_number?type=register&phone={phone}",
                    'Accept-Language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
                },
                "payload": json.dumps({
                    "user": {
                        "phone": phone,
                        "uuid": str(uuid.uuid4())
                    },
                    "request_via": "sms"
                })
            }
        }
        
        if service not in OTP_SERVICES:
            return jsonify({
                'status': 'error',
                'message': f'Layanan {service} tidak tersedia'
            }), 400
        
        # Get service configuration
        svc = OTP_SERVICES[service]
        
        try:
            # Send OTP request
            response = requests.post(
                svc['url'],
                data=svc['payload'],
                headers=svc['headers'],
                timeout=10
            )
            
            # Parse response
            try:
                resp_json = response.json()
            except Exception:
                return jsonify({
                    'status': 'error',
                    'message': 'Response dari server OTP tidak valid',
                    'service': service,
                    'phone': phone
                }), 502
            
            # Log successful request
            logging.info(f"OTP sent successfully - Service: {service}, Phone: {phone}, Response: {resp_json}")
            
            return jsonify({
                'status': 'success',
                'message': f'OTP berhasil dikirim ke {phone} melalui {service}',
                'service': service,
                'phone': phone,
                'response': resp_json,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except requests.RequestException as e:
            logging.error(f"Network error sending OTP: {e}")
            return jsonify({
                'status': 'error',
                'message': f'Gagal menghubungi server {service}',
                'error': str(e)
            }), 502
        
    except Exception as e:
        logging.error(f"Error sending OTP: {e}")
        return jsonify({
            'status': 'error', 
            'message': 'Terjadi kesalahan saat memproses permintaan OTP',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('dashboard.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('dashboard.html', error="Internal server error"), 500
