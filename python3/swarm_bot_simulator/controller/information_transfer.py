import paho.mqtt.client as mqtt


class Messenger:
    def __init__(self, topic, communication_settings):
        self.client = mqtt.Client(str(topic) + "_client")
        self.topic = topic
        self.client.on_connect = self.on_connect
        self.client.on_log = self.on_log
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        print("connecting to broker", communication_settings.broker)
        self.client.connect(communication_settings.broker, communication_settings.port)

        self.client.subscribe(topic)
        self.client.loop_start()

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

    def send(self, message):
        self.client.publish(topic=self.topic, message=message)

    def recieve(self):
        def connection_execute(self):
            # mqtt.Client.connected_flag=False#create flag in class

            # self.client.loop_forever(200.0)

            self.client.publish("swarm_bot2/commands", "my first command")
            time.sleep(10)
            self.client.loop_stop()
            self.client.disconnect()

    def __del__(self):
        self.client.loop_stop()
        self.client.disconnect()
