from swarm_bot_simulator.model.simulation.bot_manager_module import *
from swarm_bot_simulator.model.communication.communication_module import *

app_config = None
with open(os.path.join("swarm_bot_simulator", "resources", "app_config.json"), "r", encoding="utf-8") as f:
    app_config = json.load(f)

config = Config(app_config)
board = Board(config)
try:
    # simulator = Simulator(config)
    e = threading.Event()
    bot_info = BotInfo()
    bot_info.from_dict({"is_real": True, "bot_id": "1", "dir": 0, "position": [0, 0], "acceleration": [0, 0], "speed": [1, 1]})
    board = Board(config)

    message = Message("1", MTYPE.BOARD, board)
    # message = Message("1", MTYPE.BOT_INFO, bot_info)
    # sender = mqtt.Client("sender")
    # sender.publish(topic="1/receive", payload="asadasdasdasd")



    server = Messenger(name="server",
                       broker=config.communication_settings.broker,
                       port=config.communication_settings.port,
                       mess_event=e)

    server.add_topic_to_send("1/receive")
    server.send(topic="1/receive", message=message)

    time.sleep(300)

except ConnectionRefusedError as e:
    print("Have you started mosquitto.exe?")
    raise e
