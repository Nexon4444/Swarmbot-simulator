# import json
# import os
# # from swarm_bot_simulator.model.bot_components import *
# from swarm_bot_simulator.model.config import *
# app_config = None
# with open(os.path.join("swarm_bot_simulator", "resources", "app_config.json"), "r", encoding="utf-8") as f:
#     app_config = json.load(f)
# config = Config(app_config)
# mes = Messenger("1", config.communication_settings)
# # mes.subscribe(topic="test")
# mes.send(topic="test", message="Asdasdasd")
# # bot = Bot(app_config["bots"][0], config.communication_settings, config.bot_settings, config.board_settings)
# # bot.movement.move_prim(1)2
# # python3/swarm_bot_simulator/resources/app_config.json

import paho.mqtt.client as mqtt #import the client1
import time
############
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    # print("message topic=",message.topic)
    # print("message qos=",message.qos)
    # print("message retain flag=",message.retain)
########################################
# broker_address="192.168.0.106"
# #broker_address="iot.eclipse.org"
# print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect("192.168.0.106", port=2000) #connect to broker
client.loop_start() #start the loop
client.subscribe("test")
time.sleep(200) # wait
client.loop_stop() #stop the loop