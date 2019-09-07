# from swarm_bot_simulator.model.board import *
# from typing import Dict, Any
import time

# from swarm_bot_simulator.controller.information_transfer import Message
from swarm_bot_simulator.model.algorithm.algorithm_module import Board, Bot
from swarm_bot_simulator.view.visualization.visualization_module import Visualizer
# from swarm_bot_simulator.model.bot_components import *
from swarm_bot_simulator.model.communication.communication_module import *
from swarm_bot_simulator.utilities.util import merge_two_dicts, log_flush
from swarm_bot_simulator.model.image_detection import image_analyzer_module as va

import threading, queue
import logging

class Bot_manager:
    def __init__(self, config):
        self.id = 0
        self.config = config
        self.mess_event = threading.Event()
        self.board = Board(config=config)

        self.bots = [Bot(bot_info["bot_id"],
                         config["communication_settings"]["broker"],
                         config["communication_settings"]["port"])
                         for bot_info in config["bots"] if bot_info["is_real"]
                                                                is not True]

        self.video_analyser = va.VideoAnalyzer
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
        # q.put()
        self.simulate_bots()
        board_activation_event = threading.Event()
        board_activation_event.clear()
        t_talk = threading.Thread(target=self.communicate_with_bots, args=[q, board_activation_event, self.config])
        t_talk.start()

        if self.config["view_settings"]["launch"]is True:
            visualization_thread = threading.Thread(target=self.visualization_thread, args=[q, board_activation_event])
            visualization_thread.start()
            visualization_thread.join()

        t_talk.join()

    def visualization_thread(self, q, board_activation_event):
        board_activation_event.wait()
        vis = Visualizer(self.config["board_settings"], board_activation_event)
        stop = False
        vis.visualize(q)

        # while not stop:
        # stop = vis.visualize(q)

    def simulate_bots(self):
        for bot in self.bots:
            bot.start_thread()

    def simulate_movement(self):
        pass

    def communicate(self, bot_info):
        # me = .encode
        me = MessageEncoder()
        # bie = BotInfoEncoder()
        # encoded_string = me.encode(Message(MTYPE.BOT_INFO, bot_info))
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
        :return:
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
                    # log_flush("NO READY FROM: " + str(bot_id) + " ", start, end)
                    # logging.debug("NOT ALL READY messages received from all bots")
                    break

            # time.sleep(0.1)

        print("\n")
        # logging.debug("READY messages received from all bots")

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
                    # log_flush("NO BOARD FROM BOT: " + bot_id, start, end)
                    break
            # time.sleep(0.01)

        print("\n")
        # logging.debug("BOARD messages received from all bots")

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
                    end = time.time()
                    # log_flush("NOT ALL BOT_INFO messages received from all bots: ", start, end)
                    break
            # time.sleep(1)

        print("\n")
        # logging.debug("BOARD messages received from all bots")
        return received_messages

    # def send_order(self, order):
    #     me = MessageEncoder()
    #
    #     if order == "continue":
    #         encoded_string = me.encode(Message(self.id, MTYPE.ALGORITHM_COMMAND, MALGORITHM_COMMAND.CONTINUE))
    #         self.messenger.send(message=encoded_string)
    #     else

    def send_continue(self):
        me = MessageEncoder()
        encoded_string = me.encode(Message(self.id, MTYPE.ALGORITHM_COMMAND, MALGORITHM_COMMAND.CONTINUE))
        self.messenger.send(message=encoded_string)

    def send_config(self, config):
        me = MessageEncoder()
        # encoded_string =
        encoded_string = me.encode(Message(self.id, MTYPE.CONFIG, config))
        self.messenger.send(message=encoded_string)

    def communicate_with_bots(self, q, board_activation_event, config):
        self.send_server_info()
        self.await_ready()
        # time.sleep(0.1)
        self.send_config(config)
        self.await_ready()
        board_activation_event.set()
        while True:
            time.sleep(0.5)
            self.send_boards()
            self.await_ready()

            self.send_continue()
            self.calculate_positions(self.get_info_from_bots())
            self.synchronise_with_camera()
            self.visualize_data(q)

        # x = self.messenger.get_last_messages()
        # logging.debug(str(self.messenger.get_last_messages()))
        # logging.debug("Stopping simulation")

    def get_info_from_bots(self):
        messages_dict = self.await_bot_info()
        bots_info_dict = self.bot_info_messages_dict2bots_info_dict(messages_dict)
        return bots_info_dict

    def synchronise_with_camera(self):
        return
        for bot_info in self.board.bots_info:
            if bot_info.is_real:
                photo_params = self.video_analyser.load_photo()
                board_params = photo_params[0]
                board_width = board_params[1][0]
                board_height = board_params[1][1]

                marker_params = photo_params[1]
                marker_poz_x = marker_params[0][0]
                marker_poz_y = marker_params[0][1]
                marker_direction = marker_params[1]
                # bot_info

    def calculate_positions(self, bot_infos_dict):
        for key, bot_info in bot_infos_dict.items():
            self.board.bots_info[key] = bot_infos_dict[key]

    def bot_info_messages_dict2bots_info_dict(self, bot_info_messages):
        return {key: message.content for key, message in bot_info_messages.items()}

    def visualize_data(self, q):
        q.put(self.board)

