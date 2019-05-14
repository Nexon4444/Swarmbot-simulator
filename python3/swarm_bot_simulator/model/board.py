import time
from json import JSONEncoder
import json
# from swarm_bot_simulator.model.server import Server
from swarm_bot_simulator.controller.information_transfer import Messenger

class Board():
    # all_bots: list()

    def __init__(self, config):
        self.bot_n = config.bot_n
        # self.server = Server(config)
        # self.server.initialize_comm()
        self.all_bots = config.swarm_bots
        for bot in self.all_bots:
            bot.update_board_info(self)
            bot.initialize_comm()

        mess = Messenger("TEST", communication_settings=config.communication_settings)

        mess.subscribe("server/main")
        # self.server.messenger.send(topic="server/main", message="tralalalalalatralalalalalatralalalalalatralalalalala")


    def __str__(self):
        bot_list = [str(bot)for bot in self.all_bots]
        return "\n".join(bot_list)

    def calibrate(self):
        pass

    def run(self):
        pass
    #

class BoardEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Board):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, o)

