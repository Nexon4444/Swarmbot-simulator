# from controller.physical_bot import Physical_bot
import os

from model.bot_components import Bot
from model.config import *
import argparse
import time
from model.config import *
parser = argparse.ArgumentParser(description='Swarmbot')
parser.add_argument('-id', '--bot_id', type=int,
                    help='id of the bot on  which we are launching the configuration')

parser.add_argument('-b', '--broker', type=str,
                    help='broker ip address')

parser.add_argument('-p', '--port', type=int,
                    help='broker port')

parser.add_argument('-o', '--on_bot', type=int,
                    help='is program on bot?')

args = parser.parse_args()

if args.on_bot == 1:
    on_bot = True
else:
    on_bot = False

communication_settings = {
    "bot_id": args.bot_id,
    "broker": args.broker,
    "port": args.port,
    "mock": True,
    "method_is_direct": False
}

bot_settings = {
    "mode": "1lf",
    "view_mode_is_omni": True,
    "separation_distance": 100,
    "cohesion_distance": 200,
    "alignment_distance": 200,
    "sep_mul": 4.5,
    "ali_mul": 2.0,
    "coh_mul": 1.0,
    "max_speed": 5,
    "max_force": 1
}

board_settings = {
    "border_x": 2,
    "border_y": 2,
    "side": 20
}

bot_info = {
    "is_real": True,
    "bot_id": str(args.bot_id),
    "direction": 0,
    "speed": [0, 0],
    "poz_x": 0,
    "poz_y": 0,
    "on_robot": on_bot

}

bots = [
    bot_info
    ]

sensor_settings = {
    "1lf": {
        "min_impulse_time": 0.5
    }
}

config = {
    "communication_settings": communication_settings,
    "bot_settings": bot_settings,
    "board_settings": board_settings,
    "sensor_settings": sensor_settings,
    # "view_settings"
    "bots": bots
}

# config = Config(config)
# swarm_bot = Physical_bot(config)
# mess = Messenger(1, broker=args.broker, port=args.port)
# swarm_bot.start_communication()
print("attempt to analyze")
swarm_bot = Bot(bot_id=args.bot_id, config=config)
swarm_bot.run()

# Bot.swarm_bot.start_communication()
# swarm_bot.analyze_sensor_data()

time.sleep(10)
# print (str(swarm_bot.messenger.get_last_message()))


