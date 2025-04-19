import os

"""
Configuration settings for the file size reducer application.
Dosya boyutu azaltıcı uygulaması için yapılandırma ayarları.
"""

# File storage configurations / Dosya depolama yapılandırmaları
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

# Maximum upload size (10GB) / Maksimum yükleme boyutu (10GB)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024

# Cleanup intervals / Temizleme aralıkları
CLEANUP_INTERVAL = 10 * 60  # 10 minutes in seconds / 10 dakika (saniye cinsinden)
URGENT_CLEANUP_INTERVAL = 300  # 5 minutes for urgent cleanup / Acil temizleme için 5 dakika

# Allowed file extensions / İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'wmv'},
    'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}
}

# Default port / Varsayılan port
DEFAULT_PORT = int(os.environ.get('PORT', 8080)) 