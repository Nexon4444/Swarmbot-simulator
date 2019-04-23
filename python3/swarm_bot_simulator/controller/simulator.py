from swarm_bot_simulator.model.board import *
from swarm_bot_simulator.view.visualize import *
from swarm_bot_simulator.model.config import *
import threading, queue
import logging

class Simulator:
    def __init__(self, config):
        self.config = config

    def simulate(self):
        board = Board(self.config)
        vis = Visualizer()

        q = queue.Queue()

        # vis.visualize(test_board)
        q.put(board)
        main_thread = threading.Thread(target=self.simulate_bots, args=[board, q])
        main_thread.start()
        # thread.daemon = True
        # assert isinstance(self.config.view_settings, ViewSettings)
        if self.config.view_settings.launch is True:
            visualization_thread = threading.Thread(target=vis.visualize, args=[q])
            visualization_thread.start()
            visualization_thread.join()

        main_thread.join()


    def simulate_bots(self, board, q):
        time.sleep(3)
        logging.debug("Starting simulating bots")
        print("SIMULATE_BOTS")
        for i in range(0, 10):
            for bot in board.all_bots:
                bot.run()
            q.put(board)
        logging.debug("Stopping simulating bots")




