import logging
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from books.models import Books, Genres
from books.forms import BookForm
from books.services import BookCacheService, RabbitMQPublisher
from books.services.metrics import get_metric, update_books_metrics


BOOKS_EXCHANGED = get_metric('BOOKS_EXCHANGED')
REQUEST_LATENCY = get_metric('REQUEST_LATENCY')

logger = logging.getLogger(__name__)

def catalog(request, genre_slug=None):
    start_time = time.time()
    try:
        page = request.GET.get('page', 1)
        query = request.GET.get('q', None)

        if query:
            books = BookCacheService.get_search_results(query)
            #BOOK_OPERATIONS.labels(operation='search', object_type='book').inc()
        else:
            books = BookCacheService.get_books_by_genre(genre_slug)
            #BOOK_OPERATIONS.labels(operation='browse', object_type='book').inc()

        paginator = Paginator(books, 3)
        current_page = paginator.page(int(page))

        # Обновляем метрики доступных книг
        update_books_metrics(genre_slug)

        context = {'title': 'Каталог', 'books': current_page}
        REQUEST_LATENCY.labels(endpoint='catalog').observe(time.time() - start_time)
        return render(request, 'books/catalog.html', context)
    
    except Exception as e:
        logger.error(f"Error in catalog view: {str(e)}")
        #BOOK_OPERATIONS.labels(operation='error', object_type='system').inc()
        raise

def book(request, book_slug):
    start_time = time.time()
    try:
        book = BookCacheService.get_book(book_slug)
        #BOOK_OPERATIONS.labels(operation='view', object_type='book').inc()

        context = {'book': book}
        REQUEST_LATENCY.labels(endpoint='book_detail').observe(time.time() - start_time)
        return render(request, 'books/book.html', context)
    
    except Exception as e:
        logger.error(f"Error in book view: {str(e)}")
        #BOOK_OPERATIONS.labels(operation='error', object_type='system').inc()
        raise

def create_book(request):
    start_time = time.time()
    try:
        if request.method == 'POST':
            form = BookForm(request.POST, request.FILES)
            if form.is_valid():
                book = form.save()

                logger.info(f"BEFORE METRICS UPDATE - Book ID: {book.id}, Genre: {book.genre.slug}")

                BOOKS_EXCHANGED.labels(status='created').inc()
                #BOOK_OPERATIONS.labels(operation='create', object_type='book').inc()
                
                # Затем принудительно обновляем счетчики книг
                update_books_metrics(book.genre.slug)  # Обновляем конкретный жанр
                update_books_metrics()  # Обновляем все метрики

                logger.info(f"AFTER METRICS UPDATE - Book ID: {book.id}")
        
                # Инвалидация кэша
                BookCacheService.invalidate_genre_books(book.genre.slug)
                
                # Отправка в RabbitMQ
                rabbit = RabbitMQPublisher()
                rabbit.send_book_event('book_created', {
                    'id': str(book.id),
                    'title': book.name,
                    'author': book.author,
                    'slug': book.slug,
                    'genre': book.genre.slug
                })
                rabbit.close()
                
                REQUEST_LATENCY.labels(endpoint='create_book').observe(time.time() - start_time)
                return redirect('book', book_slug=book.slug)
        else:
            form = BookForm()
        
        REQUEST_LATENCY.labels(endpoint='create_book_form').observe(time.time() - start_time)
        return render(request, 'books/create.html', {'form': form})
    
    except Exception as e:
        logger.error(f"Error in create_book view: {str(e)}")
        #BOOK_OPERATIONS.labels(operation='error', object_type='system').inc()
        raise

def update_book(request, book_slug):
    start_time = time.time()
    try:
        book = get_object_or_404(Books, slug=book_slug)
        
        if request.method == 'POST':
            old_genre = book.genre.slug
            form = BookForm(request.POST, request.FILES, instance=book)
            if form.is_valid():
                book = form.save()
                
                # Обновляем метрики
                BOOKS_EXCHANGED.labels(status='updated').inc()
                if old_genre != book.genre.slug:
                    update_books_metrics(old_genre)
                update_books_metrics(book.genre.slug)
                #BOOK_OPERATIONS.labels(operation='update', object_type='book').inc()
                
                # Инвалидация кэша
                BookCacheService.invalidate_book(book.slug)
                BookCacheService.invalidate_genre_books(old_genre)
                if old_genre != book.genre.slug:
                    BookCacheService.invalidate_genre_books(book.genre.slug)
                
                # Отправка в RabbitMQ
                rabbit = RabbitMQPublisher()
                rabbit.send_book_event('book_updated', {
                    'id': str(book.id),
                    'title': book.name,
                    'author': book.author,
                    'slug': book.slug,
                    'genre': book.genre.slug,
                    'old_genre': old_genre
                })
                rabbit.close()

                REQUEST_LATENCY.labels(endpoint='update_book').observe(time.time() - start_time)
                return redirect('book', book_slug=book.slug)
        else:
            form = BookForm(instance=book)
        
        REQUEST_LATENCY.labels(endpoint='update_book_form').observe(time.time() - start_time)
        return render(request, 'books/update.html', {'form': form, 'book': book})
    
    except Exception as e:
        logger.error(f"Error in update_book view: {str(e)}")
        #BOOK_OPERATIONS.labels(operation='error', object_type='system').inc()
        raise

def delete_book(request, book_slug):
    start_time = time.time()
    try:
        book = get_object_or_404(Books, slug=book_slug)
        
        if request.method == 'POST':
            genre_slug = book.genre.slug
            book.delete()
            
            # Обновляем метрики
            BOOKS_EXCHANGED.labels(status='deleted').inc()
            update_books_metrics(genre_slug)
            #BOOK_OPERATIONS.labels(operation='delete', object_type='book').inc()
            
            # Инвалидация кэша
            BookCacheService.invalidate_genre_books(genre_slug)
            
            # Отправка в RabbitMQ
            rabbit = RabbitMQPublisher()
            rabbit.send_book_event('book_deleted', {
                'slug': book_slug,
                'genre': genre_slug
            })
            rabbit.close()
            
            REQUEST_LATENCY.labels(endpoint='delete_book').observe(time.time() - start_time)
            return redirect('catalog', genre_slug=genre_slug)
        
        REQUEST_LATENCY.labels(endpoint='delete_book_form').observe(time.time() - start_time)
        return render(request, 'books/delete.html', {'book': book})
    
    except Exception as e:
        logger.error(f"Error in delete_book view: {str(e)}")
        #BOOK_OPERATIONS.labels(operation='error', object_type='system').inc()
        raise