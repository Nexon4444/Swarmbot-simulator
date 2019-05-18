from swarm_bot_simulator.model.board import *
from swarm_bot_simulator.view.visualize import *
from swarm_bot_simulator.model.bot_components import *
from swarm_bot_simulator.model.config import *
# from swarm_bot_simulator.controller.information_transfer import Message.
import threading, queue
import logging

class Simulator:
    def __init__(self, config):
        self.config = config
        self.mess_event = threading.Event()

        self.messenger = Messenger("server", config, mess_event=self.mess_event)

    def simulate(self):
        q = queue.Queue()
        # q.put()
        board_activation_event = threading.Event()
        board_activation_event.clear()
        board_thread = threading.Thread(target=self.talk_with_bots, args=[q, board_activation_event])
        board_thread.start()

        if self.config.view_settings.launch is True:
            visualization_thread = threading.Thread(target=self.talk_with_bots, args=[q, board_activation_event])
            visualization_thread.start()
            visualization_thread.join()

        board_thread.join()

    def visualization_thread(self, q, board_activation_event: threading.Event()):
        vis = Visualizer(self.config.board_settings, board_activation_event)
        stop = False
        vis.visualize(q)
        # while not stop:
            # stop = vis.visualize(q)

    def simulate_movement(self):
        pass

    def communicate(self, bot_info, board):
        # me = .encode
        me = MessageEncoder()
        be = BoardEncoder()
        encoded_string = me.encode(Message(MTYPE.BOARD, be.encode(board)))
        self.messenger.add_client("1/receive")
        self.messenger.send(message=encoded_string)

    def talk_with_bots(self, q, board_activation_event: threading.Event()):
        board = Board(self.config)
        x = self.config.bot_infos
        bot_infos = copy.deepcopy(self.config.bot_infos)
        all_bots = [Bot(BotInfo(bot_info_parsed, self.config), config=self.config) for bot_info_parsed in self.config.bot_infos]
        all_bot_infos = [BotInfo(bot_info_parsed, self.config) for bot_info_parsed in self.config.bot_infos]


        board.update_all_bots(bot_infos)
        q.put(board)
        board_activation_event.set()
        logging.debug("Starting simulation")
        print("SIMULATE_BOTS")
        for i in range(0, 1000):
            for bot_info in all_bot_infos:
                self.communicate(bot_info, board)
                bot.update_board_info(board)
                bot.run()
            for bot in all_bots:
                bot.update()
            for bot in all_bots:
                bot.pass_line()
                bot.update_real_data()

            board.calculate_locations_from_bot_data()
            time.sleep(0.1)
            board.update_all_bots(bot_infos)
            q.put(board)
        logging.debug("Stopping simulation")

    # def board_thread(self, q, board_activation_event: threading.Event()):
    #     board = Board(self.config)
    #     x = self.config.bot_infos
    #     bot_infos = copy.deepcopy(self.config.bot_infos)
    #     all_bots = [Bot(BotInfo(bot_info_parsed, self.config), config=self.config) for bot_info_parsed in self.config.bot_infos]
    #     board.update_all_bots(bot_infos)
    #     q.put(board)
    #     board_activation_event.set()
    #     logging.debug("Starting simulation")
    #     print("SIMULATE_BOTS")
    #     for i in range(0, 1000):
    #         for bot in all_bots:
    #             bot.update_board_info(board)
    #
    #             bot.run()
    #         for bot in all_bots:
    #             bot.update()
    #         for bot in all_bots:
    #             bot.pass_line()
    #             bot.update_real_data()
    #
    #         board.calculate_locations_from_bot_data()
    #         time.sleep(0.1)
    #         board.update_all_bots(bot_infos)
    #         q.put(board)
    #     logging.debug("Stopping simulation")

    def tune_time2position(self):
        pass

    def tune(self):
        pass

    # def simulate_bots(self, board, q):
    #     time.sleep(3)
    #     logging.debug("Starting simulating bots")
    #     print("SIMULATE_BOTS")
    #     for i in range(0, 10):
    #         for bot in board.all_bots:
    #             bot.run()
    #         q.put(board)
    #     logging.debug("Stopping simulating bots")




