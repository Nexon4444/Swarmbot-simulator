import swarm_bot_simulator.model.image_analyzer_module as ia
from swarm_bot_simulator.resources.config import config
from swarm_bot_simulator.view.visualization_module import Visualizer
from swarm_bot_simulator.utilities.util import *
from swarm_bot_simulator.model.algorithm_module import *
from queue import Queue
import threading
qu = Queue()

def visualize_data(q, board):
    # logging.debug(str("given board position: ") + str(self.board.bots_info["1"]))
    q.put(board)

def visualization_thread(q, board_activation_event, start_simulation_event):
    vis = Visualizer(config["board_settings"], board_act_event, start_sim_event)
board_act_event = threading.Event()
start_sim_event = threading.Event()

va = ia.VideoAnalyzer(config)
board = Board(config)
t_vis = threading.Thread(target=visualization_thread,
                        args=[q,
                              board_activation_event,
                              start_simulation_event
                              ])
self.t_vis.start()

vis.visualize(q)
while True:
    bot_info = board.bots_info[0]
    photo_params = va.load_photo()
    board_params = photo_params[0]
    marker_params = photo_params[1]
    marker_transformed = photo_params[2]
    marker_transformed_poz_x = marker_transformed[0][0]
    marker_transformed_poz_y = marker_transformed[0][1]
    marker_direction = marker_params[1]
    bot_info.position = Vector(marker_transformed_poz_x, marker_transformed_poz_y)
    # logging.debug("bot_info_before: " + str(bot_info.dir))
    bot_info.dir = marker_direction
    # logging.debug(str("marker params: ") + str((marker_transformed_poz_x, marker_transformed_poz_y)))
    # logging.debug(str(bot_info.dir))True