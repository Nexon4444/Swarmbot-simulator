# from swarm_bot_simulator.model.config import PozInfo
import json

import logging
from json import JSONEncoder
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

# from swarm_bot_simulator.model.board import Board
# from swarm_bot_simulator.controller.information_transfer import Messenger
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from swarm_bot_simulator.controller.information_transfer import *
# from swarm_bot_simulator.model.board import Board
import math
import copy
import threading

class Bot:
    # last_id = 0
    view_range = 1000
    view_cone = 60

    def __init__(self, bot_info, config):
        self.communication_settings = config.communication_settings
        self.bot_settings = config.bot_settings
        self.board_settings = config.board_settings
        self.bot_info = copy.deepcopy(bot_info)
        self.bot_info_real = copy.deepcopy(bot_info)
        self.bot_info_sensor = copy.deepcopy(bot_info)
        self.config = config
        # self.bot_info_seBotInfo(parsed_bot_info, config.bot_settings)
        # self.bot_info_real = BotInfo(parsed_bot_info, config.bot_settings)

        self.mess_event = threading.Event()
        self.messenger = Messenger(name=str(self.bot_info.bot_id), config=config,
                                   mess_event=self.mess_event)

        # self.messenger.subscribe(self.bot_info.bot_id)
        self.movement = Movement(communication_channel=self.bot_info.bot_id, messenger=self.messenger)

        self.lock = threading.Lock()
        self.signal = threading.Condition()
        self.line = 0
        self.line_event = threading.Event()
        self.board = None
        self.hardware = Hardware()
        self.listen_lf = None
        # self.model = model
        self.name = "swarm_bot" + str(self.bot_info.bot_id)
        # self.bot_info.speed = Vector(0, 0)
        # self.bot_info.acceleration = Vector(0, 0)

        self.start_sensor_threads()

    def pass_line(self):
        self.counter()
        self.line_event.set()

    def counter(self):
        with self.lock:
            self.line = self.line + 1

    def update_board_info(self, board):
        self.board = board

    def update_real_data(self):
        # bot_info_list = self.get_sensor_info()
        self.bot_info = self.negotiate(self.bot_info, self.bot_info_sensor)

    def negotiate(self, bot_info, bot_real):
        bot_info.position.x = bot_real.position.x
        return bot_info

    def start_sensor_threads(self):
        self.listen_lf = threading.Thread(target=self.get_single_line_follower, args=[self.line_event])
        self.listen_lf.start()

    def get_sensor_info(self):
        BotInfo = self.get_single_line_follower()
        return BotInfo()

    def initialize_comm(self):
        # topic_name = "swarm_bot" + str(self.bot_info.bot_id)
        self.messenger = Messenger(name=self.name, communication_settings=self.communication_settings)

    def comm_out(self):
        self.messenger.send(self.bot_info)

    def comm_in(self):
        self.messenger.recieve()

    def update_data(self):
        self.comm_out(self.bot_info.serialize())
        self.model = self.comm_in()

    def designate_coords(self):
        self.update_data()

    def move(self, vec):
        self.bot_info.position.add_vector(vec)
        # self.update_data()

    def calibrate(self):
        pass

    def report_val(self):
        print(str(self))

    def flock(self):
        visible_bots = self.get_visible_bots(self.board)

        sep = self.separation(visible_bots)
        # ali = self.alignment(visible_bots)
        coh = self.cohesion(visible_bots)

        sep.mul_scalar(self.config.bot_settings.sep_mul)
        # ali.mul_scalar(self.bot_settings.ali_mul)
        coh.mul_scalar(self.config.bot_settings.coh_mul)

        self.apply_force(sep)
        # self.apply_force(ali)
        self.apply_force(coh)

        self.set_direction()
        self.report_val()

    def separation(self, visible_bots):
        steer = Vector(0, 0)
        for bot in visible_bots:
            dist = self.distance(bot)
            steer = self.separation_steer(bot, dist, steer, visible_bots)
            print(str(self.bot_info))
            print("distance from bot: " + str(bot.bot_info.bot_id) + " :" + str(self.distance(bot)))

        self.correct_separation(steer, visible_bots)
        # steer.invert()
        print("steer" + str(steer))
        return steer
        # if steer.magnitude() > 0:
        #     steer.normalize()
        #     steer.

    def separation_steer(self, bot, dist, steer, visible_bots):
        # self.distance()
        # diff = Vector2(0, 0)
        if self.bot_settings.separation_distance < dist:
            return Vector(0, 0)

        diff_vec = self.points2vector(bot)
        diff_vec.div_scalar(dist)
        diff_vec.normalize()
        steer.sub_vector(diff_vec)

        # print("diff: " + str(diff_vec))
        return steer

    def correct_separation(self, steer, visible_bots):
        if len(visible_bots) > 0:
            steer.div_scalar(len(visible_bots))
        if steer.magnitude() > 0:
            steer.normalize()
            steer.mul_scalar(self.bot_settings.max_speed)
            steer.sub_vector(self.bot_info.speed)
            steer.limit(self.bot_settings.max_force)

    def points2vector(self, bot):
        diff_poz = Point(bot.bot_info.position.x - self.bot_info.position.x,
                         bot.bot_info.position.y - self.bot_info.position.y)
        diff_vec = Vector(diff_poz.x, diff_poz.y)
        return diff_vec

    def cohesion(self, visible_bots):
        steer = Vector(0, 0)
        for bot in visible_bots:
            dist = self.distance(bot)
            steer = self.cohesion_steer(bot, dist, steer, visible_bots)

        visible_bots_amount = len(visible_bots)
        if visible_bots_amount is not 0:
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

    def alignment(self, visible_bots):
        steer = Vector(0, 0)
        for bot in visible_bots:
            dist = self.distance(bot)
            steer = self.alignment_steer(bot, dist, steer, visible_bots)
            print(str(self.bot_info))
            print("distance from bot: " + str(bot.bot_info.bot_id) + " :" + str(self.distance(bot)))

        visible_bot_amount = len(visible_bots)
        if visible_bot_amount is not 0:
            steer.div_scalar(visible_bot_amount)

        return self.correct_alignment(steer, visible_bots)

    def alignment_steer(self, bot, dist, steer, visible_bots):
        if dist > self.bot_settings.alignment_distance:
            return steer

        steer.add_vector(bot.bot_info.speed)
        return steer

    def correct_alignment(self, steer, visible_bots):
        if len(visible_bots) > 0:
            steer.div_scalar(len(visible_bots))

        steer.normalize()
        steer.mul_scalar(self.bot_settings.max_speed)
        steer.sub_vector(self.bot_info.speed)
        steer.limit(self.bot_settings.max_force)
        return steer

    def get_single_line_follower(self, line_event):
        while True:
            line_event.wait()
            logging.log(logging.DEBUG, "Sensors reporting robot movement")
            self.hardware.lf_sensor.add_pulse()
            self.bot_info_sensor.position.x += 1
            line_event.clear()
        # return next_bot_real

        # next_bot_real = copy.deepcopy(self.bot_real)
        # next_bot_real.position.x += 1
        # return next_bot_real

    def get_model_info(self):
        pass

    def get_other_bots_info(self):
        if self.communication_settings.method is "direct":
            return self.get_sensor_info()
        else:
            return self.get_model_info()

    def get_visible_bots(self, model):
        '''
        Function to get all the bots visible in a triangle got by counting the sides
        :type model: Board
        :return:
        '''
        assert isinstance(self.bot_settings.view_is_omni, bool)
        if self.bot_settings.view_is_omni is True:
            all_bots_cp = {bot_info.bot_id: bot_info for key, bot_info in model.bots_info.items() if bot_info.bot_id != self.bot_info.bot_id}
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

    def apply_force(self, sep):
        self.bot_info.acceleration.add_vector(sep)

    def seek(self, vec):
        desired = Vector(0, 0)
        desired.add_vector(vec)
        desired.normalize()
        desired.mul_scalar(self.bot_settings.max_speed)
        desired.sub_vector(self.bot_info.speed)
        desired.limit(self.bot_settings.max_force)
        # desired.invert()
        return desired

    def run(self):
        self.flock()
        self.borders()
        return self.bot_info

    def borders(self):
        next_pos = self.bot_info.position + self.bot_info.speed
        if next_pos.in_borders(Vector(self.board_settings.border_x, self.board_settings.border_y)) is False:
            self.stop()

    def update(self):
        self.bot_info.acceleration.mul_scalar(1)

        self.bot_info.speed.add_vector(self.bot_info.acceleration)
        self.bot_info.speed.limit(self.bot_settings.max_speed)
        self.bot_info.position.add_vector(self.bot_info.speed)
        self.bot_info.acceleration.mul_scalar(0)

    def set_direction(self):
        self.bot_info.dir = math.degrees(self.bot_info.speed.get_angle())

    def stop(self):
        self.bot_info.speed.set_xy(0, 0)

    def __del__(self):
        pass
        # self.listen_lf.join()

    def __str__(self):
        return ("\nbot ID: " + str(self.bot_info.bot_id)
                + "\nposition: " + str(self.bot_info.position)
                + "\nspeed: " + str(self.bot_info.speed)
                + "\naccel: " + str(self.bot_info.acceleration)
                + "\ndir: " + str(self.bot_info.dir))

class BotInfo:
    size_x = 20
    size_y = 20

    def __init__(self, bot_info_parsed, config):
        self.is_real = bot_info_parsed.is_real
        self.bot_id = bot_info_parsed.bot_id
        self.dir = float(bot_info_parsed.direction)
        self.position = Vector(float(bot_info_parsed.poz_x), float(bot_info_parsed.poz_y))
        self.acceleration = Vector(0, 0)

        speed_vec = Vector(bot_info_parsed.speed[0], bot_info_parsed.speed[1])

        if bot_info_parsed.speed[0] > config.bot_settings.max_speed:
            speed_vec.x = config.bot_settings.max_speed

        if bot_info_parsed.speed[1] > config.bot_settings.max_speed:
            speed_vec.y = config.bot_settings.max_speed

        self.speed = Vector(speed_vec.x, speed_vec.y)

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

class BotInfoEncoder(JSONEncoder):
    def default(self, o):
        ve = VectorEncoder()
        if isinstance(o, BotInfo):
            return {
                "is_real": o.is_real,
                "bot_id": o.bot_id,
                "dir": o.dir,
                "position": ve.encode(o.position),
                "acceleration": ve.encode(o.acceleration)
            }
        else:
            return json.JSONEncoder.default(self, o)
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
        else:
            self.x = 0
            self.y = 0

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

        if size is 0:
            return

        if size > max:
            self.x = self.x / size
            self.y = self.y / size

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def get_angle(self):
        return math.atan2(self.x, self.y)

    def sub2Vector(self, vec1, vec2):
        return Vector(vec1.x - vec2.x, vec1.y - vec2.y)

    def distance(self, vec):
        return math.sqrt(math.pow(vec.x - self.x, 2) + math.pow(vec.y - self.y, 2))

    def in_borders(self, border):
        if self.x < 0:
            return False
        elif self.y < 0:
            return False
        elif self.x > border.x:
            return False
        elif self.y > border.y:
            return False
        else:
            return True

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __str__(self):
        return '[' + str(self.x) + ", " + str(self.y) + ']'

    # def __default(self):
    #     return self.__dict__

class VectorEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Vector):
            return [o.x, o.y]
        else:
            return json.JSONEncoder.default(self, o)
class MovementData:
    def __init__(self, poz: Vector, direction: float, time: float, command: str):
        self.poz = poz
        self.direction = direction
        self.time = time
        self.command = command

class MovementDataEncoder(JSONEncoder):
    ve = VectorEncoder()
    def default(self, o):
        if isinstance(o, MovementData):
            return {
                'poz': MovementDataEncoder.ve.encode(o.poz),
                'dir': o.direction,
                'time': o.time,
                'command': o.command
            }
        else:
            return json.JSONEncoder.default(self, o)

class Movement:
    MOVE_PRIM = "forward"
    encoder = MovementDataEncoder()

    def __init__(self, communication_channel, messenger):
        self.communication_channel = str(communication_channel)
        self.messenger = messenger

    def move_prim(self, time):
        md = MovementData(poz=Vector(None, None), direction=0.0, time=time, command=Movement.MOVE_PRIM)
        encoded_message = Movement.encoder.encode(md)
        self.messenger.send(topic=self.communication_channel, message=encoded_message)

    def turn_prim(self, time):
        self.messenger.send(MovementDataEncoder.encode(MovementData(poz=None, direction=None, time=time, command="turn_prim")))

    def move(self, bot_info : BotInfo, position: Vector, speed: Vector):
        pass

    def face_direction(self):
        pass

class Hardware:
    def __init__(self):
        self.lf_sensor = LFSensor()

    def get_lf_sensor(self):
        return self.lf_sensor

class LFSensor:
    def __init__(self):
        self.current = 0
        self.lf_sensor_no_pulses = 0
        self.lock = threading.Lock()

    def add_pulse(self):
        with self.lock:
            self.lf_sensor_no_pulses += 1


