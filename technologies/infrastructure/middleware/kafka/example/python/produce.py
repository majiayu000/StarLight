import socket
from typing import Optional

from confluent_kafka import Producer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str, client_id: str) -> None:
        self.conf = {"bootstrap.servers": bootstrap_servers, "client.id": client_id}
        self.producer = Producer(self.conf)

    def acked(self, err: Optional[str], msg: str) -> None:
        if err is not None:
            print(f"Failed to deliver message: {msg}: {err}")
        else:
            print(f"Message produced: {msg}")

    def produce(
        self, topic: str, key: Optional[str] = None, value: Optional[str] = None
    ) -> None:
        self.producer.produce(topic, key=key, value=value, callback=self.acked)

    def poll(self, timeout: float) -> None:
        self.producer.poll(timeout)

    def flush(self) -> None:
        self.producer.flush()


if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers="kafka:9092", client_id=socket.gethostname()
    )
    topic = "test"
    producer.produce(topic, key="key", value="value")
    producer.poll(1)
