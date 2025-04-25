import logging
import sys
from app import create_app

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout # Explicitly use stdout
)
# --- End Logging Setup ---

# Create the Flask app instance using the factory
app = create_app()

# The "Application has started successfully" log is now handled within create_app

if __name__ == "__main__":
    # This block runs only when executing `python run.py` directly.
    # Gunicorn runs the 'app' object directly without executing this block.
    app.logger.info("🚀 Starting development server...") # Log specific to direct run
    # Use debug=True only for local development, never in production (as Gunicorn handles it)
    # The host='0.0.0.0' is needed to access it from outside the container/VM if running locally
    app.run(host="0.0.0.0", port=5000, debug=False) # Keep debug=False for consistency with prod intent
