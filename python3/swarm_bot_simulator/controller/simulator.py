# from swarm_bot_simulator.model.board import *
from swarm_bot_simulator.view.visualize import *
from swarm_bot_simulator.model.bot_components import *
from swarm_bot_simulator.model.config import *
from swarm_bot_simulator.controller.information_transfer import *
import threading, queue
import logging

class Simulator:
    def __init__(self, config):
        self.config = config
        self.mess_event = threading.Event()
        # self.info_sent_events = {bot_info.id: Event() for bot_info in config.bot_info}
        self.board = Board(config=config)
        # self.bots_info = {
        #     bot_info_parsed.bot_id: BotInfo(bot_info_parsed=bot_info_parsed) for
        #     bot_info_parsed in config.bot_infos}
        # self.bots = [Bot(config, self.info_sent_events[bot_info.id], bot_info) for bot_info in config.bot_infos]
        self.bots = [Bot(bot_info.bot_id, config) for bot_info in config.bot_infos]
        self.messenger = Messenger("server", config.communication_settings.broker, config.communication_settings.port,
                                   mess_event=self.mess_event)
        for bot_info in config.bot_infos:
            self.messenger.add_client(bot_info)
        for bot_info in config.bot_infos:
            self.messenger.subscribe(self.messenger.create_topic(bot_info.bot_id, "send"))

    def simulate(self):
        q = queue.Queue()
        # q.put()
        self.simulate_bots()
        board_activation_event = threading.Event()
        board_activation_event.clear()
        t_talk = threading.Thread(target=self.talk_with_bots, args=[q, board_activation_event])
        t_talk.start()

        if self.config.view_settings.launch is True:
            visualization_thread = threading.Thread(target=self.visualization_thread, args=[q, board_activation_event])
            visualization_thread.start()
            visualization_thread.join()

        t_talk.join()

    def visualization_thread(self, q, board_activation_event: threading.Event()):
        vis = Visualizer(self.config.board_settings, board_activation_event)
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
        encoded_string = me.encode(Message(MTYPE.BOT_INFO, bot_info))
        self.messenger.send(message=encoded_string)

    def send_boards(self):
        me = MessageEncoder()
        encoded_string = me.encode(Message(MTYPE.BOARD, self.board))
        self.messenger.send(message=encoded_string)

    def send_server_info(self):
        me = MessageEncoder()
        encoded_string = me.encode(Message(MTYPE.SERVER, self.messenger.receiver_topic))
        self.messenger.send(message=encoded_string)

    def talk_with_bots(self, q, board_activation_event):
        self.send_server_info()
        self.messenger.wait_for_ack()

        # self.send_boards()

        # for key, bot_info in self.board.bots_info.items():
        #     self.communicate(bot_info)


        # board = Board(self.config)
        # x = self.config.bot_infos
        # bot_infos = copy.deepcopy(self.config.bot_infos)

        # all_bots = [Bot(BotInfo(bot_info_parsed, self.config), config=self.config) for bot_info_parsed in self.config.bot_infos]
        # all_bot_infos = [BotInfo(bot_info_parsed, self.config) for bot_info_parsed in self.config.bot_infos]


        # board.update_all_bots(bot_infos)
        # q.put(board)
        # board_activation_event.set()
        # logging.debug("Starting simulation")
        # print("SIMULATE_BOTS")
        # for i in range(0, 1000):
        #     for bot_info in all_bot_infos:
        #         self.communicate(bot_info, board)
        #         bot.update_board_info(board)
        #         bot.run()
        #     for bot in all_bots:
        #         bot.update()
        #     for bot in all_bots:
        #         bot.pass_line()
        #         bot.update_real_data()
        #
        #     board.calculate_locations_from_bot_data()
        #     time.sleep(0.1)
        #     board.update_all_bots(bot_infos)
        #     q.put(board)
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
    #     logging.damount of testosteron on nofap



# class Board:
#     # all_bots: list()
#
#     def __init__(self, config):
#
#         self.bots_info = {
#             bot_info_parsed.bot_id: BotInfo(bot_info_parsed=bot_info_parsed) for
#             bot_info_parsed in config.bot_infos}
#
#         # self.all_bots_data = None
#
#     # def update_all_bots(self, all_bots_data):
#     #     self.all_bots_data = copy.deepcopy(all_bots_data)
#
#     def __str__(self):
#         bot_list = [str(bot) for bot in self.all_bots_data]
#         return "\n".join(bot_list)
#
#     def calibrate(self):
#         pass
#
#     def run(self):
#         pass
#     #
#     def calculate_locations_from_bot_data(self):
#         pass





