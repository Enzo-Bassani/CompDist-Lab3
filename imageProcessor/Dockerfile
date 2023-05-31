FROM python:3.10

RUN pip install redis pika Pillow

COPY . .

CMD ["python", "-u", "imageProcessor.py"]