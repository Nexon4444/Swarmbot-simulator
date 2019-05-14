import time
from threading import *
import paho.mqtt.client as mqtt
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class Messenger:
    logging_on = False
    logging_mess_on = True

    def __init__(self, name, communication_settings, mess_event):
        self.name = name

        self.sender = mqtt.Client(str(name) + "_sender")
        self.receiver = mqtt.Client(str(name) + "_receiver")

        self.sender.on_connect = self.on_connect
        self.sender.on_log = self.on_log
        self.sender.on_disconnect = self.on_disconnect

        self.receiver.on_message = self.on_message
        # self.main_channel = "main"
        #threading

        self.log("connecting to broker: " + str(communication_settings.broker))
        self.sender.connect(communication_settings.broker, communication_settings.port)
        self.receiver.connect(communication_settings.broker, communication_settings.port)

        self.receiver_topic = self.create_topic(str(self.name), str("receive"))
        self.sender_topic = self.create_topic(str(self.name), str("send"))

        self.last_message = ""
        self.mess_event = mess_event
        self.cond = Condition()
        # print ("loop started!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def listen(self):
        self.receiver.subscribe(self.receiver_topic)
        self.receiver.loop_start()

    def subscribe(self, topic):
        # print  topic
        self.log("\n===========================\nSubscribed: " + str(topic) + "\n===========================")
        self.receiver.subscribe(topic)
        # print str("1/main").decode("UTF-8")
        # self.client.subscribe(str("1/main").decode("UTF-8"))


    def on_log(self, client, userdata, level, buf):
        self.log(str(self.name) + " log: " + str(buf) + " ")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # client.connected_flag = True  # set flag
            self.log("connected OK")
        else:
            self.log("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.log("Disconnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        # topic = msg.topic
        logging.debug("received message: " + str(msg))
        m_decode = str(msg.payload.decode("utf-8"))
        # print("=========++++++++++++=============")
        self.log(str(self.name) + " received message: " + str(m_decode))
        if not Messenger.logging_on and Messenger.logging_mess_on:
            logging.debug(str(self.name) + " received message: " + str(m_decode))

        with self.cond:
            self.last_message = m_decode
        self.mess_event.set()

    def send(self, topic=None, message="DEFAULT"):
        self.log("sending message: " + str(message))

        if topic is None:
            self.sender.publish(topic=self.sender_topic, payload=message)

        self.sender.publish(topic=topic, payload=message)


    def create_topic(self, *args):
        return '/'.join(args)

    def log(self, msg):
        if Messenger.logging_on:
            logging.debug(msg)


    def get_last_message(self):
        with self.cond:
            return self.last_message

    def __del__(self):
        self.receiver.loop_stop()
        self.receiver.disconnect()

        self.sender.disconnect()
