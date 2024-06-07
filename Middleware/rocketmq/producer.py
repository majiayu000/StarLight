from rocketmq.client import Producer, Message

producer = Producer("PID-XXX")
producer.set_name_server_address("")
producer.start()

msg = Message("TEST_TOPIC")
msg.set_keys("XXX")
msg.set_tags("XXX")
msg.set_body("XXXX")
ret = producer.send_sync(msg)
print(ret.status, ret.msg_id, ret.offset)
producer.shutdown()
