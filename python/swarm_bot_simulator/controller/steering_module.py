import math
import os
import sys
if os.name is not 'nt' and sys.version_info[0] < 3:
    import mraa
import time
import threading
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )
if sys.version_info[0] > 2:
    from queue import Queue
else:
    from Queue import Queue

class Control(object):
    sensor_1lf = 45

    def __init__(self, bot_id=None, sensor_event_1lf=None, config=None, on_robot=False):
        # on_robot = False
        if bot_id is not None:
            for bot in config["bots"]:
                if bot["bot_id"] == bot_id and bot["is_real"]:
                    on_robot = True

        if on_robot is True:
            mraa.pwma = mraa.Pwm(20)
            mraa.pwma.period_us(1000)
            mraa.pwma.enable(True)

            mraa.pwmb = mraa.Pwm(14)
            mraa.pwmb.period_us(1000)
            mraa.pwmb.enable(True)

            mraa.a1 = mraa.Gpio(33)
            mraa.a1.dir(mraa.DIR_OUT)
            mraa.a2 = mraa.Gpio(46)
            mraa.a2.dir(mraa.DIR_OUT)

            mraa.b1 = mraa.Gpio(48)
            mraa.b1.dir(mraa.DIR_OUT)
            mraa.b2 = mraa.Gpio(36)
            mraa.b2.dir(mraa.DIR_OUT)

            mraa.pwma.write(0)
            mraa.pwmb.write(0)
            mraa.a1.write(0)
            mraa.b1.write(0)
            mraa.a2.write(0)
            mraa.b2.write(0)

        if sensor_event_1lf is not None:
            self.sensor_event_1lf = sensor_event_1lf
            self.sensors_dict = {
                "1lf": Sensor(Control.sensor_1lf, self.sensor_event_1lf, config=config)
            }

    def turn(self, time, pwm):
        if time < 0:
            self.lrotate_for(math.fabs(time), pwm)
        else:
            self.rrotate_for(time, pwm)


    def move(self, xpa, xpb, xa1, xa2, xb1, xb2, t):
        # time.sleep(0.1)
        print ("moving motors")
        pwma = mraa.pwma.read()
        pwmb = mraa.pwmb.read()
        a1 = mraa.a1.read()
        b1 = mraa.b1.read()
        a2 = mraa.a2.read()
        b2 = mraa.b2.read()

        print ("before:\n" +
               "pwma: " + str(pwma) +
               " pwmb: " + str(pwmb) +
               " a1: " + str(a1) +
               " b1: " + str(b1) +
               " a2: " + str(a2) +
               " b2: " + str(b2))

        mraa.pwma.write(xpa)
        mraa.pwmb.write(xpb)
        mraa.a1.write(xa1)
        mraa.b1.write(xb1)
        mraa.a2.write(xa2)
        mraa.b2.write(xb2)

        print ("after:\n" +
               " pwma: " + str(pwma) +
               " pwmb: " + str(pwmb) +
               " a1: " + str(a1) +
               " b1: " + str(b1) +
               " a2: " + str(a2) +
               " b2: " + str(b2))

        logging.debug("t: " + str(t))
        time.sleep(t)
        mraa.a1.write(0)
        mraa.b1.write(0)
        mraa.a2.write(0)
        mraa.b2.write(0)
        mraa.pwma.write(0)
        mraa.pwma.write(0)
        # time.sleep(0.1)

    def forward(self, tide, pwm):
        print("driving forward for: " + str(tide) + " with speed: " + str(pwm))
        self.move(pwm, pwm, 1, 0, 1, 0, tide)

    def back(self, tide):
        print("driving back")
        self.move(1, 1, 0, 1, 0, 1, tide)

    def lrotate(self, tide):

        print("lrotating: " + str(tide))
        self.move(1, 1, 0, 1, 1, 0, float(tide))

    def rrotate(self, tide):
        print("rrotating")
        self.move(1, 1, 1, 0, 0, 1, tide)

    def lturn(self, tide):
        print("lturning")
        self.move(0.5, 1, 1, 0, 1, 0, tide)

    def rturn(self, tide):
        print ("rturning")
        self.move(1, 0.5, 1, 0, 1, 0, tide)

    def movement_front_until_event(self, e):
        # print "q: " + str(q.get())
        logging.log(logging.DEBUG, "before wait")
        self.forward_nonstop()
        e.wait()
        self.stop()
        logging.log(logging.DEBUG, "after stop")

    # def get_sensor_info(self, e, switching_to, sensor_pin_id):
    #     # e = threading.Event()
    #     gpio = mraa.Gpio(sensor_pin_id)
    #     prev_switch = gpio.read()
    #     while (True):
    #         switch = gpio.read()
    #         # logging.log(logging.DEBUG, "switch: " + str(switch))
    #         if switch != prev_switch and switch == switching_to:
    #             # logging.log(logging.DEBUG, "switch: " + str(switch))
    #             # logging.log(logging.DEBUG, "event before: " + str(e.is_set()))
    #             e.set()
    #             # logging.log(logging.DEBUG, "event after: " + str(e.is_set()))
    #         prev_switch = switch

    def move_nonstop(self, xpa, xpb, xa1, xa2, xb1, xb2):
        print ("moving motors")
        pwma = mraa.pwma.read()
        pwmb = mraa.pwmb.read()
        a1 = mraa.a1.read()
        b1 = mraa.b1.read()
        a2 = mraa.a2.read()
        b2 = mraa.b2.read()

        print ("before:\n" + "pwma: " + str(pwma) +
               "pwmb: " + str(pwmb) +
               "a1: " + str(a1) +
               "b1: " + str(b1) +
               "a2: " + str(a2) +
               "b2: " + str(b2))

        mraa.pwma.write(xpa)
        mraa.pwmb.write(xpb)
        mraa.a1.write(xa1)
        mraa.b1.write(xb1)
        mraa.a2.write(xa2)
        mraa.b2.write(xb2)
        print ("after:\n" +
               "pwma: " + str(pwma) +
               "pwmb: " + str(pwmb) +
               "a1: " + str(a1) +
               "b1: " + str(b1) +
               "a2: " + str(a2) +
               "b2: " + str(b2))

    def stop(self):
        mraa.a1.write(0)
        mraa.b1.write(0)
        mraa.a2.write(0)
        mraa.b2.write(0)
        mraa.pwma.write(0)
        mraa.pwma.write(0)

    def forward_nonstop(self, speed):
        print("driving forward")
        self.move_nonstop(speed, speed, 1, 0, 1, 0)

    def back_nonstop(self, speed):
        print("driving back")
        self.move_nonstop(speed, speed, 0, 1, 0, 1)

    def lrotate_nonstop(self, speed):
        print("lrotating nonstop")
        self.move_nonstop(speed, speed, 0, 1, 1, 0)

    def rrotate_nonstop(self, speed):
        print("rrotating")
        self.move_nonstop(speed, speed, 1, 0, 0, 1)

    def lturn_nonstop(self, speed):
        print("lturning")
        self.move_nonstop(0.5, 1, 1, 0, 1, 0)

    def rturn_nonstop(self, speed):
        print ("rturning")
        self.move_nonstop(1, 0.5, 1, 0, 1, 0)

    def lrotate_for(self, tide, speed):
        print ("rotating left for t: " + str(tide) + " speed: " + str(speed))
        self.lrotate_nonstop(speed)
        time.sleep(tide)
        self.stop()

    def rrotate_for(self, tide, speed):
        print ("rotating left for t: " + str(tide) + " speed: " + str(speed))
        self.rrotate_nonstop(speed)
        time.sleep(tide)
        self.stop()

    # def move_front_until_sensor_act(self):
    #     e = threading.Event()
    #     con = Control()
    #     # q = Queue()
    #     # q.put(1)
    #     # con.forward_nonstop()
    #     # time.sleep(1)
    #     # con.stop()
    #     t = threading.Thread(target=self.movement_front_until_event, args=[con, e])
    #     t2 = threading.Thread(target=self.get_sensor_info, args=[e])
    #     t.start()
    #     t2.start()
    #
    #     t.join()
    #     t2.join()

    def measure_turn_rate(self, e, speed, q):
        # e = threading.Event()
        number_of_turns = 5
        start = time.time()

        for i in range(0, number_of_turns):
            self.rrotate_nonstop(speed)
            logging.log(logging.DEBUG, "i: " + str(i))

            e.wait()
            e.clear()
            logging.log(logging.DEBUG, "stopped waiting")

        self.stop()
        end = time.time()
        time_of_turns = end - start
        time_per_degree = time_of_turns/(number_of_turns*180)
        q.put(time_per_degree)
        print (time_of_turns)

    def measure_moving_speed(self, e, speed, q):
        number_of_lines = 1
        start = time.time()

        for i in range(0, number_of_lines):
            self.forward_nonstop(speed)
            logging.log(logging.DEBUG, "i: " + str(i))

            e.wait()
            e.clear()
            logging.log(logging.DEBUG, "stopped waiting")

        self.stop()
        end = time.time()
        time_of_movement = end - start
        logging.log(logging.DEBUG, "movement time: " + str(time_of_movement))
        q.put(time_of_movement)

    # def calibrate(self):
    #     print ("put robot on a calibration sheet, enter '1' to continue")
    #     entered = input("put robot on a calibration sheet, enter '1' to continue: ")
    #     while (entered is not 1):
    #         entered = input("put robot on a calibration sheet, enter '1' to continue: ")
    #
    #     e = threading.Event()
    #     pwm = 0.65
    #     q = Queue()
    #     # t_measure_speed = threading.Thread(target=self.measure_moving_speed, args=[e, pwm, Control.sensor_1lf])
    #     t_measure = threading.Thread(target=self.measure_turn_rate, args=[e, pwm, q])
    #     t_sensor = threading.Thread(target=self.get_sensor_info, args=[e, 0])
    #
    #     # t_measure_speed.start()
    #     t_measure.start()
    #     t_sensor.start()
    #
    #     # t_measure_speed.join()
    #     t_measure.join()
    #     # t_sensor.join()
    #
    # # def get_sensor_info(self, q):
    # #     gpio = mraa.Gpio(Control.sensor_pin_id)
    # #     while (True):
    # #         s = gpio.read()
    # #         print s
    # #         q.put(s)
    # #
    # # def movement_front(self, q):
    # #     x = 0def activate_sensor_1lf(self):
    #     t_sensor_lf = threading.Thread(target=self.get_sensor_info, args=[self.sensor_event_1lf, 0, Control.sensor_1lf])
    #     t_sensor_lf.start()
    #     t_sensor_lf.join()
    #     for i in range(0, 10):
    #         if q.get() is 0:
    #             exit()
    #         print "q: " + q.get()
    #         self.forward(float(1))
    #         print "x =" + str(x)
    #         x = x + 1
    def measure_line(self):
        # print ("put robot on a calibration sheet, enter '1' to continue")
        # entered = input("put robot on a calibration sheet, enter '1' to continue: ")
        # while (entered is not 1):
        #     entered = input("put robot on a calibration sheet, enter '1' to continue: ")
        q = Queue()

        e = threading.Event()
        pwm = 0.65
        t_measure_speed = threading.Thread(target=self.measure_moving_speed, args=[e, pwm, q])
        # t_measure = threading.Thread(target=self.measure_turn_rate, args=[e, speed])
        t_sensor = threading.Thread(target=self.get_sensor_info, args=[e, 0])

        t_measure_speed.start()
        # t_measure.start()
        t_sensor.start()

        t_measure_speed.join()
        # t_measure.join()
        t_sensor.join()
        print (q.get())

    def activate_sensors(self):
        logging.debug("Starting sensors")
        for key, sensor in self.sensors_dict.items():
            sensor.activate()
        logging.debug("All sensors activated")

class Sensor:
    def __init__(self, sensor_pin, sensor_event, config):
        self.sensor_pin = sensor_pin
        self.number_of_activations = 0
        self.sensor_event = sensor_event
        self.r_lock = threading.RLock()
        self.t_sensor_lf = threading.Thread(target=self.get_sensor_info,
                                            args=[self.sensor_event, 1, Control.sensor_1lf,
                                                  config.sensor_settings["1lf"]["min_impulse_time"]])

    def activate(self):
        logging.debug("Activating sensor on pin: " + str(self.sensor_pin))
        self.t_sensor_lf.start()


    def get_sensor_info(self, e, switching_to, min_impulse_time):
        # e = threading.Event()
        gpio = mraa.Gpio(self.sensor_pin)
        prev_switch = gpio.read()
        logging.log(logging.DEBUG, "number_of_activations: " + str(self.number_of_activations))
        start = time.time()

        while (True):
            switch = gpio.read()
            # logging.log(logging.DEBUG, "switch: " + str(switch))
            # '''switching_to  - to what will'''

            if switch != prev_switch and switch == switching_to:
                end = time.time()
                # print ("end - start: " + str(end - start))
                if end - start > min_impulse_time:
                # logging.log(logging.DEBUG, "switch: " + str(switch))
                #     logging.log(logging.DEBUG, "event before: " + str(e.is_set()))
                    e.set()
                    logging.log(logging.DEBUG, "event: " + str(e.is_set()))
                    self.number_of_activations += 1
                    logging.log(logging.DEBUG, "number_of_activations: " + str(self.number_of_activations))
                    start = time.time()
                    # logging.log(logging.DEBUG, "event after: " + str(e.is_set()))

            prev_switch = switch

    @property
    def number_of_activations(self):
        with self.r_lock:
            return self._number_of_activations

    @number_of_activations.setter
    def number_of_activations(self, value):
        with self.r_lock:
            self._number_of_activations = value
