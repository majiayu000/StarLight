import sys
from typing import List, Optional

from confluent_kafka import Consumer, KafkaError, KafkaException


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, group_id: str, auto_offset_reset: str = 'smallest') -> None:
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': auto_offset_reset
        }
        self.consumer = Consumer(self.conf)
        self.running = True

    def basic_consume_loop(self, topics: List[str], timeout: float = 1.0) -> None:
        try:
            self.consumer.subscribe(topics)

            while self.running:
                msg = self.consumer.poll(timeout=timeout)
                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                         (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    print(msg.value().decode('utf-8'))
                    # do something with msg.value()
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()

    def shutdown(self) -> None:
        self.running = False

if __name__ == "__main__":
    consumer = KafkaConsumer(bootstrap_servers="kafka:9092", group_id="foo", auto_offset_reset="smallest")
    topics = ["test"]
    consumer.basic_consume_loop(topics)
