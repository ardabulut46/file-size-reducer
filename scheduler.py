from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from utils.cleanup_utils import perform_scheduled_cleanup

"""
Scheduler for automated background tasks.
Otomatikleştirilmiş arka plan görevleri için zamanlayıcı.
"""

class CleanupScheduler:
    """
    Scheduler for periodic file cleanup tasks.
    Periyodik dosya temizleme görevleri için zamanlayıcı.
    """
    
    def __init__(self, app=None, processing_status=None):
        """
        Initialize the scheduler.
        Zamanlayıcıyı başlat.
        
        Args:
            app: Flask application instance
            processing_status: Processing status dictionary for tracking
        """
        self.app = app
        self.processing_status = processing_status
        self.scheduler = BackgroundScheduler()
        
        # If app is provided, initialize with the app / Uygulama sağlanmışsa, uygulama ile başlat
        if app is not None:
            self.init_app(app, processing_status)
    
    def init_app(self, app, processing_status):
        """
        Initialize the scheduler with a Flask app.
        Zamanlayıcıyı bir Flask uygulamasıyla başlat.
        
        Args:
            app: Flask application instance
            processing_status: Processing status dictionary for tracking
        """
        self.app = app
        self.processing_status = processing_status
        
        # Schedule the cleanup to run at the defined interval / Temizliği tanımlanan aralıkta çalışacak şekilde zamanla
        self.scheduler.add_job(
            self._run_cleanup, 
            'interval', 
            minutes=1  # Run every minute for more reliable cleanup / Daha güvenilir temizlik için her dakika çalıştır
        )
        
        # Register shutdown function / Kapatma işlevini kaydet
        atexit.register(self._shutdown)
    
    def start(self):
        """
        Start the scheduler.
        Zamanlayıcıyı başlat.
        """
        if not self.scheduler.running:
            self.scheduler.start()
    
    def _shutdown(self):
        """
        Shutdown the scheduler gracefully.
        Zamanlayıcıyı düzgün bir şekilde kapat.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
    
    def _run_cleanup(self):
        """
        Run the scheduled cleanup task.
        Zamanlanmış temizleme görevini çalıştır.
        """
        with self.app.app_context():
            perform_scheduled_cleanup(self.processing_status) 