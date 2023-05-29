FROM python:3.12.0b1-alpine3.18

RUN pip install redis && \
    pip install pika

COPY . .

CMD ["python3", "imageProcessor.py"]