import time

import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("test")
    client.subscribe("Example/topic")


def on_message(client, userdata, msg):

    print(msg.topic+" "+str(msg.payload))


    if msg.payload == b"Hello":
        print("Received message #1, do something")

    if msg.payload == b"World":
        print("Received message #2, do something else")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 2000)
client.subscribe(topic="test")
client.publish('test', 'is this real life?')
client.loop_start()
time.sleep(200)
client.loop_stop()

