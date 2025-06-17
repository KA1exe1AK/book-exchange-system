from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from books.models import Books
from books.services.rabbitmq_publisher import RabbitMQPublisher
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Books)
def book_saved(sender, instance, created, **kwargs):
    event_type = 'book_created' if created else 'book_updated'
    publisher = RabbitMQPublisher()
    try:
        publisher.publish_to_all_exchanges(
            event_type=event_type,
            data={
                'id': str(instance.id),
                'title': instance.name,
                'author': instance.author
            }
        )
        logger.info(f"Published {event_type} event for book {instance.id}")
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
    finally:
        publisher.close()

@receiver(post_delete, sender=Books)
def book_deleted(sender, instance, **kwargs):
    publisher = RabbitMQPublisher()
    try:
        publisher.publish_to_all_exchanges(
            event_type='book_deleted',
            data={
                'id': str(instance.id),
                'title': instance.name
            }
        )
        logger.info(f"Published book_deleted event for book {instance.id}")
    except Exception as e:
        logger.error(f"Error publishing event: {e}")
    finally:
        publisher.close()