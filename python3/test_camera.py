from swarm_bot_simulator.model.image_detection import Camera
from swarm_bot_simulator.resources.config import config as con
cam = Camera(config=con)
cam.load_video()