import paho.mqtt.client as mqtt
import time
class Server:
    def __init__(self, config):
        self.bot_n = config.bot_n
        self.all_bot_info = config.start_bots
        self.config = config

    def print_all_info(self):
        for bot_info in self.all_bot_info:
            print(str(bot_info.id) + str(bot_info.poz_x) + str(bot_info.poz_y) + str(bot_info.direction))

    # def listen(self):
    #     # Import package
    #     self.config.communication_settings.broker = "192.168.0.103"
    #     self.config.communication_settings.port = 1883

    def on_log(self, client, userdata, level, buf):
            print("log: " + buf)

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
        print("message received", m_decode)

    def connection_execute(self):
    # mqtt.Client.connected_flag=False#create flag in class
        client = mqtt.Client("python")
        client.on_connect = self.on_connect
        client.on_log = self.on_log
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

        print("connecting to broker", self.config.communication_settings.broker)
        client.connect(self.config.communication_settings.broker, self.config.communication_settings.port)

        # while not client.connected_flag: #wait in loop
        #     print("In wait loop")
        #     time.sleep(1)
        client.subscribe("swarm_bot2/commands")
        client.loop_start()
        # client.loop_forever(200.0)

        client.publish("swarm_bot2/commands", "my first command")
        time.sleep(10)
        client.loop_stop()
        client.disconnect()