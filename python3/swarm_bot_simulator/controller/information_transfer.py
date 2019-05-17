import json
import time
from threading import *
import paho.mqtt.client as mqtt
import logging
from ast import literal_eval
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class Messenger:
    logging_on = True
    logging_mess_on = True


    def __init__(self, name, config, mess_event):
        self.name = name

        self.sender = mqtt.Client(str(name) + "_sender")
        self.receiver = mqtt.Client(str(name) + "_receiver")

        self.sender.on_connect = self.on_connect
        self.sender.on_log = self.on_log
        self.sender.on_disconnect = self.on_disconnect

        self.receiver.on_message = self.on_message
        # self.main_channel = "main"
        #threading

        self.log("connecting to broker: " + str(config.communication_settings.broker))
        self.sender.connect(config.communication_settings.broker, config.communication_settings.port)
        self.receiver.connect(config.communication_settings.broker, config.communication_settings.port)

        self.receiver_topic = self.create_topic(str(self.name), str("receive"))
        self.sender_topic = self.create_topic(str(self.name), str("send"))

        self.client_topics = list()

        self.cond = Condition()
        self.last_message = ""
        self.mess_event = mess_event
        self.listen()
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

    def add_client(self, topic):
        self.client_topics.append(topic)

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
            message_dict = literal_eval(m_decode)
            self.last_message = Message.create_message_from_string(m_decode)
        self.mess_event.set()

    def send(self, topic=None, message="DEFAULT"):
        self.log("sending message: " + str(message) + " on topic: " + str(topic))

        if topic is None:
            for client_topic in self.client_topics:
                self.sender.publish(topic=client_topic, payload=message)

        self.sender.publish(topic=str(topic), payload=str(message))


    def create_topic(self, *args):
        return '/'.join(args)

    def log(self, msg):
        if Messenger.logging_on:
            logging.debug(msg)

    @property
    def last_message(self):
        with self.cond:
            to_return = self._last_message
        return to_return

    @last_message.setter
    def last_message(self, value):
        with self.cond:
            self._last_message = value

    def get_last_message(self):
        with self.cond:
            return self.last_message

    def __del__(self):
        self.receiver.loop_stop()
        self.receiver.disconnect()

        self.sender.disconnect()

class MTYPE:
    BOARD = "BOARD"
    SIMPLE = "SIMPLE"

class Message:
    def get_message_type_from_string(self, type_str):
        if type_str == "BOARD":
            return MTYPE.BOARD

        elif type_str == "SIMPLE":
            return MTYPE.SIMPLE

        else:
            return None

    def create_message_from_string(self, mess_str):
        message_dict = literal_eval(mess_str)
        return Message(Message.get_message_type_from_string(message_dict["type"]),
                                    json.dumps(message_dict["message"]))

    def __init__(self, type, message):
        self.type = type
        self.message = message

class MessageEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Message):
            return {
                "type": o.type,
                "message": o.message
            }
        else:
            return json.JSONEncoder.default(self, o)