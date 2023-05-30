import pika
import time
import sys
import io
import json
import base64
import uuid
from PIL import Image

def rabbitMQconnect(queue: str):
    print('Connecting to RabbitMQ')
    while (True):
        time.sleep(1)
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            break
        except:
            continue
    print('Connected')

    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    return connection, channel


def callback(ch, method, properties, body):
    job = json.loads(body)

    image64str: str = job['image']
    jobID = job['id']
    print(image64str)

    image64bytes = image64str.encode()
    imageBytes = base64.decodebytes(image64bytes)

    image = Image.open(io.BytesIO(imageBytes))
    image.save(jobID + '_poggerton.png')


def main():
    queue = 'image_processing'
    connection, channel = rabbitMQconnect(queue)

    channel.basic_consume(queue=queue,
                          auto_ack=True,
                          on_message_callback=callback)

    channel.start_consuming()

    connection.close()


main()
