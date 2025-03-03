import os
import time
import uuid
import cv2
import numpy as np
import threading
import re
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import ffmpeg
import shutil
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024  # 10GB max upload size
app.config['ALLOWED_EXTENSIONS'] = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'wmv'},
    'document': {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}
}

# In-memory storage for processing progress
processing_status = {}

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def is_ffmpeg_installed():
    """Check if FFmpeg is installed and accessible in the PATH."""
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
    """Check if the file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in app.config['ALLOWED_EXTENSIONS'].items():
        if ext in extensions:
            return True
    return False

def get_file_type(filename):
    """Determine file type based on extension"""
    if '.' not in filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in app.config['ALLOWED_EXTENSIONS'].items():
        if ext in extensions:
            return file_type
    return None

def get_video_duration(input_path):
    """Get the duration of a video file using ffprobe"""
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

def process_image(input_path, output_path, quality=70, resize_factor=0.8):
    """Process and compress an image file using OpenCV"""
    # Read the image
    img = cv2.imread(input_path)
    
    if img is None:
        print(f"Error: Could not read image {input_path}")
        # If we can't read the image, just copy it
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path)
    
    # Calculate new dimensions
    height, width = img.shape[:2]
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    
    # Resize the image
    resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Set JPEG compression quality (0-100)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    
    # Get file extension
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    # Save with appropriate format and compression
    if ext in ['.jpg', '.jpeg']:
        cv2.imwrite(output_path, resized, encode_param)
    elif ext == '.png':
        # For PNG, we can set compression level (0-9)
        png_compression = min(9, int(9 * (100 - quality) / 100))
        cv2.imwrite(output_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, png_compression])
    else:
        # For other formats, just write with default options
        cv2.imwrite(output_path, resized)
    
    return os.path.getsize(output_path)

def process_video_with_progress(task_id, input_path, output_path, crf=28):
    """Process video in a background thread with progress tracking"""
    try:
        # Set initial status
        processing_status[task_id] = {
            'state': 'starting',
            'progress': 0,
            'message': 'Starting video processing...',
            'timestamp': time.time(),
            'reduced_size': 0,
            'size_reduction': 0,
            'percentage_reduction': 0
        }
        
        # Get video duration
        duration = get_video_duration(input_path)
        if duration is None:
            processing_status[task_id] = {
                'state': 'error',
                'progress': 0,
                'message': 'Could not determine video duration',
                'timestamp': time.time(),
                'reduced_size': 0,
                'size_reduction': 0,
                'percentage_reduction': 0
            }
            shutil.copy2(input_path, output_path)
            return
        
        # Prepare FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-crf', str(crf),
            '-preset', 'medium',
            '-y',  # Overwrite output files without asking
            output_path
        ]
        
        # Start the FFmpeg process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        processing_status[task_id].update({
            'state': 'processing',
            'timestamp': time.time()
        })
        
        # Process output in real-time to update progress
        time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
        
        for line in process.stderr:
            # Look for time information in FFmpeg output
            match = time_pattern.search(line)
            if match:
                hours, minutes, seconds = match.groups()
                current_time = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
                progress = min(100, (current_time / duration) * 100)
                
                processing_status[task_id].update({
                    'state': 'processing',
                    'progress': progress,
                    'message': f'Processing: {progress:.1f}%',
                    'timestamp': time.time()
                })
        
        # Check if process completed successfully
        if process.wait() == 0:
            # Calculate size reduction
            original_size = os.path.getsize(input_path)
            reduced_size = os.path.getsize(output_path)
            size_reduction = original_size - reduced_size
            percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
            
            processing_status[task_id].update({
                'state': 'completed',
                'progress': 100,
                'message': 'Processing completed successfully',
                'timestamp': time.time(),
                'original_size': original_size,
                'reduced_size': reduced_size,
                'size_reduction': size_reduction,
                'percentage_reduction': percentage_reduction
            })
        else:
            processing_status[task_id].update({
                'state': 'error',
                'progress': 0,
                'message': 'FFmpeg error during processing',
                'timestamp': time.time()
            })
            # Copy original if processing failed
            shutil.copy2(input_path, output_path)
    
    except Exception as e:
        processing_status[task_id].update({
            'state': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}',
            'timestamp': time.time()
        })
        # Copy original if processing failed
        try:
            shutil.copy2(input_path, output_path)
        except Exception:
            pass

def process_video(input_path, output_path, crf=28):
    """Process and compress a video file using FFmpeg"""
    # First check if FFmpeg is installed
    if not is_ffmpeg_installed():
        print("FFmpeg is not installed or not in PATH. Cannot process video.")
        # Just copy the file if FFmpeg is not available
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path), False, None
    
    try:
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Start processing in a background thread
        thread = threading.Thread(
            target=process_video_with_progress,
            args=(task_id, input_path, output_path, crf)
        )
        thread.daemon = True
        thread.start()
        
        # Return immediately with the task ID for progress tracking
        return None, True, task_id
        
    except Exception as e:
        print(f"Unexpected error processing video: {str(e)}")
        # For any other error, just copy the file
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path), False, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Check if the file has a name
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if the file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Generate a unique filename to prevent collisions
    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    unique_filename = f"{base_name}_{str(uuid.uuid4())[:8]}{extension}"
    
    # Save the uploaded file
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(upload_path)
    
    # Process the file based on its type
    processed_filename = f"reduced_{unique_filename}"
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    
    file_type = get_file_type(filename)
    original_size = os.path.getsize(upload_path)
    
    # Process based on file type
    processing_success = True
    task_id = None
    
    if file_type == 'image':
        # Get compression parameters from request or use defaults
        quality = int(request.form.get('quality', 70))
        resize_factor = float(request.form.get('resize_factor', 0.8))
        reduced_size = process_image(upload_path, processed_path, quality, resize_factor)
        
        # Return immediate result for images
        size_reduction = original_size - reduced_size
        percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
        
        return jsonify({
            'message': 'File processed successfully',
            'original_name': filename,
            'processed_name': processed_filename,
            'original_size': original_size,
            'reduced_size': reduced_size,
            'size_reduction': size_reduction,
            'percentage_reduction': percentage_reduction,
            'processing_success': True,
            'processing_completed': True
        })
        
    elif file_type == 'video':
        # Get compression parameter from request or use default
        crf = int(request.form.get('crf', 28))
        reduced_size, processing_success, task_id = process_video(upload_path, processed_path, crf)
        
        if task_id:
            # For videos, return a task ID for progress tracking
            return jsonify({
                'message': 'Video processing started',
                'original_name': filename,
                'processed_name': processed_filename,
                'original_size': original_size,
                'task_id': task_id,
                'processing_success': processing_success,
                'processing_completed': False
            })
        else:
            # If no task ID (immediate processing or error), return full result
            reduced_size = os.path.getsize(processed_path)
            size_reduction = original_size - reduced_size
            percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
            
            response_data = {
                'message': 'File copied (processing not available)' if not processing_success else 'File processed successfully',
                'original_name': filename,
                'processed_name': processed_filename,
                'original_size': original_size,
                'reduced_size': reduced_size,
                'size_reduction': size_reduction,
                'percentage_reduction': percentage_reduction,
                'processing_success': processing_success,
                'processing_completed': True
            }
            
            if not processing_success:
                response_data['warning'] = 'FFmpeg is not installed. Please install FFmpeg to enable video compression.'
            
            return jsonify(response_data)
    else:
        # For other file types, just copy and return result immediately
        shutil.copy2(upload_path, processed_path)
        reduced_size = os.path.getsize(processed_path)
        size_reduction = original_size - reduced_size
        percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
        
        return jsonify({
            'message': 'File copied (no compression available for this file type)',
            'original_name': filename,
            'processed_name': processed_filename,
            'original_size': original_size,
            'reduced_size': reduced_size,
            'size_reduction': size_reduction,
            'percentage_reduction': percentage_reduction,
            'processing_success': True,
            'processing_completed': True
        })

@app.route('/processing-status/<task_id>')
def get_processing_status(task_id):
    """Get the current status of a video processing task"""
    if task_id not in processing_status:
        return jsonify({'error': 'Task not found'}), 404
    
    status = processing_status[task_id]
    
    # If processing is complete, add file size information
    if status['state'] == 'completed':
        # Find the processed file
        for filename in os.listdir(app.config['PROCESSED_FOLDER']):
            if task_id in filename:
                processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
                original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.replace('reduced_', ''))
                
                if os.path.exists(processed_path) and os.path.exists(original_path):
                    original_size = os.path.getsize(original_path)
                    reduced_size = os.path.getsize(processed_path)
                    size_reduction = original_size - reduced_size
                    percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
                    
                    status.update({
                        'original_size': original_size,
                        'reduced_size': reduced_size,
                        'size_reduction': size_reduction,
                        'percentage_reduction': percentage_reduction
                    })
                    break
    
    return jsonify(status)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Cleanup temporary files older than 1 hour"""
    current_time = time.time()
    one_hour_ago = current_time - 3600
    
    # Clean up uploads folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.getmtime(file_path) < one_hour_ago:
            os.remove(file_path)
    
    # Clean up processed folder
    for filename in os.listdir(app.config['PROCESSED_FOLDER']):
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        if os.path.getmtime(file_path) < one_hour_ago:
            os.remove(file_path)
    
    # Clean up processing_status dict
    for task_id in list(processing_status.keys()):
        status = processing_status[task_id]
        if status['state'] in ['completed', 'error'] and 'timestamp' in status:
            if status['timestamp'] < one_hour_ago:
                del processing_status[task_id]
    
    return jsonify({'message': 'Cleanup completed'})

@app.route('/check-ffmpeg')
def check_ffmpeg():
    """Check if FFmpeg is installed"""
    return jsonify({'ffmpeg_installed': is_ffmpeg_installed()})

if __name__ == '__main__':
    app.run(debug=True) 