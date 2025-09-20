# routes/file_routes.py

from flask import request, render_template, jsonify, send_from_directory, after_this_request
import os
import shutil
import uuid
from werkzeug.utils import secure_filename
import config
from services import processor
from services import file_manager
from utils.file_utils import allowed_file, get_file_type

"""
Routes for file uploading, processing, and downloading.
"""

def register_routes(app):
    """
    Register all routes with the Flask app.
    """
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        filename = secure_filename(file.filename)
        base_name, extension = os.path.splitext(filename)
        unique_id = str(uuid.uuid4())[:8]
        unique_filename = f"{base_name}_{unique_id}{extension}"
        
        upload_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        
        processed_filename = f"reduced_{unique_filename}"
        processed_path = os.path.join(config.PROCESSED_FOLDER, processed_filename)
        
        file_type = get_file_type(filename)
        original_size = os.path.getsize(upload_path)
        
        if file_type == 'image':
            quality = int(request.form.get('quality', 70))
            resize_factor = float(request.form.get('resize_factor', 0.8))
            reduced_size = processor.process_image(upload_path, processed_path, quality, resize_factor)
            
            # Clean up the original image immediately
            try:
                os.remove(upload_path)
            except Exception as e:
                print(f"Error removing original image {upload_path}: {e}")

            size_reduction = original_size - reduced_size
            percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
            
            return jsonify({
                'processing_completed': True,
                'original_size': original_size,
                'reduced_size': reduced_size,
                'size_reduction': size_reduction,
                'percentage_reduction': percentage_reduction,
                'processed_name': processed_filename,
            })
            
        elif file_type == 'video':
            crf = int(request.form.get('crf', 28))
            # Process video directly - simple and synchronous
            reduced_size = processor.process_video(upload_path, processed_path, crf)
            
            # Clean up the original video file
            try:
                os.remove(upload_path)
            except Exception as e:
                print(f"Error removing original video {upload_path}: {e}")

            size_reduction = original_size - reduced_size
            percentage_reduction = (size_reduction / original_size) * 100 if original_size > 0 else 0
            
            return jsonify({
                'processing_completed': True,
                'original_size': original_size,
                'reduced_size': reduced_size,
                'size_reduction': size_reduction,
                'percentage_reduction': percentage_reduction,
                'processed_name': processed_filename,
            })
        else:
            # For other files, just copy them and clean up
            shutil.copy2(upload_path, processed_path)
            os.remove(upload_path)
            return jsonify({'message': 'File type not compressible, copied as-is.', 'processed_name': processed_filename})


    @app.route('/download/<filename>')
    def download_file(filename):
        file_path = os.path.join(config.PROCESSED_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found or has been deleted.'}), 404

        @after_this_request
        def cleanup(response):
            # Use the simple background thread deletion
            file_manager.schedule_deletion_in_background(file_path)
            return response

        return send_from_directory(config.PROCESSED_FOLDER, filename, as_attachment=True)


    @app.route('/check-ffmpeg')
    def check_ffmpeg():
        from utils.file_utils import is_ffmpeg_installed
        return jsonify({'ffmpeg_installed': is_ffmpeg_installed()})