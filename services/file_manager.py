import os
import time
import threading

def delete_file_with_retry(path, attempts=5, delay=3):
    """
    Tries to delete a file, retrying a few times if it's locked.
    This is the core deletion logic.
    """
    for i in range(attempts):
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"Background thread deleted {os.path.basename(path)}")
            return # Exit the function if deletion is successful or file doesn't exist
        except PermissionError:
            print(f"Permission error deleting {os.path.basename(path)}, attempt {i + 1}/{attempts}. Retrying...")
            time.sleep(delay)
        except FileNotFoundError:
            print(f"File {os.path.basename(path)} was already deleted")
            return
        except Exception as e:
            print(f"Error deleting {os.path.basename(path)} on attempt {i + 1}: {e}")
            time.sleep(delay)

    print(f"Failed to delete {os.path.basename(path)} after {attempts} attempts")


def schedule_deletion_in_background(path, initial_delay=10):
    """
    Starts a new, non-blocking background thread to delete a file after a delay.
    This completely detaches the deletion from the web request.
    """
    def _delete_task():
        """The actual work done by the thread."""
        print(f"Background thread started for {os.path.basename(path)}. Waiting {initial_delay}s before starting deletion attempts.")
        # Wait for a generous amount of time to ensure the web server has released the file lock.
        # This sleep does NOT block the web server, as it's in a separate thread.
        time.sleep(initial_delay)
        
        # Now, call our robust retry logic.
        delete_file_with_retry(path)

    # Create and start the daemon thread.
    # A 'daemon' thread will not prevent the main application from exiting.
    thread = threading.Thread(target=_delete_task)
    thread.daemon = True
    thread.start()