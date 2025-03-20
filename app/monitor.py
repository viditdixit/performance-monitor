import psutil
import platform
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
import os
import smtplib
from email.mime.text import MIMEText
import random

# Define model file path
MODEL_FILE = "app/anomaly_model.pkl"

# -----------------------------
# Get system metrics in real time
# -----------------------------
def get_system_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)  # CPU usage percentage
        memory_info = psutil.virtual_memory().percent  # Memory usage percentage
        
        # Handle load average based on OS
        if platform.system() == "Windows":
            load_avg = 0.0  # Placeholder for Windows
        else:
            load_avg = os.getloadavg()[0]  # Load average (last 1 min)

        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_info,
            "load_avg": load_avg,
        }

    except Exception as e:
        print(f"Error while getting system metrics: {e}")
        # Safe fallback with 0.0 values to prevent crashes
        return {"cpu_usage": 0.0, "memory_usage": 0.0, "load_avg": 0.0}

# -----------------------------
# Train a new anomaly detection model (if required)
# -----------------------------
def train_anomaly_model():
    try:
        # Generate normal synthetic data for training
        normal_data = np.random.normal(
            loc=[30, 40, 1],  # Mean values [CPU, Memory, Load]
            scale=[10, 15, 0.5],  # Standard deviations
            size=(100, 3)  # 100 samples, 3 features
        )

        # Create and train Isolation Forest model
        model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        model.fit(normal_data)

        # Save model to file
        joblib.dump(model, MODEL_FILE)
        print("✅ Anomaly model trained and saved successfully!")
    
    except Exception as e:
        print(f"Error while training the anomaly model: {e}")

# -----------------------------
# Load the saved model
# -----------------------------
def load_model():
    try:
        if os.path.exists(MODEL_FILE):
            return joblib.load(MODEL_FILE)  # Load existing model
        else:
            print("⚠️ Model not found, training a new one...")
            train_anomaly_model()
            return joblib.load(MODEL_FILE)
    except Exception as e:
        print(f"Error loading the model: {e}")
        return None

# -----------------------------
# Detect anomaly in system metrics
# -----------------------------
def detect_anomaly(metrics):
    model = load_model()
    
    if model is None:
        return False  # No model loaded, assume no anomaly
    
    try:
        # Convert metrics to numpy array for prediction
        metrics_array = np.array([metrics["cpu_usage"], metrics["memory_usage"], metrics["load_avg"]]).reshape(1, -1)
        
        # Predict anomaly using the model
        prediction = model.predict(metrics_array)
        
        # Return True if anomaly is detected
        return prediction[0] == -1
    
    except Exception as e:
        print(f"Error while detecting anomaly: {e}")
        return False

# -----------------------------
# Send Email Alerts
# -----------------------------
def send_alert(metric_name, value):
    sender_email = "viditdixit03@gmail.com"  # 🔥 Your email address
    receiver_email = "backlog.2000@gmail.com"  # 🔥 Recipient's email address
    subject = f"🚨 Alert: {metric_name} Threshold Exceeded"
    message = f"The value of {metric_name} has crossed the threshold. Current value: {value}%"

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, "prqr gajy ubhe elww")  # 🔥 Replace with your App Password
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print(f"🚀 Alert sent to {receiver_email}!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# -----------------------------
# Check and trigger alerts based on thresholds
# -----------------------------
def check_alerts(data):
    if data["cpu_usage"] > 80:
        send_alert("CPU Usage", data["cpu_usage"])
    if data["load_avg"] > 5:
        send_alert("Load Average", data["load_avg"])
    if data["memory_usage"] > 80:
        send_alert("Memory Usage", data["memory_usage"])

# -----------------------------
# Simulate random performance data (for testing)
# -----------------------------
def generate_metrics():
    return {
        "cpu_usage": round(random.uniform(0, 100), 2),
        "load_avg": round(random.uniform(0, 10), 2),
        "memory_usage": round(random.uniform(0, 100), 2),
    }
