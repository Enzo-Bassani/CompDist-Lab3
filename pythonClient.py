import pika
import time
import sys
import io
import json
import base64
import uuid
from PIL import Image

id_to_filename = {}
pendingRequestsCounter = 0

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


def main():
    queue = 'image_processing'
    connection, channel = rabbitMQconnect(queue)

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    op = sys.argv[1]
    imagesPaths = sys.argv[2:]
    global pendingRequestsCounter
    pendingRequestsCounter = len(imagesPaths)
    print(pendingRequestsCounter)

    for imagePath in imagesPaths:
        jobID = str(uuid.uuid4())
        id_to_filename[jobID] = imagePath

        with open(imagePath, 'rb') as imageFile:
            imageBytes = imageFile.read()
            image64bytes = base64.encodebytes(imageBytes)
            image64str = image64bytes.decode()

            job = {
                'image': image64str,
                'id': jobID,
                'op': op
            }
            jobJson = json.dumps(job)
            channel.basic_publish(exchange='',
                                  routing_key=queue,
                                  properties=pika.BasicProperties(
                                      reply_to=callback_queue
                                  ),
                                  body=jobJson)

    def callback(ch, method, properties, body):
        job = json.loads(body)

        image64str: str = job['image']
        jobID = job['id']

        image64bytes = image64str.encode()
        imageBytes = base64.decodebytes(image64bytes)

        image = Image.open(io.BytesIO(imageBytes))
        filename: str = id_to_filename[jobID]
        filename.removesuffix('.png')
        image.save(filename + '_processed.png')

        global pendingRequestsCounter
        pendingRequestsCounter = pendingRequestsCounter - 1
        if (pendingRequestsCounter == 0):
            channel.basic_cancel(consumer_tag="1")

    channel.basic_consume(queue=callback_queue,
                          auto_ack=True,
                          on_message_callback=callback,
                          consumer_tag="1")

    channel.start_consuming()

    connection.close()


main()
