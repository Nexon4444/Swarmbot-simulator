import argparse
import time
# from resources.config import *
from controller.steering_module import Control
# from model.image_analyzer_module import VideoAnalyzer
# config = dict()
# config ["camera_settings"] = {
#     "photo_url": "http://192.168.0.101:8080/shot.jpg"}
# camera = VideoAnalyzer(config)
con = Control(on_robot=True)
parser = argparse.ArgumentParser(description='Swarmbot')
parser.add_argument('-m', '--movement_type', type=str,
                    help='movement type (left-l, right-r, front-f)')

# parser.add_argument('-t', '--time', type=float,
#                     help='movement time')

parser.add_argument('-ds', '--deg_per_sec', type=float,
                    help='deg per sec')

parser.add_argument('-d', '--deg', type=float,
                    help='deg ')

parser.add_argument('-p', '--pwm', type=float,
                    help='pwm signal')

args = parser.parse_args()
t = args.deg/args.deg_per_sec

if args.movement_type is 'f':
    print("moving forward with parameters: pwm - " + str(args.pwm) + " time - " + str(args.time))

if_continue = True
while if_continue:
    # print(str(camera.load_photo_once()))
    start = time.time()
    if args.movement_type is 'f':
        con.forward(t, args.pwm)
    elif args.movement_type is 'l':
        con.lrotate_for(t, args.pwm)
    elif args.movement_type is 'r':
        con.rrotate_for(t, args.pwm)
    end = time.time()
    dif = end - start
    print(("t: " + str(dif)))
    time.sleep(0.5)
    # print(str(camera.load_photo_once()))

    input_value = input("0 - end, 1 - continue")
    if input_value == 0:
        if_continue = False
    elif input_value == 1:
        if_continue = True





