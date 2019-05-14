from threading import *
import json
import os
# from swarm_bot_simulator.model.bot_components import *
from swarm_bot_simulator.model.config import *
app_config = None
with open(os.path.join("swarm_bot_simulator", "resources", "app_config.json"), "r", encoding="utf-8") as f:
    app_config = json.load(f)
config = Config(app_config)
e1 = Event()
e2 = Event()

mes1 = Messenger("1", config.communication_settings, e1)
mes2 = Messenger("2", config.communication_settings, e2)

mes1.listen()
mes2.listen()

mes1.send(topic="2/receive", message="from mes1")
mes2.send(topic="1/receive", message="from mes2")

# mes1.start_loop_and_wait(200)
# print("---------------------------------------------------")
# time.sleep(900)

























# bot = Bot(app_config["bots"][0], config.communication_settings, config.bot_settings, config.board_settings)
# bot.movement.move_prim(1)2
# python3/swarm_bot_simulator/resources/app_config.json

import paho.mqtt.client as mqtt #import the client1
import time
############
# def on_message(client, userdata, message):
#     print("message received " ,str(message.payload.decode("utf-8")))
#
# client = mqtt.Client("P1") #create new instance
# client.on_message=on_message #attach function to callback
# print("connecting to broker")
# client.connect("192.168.0.106", port=2000) #connect to broker
# client.loop_start() #start the loop
# client.subscribe("test")
# time.sleep(200) # wait
# client.loop_stop() #stop the loop