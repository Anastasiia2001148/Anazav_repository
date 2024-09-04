import json
from datetime import datetime
import pika
from faker import Faker


credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='email_exchange', exchange_type='direct')
channel.queue_declare(queue='email_queue', durable=True)
channel.queue_bind(exchange='email_exchange', queue='email_queue')

def create_contacts(nums: int):
    fake = Faker()
    for _ in range(nums):
        message = {
            'id': str(_),
            'email': fake.email(),
            'timestamp': datetime.now().isoformat()
        }
        channel.basic_publish(exchange='email_exchange', routing_key='email_queue', body=json.dumps(message).encode())
    connection.close()

if __name__ == '__main__':
    create_contacts(15)