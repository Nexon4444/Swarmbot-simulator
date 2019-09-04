import swarm_bot_simulator.model.image_detection.video_analyzer as va
from swarm_bot_simulator.resources.config import config

video_analyser = va.VideoAnalyzer(config)
video_analyser.load_video()
video_analyser
