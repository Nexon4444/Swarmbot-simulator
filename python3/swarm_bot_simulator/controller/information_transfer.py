import time

import paho.mqtt.client as mqtt


class Messenger:
    def __init__(self, name, communication_settings):
        self.name = name
        self.client = mqtt.Client(str(name) + "_client")
        # self.name_topic = name + "/" + topic
        self.client.on_connect = self.on_connect
        self.client.on_log = self.on_log
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.main_channel = "main"

        print("connecting to broker", communication_settings.broker)
        self.client.connect(communication_settings.broker, communication_settings.port)

        self.client.subscribe(self.create_topic(self.name, self.main_channel))
        self.client.loop_start()

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def on_log(self, client, userdata, level, buf):
        print(self.name + " log: " + buf + " ")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # client.connected_flag = True  # set flag
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("Disconnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8"))
        print("message received: ", m_decode)

    def send(self, topic=None, message="DEFAULT"):
        if topic is None:
            topic = self.create_topic(self.name, self.main_channel)
        self.client.publish(topic=topic, payload=message)


    def create_topic(self, *args):
        return '/'.join(args)


# def recieve(self):
#     def connection_execute(self):
#         # mqtt.Client.connected_flag=False#create flag in class
#
#         # self.client.loop_forever(200.0)
#
#         self.client.publish("swarm_bot2/commands", "my first command")
#         time.sleep(10)
#         self.client.loop_stop()
#         self.client.disconnect()

def __del__(self):
    self.client.loop_stop()
    self.client.disconnect()
