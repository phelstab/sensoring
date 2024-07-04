from confluent_kafka import Consumer, KafkaException, KafkaError
import cv2
import numpy as np
import json

class KafkaSubscriber:
    def __init__(self, broker, group_id, topic, message_handler):
        self.broker = broker
        self.group_id = group_id
        self.topic = topic
        self.consumer = None
        self.message_handler = message_handler

    def _create_consumer(self):
        self.consumer = Consumer({
            'bootstrap.servers': self.broker,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest'
        })

    def subscribe(self):
        if self.consumer is None:
            self._create_consumer()

        self.consumer.subscribe([self.topic])
        print(f"Subscribed to topic: {self.topic}")

        try:
            while True:
                if cv2.waitKey(1) == ord('r'):
                    break
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print(f"{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}")
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    # Proper message
                    self.message_handler(msg.value())

        except KeyboardInterrupt:
            pass
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()

def handle_image_message(msg_value):
    # Decode the image
    img_array = np.frombuffer(msg_value, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is not None:
        cv2.imshow('Received Image', img)
        cv2.waitKey(1)

def handle_skeleton_message(msg_value):
    # Decode the skeleton data
    skeleton_data = json.loads(msg_value.decode('utf-8'))
    print(f"Received skeleton data: {skeleton_data}")

if __name__ == "__main__":
    broker = 'localhost:9092'  # Replace with your Kafka broker address
    group_id = 'my_group'

    # Subscribe to image topic
    image_subscriber = KafkaSubscriber(broker, group_id, 'image_topic', handle_image_message)
    
    # Subscribe to skeleton topic
    skeleton_subscriber = KafkaSubscriber(broker, group_id, 'skeleton_topic', handle_skeleton_message)

    # Run subscribers
    import threading
    image_thread = threading.Thread(target=image_subscriber.subscribe)
    skeleton_thread = threading.Thread(target=skeleton_subscriber.subscribe)

    image_thread.start()
    skeleton_thread.start()

    image_thread.join()
    skeleton_thread.join()
