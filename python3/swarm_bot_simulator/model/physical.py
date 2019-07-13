from sympy.physics.vector import *
import pymunk
import math
class PhysicalCalculator:
    def __init__(self, position, direction, motor_poz, center_of_mass, mass, inertia):
        self.space = pymunk.Space()
        self.body = pymunk.Body()
        self.body.position = position
        self.body.moment = inertia

        self.motor_poz = motor_poz

        self.center_of_mass = center_of_mass

        self.direction = direction


    def calculate(self, speed, force, time):

        # dp = time*speed_right
        # dl = time*speed_left
        #
        # deg = (dp - dl)/(math.pi*self.l)
        # r = dp*self.l/(dp-dl)








