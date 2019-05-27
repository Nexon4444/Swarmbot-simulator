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
    message = Message(MTYPE.SIMPLE, MovementData(Vector(0, 1), 90.0, 3, Movement.MOVE_PRIM))

    server = Messenger("server", config, e)
    server.add_topic_to_send("1/receive")
    server.send(message=message)

    time.sleep(300)

except ConnectionRefusedError as e:
    print("Have you started mosquitto.exe?")
    raise e
