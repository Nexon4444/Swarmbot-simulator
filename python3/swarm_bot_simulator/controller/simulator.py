from swarm_bot_simulator.model.board import *
from swarm_bot_simulator.view.visualize import *
from swarm_bot_simulator.model.config import *
class Simulator:
    def __init__(self, config):
        self.config = config

    def simulate(self):
        test_board = Board(self.config)
        vis = Visualizer()


        # vis.visualize(test_board)

        main_thread = Thread(target=self.simulate_bots, args=[test_board])
        assert isinstance(self.config.view_settings, ViewSettings)
        if self.config.view_settings.launch is True:
            visualization_thread = Thread(target=vis.visualize, args=[test_board])
        # thread.daemon = True
        main_thread.start()
        if self.config.view_settings.launch is True:
            visualization_thread.start()

        main_thread.join()
        if self.config.view_settings.launch is True:
            visualization_thread.join()


    def simulate_bots(self, board):
        print("SIMULATE_BOTS")
        for bot in board.all_bots:
            bot.think()




