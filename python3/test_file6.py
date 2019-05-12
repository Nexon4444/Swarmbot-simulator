import json
import os
# from swarm_bot_simulator.model.bot_components import *
from swarm_bot_simulator.model.config import *
app_config = None
with open(os.path.join("swarm_bot_simulator", "resources", "app_config.json"), "r", encoding="utf-8") as f:
    app_config = json.load(f)
config = Config(app_config)
mes = Messenger("server", config.communication_settings)
mes.subscribe("1/main")
bot = Bot(app_config["bots"][0], config.communication_settings, config.bot_settings, config.board_settings)
bot.movement.move_prim(1)
# python3/swarm_bot_simulator/resources/app_config.json