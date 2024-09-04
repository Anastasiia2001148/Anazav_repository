import json
import pika
import time

credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='email_queue', durable=True)

def send_email(email):
    print(f"Send email to {email}")

def callback(ch, method, properties, body):
    message = json.loads(body.decode('utf-8'))
    print(f"Received : {message}")
    send_email(message['email'])
    time.sleep(0.5)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='email_queue', on_message_callback=callback)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
