import os
import subprocess
import config
import re
import time
import shutil

"""
Utility functions for file operations.
Dosya işlemleri için yardımcı fonksiyonlar.
"""

def is_ffmpeg_installed():
    """
    Check if FFmpeg is installed and accessible in the PATH.
    FFmpeg'in kurulu olup olmadığını ve PATH'de erişilebilir olup olmadığını kontrol eder.
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
    """
    Check if the file extension is allowed.
    Dosya uzantısının izin verilen uzantılardan olup olmadığını kontrol eder.
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in config.ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return True
    return False

def get_file_type(filename):
    """
    Determine file type based on extension.
    Uzantıya göre dosya türünü belirler.
    """
    if '.' not in filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in config.ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return None

def get_video_duration(input_path):
    """
    Get the duration of a video file using ffprobe.
    ffprobe kullanarak bir video dosyasının süresini alır.
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            try:
                return float(result.stdout.strip())
            except ValueError:
                return None
        return None
    except Exception:
        return None

def create_necessary_folders():
    """
    Ensure upload and processed directories exist.
    Yükleme ve işlenmiş klasörlerinin var olduğundan emin olun.
    """
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(config.PROCESSED_FOLDER, exist_ok=True)

def mark_file_for_urgent_cleanup(file_path):
    """
    Mark a file for urgent cleanup by modifying its timestamps.
    Zaman damgalarını değiştirerek bir dosyayı acil temizleme için işaretler.
    """
    try:
        current_time = time.time()
        urgency_time = current_time - config.URGENT_CLEANUP_INTERVAL - 10
        os.utime(file_path, (current_time, urgency_time))
        return True
    except Exception as e:
        print(f"Error setting file timestamps: {e}")
        return False

def parse_ffmpeg_time(line):
    """
    Parse time information from FFmpeg output.
    FFmpeg çıktısından zaman bilgisini ayrıştırır.
    """
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
    match = time_pattern.search(line)
    
    if match:
        hours, minutes, seconds = match.groups()
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return None 