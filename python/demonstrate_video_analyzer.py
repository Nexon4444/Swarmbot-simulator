import swarm_bot_simulator.model.image_analyzer_module as ia
from swarm_bot_simulator.resources.config import config
va = ia.VideoAnalyzer(config)
va.load_video()