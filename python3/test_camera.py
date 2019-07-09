from swarm_bot_simulator.controller.camera import Camera
from swarm_bot_simulator.resources.config import config as con
cam = Camera(config=con)
cam.load_video()