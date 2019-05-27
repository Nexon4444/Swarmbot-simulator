# -*- coding: utf-8 -*-
import json
import subprocess
import warnings
import os

from swarm_bot_simulator.controller.simulator import Simulator
from swarm_bot_simulator.model.config import *
from swarm_bot_simulator.view.visualize import *
from swarm_bot_simulator.model.bot_components import *

app_config = None

with open(os.path.join("resources", "app_config.json"), "r", encoding="utf-8") as f:
    app_config = json.load(f)

print(app_config)
config = Config(app_config)
# config.swarm_bots[0].messenger.subscribe(topic="test") #, message="test dzialaj")
# config.swarm_bots[0].movement.move_prim(5)
try:
    simulator = Simulator(config)
    simulator.simulate()

except ConnectionRefusedError as e:
    warnings.warn("Have you started mosquitto.exe?")
    raise e
