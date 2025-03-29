## 🚀 Performance Monitoring System with AI-Powered Anomaly Detection

This project monitors system performance (CPU, Load, etc.) and detects anomalies using an AI model. It features a **real-time interactive dashboard** and is packaged in Docker for easy deployment. 🎉

---

## 📚 Table of Contents
- [Features](#-features)
- [Quick Start (For Beginners)](#-quick-start-for-beginners)
- [Advanced Setup (For Pros)](#-advanced-setup-for-pros)
- [How It Works](#-how-it-works)
- [Environment Variables](#-environment-variables)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features
👉 Monitors CPU utilization, load average, and more  
👉 AI-powered anomaly detection  
👉 Real-time web dashboard  
👉 Docker containerized for easy deployment  
👉 Auto-recovery and security built-in  

---

## 🥽️ Quick Start (For Beginners)

⚡️ **Step 1:** Clone the repository  
```bash
git clone https://github.com/viditdixit/performance-monitor.git
cd performance-monitor
```

⚡️ **Step 2:** Set up environment variables  
- Create a `.env` file in the project root:
```
FLASK_ENV=production
FLASK_SECRET_KEY=your_secret_key
```

⚡️ **Step 3:** Build and run using Docker  
```bash
docker-compose up --build
```

⚡️ **Step 4:** Open the dashboard!  
- Go to [http://localhost:5000/dashboard](http://localhost:5000/dashboard)  
- Enjoy real-time monitoring! 🎉  

---

## 🧠 Advanced Setup (For Pros)

📌 **Without Docker (For Debugging/Testing)**  
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

📌 **Push to GitHub**
```bash
git add .
git commit -m "Updated project"
git push origin main
```

📌 **Deploy to Render or Any Hosting**
- Connect your GitHub repo.
- Choose Docker or Manual deployment.
- Set environment variables in Render settings.
- Deploy!

---

## 🖹️ How It Works
1. **System Metrics:** `monitor.py` collects CPU and load data.  
2. **AI Model:** `anomaly_model.pkl` detects anomalies.  
3. **Dashboard:** `dashboard.html` displays metrics and alerts.  
4. **Docker:** Containers ensure portability and consistency.  

---

## ⚙️ Environment Variables
Set these variables in `.env`:
```bash
FLASK_ENV=production
FLASK_SECRET_KEY=your_secret_key
```

---

## 🛠️ Troubleshooting
- **Docker not running?**  
   Run `docker-compose down` and try again.  
- **Dashboard not loading?**  
   Check the URL: [http://localhost:5000/dashboard](http://localhost:5000/dashboard)  
- **Permission Denied?**  
   Run `chmod +x` on scripts if required.  

---

## 🤝 Contributing
Want to contribute? Awesome!  
- Fork the repo  
- Create a new branch  
- Submit a pull request  

---

## 💜 License
This project is licensed under the MIT License.  
