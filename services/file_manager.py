import os
import time
import threading
import config
from utils.file_utils import mark_file_for_urgent_cleanup

"""
Service for managing file downloads and cleanup.
Dosya indirme ve temizleme işlemlerini yönetme hizmeti.
"""

def schedule_file_deletion(processed_path, original_path):
    """
    Schedule a file for deletion after download.
    İndirme sonrası silmek için bir dosyayı zamanla.
    
    Args:
        processed_path (str): Path to the processed file
        original_path (str): Path to the original file
    """
    # Mark these files for "urgent cleanup" with a very short time window
    # Bu dosyaları çok kısa bir zaman penceresiyle "acil temizleme" için işaretle
    try:
        # Update file access time to now, but modification time to make it appear old
        # Bu, dosyanın erişim zamanını şimdiye, ancak değiştirilme zamanını eski görünecek şekilde günceller
        mark_file_for_urgent_cleanup(processed_path)
        if os.path.exists(original_path):
            mark_file_for_urgent_cleanup(original_path)
    except Exception as e:
        print(f"Error setting file timestamps: {e}")
    
    # Schedule an immediate background cleanup with a small delay
    # Küçük bir gecikmeyle hemen arka plan temizlemesi zamanlayın
    try:
        def delayed_cleanup():
            # Wait longer to let the download start
            # İndirmenin başlaması için daha uzun bekle
            time.sleep(30)  # 30 seconds / 30 saniye
            
            try:
                # Check if the file has been accessed recently before deleting
                # Silmeden önce dosyaya yakın zamanda erişilip erişilmediğini kontrol et
                if os.path.exists(processed_path):
                    try:
                        # Try opening the file to see if it's in use
                        # Kullanımda olup olmadığını görmek için dosyayı açmayı dene
                        with open(processed_path, 'rb') as test_file:
                            # File is not in use if we can open it
                            # Açabiliyorsak dosya kullanımda değil
                            pass
                        
                        # Get the last access time of the file
                        # Dosyanın son erişim zamanını al
                        last_access = os.path.getatime(processed_path)
                        current_time = time.time()
                        # If file hasn't been accessed in last 30 seconds, it's safe to delete
                        # Dosyaya son 30 saniyede erişilmediyse, silmek güvenlidir
                        if current_time - last_access > 30:
                            os.remove(processed_path)
                            print(f"Background thread: Deleted processed file {processed_path}")
                        else:
                            print(f"Background thread: File {processed_path} was recently accessed, skipping deletion")
                    except PermissionError:
                        # File is in use (likely being downloaded)
                        # Dosya kullanımda (muhtemelen indiriliyor)
                        print(f"Background thread: File {processed_path} is in use, skipping deletion")
                
                # Do the same for the original file
                # Orijinal dosya için de aynısını yap
                if os.path.exists(original_path):
                    try:
                        # Try opening the file to see if it's in use
                        # Kullanımda olup olmadığını görmek için dosyayı açmayı dene
                        with open(original_path, 'rb') as test_file:
                            # File is not in use if we can open it
                            # Açabiliyorsak dosya kullanımda değil
                            pass
                        
                        last_access = os.path.getatime(original_path)
                        current_time = time.time()
                        if current_time - last_access > 30:
                            os.remove(original_path)
                            print(f"Background thread: Deleted original file {original_path}")
                        else:
                            print(f"Background thread: File {original_path} was recently accessed, skipping deletion")
                    except PermissionError:
                        # File is in use
                        # Dosya kullanımda
                        print(f"Background thread: File {original_path} is in use, skipping deletion")
            except Exception as e:
                print(f"Background thread: Error deleting files: {e}")
        
        # Start the delayed cleanup in a background thread
        # Gecikmeli temizlemeyi bir arka plan iş parçacığında başlat
        thread = threading.Thread(target=delayed_cleanup)
        thread.daemon = True
        thread.start()
    except Exception as e:
        print(f"Error scheduling background cleanup: {e}")
    
    return True

def cleanup_after_download(processed_path, original_path):
    """
    Function to be registered with Flask's call_on_close for file cleanup.
    Dosya temizliği için Flask'ın call_on_close ile kaydedilecek işlev.
    
    Args:
        processed_path (str): Path to the processed file
        original_path (str): Path to the original file
    """
    try:
        # Attempt to delete the processed file
        # İşlenmiş dosyayı silmeyi dene
        if os.path.exists(processed_path):
            os.remove(processed_path)
            print(f"call_on_close: Deleted processed file: {processed_path}")
            
        # Attempt to delete the original file
        # Orijinal dosyayı silmeyi dene
        if os.path.exists(original_path):
            os.remove(original_path)
            print(f"call_on_close: Deleted original file: {original_path}")
        
        return True
    except Exception as e:
        print(f"call_on_close: Error during file cleanup: {str(e)}")
        return False 