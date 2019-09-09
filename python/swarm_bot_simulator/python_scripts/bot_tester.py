import argparse
import time
from swarm_bot_simulator.resources.config import *
from swarm_bot_simulator.controller.steering_module import Control
from swarm_bot_simulator.model.image_analyzer_module import VideoAnalyzer

camera = VideoAnalyzer(config)
con = Control()
parser = argparse.ArgumentParser(description='Swarmbot')
parser.add_argument('-m', '--movement_type', type=str,
                    help='movement type (left-l, right-r, front-f)')

parser.add_argument('-t', '--time', type=float,
                    help='movement time')

parser.add_argument('-p', '--pwm', type=float,
                    help='pwm signal')

args = parser.parse_args()

if args.movement_type is 'f':
    print ("moving forward with parameters: pwm - " + str(args.pwm) + " time - " + str(args.time))

if_continue = True
while if_continue:
    print(str(camera.load_photo()))
    start = time.time()
    if args.movement_type is 'f':
        con.forward(args.time, args.pwm)
    elif args.movement_type is 'l':
        con.lrotate_for(args.time, args.pwm)
    elif args.movement_type is 'r':
        con.rrotate_for(args.time, args.pwm)
    end = time.time()
    dif = end - start
    print(("t: " + dif))
    print(str(camera.load_photo()))

    input_value = input("0 - end, 1 - continue")
    if input_value == 0:
        if_continue = False
    elif input_value == 1:
        if_continue = True





