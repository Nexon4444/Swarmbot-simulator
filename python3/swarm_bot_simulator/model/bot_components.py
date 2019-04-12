# from swarm_bot_simulator.model.config import PozInfo
import json
from swarm_bot_simulator.model.board import Board
from swarm_bot_simulator.controller.information_transfer import Messenger
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import math

class Bot:
    # last_id = 0
    view_range = 30
    view_cone = 60
    def __init__(self, parsed_bot_info, communication_settings, bot_settings):
        self.bot_info = BotInfo(parsed_bot_info)
        # self.model = model
        self.name = "swarm_bot" + str(self.bot_info.bot_id)
        self.acceleration = 0
        self.communication_settings = communication_settings
        self.bot_settings = bot_settings
        self.messenger = None

    def initialize_comm(self):
        # topic_name = "swarm_bot" + str(self.bot_info.bot_id)
        self.messenger = Messenger(name=self.name, communication_settings=self.communication_settings)

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

    def think(self):
        pass

    def separation(self):
        pass

    def cohesion(self):
        pass

    def alignment(self):
        pass

    def get_other_bots_info(self):
        if self.communication_settings.method is "direct":
            return self.get_sensor_info()
        else:
            return self.get_model_info()

    def get_sensor_info(self):
        pass

    def get_model_info(self):
        pass

    def get_visible_bots(self, model: Board):
        '''
        Function to get all the bots visible in a triangle got by counting the sides
        :return:
        '''
        assert isinstance(self.bot_settings.view_is_omni, bool)
        if self.bot_settings.view_is_omni is False:
            return model.all_bots

        visible_bots = []
        self_point = Point(self.bot_info.poz_x, self.bot_info.poz_y)
        left_cone_angle = self.bot_info.dir - Bot.view_cone/2
        right_cone_angle = self.bot_info.dir + Bot.view_cone/2

        side = math.cos(Bot.view_cone/2) * Bot.view_range
        left = (math.sin(left_cone_angle)*side, math.cos(left_cone_angle)*side)
        right = (math.sin(right_cone_angle)*side, math.cos(right_cone_angle)*side)
        triangle = Polygon([self_point, right, left])
        for bot in model.all_bots:
            if triangle.contains((bot.bot_info.poz_x, bot.bot_info.poz_y)):
                visible_bots.append(bot)

        return visible_bots



class BotInfo:
    size_x = 20
    size_y = 20

    def __init__(self, bot_info_parsed):
        self.bot_id = bot_info_parsed["bot_id"]
        self.poz_x = float(bot_info_parsed["poz_x"])
        self.poz_y = float(bot_info_parsed["poz_y"])
        self.dir = float(bot_info_parsed["direction"])

    def serialize(self):
        message = {
            "bot_id": self.bot_id,
            "poz_x": self.poz_x,
            "poz_y": self.poz_y,
            "direction": self.dir
        }
        return json.dumps(message)