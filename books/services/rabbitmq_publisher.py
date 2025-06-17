import json
import pika
from django.conf import settings


class RabbitMQPublisher:
    def __init__(self):
        self.config = settings.RABBITMQ_CONFIG
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config['HOST'],
                port=self.config['PORT'],
                credentials=pika.PlainCredentials(
                    self.config['USER'],
                    self.config['PASSWORD']
                )
            )
        )
        self.channel = self.connection.channel()

    def send_book_event(self, event_type, book_data):
        message = {
            'event_type': event_type,
            'book_data': book_data
        }
        
        self._send_to_exchange('direct', message)
        self._send_to_exchange('fanout', message)
        self._send_to_exchange('topic', message)
        self._send_to_exchange('headers', message)

    def _send_to_exchange(self, ex_type, message):
        exchange_name = self.config['EXCHANGES'][ex_type.upper()]
        
        properties = pika.BasicProperties(
            delivery_mode=2, 
            headers=self.config.get('HEADERS', {}) if ex_type == 'headers' else None
        )

        routing_key = ''
        if ex_type == 'direct':
            routing_key = self.config['ROUTING_KEY']
        elif ex_type == 'topic':
            routing_key = f"{self.config['HEADERS']['group']}.{self.config['HEADERS']['number']}.routing.key"

        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=properties
        )

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()


