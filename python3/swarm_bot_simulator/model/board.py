import time

from swarm_bot_simulator.model.server import Server
from swarm_bot_simulator.controller.information_transfer import Messenger

class Board:
    def __init__(self, config):
        self.bot_n = config.bot_n
        self.server = Server(config)
        self.server.initialize_comm()
        self.all_bots = config.start_bots
        for bot in self.all_bots:
            bot.update_board_info(self)
            bot.initialize_comm()

        mess = Messenger("TEST", communication_settings=config.communication_settings)

        mess.subscribe("server/main")
        self.server.messenger.send(topic="server/main", message="tralalalalalatralalalalalatralalalalalatralalalalala")
        # time.sleep(5)

    def calibrate(self):
        pass

    def run(self):
        pass