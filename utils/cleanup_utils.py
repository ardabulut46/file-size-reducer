import os
import time
import config

"""
Utility functions for cleaning up temporary files.
Geçici dosyaları temizlemek için yardımcı fonksiyonlar.
"""

def perform_scheduled_cleanup(processing_status):
    """
    Run cleanup automatically on a schedule.
    Otomatik olarak zamanlanmış temizleme işlemi gerçekleştirir.
    
    Args:
        processing_status (dict): Current processing status dictionary
        
    Returns:
        tuple: (removed_files, skipped_files) lists of file paths
    """
    removed_files = []
    skipped_files = []
    
    current_time = time.time()
    regular_cleanup_threshold = current_time - config.CLEANUP_INTERVAL
    urgent_cleanup_threshold = current_time - config.URGENT_CLEANUP_INTERVAL
    
    # Clean up uploads folder / Yükleme klasörünü temizle
    for filename in os.listdir(config.UPLOAD_FOLDER):
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        # Check if file is marked for urgent cleanup or past regular threshold
        # Dosyanın acil temizleme için işaretlenip işaretlenmediğini veya normal eşiği geçip geçmediğini kontrol et
        if os.path.getmtime(file_path) < urgent_cleanup_threshold:
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"Scheduler: Removed urgent file {file_path}")
            except PermissionError as e:
                # File is in use, ignore and try again later
                # Dosya kullanımda, görmezden gel ve daha sonra tekrar dene
                skipped_files.append(file_path)
                print(f"Scheduler: File {file_path} is in use, skipping")
            except Exception as e:
                print(f"Scheduler: Error removing {file_path}: {e}")
        elif os.path.getmtime(file_path) < regular_cleanup_threshold:
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"Scheduler: Removed old upload {file_path}")
            except PermissionError as e:
                # File is in use, ignore and try again later
                # Dosya kullanımda, görmezden gel ve daha sonra tekrar dene
                skipped_files.append(file_path)
                print(f"Scheduler: File {file_path} is in use, skipping")
            except Exception as e:
                print(f"Scheduler: Error removing {file_path}: {e}")
    
    # Clean up processed folder / İşlenmiş klasörü temizle
    for filename in os.listdir(config.PROCESSED_FOLDER):
        file_path = os.path.join(config.PROCESSED_FOLDER, filename)
        
        # Check if file is marked for urgent cleanup or past regular threshold
        # Dosyanın acil temizleme için işaretlenip işaretlenmediğini veya normal eşiği geçip geçmediğini kontrol et
        if os.path.getmtime(file_path) < urgent_cleanup_threshold:
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"Scheduler: Removed urgent processed file {file_path}")
            except PermissionError as e:
                # File is in use, ignore and try again later
                # Dosya kullanımda, görmezden gel ve daha sonra tekrar dene
                skipped_files.append(file_path)
                print(f"Scheduler: File {file_path} is in use, skipping")
            except Exception as e:
                print(f"Scheduler: Error removing {file_path}: {e}")
        elif os.path.getmtime(file_path) < regular_cleanup_threshold:
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"Scheduler: Removed old processed file {file_path}")
            except PermissionError as e:
                # File is in use, ignore and try again later
                # Dosya kullanımda, görmezden gel ve daha sonra tekrar dene
                skipped_files.append(file_path)
                print(f"Scheduler: File {file_path} is in use, skipping")
            except Exception as e:
                print(f"Scheduler: Error removing {file_path}: {e}")
    
    # Clean up processing_status dict / processing_status sözlüğünü temizle
    for task_id in list(processing_status.keys()):
        status = processing_status[task_id]
        if status['state'] in ['completed', 'error'] and 'timestamp' in status:
            if status['timestamp'] < regular_cleanup_threshold:
                del processing_status[task_id]
                print(f"Scheduler: Removed old task status {task_id}")
    
    return removed_files, skipped_files

def cleanup_all_files():
    """
    Forcibly clean up all temporary files.
    Tüm geçici dosyaları zorla temizle.
    
    Returns:
        tuple: (removed_files, skipped_files) lists of file paths
    """
    removed_files = []
    skipped_files = []
    
    # Clean up uploads folder / Yükleme klasörünü temizle
    for filename in os.listdir(config.UPLOAD_FOLDER):
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        try:
            os.remove(file_path)
            removed_files.append(file_path)
        except PermissionError:
            # File is in use, skip it / Dosya kullanımda, atla
            skipped_files.append(file_path)
            print(f"Cleanup-all: File {file_path} is in use, skipping")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
    
    # Clean up processed folder / İşlenmiş klasörü temizle
    for filename in os.listdir(config.PROCESSED_FOLDER):
        file_path = os.path.join(config.PROCESSED_FOLDER, filename)
        try:
            os.remove(file_path)
            removed_files.append(file_path)
        except PermissionError:
            # File is in use, skip it / Dosya kullanımda, atla
            skipped_files.append(file_path)
            print(f"Cleanup-all: File {file_path} is in use, skipping")
        except Exception as e:
            print(f"Error removing {file_path}: {e}")
    
    return removed_files, skipped_files

def delete_specific_files(processed_filename):
    """
    Delete a specific processed file and its corresponding original file.
    Belirli bir işlenmiş dosyayı ve ona karşılık gelen orijinal dosyayı siler.
    
    Args:
        processed_filename (str): The filename of the processed file
        
    Returns:
        tuple: (removed_files, skipped_files) lists of file paths
    """
    original_filename = processed_filename.replace('reduced_', '')
    removed_files = []
    skipped_files = []
    
    # Delete processed file / İşlenmiş dosyayı sil
    processed_path = os.path.join(config.PROCESSED_FOLDER, processed_filename)
    if os.path.exists(processed_path):
        try:
            os.remove(processed_path)
            removed_files.append(processed_path)
        except PermissionError:
            # File is in use, skip it / Dosya kullanımda, atla
            skipped_files.append(processed_path)
            print(f"Delete-files: File {processed_path} is in use, skipping")
        except Exception as e:
            print(f"Error removing {processed_path}: {e}")
    
    # Delete original file / Orijinal dosyayı sil
    original_path = os.path.join(config.UPLOAD_FOLDER, original_filename)
    if os.path.exists(original_path):
        try:
            os.remove(original_path)
            removed_files.append(original_path)
        except PermissionError:
            # File is in use, skip it / Dosya kullanımda, atla
            skipped_files.append(original_path)
            print(f"Delete-files: File {original_path} is in use, skipping")
        except Exception as e:
            print(f"Error removing {original_path}: {e}")
    
    return removed_files, skipped_files 