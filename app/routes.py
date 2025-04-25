from flask import Blueprint, jsonify, redirect, url_for, render_template, current_app
from .monitor import get_system_metrics, detect_anomaly, check_alerts

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Redirects root URL to the dashboard."""
    return redirect(url_for('main.dashboard'))

@main.route('/metrics')
def metrics():
    """API endpoint to fetch system metrics and anomaly status."""
    data = get_system_metrics() # Returns dict or None

    if data is None:
        # Logged in get_system_metrics already
        return jsonify({"error": "Unable to fetch system metrics"}), 500

    # Perform anomaly detection and check alerts based on fetched data
    # Wrap anomaly detection in try-except as it involves file I/O (loading model)
    try:
        anomaly_detected = detect_anomaly(data)
    except Exception as e:
        current_app.logger.error(f"Error during anomaly detection route: {e}", exc_info=True)
        anomaly_detected = False # Default to false on error

    # Check alerts (this function handles its own errors/logging)
    check_alerts(data)

    # Prepare and return JSON response
    return jsonify({
        "cpu_usage": float(data.get("cpu_usage", 0.0)), # Keep float conversion
        "memory_usage": float(data.get("memory_usage", 0.0)),
        "load_avg": float(data.get("load_avg", 0.0)),
        "anomaly_detected": bool(anomaly_detected) # Keep bool conversion
    })

@main.route('/dashboard')
def dashboard():
    """Renders the main dashboard page."""
    # Render the template. The actual data will be populated by JavaScript
    # calling the /metrics endpoint. Pass initial state if needed, or just render.
    # No need to call get_system_metrics here anymore.
    return render_template('dashboard.html') # Pass no data initially