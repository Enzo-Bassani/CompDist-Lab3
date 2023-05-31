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


def rabbitMQconnect(queue: str):
    while (True):
        print('Connecting to RabbitMQ')
        time.sleep(1)
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            break
        except:
            continue
    print('RabbitMQ connected')

    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    return connection, channel


def redis_connect(url: str):
    while (True):
        print('Connecting to redis')
        time.sleep(1)
        try:
            global redis_client
            redis_client = redis.from_url(url)
            break
        except:
            continue
    print('Redis connected')


def callback(ch, method, properties, body):
    job = json.loads(body)
    dict_json = {
            'operation': None,
            'id': None,
            'imageBytes': None}

    image64str: str = job['image']
    dict_json['operation'] = job['operation']
    idstr: str = job['id']
    idbytes = idstr.encode()
    dict_json['id'] = base64.decodebytes(idbytes)

    image64bytes = image64str.encode()
    imageBytes = base64.decodebytes(image64bytes)
    dict_json['imageBytes'] = imageBytes

    requestEntry = {
        'status': 'processing',
        'image': '',
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    redis_client.hset(dict_json['id'], json.dumps(requestEntry))
    execute_operations(dict_json)

    
def execute_operations(dict_json):
    if dict_json['operation'] == 'pb':
        processed = convert_pb(dict_json['imageBytes'])

    if dict_json['operation'] == 'inv':
        processed = invert_color(dict_json['imageBytes'])

    if dict_json['operation'] == 'blur':
        processed = blur_image(dict_json['imageBytes'])

    output_stream = io.BytesIO()
    processed.save(output_stream, format='PNG')
    output_bytes = output_stream.getvalue()
    base64processed = base64.b64encode(output_bytes).decode("utf-8")
    print(base64processed)


def convert_pb(imageBytes):
    imagem = Image.open(io.BytesIO(imageBytes))
    imagem_pb = imagem.convert("L")

    return imagem_pb


def blur_image(imageBytes):
    imagem = Image.open(io.BytesIO(imageBytes))
    imagem_borrada = imagem.filter(ImageFilter.BLUR)
    
    return imagem_borrada


def invert_color(imageBytes):
    imagem = Image.open(io.BytesIO(imageBytes))
    imagem = imagem.convert("RGB")
    imagem_invert = ImageOps.invert(imagem)
    
    return imagem_invert


def main():
    queue = 'image_processing'
    connection, channel = rabbitMQconnect(queue)

    url = 'redis://redis:6379'
    redis_connect(url)

    channel.basic_consume(queue=queue,
                          auto_ack=True,
                          on_message_callback=callback)

    channel.start_consuming()

    connection.close()


main()
