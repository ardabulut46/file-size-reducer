import os

"""
Configuration settings for the file size reducer application.
"""

# File storage configurations
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

# Maximum upload size (10GB)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024


# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'wmv'},
    'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}
}

# Default port
DEFAULT_PORT = int(os.environ.get('PORT', 8080))