# services/processor.py
import os
import cv2
import shutil
import subprocess
from utils.file_utils import is_ffmpeg_installed

def process_image(input_path, output_path, quality=70, resize_factor=0.8):
    """
    Process and compress an image file.
    """
    img = cv2.imread(input_path)
    if img is None:
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path)
    
    height, width = img.shape[:2]
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    _, ext = os.path.splitext(input_path)
    if ext.lower() in ['.jpg', '.jpeg']:
        cv2.imwrite(output_path, resized, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    elif ext.lower() == '.png':
        png_compression = min(9, int(9 * (100 - quality) / 100))
        cv2.imwrite(output_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, png_compression])
    else:
        cv2.imwrite(output_path, resized)
    
    return os.path.getsize(output_path)

def process_video(input_path, output_path, crf=28):
    """
    Process video using FFmpeg directly - simple and synchronous.
    """
    if not is_ffmpeg_installed():
        print("FFmpeg not found. Copying file instead.")
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path)
    
    try:
        original_size = os.path.getsize(input_path)
        
        # Simple FFmpeg command - no progress tracking needed for local use
        cmd = ['ffmpeg', '-i', input_path, '-crf', str(crf), '-preset', 'medium', '-y', output_path]
        
        print(f"Processing video: {os.path.basename(input_path)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            reduced_size = os.path.getsize(output_path)
            print(f"Video processed successfully. Size reduced from {original_size} to {reduced_size} bytes")
            return reduced_size
        else:
            print(f"FFmpeg failed: {result.stderr.decode()}")
            shutil.copy2(input_path, output_path)
            return os.path.getsize(output_path)
            
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path)