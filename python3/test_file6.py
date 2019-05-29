import paho.mqtt.client as mqtt
import logging
import time
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
def on_message(client, userdata, msg):
    logging.debug(str(msg.payload.decode("utf-8")))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # client.connected_flag = True  # set flag
        logging.debug("connected OK")
    else:
        logging.debug("Bad connection Returned code=", rc)


client = mqtt.Client("client")
client.on_message = on_message
client.on_connect = on_connect
client.connect("192.168.0.106", port=2000)
client.subscribe(topic="1/receive")
client.loop_start()

client2 = mqtt.Client("client2")
client2.on_connect = on_connect
client2.on_message = on_message
client2.connect("192.168.0.106", port=2000)
# client2.loop_start()
client2.publish(topic="2/receive", payload="asdasdasdasd")

client.loop_stop()
# time.sleep(50)