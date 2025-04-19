import os
from flask import Flask
import config
from utils.file_utils import create_necessary_folders
from routes.file_routes import register_routes
from services.processor import processing_status
from scheduler import CleanupScheduler

"""
Main application file for the File Size Reducer web application.
Dosya Boyutu Azaltıcı web uygulaması için ana uygulama dosyası.
"""

def create_app():
    """
    Create and configure the Flask application.
    Flask uygulamasını oluştur ve yapılandır.
    
    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    
    # Configure app / Uygulamayı yapılandır
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['PROCESSED_FOLDER'] = config.PROCESSED_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['CLEANUP_INTERVAL'] = config.CLEANUP_INTERVAL
    app.config['URGENT_CLEANUP_INTERVAL'] = config.URGENT_CLEANUP_INTERVAL
    app.config['ALLOWED_EXTENSIONS'] = config.ALLOWED_EXTENSIONS
    
    # Ensure upload and processed directories exist / Yükleme ve işlenmiş dizinlerin var olduğundan emin ol
    create_necessary_folders()
    
    # Register routes / Rotaları kaydet
    register_routes(app)
    
    # Initialize and start the scheduler / Zamanlayıcıyı başlat
    scheduler = CleanupScheduler(app, processing_status)
    scheduler.start()
    
    return app

# Create the application instance / Uygulama örneğini oluştur
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use the default / Ortam değişkeninden portu al veya varsayılanı kullan
    port = config.DEFAULT_PORT
    # Bind to 0.0.0.0 to make the app accessible from outside the container / Uygulamayı konteyner dışından erişilebilir kılmak için 0.0.0.0'a bağla
    app.run(host='0.0.0.0', port=port)