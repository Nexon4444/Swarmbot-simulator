from swarm_bot_simulator.model.simulation.simulator import *
from swarm_bot_simulator.model.communication.information_transfer import *

app_config = None
# python3/swarm_bot_simulator/resources/app_config.json
with open(os.path.join("swarm_bot_simulator", "resources", "app_config.json"), "r", encoding="utf-8") as f:
    app_config = json.load(f)

print(app_config)
config = Config(app_config)
# config.swarm_bots[0].messenger.subscribe(topic="test") #, message="test dzialaj")
# config.swarm_bots[0].movement.move_prim(5)
board = Board(config)
try:
    simulator = Simulator(config)
    e = threading.Event()
    mess = Messenger(1, config, e)
    # mess.listen()
    # time.sleep(5)
    # simulator.communicate(BotInfo(bot_info_parsed=config.bot_infos[0], config=config), board)
    # board = json.loads(mess.last_message)
    # print(str(mess.last_message))
    # time.sleep(3)

    print(str(Messenger.create_message_from_string(mess.receiver.last_message)))
    # simulator.simulate()

except ConnectionRefusedError as e:
    print("Have you started mosquitto.exe?")
    raise e
