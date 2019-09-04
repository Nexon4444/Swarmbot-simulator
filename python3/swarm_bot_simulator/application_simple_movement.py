# -*- coding: utf-8 -*-
import warnings
import subprocess
from swarm_bot_simulator.model.simulation.simulator import Simulator
from swarm_bot_simulator.model.image_detection import Camera
from swarm_bot_simulator.resources.config import config

def launch_mosquitto(port):
    subprocess.Popen(["mosquitto", "-p", str(port)])
launch_mosquitto(config["communication_settings"]["port"])
# os.system("cmd")
# os.system(str(mosquitto_path) + str (" -p ") + str(port))

# subprocess.Popen([ls, "-p", port])

config = config
# config_dumped = json.dumps(config)
# print(config_dumped)
# config_loaded = json.loads(config_dumped)

img_path = "/home/nexon/Projects/Swarmbot-simulator/python3/swarm_bot_simulator/resources/trojkat.jpg"
camera = Camera(config)
photo_params = camera.load_photo(img_path)
board_params = photo_params[0]
board_width = board_params[1][0]
board_height = board_params[1][1]

marker_params = photo_params[1]
marker_poz_x = marker_params[0][0]
marker_poz_y = marker_params[0][1]
marker_direction = marker_params[1]

if config["bots"][0]["is_real"] is True:
    config["bots"][0]["direction"] = marker_direction
    config["bots"][0]["poz_x"] = marker_poz_x
    config["bots"][0]["poz_y"] = marker_poz_y

config["board_settings"] = {}
config["board_settings"]["border_x"] = board_width
config["board_settings"]["border_y"] = board_height

# with open(os.path.join("resources", "app_config.json"), "r", encoding="utf-8") as f:
#     app_config = json.load(f)

print(config)
# config = Config(app_config)
# config.swarm_bots[0].messenger.subscribe(topic="test") #, message="test dzialaj")
# config.swarm_bots[0].movement.move_prim(5)
try:
    simulator = Simulator(config)
    simulator.simulate()

except ConnectionRefusedError as e:
    warnings.warn("Have you started mosquitto.exe?")
    raise e
