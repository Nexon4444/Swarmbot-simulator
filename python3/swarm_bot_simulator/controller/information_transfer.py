import json
import time
# from swarm_bot_simulator.model.bot_components import MovementDataEncoder, MovementData, BotInfo, BotInfoEncoder, Vector, VectorEncoder
import swarm_bot_simulator.model.bot_components as comp
# import MovementDataEncoder, MovementData, BotInfo, BotInfoEncoder, Vector, VectorEncoder
from threading import *
import paho.mqtt.client as mqtt
import logging
from ast import literal_eval
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
last_message = None
class Messenger:
    logging_on = True
    logging_mess_on = True

    def __init__(self, name, broker, port, mess_event):
        self.name = name

        self.sender = mqtt.Client(str(name) + "_sender")
        self.receiver = mqtt.Client(str(name) + "_receiver")

        # self.sender.
        self.sender.on_connect = self.on_connect
        self.sender.on_log = self.on_log
        self.sender.on_disconnect = self.on_disconnect
        self.sender.on_subscribe = self.on_subscribe

        self.receiver.on_connect = self.on_connect
        self.receiver.on_message = self.on_message
        self.receiver.on_subscribe = self.on_subscribe
        self.receiver.mess_event = mess_event
        # self.main_channel = "main"
        #threading

        self.log("connecting to broker: " + str(broker))
        self.sender.connect(broker, port)
        self.receiver.connect(broker, port)

        self.receiver_topic = self.create_topic(str(self.name), str("receive"))
        self.sender_topic = self.create_topic(str(self.name), str("send"))

        self.receiver.subscribe(self.receiver_topic)

        self.receiver.last_message = None
        self.sender.last_message = None

        self.client_topics = list()
        self.wait_topics = list()

        self.last_message_lock = Lock()
        self.cond = Condition()
        self.last_message = None
        self.listen()
        # print ("loop started!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def listen(self):
        self.receiver.loop_start()

    def subscribe(self, topic):
        # print  topic

        self.receiver.subscribe(topic)
        # print str("1/main").decode("UTF-8")
        # self.client.subscribe(str("1/main").decode("UTF-8"))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.log("\n===========================\nSubscribed: " + str(client) + "\n===========================")

    def add_topic_to_send(self, topic):
        self.client_topics.append(topic)

    def add_client(self, bot_info):
        self.add_topic_to_send(self.create_topic(bot_info.bot_id, "receive"))

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
        # global last_message
        # topic = msg.topic
        # self.x = 3
        # logging.debug("received message: " + str(msg))
        m_decode = str(msg.payload.decode("utf-8"))
        # print("=========++++++++++++=============")
        self.receiver.last_message = m_decode #self.create_message_from_string(m_decode)
        self.log(str(self.name) + " received message: " + str(m_decode))

        if not Messenger.logging_on and Messenger.logging_mess_on:
            logging.debug(str(self.name) + " received message: " + str(m_decode))

        self.receiver.mess_event.set()
        # message = self.create_message_from_string(m_decode)
        # x=3

    def send(self, topic=None, message="DEFAULT"):
        if isinstance(message, Message):
            me = MessageEncoder()
            message = me.encode(message)

        if topic is None:
            for client_topic in self.client_topics:
                self.log("sending message: " + str(message) + " on topic: " + str(client_topic))
                self.sender.publish(topic=client_topic, payload=message)
        else:
            self.log("sending message: " + str(message) + " on topic: " + str(topic))
            self.sender.publish(topic=topic, payload=message)

        self.sender.last_message = message

    @staticmethod
    def get_message_type_from_string(type_str):
        if type_str in [mtype_str for key, mtype_str in MTYPE.__dict__.items()]:
            return MTYPE.__dict__[type_str]
        # if type_str == "BOARD":
        #     return MTYPE.BOARD
        #
        # elif type_str == "SIMPLE":
        #     return MTYPE.SIMPLE

        else:
            return None

    @staticmethod
    def create_message_from_string(mess_str):
        message_dict = literal_eval(mess_str)
        if "message" in message_dict:
            json_loaded = json.loads(message_dict["message"])
        else:
            json_loaded = None

        # mess_type = message_dict["type"]
        # if mess_type is MTYPE.BOT_INFO:
        #     return Message(mess_type, BotInfo(json_loaded))
        return Message(Messenger.get_message_type_from_string(message_dict["type"]),
                       json_loaded)

    def create_topic(self, *args):
        return '/'.join([str(arg) for arg in args])

    def log(self, msg):
        if Messenger.logging_on:
            logging.debug(msg)

    def set_last_message(self, message):
        with self.last_message_lock:
            self.last_message = message

    def get_last_message(self):
        if self.receiver.last_message is not None:
            with self.last_message_lock:
                return Messenger.create_message_from_string(self.receiver.last_message)
        else:
            return None

    def __del__(self):
        self.receiver.loop_stop()
        self.receiver.disconnect()

        self.sender.disconnect()

class MTYPE:
    BOARD = "BOARD"
    BOT_INFO = "BOT_INFO"
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"
    MACRO = "MACRO"
    ALGORITHM_COMMAND = "ALGORITHM_COMMAND"
    SERVER = "SERVER"

class MSIMPLE:
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"
    TURN_RIGHT = "TURN_RIGHT"
    TURN_LEFT = "TURN_LEFT"

class MMACRO:
    MEASURE_LINE = "MEASURE_LINE"

class MALGORITHM_COMMAND:
    STOP = "STOP"

class MSERVER:
    READY = "READY"
# class MCOMPLEX:



class Message:
    def __init__(self, type, message):
        # from model.board import BoardEncoder
        # from model.bot_components import MovementDataEncoder
        # if type is MTYPE.BOARD:
        #     be = BoardEncoder()
        #     self.message = be.encode(message)
        # elif type is MTYPE.SIMPLE:
        #     mde = MovementDataEncoder()
        #     self.message = mde.encode(message)
        # else:
        #     self.message = message
        if isinstance(message, dict) and type == MTYPE.BOT_INFO:
            bot_info = comp.BotInfo()
            bot_info.from_dict(message)
            message = bot_info

        elif isinstance(message, dict) and type == MTYPE.BOARD:
            board = comp.Board()
            board.from_dict(message)
            message = board

        self.message = message
        self.type = type

    def __str__(self):
        return str(self.__dict__)

class MessageEncoder(json.JSONEncoder):
    def default(self, o):
        be = comp.BoardEncoder()
        mde = comp.MovementDataEncoder()
        bie = comp.BotInfoEncoder()
        if isinstance(o, Message):
            if isinstance(o.message, comp.Board):
                return {
                    "type": o.type,
                    "message": be.encode(o.message)
                }
            elif isinstance(o.message, comp.BotInfo):
                return {
                    "type": o.type,
                    "message": bie.encode(o.message)
                }

            elif isinstance(o.message, comp.MovementData):
                return {
                    "type": o.type,
                    "message": mde.encode(o.message)
                }
            elif isinstance(o.message, comp.Board):
                return {
                    "type": o.type,
                    "message": mde.encode(o.message)
                }
            elif isinstance(o.message, str):
                return {
                    "type": o.type,
                    "message": json.dumps(o.message)
                }
            else:
                return {
                    "type": o.type,
                }
        else:
            return json.JSONEncoder.default(self, o)