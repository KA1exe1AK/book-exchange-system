import json
import logging 
import pika
from django.conf import settings

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self):
        self.config = settings.RABBITMQ_CONFIG
        self.connection = None
        self.channel = None

    def connect(self):
        try: 
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.config['HOST'],
                    port=self.config['PORT'],
                    credentials=pika.PlainCredentials(
                        self.config['USER'],
                        self.config['PASSWORD']
                    ),
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            self.channel = self.connection.channel()
            
            self.channel.queue_declare(
                queue=self.config['QUEUE'],
                durable=True
            )
                        
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise

    def process_message(self, body):
        logger.info("process_message called")

        try:
            message = json.loads(body.decode('utf-8'))
            logger.info(f"Received message: {message}")
            return True
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            return False

    def start_consuming(self):
        print("start_consuming called") 
        try:
            self.connect()
            logger.info("Connected to RabbitMQ")

            def callback(ch, method, properties, body):
                if self.process_message(body):
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.config['QUEUE'],
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("Waiting for messages...")
            self.channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("Connection closed")

def run_consumer():
    consumer = RabbitMQConsumer()
    consumer.start_consuming()