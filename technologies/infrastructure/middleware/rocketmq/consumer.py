import time

from rocketmq.client import PushConsumer, ConsumeStatus


def callback(msg):
    print(msg.id, msg.body)
    return ConsumeStatus.CONSUME_SUCCESS


consumer = PushConsumer("CID_XXX")
consumer.set_name_server_address("")
consumer.subscribe("TEST_TOPIC", callback)
consumer.start()

while True:
    time.sleep(3600)

consumer.shutdown()
