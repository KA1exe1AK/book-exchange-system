from django.apps import AppConfig
import logging
from django.db.utils import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

class BooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'

    def ready(self):
        from .services.metrics import BOOKS_AVAILABLE
        
        try:
            from django.db import connection
            connection.ensure_connection()
            
            from .models import Genres
            
            BOOKS_AVAILABLE.labels(genre='all').set(0)
            
            try:
                for genre in Genres.objects.all():
                    BOOKS_AVAILABLE.labels(genre=genre.slug).set(0)
            except (OperationalError, ProgrammingError):
                logger.warning("Database not ready, skipping genre metrics init")
                
            logger.info("Metrics initialized successfully")
        except Exception as e:
            logger.error(f"Metrics initialization failed: {str(e)}", exc_info=True)
