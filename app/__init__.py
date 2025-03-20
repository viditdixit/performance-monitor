from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os

# -----------------------------
# Create and configure the app
# -----------------------------
def create_app():
    app = Flask(__name__)

    # Create a logs directory if it doesn't exist
    log_dir = "/app/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging
    log_file = "/app/logs/app.log"
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Add a startup log
    app.logger.info("Application has started successfully!")

    # Import Blueprint from routes
    from .routes import main

    # Register Blueprint
    app.register_blueprint(main, url_prefix='/')

    return app
