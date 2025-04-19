from flask import request, render_template, jsonify, send_from_directory, redirect, url_for, Response
import os
import uuid
import shutil
from werkzeug.utils import secure_filename
import config
from services import processor
from services import file_manager
from utils.file_utils import allowed_file, get_file_type
from utils.cleanup_utils import cleanup_all_files, delete_specific_files, perform_scheduled_cleanup

"""
Routes for file uploading, processing, downloading, and cleanup.
Dosya yükleme, işleme, indirme ve temizleme için rotalar.
"""

def register_routes(app):
    """
    Register all routes with the Flask app.
    Tüm rotaları Flask uygulamasına kaydedin.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/')
    def index():
        """
        Render the main page.
        Ana sayfayı göster.
        """
        return render_template('index.html')
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """
        Handle file upload and processing.
        Dosya yükleme ve işlemeyi ele al.
        """
        # Check if a file was uploaded / Bir dosya yüklenip yüklenmediğini kontrol et
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        # Check if the file has a name / Dosyanın bir adı olup olmadığını kontrol et
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Check if the file type is allowed / Dosya türünün izin verilip verilmediğini kontrol et
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate a unique filename to prevent collisions / Çakışmaları önlemek için benzersiz bir dosya adı oluştur
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        unique_filename = f"{base_name}_{str(uuid.uuid4())[:8]}{extension}"
        
        # Save the uploaded file / Yüklenen dosyayı kaydet
        upload_path = os.path.join(config.UPLOAD_FOLDER, unique_filename)
        file.save(upload_path)
        
        # Process the file based on its type / Dosyayı türüne göre işle
        processed_filename = f"reduced_{unique_filename}"
        processed_path = os.path.join(config.PROCESSED_FOLDER, processed_filename)
        
        file_type = get_file_type(filename)
        original_size = os.path.getsize(upload_path)
        
        # Process based on file type / Dosya türüne göre işle
        processing_success = True
        task_id = None
        
        if file_type == 'image':
            # Get compression parameters from request or use defaults / İstek'ten sıkıştırma parametrelerini al veya varsayılanları kullan
            quality = int(request.form.get('quality', 70))
            resize_factor = float(request.form.get('resize_factor', 0.8))
            reduced_size = processor.process_image(upload_path, processed_path, quality, resize_factor)
            
            # Return immediate result for images / Görüntüler için hemen sonuç döndür
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
            # Get compression parameter from request or use default / İstek'ten sıkıştırma parametresini al veya varsayılanı kullan
            crf = int(request.form.get('crf', 28))
            reduced_size, processing_success, task_id = processor.process_video(upload_path, processed_path, crf)
            
            if task_id:
                # For videos, return a task ID for progress tracking / Videolar için ilerleme takibi için bir görev kimliği döndür
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
                # If no task ID (immediate processing or error), return full result / Görev kimliği yoksa (hemen işleme veya hata), tam sonucu döndür
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
            # For other file types, just copy and return result immediately / Diğer dosya türleri için, sadece kopyala ve hemen sonucu döndür
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
        """
        Get the current status of a video processing task.
        Bir video işleme görevinin mevcut durumunu al.
        """
        status = processor.get_processing_status(task_id)
        if not status:
            return jsonify({'error': 'Task not found'}), 404
        
        # If processing is complete, add file size information / İşleme tamamlandıysa, dosya boyutu bilgisini ekle
        if status['state'] == 'completed':
            # Find the processed file / İşlenmiş dosyayı bul
            for filename in os.listdir(config.PROCESSED_FOLDER):
                if task_id in filename:
                    processed_path = os.path.join(config.PROCESSED_FOLDER, filename)
                    original_path = os.path.join(config.UPLOAD_FOLDER, filename.replace('reduced_', ''))
                    
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
        """
        Stream the processed file to the client and delete it after download.
        İşlenmiş dosyayı istemciye aktar ve indirme sonrası sil.
        """
        import mimetypes

        # Track the original file that corresponds to this processed file
        original_filename = filename.replace('reduced_', '')
        processed_path = os.path.join(config.PROCESSED_FOLDER, filename)
        original_path = os.path.join(config.UPLOAD_FOLDER, original_filename)

        # Check if the file exists
        if not os.path.exists(processed_path):
            print(f"Error: File not found at {processed_path}")
            return jsonify({'error': 'File not found or has been deleted. Please try processing the file again.'}), 404

        file_size = os.path.getsize(processed_path)
        print(f"Starting download for file: {filename}, size: {file_size} bytes")

        def generate():
            with open(processed_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
            # After streaming, delete the files
            try:
                if os.path.exists(processed_path):
                    os.remove(processed_path)
                    print(f"Stream: Deleted processed file: {processed_path}")
                if os.path.exists(original_path):
                    os.remove(original_path)
                    print(f"Stream: Deleted original file: {original_path}")
            except Exception as e:
                print(f"Stream: Error during file cleanup: {str(e)}")

        mime_type, _ = mimetypes.guess_type(processed_path)
        mime_type = mime_type or 'application/octet-stream'
        response = Response(generate(), mimetype=mime_type)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Content-Length'] = str(file_size)
        return response
    
    @app.route('/cleanup', methods=['POST'])
    def cleanup():
        """
        Cleanup temporary files older than the configured cleanup interval.
        Yapılandırılmış temizleme aralığından daha eski geçici dosyaları temizleyin.
        """
        removed_files, skipped_files = perform_scheduled_cleanup(processor.processing_status)
        
        return jsonify({
            'message': 'Cleanup completed', 
            'files_removed': len(removed_files),
            'files_skipped': len(skipped_files)
        })
    
    @app.route('/cleanup-all', methods=['POST'])
    def cleanup_all():
        """
        Forcibly clean up all temporary files.
        Tüm geçici dosyaları zorla temizle.
        """
        removed_files, skipped_files = cleanup_all_files()
        
        return jsonify({
            'message': 'All files cleaned up',
            'files_removed': len(removed_files),
            'files_skipped': len(skipped_files),
            'removed_files': removed_files
        })
    
    @app.route('/delete-files', methods=['POST'])
    def delete_files():
        """
        Delete specific files from the request.
        İstekten belirli dosyaları sil.
        """
        processed_filename = request.json.get('processed_filename')
        if not processed_filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        removed_files, skipped_files = delete_specific_files(processed_filename)
        
        return jsonify({
            'message': 'Files deleted successfully',
            'files_removed': len(removed_files),
            'files_skipped': len(skipped_files),
            'removed_files': removed_files
        })
    
    @app.route('/check-ffmpeg')
    def check_ffmpeg():
        """
        Check if FFmpeg is installed.
        FFmpeg'in kurulu olup olmadığını kontrol et.
        """
        from utils.file_utils import is_ffmpeg_installed
        return jsonify({'ffmpeg_installed': is_ffmpeg_installed()}) 