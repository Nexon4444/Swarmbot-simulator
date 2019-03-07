# from swarm_bot_simulator.model.config import PozInfo
import json

from swarm_bot_simulator.controller.information_transfer import Messenger


class Bot:
    # last_id = 0

    def __init__(self, parsed_bot, communication_settings):
        self.bot_info = BotInfo(parsed_bot["bot_info"])
        self.acceleration = 0
        topic_name = "swarm_bot" + str(self.bot_info.bot_id)
        self.messenger = Messenger(topic=topic_name, communication_settings=communication_settings)


    # def set_communication(self):


    def comm_out(self):
        self.messenger.send(self.bot_info)

    def comm_in(self):
        self.messenger.recieve()

    def update_data(self):
        self.comm_out(self.bot_info.serialize())
        self.model = self.comm_in()

    def designate_coords(self):
        self.update_data()

    def move_front(self, distance):
        self.bot_info.poz_x = self.bot_info + distance
        self.update_data()

    def calibrate(self):
        pass

class BotInfo:
    def __init__(self, bot_info_parsed):
        self.bot_id = bot_info_parsed["bot_id"]
        self.poz_x = float(bot_info_parsed["poz_x"])
        self.poz_y = float(bot_info_parsed["poz_y"])
        self.direction = float(bot_info_parsed["direction"])

    def serialize(self):
        message = {
            "bot_id": self.bot_id,
            "poz_x": self.poz_x,
            "poz_y": self.poz_y,
            "direction": self.direction
        }
        return json.dumps(message)
        # self.head =






