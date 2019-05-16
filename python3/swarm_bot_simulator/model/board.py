import time
from json import JSONEncoder
import json
import copy
# from swarm_bot_simulator.model.server import Server
from swarm_bot_simulator.controller.information_transfer import Messenger
from swarm_bot_simulator.model.bot_components import BotInfo, Bot

class Board:
    # all_bots: list()

    def __init__(self, config):
        # self.bot_n = [Bot(b, self.communication_settings, self.bot_settings, self.board_settings) for b in app_config["bots"]]

        # self.server = Server(config)
        # self.server.initialize_comm()
        self.bots_info = {
            bot_info_parsed.bot_id: BotInfo(bot_info_parsed=bot_info_parsed, config=config) for
            bot_info_parsed in config.bot_infos}

        self.all_bots_data = None
        #
        # for bot in self.all_bots:
        #     bot.update_board_info(self)
        #     bot.initialize_comm()
        #
        # mess = Messenger("TEST", communication_settings=config.communication_settings)
        # mess.subscribe("server/main")
        # self.server.messenger.send(topic="server/main", message="tralalalalalatralalalalalatralalalalalatralalalalala")

    def update_all_bots(self, all_bots_data):
        self.all_bots_data = copy.deepcopy(all_bots_data)

    def __str__(self):
        bot_list = [str(bot) for bot in self.all_bots_data]
        return "\n".join(bot_list)

    def calibrate(self):
        pass

    def run(self):
        pass
    #
    def calculate_locations_from_bot_data(self):
        pass


class BoardEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Board):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, o)

# class BotDataContainer:
#     def __init__(self, bots, config):
#         self.bots_info = {
#         bot_info_parsed["bot_id"]: BotInfo(bot_info_parsed=bot_info_parsed, bot_settings=config.bot_settings) for
#         bot_info_parsed in bots}
#     def get_bot_info(self, id):
#         return self.bots_info[id]