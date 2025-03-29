from flask import Blueprint, jsonify, redirect, url_for, render_template
from .monitor import get_system_metrics, detect_anomaly, check_alerts

# Define Blueprint
main = Blueprint('main', __name__)

# -----------------------------
# Default route for root URL "/"
# -----------------------------
@main.route('/', methods=['GET'])
def index():
    # Redirect to /metrics by default
    return redirect(url_for('main.dashboard'))

# -----------------------------
# Route to get system metrics
# -----------------------------
@main.route('/metrics', methods=['GET'])
def metrics():
    # Get real system metrics
    data = get_system_metrics()

    # Handle error or empty data
    if not data or data.get("cpu_usage") is None:
        return jsonify({"error": "Unable to fetch system metrics"}), 500

    # Check for anomalies with fallback
    try:
        anomaly_detected = detect_anomaly(data)
    except Exception as e:
        print(f"Error detecting anomaly: {e}")
        anomaly_detected = False

    # Check for threshold-based alerts and trigger if needed
    check_alerts(data)

    # Prepare and return response
    response = {
        "cpu_usage": float(data.get("cpu_usage", 0.0)),  # Safe fallback to 0.0
        "memory_usage": float(data.get("memory_usage", 0.0)),
        "load_avg": float(data.get("load_avg", 0.0)),
        "anomaly_detected": bool(anomaly_detected)  # Explicitly cast to bool
    }

    return jsonify(response)

# -----------------------------
# New Route: Dashboard
# -----------------------------
@main.route('/dashboard', methods=['GET'])
def dashboard():
    # Get system metrics for rendering the dashboard
    data = get_system_metrics()

    # Handle error or empty data
    if not data or data.get("cpu_usage") is None:
        data = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "load_avg": 0.0,
            "anomaly_detected": False
        }

    # Pass data to dashboard.html
    return render_template('dashboard.html', data=data)
