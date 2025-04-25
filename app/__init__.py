from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys # Import sys for potential console logging fallback/addition

def create_app():
    app = Flask(__name__)

    # --- Logging Configuration ---

    # Define the path for the logs directory
    # Using an environment variable or app config is a good practice for flexibility
    log_dir = Path(os.environ.get("FLASK_LOG_DIR", "logs")) # Default to 'logs' directory

    # Create the logs directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # Log an error if directory creation fails, but don't stop the app
        # Fallback to console logging if file logging setup fails
        print(f"Error creating log directory {log_dir}: {e}", file=sys.stderr)
        # Consider adding a basic console handler here if file logging fails
        # For simplicity, we'll assume the directory can be created or handle the error later
        pass # Or add a console handler here as a fallback

    # Define the path for the log file
    log_file = log_dir / "app.log"

    # Define the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Setup rotating log file handler with UTF-8 encoding
    # Explicitly set encoding='utf-8' to handle Unicode characters
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10000, # Max size of the log file before rotating (10 KB)
            backupCount=3,  # Number of backup log files to keep
            encoding='utf-8' # Specify UTF-8 encoding for the file
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO) # Set log level for the file handler

        # Configure app logger
        app.logger.setLevel(logging.INFO) # Set the overall logger level
        # Remove existing handlers Flask might add by default if they conflict
        # This ensures only our configured handlers are used
        if app.logger.hasHandlers():
             app.logger.handlers.clear()

        app.logger.addHandler(file_handler) # Add the file handler

        # Optional: Add a console handler as well for development visibility
        # This handler will also use UTF-8 implicitly if PYTHONIOENCODING is set,
        # or you can configure it explicitly like the file handler if needed.
        # For a permanent fix for console, the previous method with io.TextIOWrapper is better.
        # Here, we'll just add a basic console handler for convenience.
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        app.logger.addHandler(console_handler)


        # Prevent propagation to root logger if Flask adds console handlers you don't want
        # Setting this to False means logs handled by app.logger won't go up to the root logger
        # This is often desired to have more control over app-specific logs.
        app.logger.propagate = False

    except Exception as e:
        # If there's an error setting up file logging (e.g., permissions),
        # fall back to basic console logging to ensure visibility of errors.
        print(f"Error setting up file logging: {e}", file=sys.stderr)
        # Ensure at least a console handler is present if file logging failed
        if not app.logger.hasHandlers():
             logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
             app.logger = logging.getLogger(__name__) # Re-get the logger to ensure basicConfig is applied


    # --- End Logging Configuration ---


    app.logger.info("✅ Flask application factory initialized.") # This line should now work

    # Register routes
    from .routes import main
    app.register_blueprint(main, url_prefix='/')

    return app