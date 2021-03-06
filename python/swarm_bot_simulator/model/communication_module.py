import json
import sys
# from swarm_bot_simulator.model.bot_components import MovementDataEncoder, MovementData, BotInfo, BotInfoEncoder, Vector, VectorEncoder
if sys.version_info[0] > 2:
    from queue import Queue
else:
    from Queue import Queue


from threading import *
import paho.mqtt.client as mqtt
import logging
from ast import literal_eval
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
last_message = None

class Messenger:
    logging_on = False
    logging_mess_on = False

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

        self.receiver.on_subscribe = self.on_subscribe
        self.receiver.subscribe(self.receiver_topic)
        # self.receiver.subscribe(self.receiver_topic)

        self.receiver.last_messages = Queue()
        self.sender.last_messages = Queue()

        self.client_topics = list()
        self.wait_topics = list()

        self.last_message_lock = Lock()
        self.cond = Condition()

        # self.last_messages = Queue.queue()
        self.listen()
        # print ("loop started!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def listen(self):
        self.receiver.loop_start()

    def subscribe(self, topic):
        self.receiver.subscribe(topic)


    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.log("Subscribed: " + str(client) + "")

    def add_topic_to_send(self, topic):
        self.client_topics.append(topic)

    def add_client(self, bot_info):
        self.add_topic_to_send(self.create_topic(bot_info["bot_id"], "receive"))

    def on_log(self, client, userdata, level, buf):
        self.log(str(self.name) + " log: " + str(buf) + " ")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # client.connected_flag = True  # set flag
            pass
            # self.log("connected OK")
        else:
            self.log("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.log("Disconnected result code " + str(rc))
        self.receiver.loop_stop()

    def on_message(self, client, userdata, msg):
        m_decode = str(msg.payload.decode("utf-8"))
        # print("=========++++++++++++=============")
        self.receiver.last_messages.put(m_decode) #self.create_message_from_string(m_decode)
        self.log(str(self.name) + " received message: " + str(m_decode))

        self.receiver.mess_event.set()


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
        else:
            return None

    @staticmethod
    def create_message_from_string(mess_str):
        # logging.debug("mess_str: " + str(mess_str))
        message_dict = literal_eval(mess_str)
        if "message" in message_dict:
            json_loaded = json.loads(message_dict["message"])
        else:
            json_loaded = None

        return Message(message_dict["id"],
                       Messenger.get_message_type_from_string(message_dict["type"]),
                       json_loaded)

    def create_topic(self, *args):
        return '/'.join([str(arg) for arg in args])

    def log(self, msg):
        if Messenger.logging_on:
            logging.debug(msg)

    def get_last_messages(self):
        result_dict = dict()
        while not self.receiver.last_messages.empty():
            last_message = Messenger.create_message_from_string(self.receiver.last_messages.get())
            result_dict[last_message.id] = last_message

        return result_dict

    def get_last_message(self):
        if self.receiver.last_messages:
            with self.last_message_lock:
                received = self.receiver.last_messages.get()
                return Messenger.create_message_from_string(received)
        else:
            return None

    def __del__(self):
        self.receiver.loop_stop()
        self.receiver.disconnect()

        self.sender.disconnect()

class ID:
    ALL = 0
class MTYPE:
    BOARD = "BOARD"
    BOT_INFO = "BOT_INFO"
    SIMPLE = "SIMPLE"
    COMPLEX = "COMPLEX"
    MACRO = "MACRO"
    ALGORITHM_COMMAND = "ALGORITHM_COMMAND"
    SERVER = "SERVER"
    CONFIG = "CONFIG"

class MSIMPLE:
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"
    TURN = "TURN"


class MMACRO:
    MEASURE_LINE = "MEASURE_LINE"

class MALGORITHM_COMMAND:
    STOP = "STOP"
    CONTINUE = "CONTINUE"

class MSERVER:
    READY = "READY"
# class MCOMPLEX:

class Message:
    def __init__(self, id, type, content):
        import swarm_bot_simulator.model.algorithm_module as comp

        if isinstance(content, dict) and type == MTYPE.BOT_INFO:
            bot_info = comp.BotInfo()
            bot_info.from_dict(content)
            content = bot_info

        elif isinstance(content, dict) and type == MTYPE.BOARD:
            board = comp.Board()
            board.from_dict(content)
            content = board


        self.id = id
        self.content = content
        self.type = type

    def __str__(self):
        return str(self.__dict__)

class MessageEncoder(json.JSONEncoder):
    def default(self, o):
        import swarm_bot_simulator.model.algorithm_module as comp
        be = comp.BoardEncoder()
        mde = comp.MovementDataEncoder()
        bie = comp.BotInfoEncoder()
        if isinstance(o, Message):
            if isinstance(o.content, comp.Board):
                return {
                    "id": o.id,
                    "type": o.type,
                    "message": be.encode(o.content)
                }
            elif isinstance(o.content, comp.BotInfo):
                return {
                    "id": o.id,
                    "type": o.type,
                    "message": bie.encode(o.content)
                }

            elif isinstance(o.content, comp.MovementData):
                return {
                    "id": o.id,
                    "type": o.type,
                    "message": mde.encode(o.content)
                }
            elif isinstance(o.content, comp.Board):
                return {
                    "id": o.id,
                    "type": o.type,
                    "message": mde.encode(o.content)
                }
            elif isinstance(o.content, str):
                return {
                    "id": o.id,
                    "type": o.type,
                    "message": json.dumps(o.content)
                }
            elif isinstance(o.content, dict):
                return {
                    "id": o.id,
                    "type": o.type,
                    "message": json.dumps(o.content)
                }
            else:
                return {
                    "id": o.id,
                    "type": o.type,
                }
        else:
            return json.JSONEncoder.default(self, o)