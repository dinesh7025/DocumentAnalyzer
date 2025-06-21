from kafka import KafkaProducer
import json

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def send_to_kafka(topic, data):
    producer = get_kafka_producer()
    producer.send(topic, value=data)
    producer.flush()
