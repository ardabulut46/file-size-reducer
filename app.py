import os
from flask import Flask
import config
from utils.file_utils import create_necessary_folders
from routes.file_routes import register_routes

"""
Main application file for the File Size Reducer web application.
"""

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    
    # Configure app
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['PROCESSED_FOLDER'] = config.PROCESSED_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['ALLOWED_EXTENSIONS'] = config.ALLOWED_EXTENSIONS
    
    # Ensure upload and processed directories exist
    create_necessary_folders()
    
    # Register routes
    register_routes(app)

    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # This block runs ONLY when you execute `python app.py`
    
    # Check if we are in a development environment.
    # We can use an environment variable for this.
    # For now, we'll just assume `python app.py` means development.
    
    print("--- Starting in DEVELOPMENT mode ---")
    print("--- For production, use 'waitress-serve' or 'gunicorn' ---")
    
    # Option 1: Use Flask's built-in server (easiest for debugging)
    app.run(host='0.0.0.0', port=8080, debug=True)

    # Option 2: Use waitress programmatically (closer to production)
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=8080)