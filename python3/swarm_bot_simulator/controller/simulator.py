from swarm_bot_simulator.model.board import *
from swarm_bot_simulator.view.visualize import *
from swarm_bot_simulator.model.bot_components import *
from swarm_bot_simulator.model.config import *
import threading, queue
import logging

class Simulator:
    def __init__(self, config):
        self.config = config

    def simulate(self):
        q = queue.Queue()
        # q.put()
        board_thread = threading.Thread(target=self.start_visualization_thread, args=[q])
        board_thread.start()
        if self.config.view_settings.launch is True:
            visualization_thread = threading.Thread(target=self.start_board_thread, args=[q])
            visualization_thread.start()
            visualization_thread.join()

        board_thread.join()

    def start_visualization_thread(self, q):
        vis = Visualizer(self.config.board_settings)
        stop = False
        vis.visualize(q)
        # while not stop:
            # stop = vis.visualize(q)

    def start_board_thread(self, q):
        board = Board(self.config)
        q.put(board)
        # vec = Vector(1, 0)
        print(str(board.serialize()))
        logging.debug("Starting simulation")
        print("SIMULATE_BOTS")
        for i in range(0, 1000):
            for bot in board.all_bots:
                bot.run()
            for bot in board.all_bots:
                bot.update()
            # board.all_bots[0].move(vec)
            time.sleep(0.1)
            q.put(board)
        logging.debug("Stopping simulatiion")

    # def simulate_bots(self, board, q):
    #     time.sleep(3)
    #     logging.debug("Starting simulating bots")
    #     print("SIMULATE_BOTS")
    #     for i in range(0, 10):
    #         for bot in board.all_bots:
    #             bot.run()
    #         q.put(board)
    #     logging.debug("Stopping simulating bots")




