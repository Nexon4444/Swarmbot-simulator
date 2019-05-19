from swarm_bot_simulator.controller.simulator import *
from swarm_bot_simulator.controller.information_transfer import *
from swarm_bot_simulator.model.config import *

app_config = None
with open(os.path.join("swarm_bot_simulator", "resources", "app_config.json"), "r", encoding="utf-8") as f:
    app_config = json.load(f)

config = Config(app_config)
board = Board(config)
try:
    simulator = Simulator(config)
    e = threading.Event()
    # message = Message(MTYPE.SIMPLE, MovementData(Vector(0, 1), 90.0, 1, Movement.MOVE_PRIM))
    message_measure_line = Message(MTYPE.MACRO, "test")
    server = Messenger("server", config.communication_settings.broker, config.communication_settings.port, e)
    mess1 = Messenger("1", config.communication_settings.broker, config.communication_settings.port, e)

    server.add_client("1/receive")
    server.send(message=message_measure_line)
    time.sleep(2)
    print(str(mess1.get_last_message()))
    time.sleep(300)

except ConnectionRefusedError as e:
    print("Have you started mosquitto.exe?")
    raise e
