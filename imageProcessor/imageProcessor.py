import pika
import redis
import base64
import io
import time

from PIL import Image

print("Hello World!")
while (1):
    time.sleep(1)
    print("tentando conectar")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        break
    except:
        continue
print('conectado')

def callback(ch, method, properties, body):
    stringbase64 = body
    ch.basic_ack(delivery_tag=method.delivery_tag)
    converter_base64_para_pb_e_base64(stringbase64)

channel.queue_declare(queue='image_processing', durable=True)

channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue='image_processing', on_message_callback=callback)
print("passo aqui antes do start")

def converter_base64_para_pb_e_base64(base64image):
    image_bytes = base64.b64decode(base64image)
    image_stream = io.BytesIO(image_bytes)
    imagem = Image.open(image_stream)
    imagem_pb = imagem.convert("L")
    output_stream = io.BytesIO()
    imagem_pb.save(output_stream, format='PNG')
    output_bytes = output_stream.getvalue()
    base64_pb = base64.b64encode(output_bytes).decode("utf-8")
    print(base64_pb)
    imagem_pb.show()

    print("finalizou a conversao")


channel.start_consuming()

#imagem_base64 = "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"
#imagem_pb_base64 = converter_base64_para_pb_e_base64(imagem_base64)
#print(imagem_pb_base64)