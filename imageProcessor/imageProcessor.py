import pika
import time
import sys
import io
import json
import base64
import uuid
from PIL import Image, ImageOps, ImageFilter
import redis
from datetime import datetime

REDIS_HOST = 'redis'
RABBIT_MQ_HOST = 'rabbitmq'

def rabbitMQconnect(queue: str):
    while (True):
        print('Connecting to RabbitMQ')
        time.sleep(1)
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_MQ_HOST))
            break
        except:
            continue
    print('RabbitMQ connected')

    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    return connection, channel


def redis_connect(host, port):
    while (True):
        print('Connecting to redis')
        time.sleep(1)
        try:
            r = redis.Redis(host, port, decode_responses=True)
            break
        except:
            continue
    print('Redis connected')
    return r


def execute_operations(operation, image: Image.Image):
    processed: Image = image
    if operation == 'pb':
        processed = image.convert("L")
    elif operation == 'inv':
        processed = ImageOps.invert(image.convert("RGB"))
    elif operation == 'blur':
        processed = image.filter(ImageFilter.BLUR)

    return processed


def convert_pb(image):
    imagem = Image.open(io.BytesIO(image))
    imagem_pb = imagem.convert("L")

    return imagem_pb


def blur_image(image):
    imagem = Image.open(io.BytesIO(image))
    imagem_borrada = imagem.filter(ImageFilter.BLUR)

    return imagem_borrada


def invert_color(image):
    imagem = Image.open(io.BytesIO(image))
    imagem = imagem.convert("RGB")
    imagem_invert = ImageOps.invert(imagem.convert("RGB"))

    return imagem_invert


def main():
    queue = 'image_processing'
    connection, channel = rabbitMQconnect(queue)

    r = redis_connect(REDIS_HOST, 6379)

    def callback(ch, method, properties, body):
        print("Beggining image processing")
        message = json.loads(body)

        jobID = message['id']
        image = Image.open(io.BytesIO(base64.decodebytes(message['image'].encode())))
        op = message['op']

        print('Processing request ' + jobID)

        requestEntry = {
            'status': 'processing',
            'image': '',
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        r.hset(jobID, mapping=requestEntry)

        processed_image: Image.Image = execute_operations(op, image)

        output_stream = io.BytesIO()
        processed_image.save(output_stream, format='PNG')
        processed_image_bytes = output_stream.getvalue()
        processed_image_base64_str = base64.b64encode(processed_image_bytes).decode("utf-8")

        requestEntry = {
            'status': 'done',
            'image': processed_image_base64_str,
            'date': requestEntry['date']
        }
        r.hset(jobID, mapping=requestEntry)

        print('Succesfully processed request ' + jobID)

    channel.basic_consume(queue=queue,
                          auto_ack=True,
                          on_message_callback=callback)

    channel.start_consuming()

    connection.close()


main()
