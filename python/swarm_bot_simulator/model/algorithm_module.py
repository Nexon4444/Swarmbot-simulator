# from swarm_bot_simulator.model.config import PozInfo
import json
import logging
import time
from json import JSONEncoder
from swarm_bot_simulator.utilities.util import Vector, VectorEncoder
from swarm_bot_simulator.controller.steering_module import Control
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

# from swarm_bot_simulator.model.board import Board
# import swarm_bot_simulator.controller.information_transfer as it
# from shapely.geometry import Point
import swarm_bot_simulator.model.communication_module as it
# from swarm_bot_simulator.model.board import Board
import math
import copy
import threading
from swarm_bot_simulator.model.simulation_module import PhysicsSimulator

# from swarm_bot_simulator.model.simulation.physical import SimulatedBot

class Commands:
    FORWARD = "FORWARD"
    TURN = "TURN"

class Bot:
    # last_id = 0
    view_range = 1000
    view_cone = 60

    # def __init__(self, bot_info, info_sent_event, config):
    def __init__(self, bot_id, broker, port):
        self.id = str(bot_id)
        # self.communication_settings = config["communication_settings"]
        # self.bot_settings = config["bot_settings"]
        # self.board_settings = config["board_settings"]
        self.bot_settings = None
        self.board_settings = None

        self.physics_simulator = None
        self.config = None
        self.bot_info_aware = None
        self.bot_info_real = None
        self.bot_info_sensor = None
        self.simulated_bot = None
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

        self.control = None
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

        if self.config["simulation_settings"]["simple_commands"] is True:
            self.run_simple()

        else:
            self.run_algorithm_with_communication()

    def run_simple(self):
        for command in self.config["bots"][self.id]["orders"]:
            self.execute_order(command)

    def execute_order(self, order):
        if self.config["bots"][self.id]["is_real"] is True:
            #TODO executing commands for real bots
            pass

        else:
            self.simulate_move(order)

    def simulate_move(self, order):
        if order[0] is Commands.FORWARD:
            self.forward(order)

    def run_algorithm_with_communication(self):
        while True:
            self.get_info_from_server()
            self.get_info_from_sensors()
            self.send_ready_to_server()
            if self.should_continue() is False:
                break

            self.run_flocking_algorithm()
            self.send_bot_info_to_server()

    def run_flocking_algorithm(self):
        self.flock()
        self.borders()
        self.update()

    def send_board_to_server(self):
        mes = it.Message(id=self.id, type=it.MTYPE.BOARD, content=self.board)
        self.messenger.send(message=mes)

    def send_bot_info_to_server(self):
        print("sending bot_info")
        mes = it.Message(id=self.id, type=it.MTYPE.BOT_INFO, content=self.bot_info_aware)
        self.messenger.send(message=mes)
        print("stopped sending bot_info")

    def send_ready_to_server(self):
        # logging.debug("sending ready to server")
        mes = it.Message(id=self.id, type=it.MTYPE.SERVER, content=it.MSERVER.READY)
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

    def get_init_info_from_server(self):
        logging.debug("waiting for init_info from server")
        self.mess_event.wait()
        received = self.messenger.get_last_message()
        logging.debug("received from server: " + str(received))

        logging.debug("received init_info from server")
        self.messenger.add_topic_to_send(str(received.content))
        self.mess_event.clear()

    def get_info_from_server(self):
        self.mess_event.wait()
        # bot_info = BotInfo()
        received = self.messenger.get_last_message()
        if received.type == it.MTYPE.ALGORITHM_COMMAND and received.content == it.MALGORITHM_COMMAND.STOP:
            logging.debug("quiting robot with ID: " + str(self.bot_info_aware.bot_id))
            exit()

        self.board = received.content
        # x = received.content.bots_info["1"]
        self.set_init_values(received.content.bots_info[str(self.id)])
        self.mess_event.clear()
        # self.messenger.

    def get_config_from_server(self):
        self.mess_event.wait()
        # bot_info = BotInfo()
        received = self.messenger.get_last_message()
        while received.type is not it.MTYPE.CONFIG:
            self.mess_event.clear()
            self.mess_event.wait()
            received = self.messenger.get_last_message()

        self.set_config_values(received.content)
        self.mess_event.clear()

    def set_config_values(self, config):
        self.config = config
        self.bot_settings = config["bot_settings"]
        self.board_settings = config["board_settings"]
        self.physics_simulator = PhysicsSimulator(config)
        self.control = Control(bot_id=self.id, config=config)

    def set_init_values(self, bot_info):
        self.bot_info_aware = copy.deepcopy(bot_info)

    def pass_line(self):
        self.counter()
        self.line_event.set()

    def counter(self):
        with self.lock:
            self.line = self.line + 1

    def update_board_info(self):
        self.board.bots_info[self.id] = self.bot_info_aware

    def update_real_data(self):
        # bot_info_list = self.get_sensor_info()
        self.bot_info_aware = self.negotiate(self.bot_info_aware, self.bot_info_sensor)

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
        self.messenger.send(self.bot_info_aware)

    def comm_in(self):
        self.messenger.recieve()

    def update_data(self):
        self.comm_out(self.bot_info_aware.serialize())
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
        ali = self.alignment(visible_bots)
        coh = self.cohesion(visible_bots)

        sep.mul_scalar(self.config["bot_settings"]["sep_mul"])
        ali.mul_scalar(self.config["bot_settings"]["ali_mul"])
        coh.mul_scalar(self.config["bot_settings"]["coh_mul"])

        # print("ID robota:" + str(self.bot_info_aware.bot_id) + "\n"
        #       + "sep: " + str(sep) + "\n"
        #       + "ali: " + str(ali) + "\n"
        #       + "coh: " + str(coh))
        # print("sep: " + str(sep))
        # print("ali: " + str(ali))
        # print("coh: " + str(coh))

        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)

        # self.set_direction()


    def separation(self, visible_bots):
        steer = Vector(0, 0)
        for key, bot_info in visible_bots.items():
            dist = self.distance(bot_info)
            steer = self.separation_steer(bot_info, dist, steer, visible_bots)

        self.correct_separation(steer, visible_bots)

        return steer


    def separation_steer(self, bot, dist, steer, visible_bots):

        if self.bot_settings["separation_distance"] < dist:
            return Vector(0, 0)
        # try:
        max = self.config["bot_settings"]["separation_distance"]

        diff_vec = self.points2vector(bot)
        diff_vec.div_scalar(dist)
        diff_vec.normalize()
        steer.sub_vector(diff_vec)
        steer.mul_scalar((max/dist)**2)
        # except:
        #     raise Exception("Bots cannot take the same position")
        return steer

    def correct_separation(self, steer, visible_bots):
        if len(visible_bots) > 0:
            steer.div_scalar(len(visible_bots))
        if steer.magnitude() > 0:
            steer.normalize()
            steer.mul_scalar(self.bot_settings["max_speed"])
            # steer.sub_vector(self.bot_info_aware.speed)
            # steer.limit(self.bot_settings["max_force"])

    def points2vector(self, bot_info):
        diff_poz = (bot_info.position.x - self.bot_info_aware.position.x,
                         bot_info.position.y - self.bot_info_aware.position.y)
        diff_vec = Vector(diff_poz[0], diff_poz[1])
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

        visible_bot_amount = len(visible_bots)
        if visible_bot_amount is not 0:
            steer.div_scalar(visible_bot_amount)

        return self.correct_alignment(steer, visible_bots)

    def alignment_steer(self, bot_info, dist, steer, visible_bots):
        if dist > self.bot_settings["alignment_distance"]:
            return steer

        steer.add_vector(bot_info.speed)
        return steer

    def correct_alignment(self, steer, visible_bots):
        if len(visible_bots) > 0:
            steer.div_scalar(len(visible_bots))

        steer.normalize()
        steer.mul_scalar(self.bot_settings["max_speed"])
        # steer.sub_vector(self.bot_info_aware.speed)
        # steer.limit(self.bot_settings["max_force"])
        return steer

    def get_single_line_follower(self, line_event):
        while True:
            line_event.wait()
            logging.log(logging.DEBUG, "Sensors reporting robot movement")
            self.control.lf_sensor.add_pulse()
            self.bot_info_sensor.position.x += 1
            line_event.clear()

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
                           if bot_info.bot_id != self.bot_info_aware.bot_id}
            return all_bots_cp
        else:
            # x = 0
            # y = 0
            # max = 0
            # x, y, max = {bot_info.bot_id: bot_info for key, bot_info in self.board.bots_info.items()
            # # Bot.doer((x, y, max))

            all_bots_cp = {bot_info.bot_id: bot_info for key, bot_info in self.board.bots_info.items()
                           if bot_info.bot_id != self.bot_info_aware.bot_id}
            return all_bots_cp

    def distance(self, bot_info):
        return self.bot_info_aware.position.distance(bot_info.position)

    def apply_force(self, sep):
        self.bot_info_aware.acceleration.add_vector(sep)

    def seek(self, vec):
        desired = Vector(0, 0)
        desired.add_vector(vec)
        desired.normalize()
        desired.mul_scalar(self.bot_settings["max_speed"])
        # desired.sub_vector(self.bot_info_aware.speed)
        # desired.limit(self.bot_settings["max_force"])
        # desired.invert()
        return desired

    def borders(self):
        next_pos = self.bot_info_aware.position + self.bot_info_aware.speed + self.bot_info_aware.acceleration
        print("bot_info_aware: " + str(self.bot_info_aware))

        if not next_pos.in_borders(Vector(self.board_settings["border_x"], self.board_settings["border_y"])):
            # self.stop()
            self.bot_info_aware.speed = Vector(0, 0)
            self.bot_info_aware.acceleration = Vector(0, 0)
    def update(self):
        self.bot_info_aware.acceleration.mul_scalar(1)

        self.bot_info_aware.speed.add_vector(self.bot_info_aware.acceleration)
        self.bot_info_aware.speed.limit(self.bot_settings["max_speed"])
        self.move_to_position(self.bot_info_aware, self.bot_info_aware.speed)

        self.bot_info_aware.acceleration.mul_scalar(0)

    def move_to_position(self, bot_info, speed):
        # print("bot_id: " + self.bot_info_aware.bot_id + "\nspeed: " + str(speed))
        speed_angle = math.degrees(self.bot_info_aware.speed.get_angle())
        self.conduct_turn(bot_info, speed_angle)
        self.conduct_forward(bot_info, speed)

    def conduct_forward(self, bot_info, speed):
        t = self.forward(bot_info, speed)
        if bot_info.is_real is True:
            self.control.forward(t, self.config["real_settings"]["pwm_forward"])
            time.sleep(self.config["simulation_settings"]["wait_time"])

    def conduct_turn(self, bot_info, absolute_dir):
        t = self.turn(bot_info, absolute_dir)

        if bot_info.is_real is True:
            self.control.turn(t, self.config["real_settings"]["pwm"])
            time.sleep(self.config["simulation_settings"]["wait_time"])

    def forward(self, bot_info, speed):
        t = self.physics_simulator.count_forward(speed)
        self.physics_simulator.simulate_forward(bot_info, speed)
        return t

    def turn(self, bot_info, absolute_dir):
        t = self.physics_simulator.count_turn(self.calc_relative_turn(bot_info, absolute_dir))
        self.physics_simulator.simulate_turn(bot_info, t)
        # bot_info.dir = math.degrees(absolute_dir)
        return t

    def calc_relative_turn(self, bot_info, absolute_dir):
        if math.fabs(absolute_dir - bot_info.dir) < 180:
            return absolute_dir - bot_info.dir
        else:
            return (absolute_dir - bot_info.dir) - 360

    @staticmethod
    def doer(x):
        return 0

    def stop(self):
        self.bot_info_aware.speed.set_xy(0, 0)

    def __del__(self):
        pass
        # self.listen_lf.join()

    def __str__(self):
        return ("\nbot ID: " + str(self.bot_info_aware.bot_id)
                + "\nposition: " + str(self.bot_info_aware.position)
                + "\nspeed: " + str(self.bot_info_aware.speed)
                + "\naccel: " + str(self.bot_info_aware.acceleration)
                + "\ndir: " + str(self.bot_info_aware.dir))

    def get_info_from_sensors(self):
        pass

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


class MovementData:
    def __init__(self, poz, direction, time, command):
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

    def move(self, bot_info, position, speed):
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
        return "\n".join([str(bot_info) for key, bot_info in self.bots_info.items()])

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

