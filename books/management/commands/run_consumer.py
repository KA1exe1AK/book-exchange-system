from django.core.management.base import BaseCommand
from books.services.rabbitmq_consumer import RabbitMQConsumer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Starts RabbitMQ consumer'

    def handle(self, *args, **options):
        logger.info("Starting RabbitMQ consumer...")
        consumer = RabbitMQConsumer()
        try:
            consumer.connect()
            consumer.start_consuming()
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")