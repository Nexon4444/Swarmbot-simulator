# from swarm_bot_simulator.model.config import PozInfo
import json
from swarm_bot_simulator.model.board import Board
from swarm_bot_simulator.controller.information_transfer import Messenger
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from vectormath import Vector2

import math


class Bot:
    # last_id = 0
    view_range = 1000
    view_cone = 60

    def __init__(self, parsed_bot_info, communication_settings, bot_settings):
        self.bot_info = BotInfo(parsed_bot_info)
        self.board = None
        # self.model = model
        self.name = "swarm_bot" + str(self.bot_info.bot_id)
        # self.bot_info.speed = Vector(0, 0)
        # self.bot_info.acceleration = Vector(0, 0)
        self.communication_settings = communication_settings
        self.bot_settings = bot_settings
        self.messenger = None

    def update_board_info(self, board: Board):
        self.board = board

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
        self.bot_info.poz_x = self.bot_info.poz_x + distance
        self.update_data()

    def calibrate(self):
        pass

    def flock(self):
        visible_bots = self.get_visible_bots(self.board)
        # sep = self.separation(visible_bots)
        # ali = self.alignment(visible_bots)
        coh = self.cohesion(visible_bots)

        # self.applyForce(sep)
        # self.applyForce(ali)
        self.applyForce(coh)
        self.report_val()

    def report_val(self):
        print("position: " + str(self.bot_info.position))
        print("speed: " + str(self.bot_info.speed))
        print("accl: " + str(self.bot_info.acceleration))

    def separation(self, visible_bots):
        steer = Vector(0, 0)
        for bot in visible_bots:
            dist = self.distance(bot)
            steer = self.separation_steer(bot, dist, steer, visible_bots)
            print(str(self.bot_info))
            print("distance from bot: " + str(bot.bot_info.bot_id) + " :" + str(self.distance(bot)))

        self.correct_steering(steer, visible_bots)
        steer.invert()
        print(steer)
        return steer
        # if steer.magnitude() > 0:
        #     steer.normalize()
        #     steer.

    def separation_steer(self, bot, dist, steer, visible_bots):
        # self.distance()
        # diff = Vector2(0, 0)
        if self.bot_settings.separation_distance > dist:
            return Vector(0, 0)

        diff_vec = self.points2vector(bot)
        diff_vec.div_scalar(dist)
        diff_vec.normalize()
        steer.add_vector(diff_vec)

        # print("diff: " + str(diff_vec))
        return steer

    def points2vector(self, bot):
        diff_poz = Point(bot.bot_info.position.x - self.bot_info.position.x,
                         bot.bot_info.position.y - self.bot_info.position.y)
        diff_vec = Vector(diff_poz.x, diff_poz.y)
        return diff_vec

    def correct_steering(self, steer, visible_bots):
        if len(visible_bots) > 0:
            steer.div_scalar(len(visible_bots))
        if steer.magnitude() > 0:
            steer.normalize()
            steer.mul_scalar(self.bot_settings.max_speed)
            steer.sub_vector(self.bot_info.speed)
            steer.limit(self.bot_settings.max_force)

    def alignment(self, visible_bots):
        return Vector(0, 0)

    def cohesion(self, visible_bots):
        steer = Vector(0, 0)
        for bot in visible_bots:
            dist = self.distance(bot)
            steer = self.cohesion_steer(bot, dist, steer, visible_bots)

        steer.div_scalar(len(visible_bots))
        return self.seek(steer)
            # print(str(self.bot_info))
            # print("distance from bot: " + str(bot.bot_info.bot_id) + " :" + str(self.distance(bot)))

        # return Vector(0, 0)

    def cohesion_steer(self, bot, dist, steer, visible_bots):
        if dist > self.bot_settings.cohesion_distance:
            return steer

        steer.add_vector(self.points2vector(bot))
        return steer

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
        if self.bot_settings.view_is_omni is True:
            all_bots_cp = model.all_bots[:]
            all_bots_cp.remove(self)
            return all_bots_cp

        visible_bots = []
        self_point = (self.bot_info.position.x, self.bot_info.position.y)  # self.bot_info.position
        left_cone_angle = self.bot_info.dir - Bot.view_cone / 2
        right_cone_angle = self.bot_info.dir + Bot.view_cone / 2

        side = math.cos(Bot.view_cone / 2) * Bot.view_range
        left = (math.sin(left_cone_angle) * side, math.cos(left_cone_angle) * side)
        right = (math.sin(right_cone_angle) * side, math.cos(right_cone_angle) * side)
        triangle = Polygon([self_point, right, left])

        for bot in model.all_bots:
            if triangle.contains(Point(bot.bot_info.position.x, bot.bot_info.position.y)):
                visible_bots.append(bot)

        return visible_bots

    def distance(self, bot):
        return self.bot_info.position.distance(bot.bot_info.position)

    def allignement(self):
        pass

    def applyForce(self, sep):
        self.bot_info.acceleration.add_vector(sep)

    def seek(self, vec):
        desired = Vector(0, 0)
        desired.sub_vector(vec)
        desired.normalize()
        desired.mul_scalar(self.bot_settings.max_speed)
        desired.sub_vector(self.bot_info.speed)
        desired.limit(self.bot_settings.max_force)
        return desired

    def run(self):
        self.flock()
        self.update()
        self.borders()

    def update(self):
        self.bot_info.acceleration.mul_scalar(.4)
        
        self.bot_info.speed.add_vector(self.bot_info.acceleration)
        self.bot_info.speed.limit(self.bot_settings.max_speed)
        self.bot_info.position.add_vector(self.bot_info.speed)
        self.bot_info.acceleration.mul_scalar(0)

    def borders(self):
        pass


class BotInfo:
    size_x = 20
    size_y = 20

    def __init__(self, bot_info_parsed):
        self.bot_id = bot_info_parsed["bot_id"]
        self.dir = float(bot_info_parsed["direction"])
        self.position = Vector(float(bot_info_parsed["poz_x"]), float(bot_info_parsed["poz_y"]))
        self.acceleration = Vector(0, 0)
        self.speed = Vector(0, 0)

    def serialize(self):
        message = {
            "bot_id": self.bot_id,
            "poz_x": self.position.x,
            "poz_y": self.position.y,
            "direction": self.dir
        }
        return json.dumps(message)

    def __str__(self):
        return str("bot id: ") + str(self.bot_id) + "\n" + str("position: ") + str(
            self.position) + "\ndirection: " + str(self.dir)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # self.y = y

    def div_scalar(self, scalar):
        self.x = self.x / scalar
        self.y = self.y / scalar
        # , self.vec.y / scalar)

    def add_vector(self, vec):
        self.x = self.x + vec.x
        self.y = self.y + vec.y

    def normalize(self):
        m = self.magnitude()

        if m > 0:
            self.x = self.x / m
            self.y = self.y / m
        # else:
        #     return Vector2(self.vec.x, self.vec.y)

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    # def size(self):

    def mul_vector(self, vec):
        self.x = self.x * vec.x
        self.y = self.y * vec.y

    def mul_scalar(self, scalar):
        self.x = self.x * scalar
        self.y = self.y * scalar

    def invert(self):
        self.x = -self.x
        self.y = -self.y

    def sub_vector(self, vec):
        self.x = self.x - vec.x
        self.y = self.y - vec.y

    def limit(self, max):
        size = self.magnitude()

        if size > max:
            self.x = self.x / size
            self.y = self.y / size

    def get_angle(self):
        return math.atan2(self.x, self.y)

    def sub2Vector(self, vec1, vec2):
        return Vector(vec1.x-vec2.x, vec1.y-vec2.y)

    def distance(self, vec):
        return math.sqrt(math.pow(vec.x-self.x, 2) + math.pow(vec.y-self.y, 2))

    def __str__(self):
        return '[' + str(self.x) + ", " + str(self.y) + ']'
