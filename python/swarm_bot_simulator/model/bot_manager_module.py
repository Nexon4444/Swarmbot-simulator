# from swarm_bot_simulator.model.board import *
# from typing import Dict, Any
import time

from swarm_bot_simulator.model.algorithm_module import Board, Bot
from swarm_bot_simulator.utilities import util
from swarm_bot_simulator.view.visualization_module import Visualizer
from swarm_bot_simulator.model.communication_module import *
from swarm_bot_simulator.utilities.util import merge_two_dicts
from swarm_bot_simulator.model import image_analyzer_module as va
import threading, queue


class Bot_manager:
    def __init__(self, config, controller):
        self.id = 0
        self.config = config
        self.mess_event = threading.Event()
        self.board = Board(config=config)
        self.controller = controller
        self.bots = [Bot(bot_info["bot_id"],
                         config["communication_settings"]["broker"],
                         config["communication_settings"]["port"])
                         for bot_info in config["bots"] if bot_info["is_real"]
                                                                is not True]
        self.t_talk = None
        self.t_vis= None
        self.video_analyser = va.VideoAnalyzer(config)
        self.messenger = Messenger("server",
                                   config["communication_settings"]["broker"],
                                   config["communication_settings"]["port"],
                                   mess_event=self.mess_event)
        for bot in config["bots"]:
            self.messenger.add_client(bot)
        for bot in config["bots"]:
            self.messenger.subscribe(self.messenger.create_topic(bot["bot_id"], "send"))

    def simulate(self):
        q = queue.Queue()
        self.simulate_bots()
        board_activation_event = threading.Event()
        board_activation_event.clear()

        start_simulation_event = threading.Event()
        start_simulation_event.clear()

        if self.config["view_settings"]["launch"]is True:
            self.t_vis = threading.Thread(target=self.visualization_thread,
                                                    args=[q,
                                                          board_activation_event,
                                                          start_simulation_event
                                                          ])
            self.t_vis.start()

        self.t_talk = threading.Thread(target=self.communicate_with_bots,
                                       args=[q,
                                             board_activation_event,
                                             start_simulation_event,
                                             self.controller.quit_event,
                                             self.config])
        self.t_talk.start()
        self.t_vis.join()
        self.controller.quit_program()
        self.t_talk.join()

    def visualization_thread(self, q, board_activation_event, start_simulation_event):
        vis = Visualizer(self.config["board_settings"], board_activation_event, start_simulation_event)
        stop = False
        vis.visualize(q)

    def simulate_bots(self):
        for bot in self.bots:
            bot.start_thread()

    def communicate(self, bot_info):
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.BOT_INFO, bot_info))
        self.messenger.send(message=encoded_string)

    def send_boards(self):
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.BOARD, self.board))
        self.messenger.send(message=encoded_string)

    def send_server_info(self):
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.SERVER, self.messenger.receiver_topic))
        self.messenger.send(message=encoded_string)

    def await_ready(self):
        """
        Blocking
        """
        start = time.time()
        all_messages_received = False
        messages = dict()
        while all_messages_received is False:
            received_messages = self.messenger.get_last_messages()
            messages = merge_two_dicts(messages, received_messages)
            all_messages_received = True
            for bot_id in self.board.bots_info.keys():
                if bot_id not in messages \
                        or messages[bot_id].type != MTYPE.SERVER \
                        or messages[bot_id].content != MSERVER.READY:

                    all_messages_received = False
                    end = time.time()
                    break
        print("\n")

    def communicate_with_bots(self, q, board_activation_event, start_simulation_event, quit_event, config):
        start_simulation_event.wait()
        self.synchronise_with_camera()
        logging.debug("communication starting")
        self.await_ready_resend(2, self.send_server_info)
        logging.debug("waiting for ready from bots")
        self.send_config(config)
        self.await_ready()
        board_activation_event.set()
        while not quit_event.is_set():

            self.send_boards()
            self.await_ready()

            self.send_continue()
            self.calculate_positions(self.get_info_from_bots())
            self.synchronise_with_camera()
            self.visualize_data(q)
            time.sleep(0.5)
        self.quit_program()


    def await_ready_resend(self, wait_time, func):
        messages = dict()
        while True:
            logging.debug("sending server info")
            func()
            start = time.time()
            all_messages_received = False

            while all_messages_received is False:
                received_messages = self.messenger.get_last_messages()
                messages = merge_two_dicts(messages, received_messages)
                all_messages_received = True
                end = time.time()
                logging.debug("waiting for: " + str(end - start))
                if end - start > wait_time:
                    break
                for bot_id in self.board.bots_info.keys():
                    if bot_id not in messages \
                            or messages[bot_id].type != MTYPE.SERVER \
                            or messages[bot_id].content != MSERVER.READY:

                        all_messages_received = False
                        logging.debug("NOT ALL READY messages received from all bots")
                        logging.debug("received: " + str(messages))
                if all_messages_received:
                    return

                # time.sleep(1)

        # print("\n")

    def await_boards(self):
        start = time.time()
        all_messages_received = False
        messages = dict()
        while all_messages_received is False:
            received_messages = self.messenger.get_last_messages()
            messages = merge_two_dicts(messages, received_messages)
            all_messages_received = True
            for bot_id in self.board.bots_info.keys():
                if bot_id not in messages or messages[bot_id].type != MTYPE.BOARD:
                    all_messages_received = False
                    end = time.time()
                    break

        # print("\n")

    def await_bot_info(self):
        received_messages = None
        start = time.time()
        all_messages_received = False
        messages = dict()
        while all_messages_received is False:
            received_messages = self.messenger.get_last_messages()
            messages = merge_two_dicts(messages, received_messages)
            all_messages_received = True
            for bot_id in self.board.bots_info.keys():
                if bot_id not in messages or messages[bot_id].type != MTYPE.BOT_INFO:
                    all_messages_received = False
                    time.sleep(0.1)
                    end = time.time()
                    break


        # print("\n")
        return received_messages


    def send_continue(self):
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.ALGORITHM_COMMAND, MALGORITHM_COMMAND.CONTINUE))
        self.messenger.send(message=encoded_string)

    def send_config(self, config):
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.CONFIG, config))
        self.messenger.send(message=encoded_string)

    def get_info_from_bots(self):
        messages_dict = self.await_bot_info()
        bots_info_dict = self.bot_info_messages_dict2bots_info_dict(messages_dict)
        return bots_info_dict

    def synchronise_with_camera(self):
        for key, bot_info in self.board.bots_info.items():
            if bot_info.is_real: #or bot_info.bot_id == "1":
                img_path = "/home/nexon/Projects/Swarmbot-simulator/python/swarm_bot_simulator/resources/trojkat.jpg"

                photo_params = self.video_analyser.load_photo()
                board_params = photo_params[0]
                marker_params = photo_params[1]
                marker_transformed = photo_params[2]
                marker_transformed_poz_x = marker_transformed[0][0]
                marker_transformed_poz_y = marker_transformed[0][1]
                marker_direction = marker_params[1]
                bot_info.position = util.Vector(marker_transformed_poz_x, marker_transformed_poz_y)
                # logging.debug("bot_info_before: " + str(bot_info.dir))
                bot_info.dir = marker_direction
                # logging.debug(str("marker params: ") + str((marker_transformed_poz_x, marker_transformed_poz_y)))
                # logging.debug(str(bot_info.dir))

    def calculate_positions(self, bot_infos_dict):
        for key, bot_info in bot_infos_dict.items():
            self.board.bots_info[key] = bot_infos_dict[key]

    def bot_info_messages_dict2bots_info_dict(self, bot_info_messages):
        return {key: message.content for key, message in bot_info_messages.items()}

    def visualize_data(self, q):
        logging.debug(str("given board position: ") + str(self.board.bots_info["1"]))
        q.put(self.board)

    def quit_program(self):
        logging.debug("quiting bot_manager")
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.ALGORITHM_COMMAND, MALGORITHM_COMMAND.STOP))
        self.messenger.send(message=encoded_string)

        quit()


