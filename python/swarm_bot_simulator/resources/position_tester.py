import swarm_bot_simulator.model.image_analyzer_module as ia
from swarm_bot_simulator.resources.config import config
from swarm_bot_simulator.view.visualization_module import Visualizer
from swarm_bot_simulator.utilities.util import *
from swarm_bot_simulator.model.algorithm_module import *
from queue import Queue
import threading
q = Queue()

def visualize_data(q, board):
    # logging.debug(str("given board position: ") + str(self.board.bots_info["1"]))
    q.put(board)

def visualization_thread(q, board_activation_event, start_simulation_event):
    vis = Visualizer(config["board_settings"], board_activation_event, start_simulation_event)
    vis.visualize(q)

camera = ia.VideoAnalyzer(config)
photo_params = camera.load_photo()
# photo_params = camera.load_photo()
board_params = photo_params[0]
board_width = board_params[1][0]
board_height = board_params[1][1]

marker_params = photo_params[1]
marker_poz_x = marker_params[0][0]
marker_poz_y = marker_params[0][1]
marker_direction = marker_params[1]
marker_transformed = photo_params[2]
marker_transformed_poz_x = marker_transformed[0][0]
marker_transformed_poz_y = marker_transformed[0][1]
# if config["bots"][]["is_real"] is True:
config["bots"][0]["direction"] = marker_direction
config["bots"][0]["poz_x"] = marker_transformed_poz_x
config["bots"][0]["poz_y"] = marker_transformed_poz_y

config["real_settings"]["pixel_2_real_ratio"] = board_width / config["board_settings"]["real_width"]
config["board_settings"] = {}
config["board_settings"]["border_x"] = board_width
config["board_settings"]["border_y"] = board_height

board_act_event = threading.Event()
start_sim_event = threading.Event()


board = Board(config)
t_vis = threading.Thread(target=visualization_thread,
                         args=[q,
                               board_act_event,
                               start_sim_event
                               ])
t_vis.start()

while True:
    bot_info = board.bots_info['1']
    photo_params = camera.load_photo()
    board_params = photo_params[0]
    marker_params = photo_params[1]
    marker_transformed = photo_params[2]
    marker_transformed_poz_x = marker_transformed[0][0]
    marker_transformed_poz_y = marker_transformed[0][1]
    marker_direction = marker_params[1]
    bot_info.position = Vector(marker_transformed_poz_x, marker_transformed_poz_y)
    bot_info.dir = marker_direction
    board_act_event.set()
    start_sim_event.set()
    visualize_data(q, board)