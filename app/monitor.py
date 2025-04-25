import psutil
# import platform # Removed as it's not used
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pathlib import Path
from flask import current_app
import random
import logging # Import logging for type hinting and clarity

# Load environment variables
load_dotenv()

# --- Configuration ---
# Use environment variables for configuration where possible
DEFAULT_MODEL_PATH = Path("models/anomaly_model.pkl")
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(DEFAULT_MODEL_PATH))) # Ensure path is string for os.getenv default

DEFAULT_CPU_THRESHOLD = 80.0
DEFAULT_MEM_THRESHOLD = 80.0
DEFAULT_LOAD_THRESHOLD = 5.0

# Convert environment variables to float, using defaults if not set
try:
    CPU_ALERT_THRESHOLD = float(os.getenv("CPU_ALERT_THRESHOLD", DEFAULT_CPU_THRESHOLD))
    MEMORY_ALERT_THRESHOLD = float(os.getenv("MEMORY_ALERT_THRESHOLD", DEFAULT_MEM_THRESHOLD))
    LOAD_ALERT_THRESHOLD = float(os.getenv("LOAD_ALERT_THRESHOLD", DEFAULT_LOAD_THRESHOLD))
except (ValueError, TypeError) as e:
    # Log an error if environment variables cannot be converted to float
    # and use default values as a fallback
    if 'current_app' in globals() and current_app:
        current_app.logger.error(f"Error converting threshold environment variables: {e}. Using default thresholds.", exc_info=True)
    else:
        logging.error(f"Error converting threshold environment variables: {e}. Using default thresholds.", exc_info=True)

    CPU_ALERT_THRESHOLD = DEFAULT_CPU_THRESHOLD
    MEMORY_ALERT_THRESHOLD = DEFAULT_MEM_THRESHOLD
    LOAD_ALERT_THRESHOLD = DEFAULT_LOAD_THRESHOLD


EMAIL_USER = os.getenv("GMAIL_USERNAME")
EMAIL_PASS = os.getenv("GMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL") # Correctly defined here
# --- End Configuration ---

def get_system_metrics():
    """Fetch real-time system metrics. Returns None on error."""
    try:
        # cpu_percent interval=1 blocks for 1 second, might not be ideal for a web request
        # Consider a shorter interval or fetching metrics less frequently in the calling code
        cpu = psutil.cpu_percent(interval=0.1) # Reduced interval slightly
        memory = psutil.virtual_memory().percent
        # Use os.getloadavg() only on non-Windows platforms
        # os.getloadavg() returns a tuple of 1, 5, and 15 minute load averages
        # We'll use the 1-minute average (index 0)
        load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0

        return {
            "cpu_usage": cpu,
            "memory_usage": memory,
            "load_avg": load,
        }
    except Exception as e:
        # Use current_app.logger for logging within the Flask application context
        # Ensure logging is configured in create_app before calling this function
        if 'current_app' in globals() and current_app:
             current_app.logger.error(f"Error fetching system metrics: {e}", exc_info=True) # Log traceback
        else:
             # Fallback logging if current_app is not available (e.g., running script directly)
             logging.error(f"Error fetching system metrics: {e}", exc_info=True)
        return None # Return None to indicate failure

def train_anomaly_model():
    """Train and save an Isolation Forest model."""
    try:
        # Ensure the models directory exists
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Generate synthetic normal data for training
        # NOTE: Replace with actual historical data for production use
        if 'current_app' in globals() and current_app:
            current_app.logger.warning("Training anomaly model with SYNTHETIC data.")
        else:
            logging.warning("Training anomaly model with SYNTHETIC data.")

        # Create synthetic data: 1000 samples, 3 features (cpu, memory, load)
        # Adjust loc (mean) and scale (std dev) based on expected normal behavior
        data = np.random.normal(loc=[20, 50, 0.5], scale=[5, 10, 0.2], size=(1000, 3))

        # Create and train Isolation Forest model
        # contamination: the proportion of outliers in the data set.
        # Adjust contamination based on your expected anomaly rate.
        model = IsolationForest(n_estimators=100, contamination='auto', random_state=42) # Use 'auto' or a specific float
        model.fit(data)

        # Save model to the specified path
        joblib.dump(model, MODEL_PATH)
        if 'current_app' in globals() and current_app:
            current_app.logger.info(f"✅ Anomaly model trained and saved to {MODEL_PATH}")
        else:
            logging.info(f"✅ Anomaly model trained and saved to {MODEL_PATH}")

    except Exception as e:
        if 'current_app' in globals() and current_app:
            current_app.logger.error(f"Error training anomaly model: {e}", exc_info=True)
        else:
            logging.error(f"Error training anomaly model: {e}", exc_info=True)


def load_model():
    """Load the trained model from disk."""
    try:
        # Check if model exists, if not, train a new one
        if not MODEL_PATH.exists():
            if 'current_app' in globals() and current_app:
                current_app.logger.warning(f"⚠️ Model not found at {MODEL_PATH}. Training new model...")
            else:
                logging.warning(f"⚠️ Model not found at {MODEL_PATH}. Training new model...")

            train_anomaly_model() # This already logs success/failure

            # Check again after training attempt
            if not MODEL_PATH.exists():
                 if 'current_app' in globals() and current_app:
                     current_app.logger.error("Failed to create model file after training attempt.")
                 else:
                     logging.error("Failed to create model file after training attempt.")
                 return None

        # Load and return the trained model
        if 'current_app' in globals() and current_app:
            current_app.logger.info(f"Loading model from {MODEL_PATH}")
        else:
            logging.info(f"Loading model from {MODEL_PATH}")

        return joblib.load(MODEL_PATH)
    except Exception as e:
        if 'current_app' in globals() and current_app:
            current_app.logger.error(f"Error loading model: {e}", exc_info=True)
        else:
            logging.error(f"Error loading model: {e}", exc_info=True)
        return None

def detect_anomaly(metrics):
    """Detect anomalies in metrics using trained model."""
    model = load_model()
    if not model:
        if 'current_app' in globals() and current_app:
            current_app.logger.error("Anomaly detection skipped: Model not loaded.")
        else:
            logging.error("Anomaly detection skipped: Model not loaded.")
        return False # Cannot detect anomaly without a model
    if metrics is None:
        if 'current_app' in globals() and current_app:
            current_app.logger.warning("Anomaly detection skipped: Invalid metrics provided.")
        else:
            logging.warning("Anomaly detection skipped: Invalid metrics provided.")
        return False

    try:
        # Prepare the input data for anomaly detection
        input_data = np.array([[
             metrics.get("cpu_usage", 0.0), # Use .get() with default for safety
             metrics.get("memory_usage", 0.0),
             metrics.get("load_avg", 0.0)
        ]])

        # Predict if an anomaly is detected (-1 means anomaly, 1 means normal)
        prediction = model.predict(input_data)[0]
        is_anomaly = prediction == -1
        if is_anomaly:
            if 'current_app' in globals() and current_app:
                current_app.logger.warning(f"Anomaly detected: {metrics}")
            else:
                logging.warning(f"Anomaly detected: {metrics}")
        return is_anomaly
    except Exception as e:
        if 'current_app' in globals() and current_app:
            current_app.logger.error(f"Anomaly detection error: {e}", exc_info=True)
        else:
            logging.error(f"Anomaly detection error: {e}", exc_info=True)
        return False # Return False on error

def send_alert(metric_name, value, threshold):
    """Send an email alert for abnormal metrics."""
    # Check if all required email configuration is available
    if not all([EMAIL_USER, EMAIL_PASS, RECEIVER_EMAIL]):
        if 'current_app' in globals() and current_app:
            current_app.logger.warning("Email credentials not configured. Skipping alert.")
        else:
            logging.warning("Email credentials not configured. Skipping alert.")
        return

    try:
        # Prepare the email message
        subject = f"🚨 Alert: {metric_name} Threshold Exceeded"
        body = (f"System Alert:\n\n"
                f"Metric '{metric_name}' has exceeded the configured threshold of {threshold}.\n"
                f"Current value: {value:.2f}\n\n"
                f"Please check the system.")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = RECEIVER_EMAIL

        # Send the email
        if 'current_app' in globals() and current_app:
            current_app.logger.info(f"Attempting to send alert email to {RECEIVER_EMAIL} for {metric_name}...")
        else:
             logging.info(f"Attempting to send alert email to {RECEIVER_EMAIL} for {metric_name}...")

        # Use a timeout for the SMTP connection
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server: # Added timeout
            server.starttls() # Secure the connection
            server.login(EMAIL_USER, EMAIL_PASS)
            # Corrected typo here: RECEVER_EMAIL -> RECEIVER_EMAIL
            server.sendmail(EMAIL_USER, RECEIVER_EMAIL, msg.as_string())

        if 'current_app' in globals() and current_app:
            current_app.logger.info(f"🚀 Email alert sent successfully for {metric_name}.")
        else:
            logging.info(f"🚀 Email alert sent successfully for {metric_name}.")


    except Exception as e:
        if 'current_app' in globals() and current_app:
            current_app.logger.error(f"❌ Failed to send alert email for {metric_name}: {e}", exc_info=True)
        else:
            logging.error(f"❌ Failed to send alert email for {metric_name}: {e}", exc_info=True)


def check_alerts(data):
    """Trigger alerts if any threshold is breached."""
    if data is None:
      if 'current_app' in globals() and current_app:
          current_app.logger.warning("Alert check skipped: Invalid metrics data.")
      else:
          logging.warning("Alert check skipped: Invalid metrics data.")
      return

    # Check thresholds and send alerts
    if data.get("cpu_usage", 0.0) > CPU_ALERT_THRESHOLD:
        send_alert("CPU Usage", data.get("cpu_usage", 0.0), CPU_ALERT_THRESHOLD)
    if data.get("memory_usage", 0.0) > MEMORY_ALERT_THRESHOLD:
        send_alert("Memory Usage", data.get("memory_usage", 0.0), MEMORY_ALERT_THRESHOLD)
    # Only check load average if it's meaningful (e.g., not always 0.0 on Windows)
    # and the value is above the threshold
    if hasattr(os, 'getloadavg') and data.get("load_avg", 0.0) > LOAD_ALERT_THRESHOLD:
        send_alert("Load Average", data.get("load_avg", 0.0), LOAD_ALERT_THRESHOLD)

# Keep generate_metrics for potential testing/debugging
def generate_metrics():
    """Simulate random metrics (for testing)."""
    return {
        "cpu_usage": round(random.uniform(0, 100), 2),
        "memory_usage": round(random.uniform(0, 100), 2),
        "load_avg": round(random.uniform(0, 10), 2),
    }
