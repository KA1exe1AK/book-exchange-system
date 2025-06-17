from django.contrib import admin
from books.models import Books, Genres
from books.services.rabbitmq_publisher import RabbitMQPublisher
import logging

logger = logging.getLogger(__name__)

@admin.register(Genres)
class GenresAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'genre', 'owner')
    list_filter = ('genre', 'city')
    search_fields = ('name', 'author')
    prepopulated_fields = {'slug': ('name',)}

    def save_model(self, request, obj, form, change):
        old_genre = None
        if change and obj.pk:
            old_genre = Books.objects.get(pk=obj.pk).genre
        
        super().save_model(request, obj, form, change)
        
        # Обновление метрик
        from books.services.metrics import update_books_metrics
        update_books_metrics(obj.genre.slug if obj.genre else None)
        if old_genre and old_genre != obj.genre:
            update_books_metrics(old_genre.slug)
        logger.info(f"Admin: Updated metrics for book {obj.id}")

        # Отправка в RabbitMQ
        publisher = RabbitMQPublisher()
        try:
            event_type = 'book_updated' if change else 'book_created'
            publisher.send_book_event(
                event_type,
                {
                    'id': str(obj.id),
                    'title': obj.name,
                    'author': obj.author,
                    'slug': obj.slug,
                    'genre': obj.genre.slug if obj.genre else None,
                    'old_genre': old_genre.slug if old_genre else None
                }
            )
        except Exception as e:
            logger.error(f"RabbitMQ error: {e}", exc_info=True)
        finally:
            publisher.close()

    def delete_model(self, request, obj):
        genre_slug = obj.genre.slug if obj.genre else None
        
        # Сначала отправляем событие и обновляем метрики
        publisher = RabbitMQPublisher()
        try:
            publisher.send_book_event(
                'book_deleted',
                {
                    'id': str(obj.id),
                    'title': obj.name,
                    'slug': obj.slug,
                    'genre': genre_slug
                }
            )
        except Exception as e:
            logger.error(f"RabbitMQ error: {e}", exc_info=True)
        finally:
            publisher.close()
        
        super().delete_model(request, obj)
        
        # Обновляем метрики после удаления
        from books.services.metrics import update_books_metrics
        update_books_metrics(genre_slug)
        logger.info(f"Admin: Updated metrics after deleting book {obj.id}")
