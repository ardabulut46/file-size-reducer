# utils/file_utils.py

import os
import subprocess
import config

"""
Utility functions for file operations.
"""

def is_ffmpeg_installed():
    """
    Check if FFmpeg is installed and accessible in the PATH.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False
        )
        return True
    except FileNotFoundError:
        return False

def allowed_file(filename):
    if '.' not in filename: return False
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in config.ALLOWED_EXTENSIONS.items():
        if ext in extensions: return True
    return False

def get_file_type(filename):
    if '.' not in filename: return None
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in config.ALLOWED_EXTENSIONS.items():
        if ext in extensions: return file_type
    return None

def create_necessary_folders():
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.PROCESSED_FOLDER, exist_ok=True)

