# from swarm_bot_simulator.model.config import PozInfo
import json

import logging
from ast import literal_eval
from json import JSONEncoder
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

# from swarm_bot_simulator.model.board import Board
# import swarm_bot_simulator.controller.information_transfer as it
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import swarm_bot_simulator.controller.information_transfer as it
# from swarm_bot_simulator.model.board import Board
import math
import copy
import threading
from math import cos, sin
from swarm_bot_simulator.model.physical import PhysicalCalculator

class Bot:
    # last_id = 0
    view_range = 1000
    view_cone = 60

    # def __init__(self, bot_info, info_sent_event, config):
    def __init__(self, bot_id, broker, port):
        self.bot_id = str(bot_id)
        # self.communication_settings = config["communication_settings"]
        # self.bot_settings = config["bot_settings"]
        # self.board_settings = config["board_settings"]
        self.bot_settings = None
        self.board_settings = None

        self.config = None
        self.bot_info = None
        self.bot_info_real = None
        self.bot_info_sensor = None
        # self.info_sent_event = info_sent_event
        # self.bot_info_seBotInfo(parsed_bot_info, config.bot_settings)
        # self.bot_info_real = BotInfo(parsed_bot_info, config.bot_settings)

        self.mess_event = threading.Event()
        self.messenger = it.Messenger(name=str(bot_id),
                                      broker=broker,
                                      port=port,
                                      mess_event=self.mess_event)

        # self.messenger.subscribe(self.bot_info.bot_id)
        self.movement = Movement(communication_channel=bot_id, messenger=self.messenger)

        self.lock = threading.Lock()
        self.signal = threading.Condition()
        self.line = 0
        self.line_event = threading.Event()
        self.board = None

        self.hardware = Hardware()
        self.listen_lf = None
        self.board = None
        self.name = "swarm_bot" + str(bot_id)
        # self.bot_info.speed = Vector(0, 0)
        # self.bot_info.acceleration = Vector(0, 0)

        self.start_sensor_threads()

    def start_thread(self):
        t_bot = threading.Thread(target=self.run)
        t_bot.start()

    def run(self):
        self.get_init_info_from_server()
        self.send_ready_to_server()

        self.get_config_from_server()
        self.send_ready_to_server()

        while True:
            self.get_info_from_server()
            self.send_ready_to_server()
            if self.should_continue() is False:
                break

            self.flock()
            self.borders()
            self.move()
            self.update()
            self.send_bot_info_to_server()
            # self.send_board_to_server()

            # self.send_info_to_server()
        # return self.bot_info

    def move(self):
        return
        if self.config["bots"]["is_real"] is True:
            self.orientiate()
        else:
            self.mock_orientiate()
            # self.mock_front()

    def orientiate(self):
        calc = PhysicalCalculator()
        self.bot_info_achieved = calc.calculate(self.bot_info.get_data_to_calc())
        
    def mock_turn(self, dir):
        pass

    def mock_front(self, length):
        pass

    def send_board_to_server(self):
        mes = it.Message(id=self.bot_id, type=it.MTYPE.BOARD, content=self.board)
        self.messenger.send(message=mes)

    def send_bot_info_to_server(self):
        mes = it.Message(id=self.bot_id, type=it.MTYPE.BOT_INFO, content=self.bot_info)
        self.messenger.send(message=mes)

    def send_ready_to_server(self):
        mes = it.Message(id=self.bot_id, type=it.MTYPE.SERVER, content=it.MSERVER.READY)
        self.messenger.send(message=mes)

    def should_continue(self):
        self.mess_event.wait()
        last_message = self.messenger.get_last_message()
        if last_message.type == it.MTYPE.ALGORITHM_COMMAND:
            self.mess_event.clear()
            if last_message.content == it.MALGORITHM_COMMAND.STOP:
                return False
            elif last_message.content == it.MALGORITHM_COMMAND.CONTINUE:
                return True
        # return True

    def get_init_info_from_server(self):
        self.mess_event.wait()
        received = self.messenger.get_last_message()
        if received.type == it.MTYPE.SERVER:
            self.messenger.add_topic_to_send(str(received.content))
            self.mess_event.clear()

    def get_info_from_server(self):
        self.mess_event.wait()
        # bot_info = BotInfo()
        received = self.messenger.get_last_message()
        self.board = received.content
        # x = received.content.bots_info["1"]
        self.set_init_values(received.content.bots_info[str(self.bot_id)])
        self.mess_event.clear()
        # self.messenger.

    def get_config_from_server(self):
        self.mess_event.wait()
        # bot_info = BotInfo()
        received = self.messenger.get_last_message()
        self.set_config_values(received.content)
        # x = received.content.bots_info["1"]

        # self.set_init_values(received.content.bots_info[str(self.bot_id)])
        self.mess_event.clear()

    def set_config_values(self, config):
        self.config = config
        self.bot_settings = config["bot_settings"]
        self.board_settings = config["board_settings"]

    def set_init_values(self, bot_info):
        self.bot_info = copy.deepcopy(bot_info)
        self.bot_info_real = copy.deepcopy(bot_info)
        self.bot_info_sensor = copy.deepcopy(bot_info)

    def pass_line(self):
        self.counter()
        self.line_event.set()

    def counter(self):
        with self.lock:
            self.line = self.line + 1

    def update_board_info(self):
        self.board.bots_info[self.bot_id] = self.bot_info

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
        self.messenger = it.Messenger(name=self.name, communication_settings=self.communication_settings)

    def comm_out(self):
        self.messenger.send(self.bot_info)

    def comm_in(self):
        self.messenger.recieve()

    def update_data(self):
        self.comm_out(self.bot_info.serialize())
        self.board = self.comm_in()

    def designate_coords(self):
        self.update_data()

    # def move(self, vec):
    #     self.bot_info.position.add_vector(vec)
        # self.update_data()

    def calibrate(self):
        pass

    def report_val(self):
        print(str(self))

    def flock(self):
        visible_bots = self.get_visible_bots()

        sep = self.separation(visible_bots)
        # ali = self.alignment(visible_bots)
        coh = self.cohesion(visible_bots)

        sep.mul_scalar(self.config["bot_settings"]["sep_mul"])
        # ali.mul_scalar(self.bot_settings.ali_mul)
        coh.mul_scalar(self.config["bot_settings"]["coh_mul"])

        self.apply_force(sep)
        # self.apply_force(ali)
        self.apply_force(coh)

        self.set_direction()
        self.report_val()

    def separation(self, visible_bots):
        steer = Vector(0, 0)
        for key, bot_info in visible_bots.items():
            dist = self.distance(bot_info)
            steer = self.separation_steer(bot_info, dist, steer, visible_bots)
            print(str(self.bot_info))
            print("distance from bot: " + str(bot_info.bot_id) + " :" + str(self.distance(bot_info)))

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
        if self.bot_settings["separation_distance"] < dist:
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
            steer.mul_scalar(self.bot_settings["max_speed"])
            steer.sub_vector(self.bot_info.speed)
            steer.limit(self.bot_settings["max_force"])

    def points2vector(self, bot_info):
        diff_poz = Point(bot_info.position.x - self.bot_info.position.x,
                         bot_info.position.y - self.bot_info.position.y)
        diff_vec = Vector(diff_poz.x, diff_poz.y)
        return diff_vec

    def cohesion(self, visible_bots):
        steer = Vector(0, 0)
        for key, bot_info in visible_bots.items():
            dist = self.distance(bot_info)
            steer = self.cohesion_steer(bot_info, dist, steer, visible_bots)

        visible_bots_amount = len(visible_bots)
        if visible_bots_amount is not 0:
            steer.div_scalar(len(visible_bots))
        return self.seek(steer)
        # print(str(self.bot_info))
        # print("distance from bot: " + str(bot.bot_info.bot_id) + " :" + str(self.distance(bot)))

        # return Vector(0, 0)

    def cohesion_steer(self, bot, dist, steer, visible_bots):
        if dist > self.bot_settings["cohesion_distance"]:
            return steer

        steer.add_vector(self.points2vector(bot))

        return steer

    def alignment(self, visible_bots):
        steer = Vector(0, 0)
        for key, bot_info in visible_bots.items():
            dist = self.distance(bot_info)
            steer = self.alignment_steer(bot_info, dist, steer, visible_bots)
            print(str(self.bot_info))
            print("distance from bot: " + str(bot_info.bot_id) + " :" + str(self.distance(bot_info)))

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

    def get_visible_bots(self):
        '''
        Function to get all the bots visible in a triangle got by counting the sides
        :type model: Board
        :return:
        '''
        assert isinstance(self.bot_settings["view_mode_is_omni"], bool)
        if self.bot_settings["view_mode_is_omni"] is True:
            all_bots_cp = {bot_info.bot_id: bot_info for key, bot_info in self.board.bots_info.items()
                           if bot_info.bot_id != self.bot_info.bot_id}
            return all_bots_cp

        # visible_bots = []
        # self_point = (self.bot_info.position.x, self.bot_info.position.y)  # self.bot_info.position
        # left_cone_angle = self.bot_info.dir - Bot.view_cone / 2
        # right_cone_angle = self.bot_info.dir + Bot.view_cone / 2
        #
        # side = math.cos(Bot.view_cone / 2) * Bot.view_range
        # left = (math.sin(left_cone_angle) * side, math.cos(left_cone_angle) * side)
        # right = (math.sin(right_cone_angle) * side, math.cos(right_cone_angle) * side)
        # triangle = Polygon([self_point, right, left])
        #
        # for bot in model.all_bots:
        #     if triangle.contains(Point(bot.bot_info.position.x, bot.bot_info.position.y)):
        #         visible_bots.append(bot)

        # return visible_bots

    def distance(self, bot_info):
        return self.bot_info.position.distance(bot_info.position)

    def apply_force(self, sep):
        self.bot_info.acceleration.add_vector(sep)

    def seek(self, vec):
        desired = Vector(0, 0)
        desired.add_vector(vec)
        desired.normalize()
        desired.mul_scalar(self.bot_settings["max_speed"])
        desired.sub_vector(self.bot_info.speed)
        desired.limit(self.bot_settings["max_force"])
        # desired.invert()
        return desired

    def borders(self):
        next_pos = self.bot_info.position + self.bot_info.speed
        if next_pos.in_borders(Vector(self.board_settings["border_x"], self.board_settings["border_y"])) is False:
            self.stop()

    def update(self):
        self.bot_info.acceleration.mul_scalar(1)

        self.bot_info.speed.add_vector(self.bot_info.acceleration)
        self.bot_info.speed.limit(self.bot_settings["max_speed"])
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

    def __init__(self, bot_info_parsed=None):
        if bot_info_parsed is not None:
            self.is_real = bot_info_parsed["is_real"]
            self.bot_id = bot_info_parsed["bot_id"]
            self.dir = float(bot_info_parsed["direction"])
            self.position = Vector(float(bot_info_parsed["poz_x"]), float(bot_info_parsed["poz_y"]))
            self.acceleration = Vector(0, 0)
            self.speed = Vector(bot_info_parsed["speed"][0], bot_info_parsed["speed"][1])
            self.color = bot_info_parsed["color"]
        else:
            self.is_real = None
            self.bot_id = None
            self.dir = None
            self.position = None
            self.acceleration = None
            self.speed = None
            self.color = None

    def from_dict(self, bot_info_dict):
        self.is_real = bot_info_dict["is_real"]
        self.bot_id = bot_info_dict["bot_id"]
        self.dir = bot_info_dict["dir"]

        position = Vector()
        position.list2vector(bot_info_dict["position"])
        self.position = position

        acceleration = Vector()
        acceleration.list2vector(bot_info_dict["acceleration"])
        self.acceleration = acceleration

        speed = Vector()
        speed.list2vector(bot_info_dict["speed"])
        self.speed = speed
        self.color = bot_info_dict["color"]

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
                "position": [o.position.x, o.position.y],
                "speed": [o.speed.x, o.speed.y],
                "acceleration": [o.acceleration.x, o.acceleration.y],
                "color": o.color
            }
        else:
            return json.JSONEncoder.default(self, o)

class Line:
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C

    def turn(self, turn_point, degrees):
        A = self.A
        B = self.B
        C = self.C

        x0 = turn_point[0]
        y0 = turn_point[1]

        x1 = cos(degrees)*x0 - sin(degrees)*y0
        y1 = sin(degrees)*x0 + cos(degrees)*y0


        # theta = math.atan(B/A)
        # beta = theta+degrees
        #
        # p = -C/math.sqrt(A**2 + B**2)
        # pnew = p + x0*(math.cos(beta)-math.cos(theta)) + y0 * (math.sin(beta)-math.sin(theta))
        # x=3


    def get_point_a_length_away_from(self, point, distance):
        xp = point[0]
        yp = point[1]

        r = distance

        A = self.A
        B = self.B
        C = self.C

        if A != 0:
            a = B**2/A**2+1
            b = 2*C*B/A**2+2*B*xp/A-2*yp
            c = C**2/A**2+2*C*xp/A + xp ** 2 + yp ** 2 - r ** 2

            delta = b**2-4*a*c
            y1 = (-b-math.sqrt(delta))/(2*a)
            y2 = (-b+math.sqrt(delta))/(2*a)

            x1 = -(C+B*y1)/A
            x2 = -(C+B*y2)/A

        else:
            a = 1
            b = -2*xp
            c = xp**2 + C**2/B**2 + 2*C/B*yp + yp**2*(C/B+yp)**2+yp**2-r**2

            delta = b ** 2 - 4 * a * c
            x1 = (-b - math.sqrt(delta)) / (2 * a)
            x2 = (-b + math.sqrt(delta)) / (2 * a)

            y1 = y2 = -C/B

        return [(x1, y1), (x2, y2)]

class Vector:
    def __init__(self, *args):
        args = list(args)
        if len(args) == 2:
            self.x = args[0]
            self.y = args[1]
        elif len(args) == 3:
            self.points_direction2vector(args[0], args[1], args[2])
        # self.y = y

    def list2vector(self, vector_list):
        self.x = vector_list[0]
        self.y = vector_list[1]

    def points_direction2vector(self, direction, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        A = y2 - y1
        B = -(x2 - x1)
        C = y1*x2 - x1*y2

        vec = Vector(A, B)

        if Vector.almost_equals(vec.get_angle(), direction, math.pi/2):
            self.set_xy(vec.x, vec.y)
        else:
            vec.invert()
            self.set_xy(vec.x, vec.y)

    def get_perpendicular_line_equation(self, point):
        x = point[0]
        y = point[1]

        A = self.x
        B = self.y
        C = -(A*x + B*y)

        return Line(A, B, C)

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
        """
        Counts the angle between vertical facing vector, and self vector
        :return: returns angle in radians
        """
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

    @staticmethod
    def almost_equals(val1, val2, span):
        if val1 <= val2 + span and val1 >= val2 - span:
            return True

        else:
            return False

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

    def move(self, bot_info: BotInfo, position: Vector, speed: Vector):
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

class Board:
    def __init__(self, config=None):
        if config is not None:
            self.bots_info = {
                bot_info_parsed["bot_id"]: BotInfo(bot_info_parsed=bot_info_parsed) for
                bot_info_parsed in config["bots"]}
        else:
            self.bots_info = None

    def from_dict(self, board_dict):
        bots_info_to_parse = json.loads(board_dict["bots_info"])

        bots_infos_dicts = {key: json.loads(bot_info_to_parse) for key, bot_info_to_parse in bots_info_to_parse.items()}
        self.bots_info = {key: BotInfo() for key, bot_info in bots_info_to_parse.items()}
        for key, bot_info in self.bots_info.items():
            bot_info.from_dict(bots_infos_dicts[key])
        # self.bots_info = {key: empty_bot_infos[key].from_dict(bots_infos_dicts[key]) for key, bot_info in empty_bot_infos.items()}
        # bot_info = BotInfo()
        # bot_info.dict2bot_info(json.loads(x["1"]))
        # self.bots_info = json.load(board_dict["bots_info"])
        # json_loaded = json.loads(self.bots_info)
        # message_dict = literal_eval(self.bots_info)
        #
        # x=3

    def __str__(self):
        # bot_list = [str(bot) for bot in self.all_bots_data]
        return "\n".join(self.__dict__)

    def calibrate(self):
        pass

    def run(self):
        pass
    #
    def calculate_locations_from_bot_data(self):
        pass

class BoardEncoder(JSONEncoder):
    bie = BotInfoEncoder()
    def default(self, o):
        if isinstance(o, Board):
            board = o
            z = board.bots_info.items()
            return {
                "bots_info": json.dumps({bot_info.bot_id: BoardEncoder.bie.encode(bot_info) for key, bot_info
                              in o.bots_info.items()})
            }
        else:
            return json.JSONEncoder.default(self, o)

l = Line(0.0, 1, 0)
print(str(l.get_point_a_length_away_from((0, 0), math.sqrt(1))))
l.turn((0, 0), math.pi/2)