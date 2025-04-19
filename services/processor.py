import os
import cv2
import shutil
import subprocess
import threading
import time
import uuid
import config
from utils.file_utils import is_ffmpeg_installed, get_video_duration, parse_ffmpeg_time

"""
Service for processing various file types to reduce their size.
Çeşitli dosya türlerinin boyutunu azaltmak için işleme hizmeti.
"""

# In-memory storage for processing progress
processing_status = {}

def process_image(input_path, output_path, quality=70, resize_factor=0.8):
    """
    Process and compress an image file using OpenCV.
    OpenCV kullanarak bir görüntü dosyasını işler ve sıkıştırır.
    
    Args:
        input_path (str): Path to the input image
        output_path (str): Path to save the processed image
        quality (int): JPEG quality (0-100)
        resize_factor (float): Resize factor for dimensions
        
    Returns:
        int: Size of the processed file
    """
    # Read the image / Görüntüyü oku
    img = cv2.imread(input_path)
    
    if img is None:
        print(f"Error: Could not read image {input_path}")
        # If we can't read the image, just copy it / Görüntüyü okuyamazsak, sadece kopyala
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path)
    
    # Calculate new dimensions / Yeni boyutları hesapla
    height, width = img.shape[:2]
    new_width = int(width * resize_factor)
    new_height = int(height * resize_factor)
    
    # Resize the image / Görüntüyü yeniden boyutlandır
    resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Set JPEG compression quality (0-100) / JPEG sıkıştırma kalitesini ayarla
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    
    # Get file extension / Dosya uzantısını al
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    # Save with appropriate format and compression / Uygun format ve sıkıştırma ile kaydet
    if ext in ['.jpg', '.jpeg']:
        cv2.imwrite(output_path, resized, encode_param)
    elif ext == '.png':
        # For PNG, we can set compression level (0-9) / PNG için, sıkıştırma seviyesini ayarlayabiliriz
        png_compression = min(9, int(9 * (100 - quality) / 100))
        cv2.imwrite(output_path, resized, [cv2.IMWRITE_PNG_COMPRESSION, png_compression])
    else:
        # For other formats, just write with default options / Diğer formatlar için, varsayılan seçeneklerle yaz
        cv2.imwrite(output_path, resized)
    
    return os.path.getsize(output_path)

def process_video_with_progress(task_id, input_path, output_path, crf=28):
    """
    Process video in a background thread with progress tracking.
    İlerlemeyi takip ederek arka planda video işle.
    
    Args:
        task_id (str): Unique identifier for this processing task
        input_path (str): Path to the input video
        output_path (str): Path to save the processed video
        crf (int): Constant Rate Factor for FFmpeg compression
    """
    try:
        # Set initial status / Başlangıç durumunu ayarla
        processing_status[task_id] = {
            'state': 'starting',
            'progress': 0,
            'message': 'Starting video processing...',
            'timestamp': time.time(),
            'reduced_size': 0,
            'size_reduction': 0,
            'percentage_reduction': 0
        }
        
        # Get video duration / Video süresini al
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
        
        # Prepare FFmpeg command / FFmpeg komutunu hazırla
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-crf', str(crf),
            '-preset', 'medium',
            '-y',  # Overwrite output files without asking / Çıktı dosyalarını sormadan üzerine yaz
            output_path
        ]
        
        # Start the FFmpeg process / FFmpeg işlemini başlat
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
        
        # Process output in real-time to update progress / İlerlemeyi güncellemek için çıktıyı gerçek zamanlı işle
        for line in process.stderr:
            current_time = parse_ffmpeg_time(line)
            if current_time is not None:
                progress = min(100, (current_time / duration) * 100)
                
                processing_status[task_id].update({
                    'state': 'processing',
                    'progress': progress,
                    'message': f'Processing: {progress:.1f}%',
                    'timestamp': time.time()
                })
        
        # Check if process completed successfully / İşlemin başarıyla tamamlanıp tamamlanmadığını kontrol et
        if process.wait() == 0:
            # Calculate size reduction / Boyut azaltmayı hesapla
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
            # Copy original if processing failed / İşlem başarısız olursa orijinali kopyala
            shutil.copy2(input_path, output_path)
    
    except Exception as e:
        processing_status[task_id].update({
            'state': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}',
            'timestamp': time.time()
        })
        # Copy original if processing failed / İşlem başarısız olursa orijinali kopyala
        try:
            shutil.copy2(input_path, output_path)
        except Exception:
            pass

def process_video(input_path, output_path, crf=28):
    """
    Process and compress a video file using FFmpeg.
    FFmpeg kullanarak bir video dosyasını işle ve sıkıştır.
    
    Args:
        input_path (str): Path to the input video
        output_path (str): Path to save the processed video
        crf (int): Constant Rate Factor for FFmpeg compression
        
    Returns:
        tuple: (processed_size, processing_success, task_id)
    """
    # First check if FFmpeg is installed / Önce FFmpeg'in kurulu olup olmadığını kontrol et
    if not is_ffmpeg_installed():
        print("FFmpeg is not installed or not in PATH. Cannot process video.")
        # Just copy the file if FFmpeg is not available / FFmpeg mevcut değilse dosyayı kopyala
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path), False, None
    
    try:
        # Generate a unique task ID / Benzersiz bir görev kimliği oluştur
        task_id = str(uuid.uuid4())
        
        # Start processing in a background thread / Arka planda işlemeyi başlat
        thread = threading.Thread(
            target=process_video_with_progress,
            args=(task_id, input_path, output_path, crf)
        )
        thread.daemon = True
        thread.start()
        
        # Return immediately with the task ID for progress tracking / İlerleme takibi için görev kimliğiyle hemen dön
        return None, True, task_id
        
    except Exception as e:
        print(f"Unexpected error processing video: {str(e)}")
        # For any other error, just copy the file / Başka bir hata için, sadece dosyayı kopyala
        shutil.copy2(input_path, output_path)
        return os.path.getsize(output_path), False, None

def get_processing_status(task_id):
    """
    Get the current status of a processing task.
    Bir işleme görevinin mevcut durumunu al.
    
    Args:
        task_id (str): Unique identifier for the processing task
        
    Returns:
        dict: Status information or None if task not found
    """
    return processing_status.get(task_id) 