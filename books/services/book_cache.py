import logging
from django.conf import settings
from typing import Optional
from django.core.cache import cache
from django.db.models import QuerySet
from books.models import Books
from books.utils import q_search


logger = logging.getLogger(__name__)

class BookCacheService:
    CACHE_TIMEOUT = 60 * 15
    
    @classmethod
    def _get_book_cache_key(cls, book_slug: str) -> str:
        return f'book:{book_slug}'
    
    @classmethod
    def _get_books_by_genre_cache_key(cls, genre_slug: str) -> str:
        return f'books:genre:{genre_slug}'
    
    @classmethod
    def _get_search_cache_key(cls, query: str) -> str:
        return f'books:search:{query}'
    
    @classmethod
    def get_book(cls, book_slug: str) -> Optional[Books]:
        cache_key = cls._get_book_cache_key(book_slug)
        book = cache.get(cache_key)
        
        if book is not None:
            logger.debug(f'Cache hit for book: {book_slug}')
            return book
        
        logger.debug(f'Cache miss for book: {book_slug}')
        try:
            book = Books.objects.get(slug=book_slug)
            cache.set(cache_key, book, cls.CACHE_TIMEOUT)
            return book
        except Books.DoesNotExist:
            logger.warning(f'Book not found: {book_slug}')
            return None
    
    @classmethod
    def get_books_by_genre(cls, genre_slug: str) -> Optional[QuerySet]:
        cache_key = cls._get_books_by_genre_cache_key(genre_slug)
        books = cache.get(cache_key)
        
        if books is not None:
            logger.debug(f'Cache hit for genre: {genre_slug}')
            return books
        
        logger.debug(f'Cache miss for genre: {genre_slug}')
        if genre_slug == 'all':
            books = Books.objects.all()
        else:
            books = Books.objects.filter(genre__slug=genre_slug)
        
        if books.exists():
            cache.set(cache_key, books, cls.CACHE_TIMEOUT)
        return books
    
    @classmethod
    def get_search_results(cls, query: str) -> Optional[QuerySet]:
        cache_key = cls._get_search_cache_key(query)
        books = cache.get(cache_key)
        
        if books is not None:
            logger.debug(f'Cache hit for search: {query}')
            return books
        
        logger.debug(f'Cache miss for search: {query}')
        books = q_search(query)
        if books.exists():
            cache.set(cache_key, books, cls.CACHE_TIMEOUT)
        return books
    
    @classmethod
    def invalidate_book(cls, book_slug: str) -> None:
        cache_key = cls._get_book_cache_key(book_slug)
        cache.delete(cache_key)
        logger.debug(f'Invalidated cache for book: {book_slug}')
    
    @classmethod
    def invalidate_genre_books(cls, genre_slug: str) -> None:
        cache_key = cls._get_books_by_genre_cache_key(genre_slug)
        cache.delete(cache_key)
        logger.debug(f'Invalidated cache for genre: {genre_slug}')
    
    @classmethod
    def invalidate_search_results(cls, query: str) -> None:
        cache_key = cls._get_search_cache_key(query)
        cache.delete(cache_key)
        logger.debug(f'Invalidated cache for search: {query}')


