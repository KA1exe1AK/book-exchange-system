from prometheus_client import Counter, Gauge, Histogram
import logging

from books.models import Books, Genres

logger = logging.getLogger(__name__)

BOOKS_EXCHANGED = Counter(
    'books_exchanged_total',
    'Total number of book exchange operations',
    ['status'] 
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Latency of requests to book views',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

BOOKS_AVAILABLE = Gauge(
    'books_available',
    'Number of books currently available for exchange',
    ['genre']
)

def get_metric(name):
    """Helper function to get metric by name"""
    metrics = {
        'BOOKS_EXCHANGED': BOOKS_EXCHANGED,
        'REQUEST_LATENCY': REQUEST_LATENCY,
        'BOOKS_AVAILABLE': BOOKS_AVAILABLE
    }
    return metrics.get(name)

def update_books_metrics(genre_slug=None):
    if genre_slug:
        count = Books.objects.filter(genre__slug=genre_slug).count()
        BOOKS_AVAILABLE.labels(genre=genre_slug).set(count)
    else:
        # Обновляем все жанры
        for genre in Genres.objects.all():
            count = Books.objects.filter(genre=genre).count()
            BOOKS_AVAILABLE.labels(genre=genre.slug).set(count)
        
        # Обновляем общее количество
        total_count = Books.objects.count()
        BOOKS_AVAILABLE.labels(genre='all').set(total_count)