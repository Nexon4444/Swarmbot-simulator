import time

import scipy.constants
from sympy.physics.vector import *
import pymunk
import pyglet
from pymunk.pyglet_util import DrawOptions
from swarm_bot_simulator.utilities.util import Vector
from threading import Thread
from queue import Queue
import math
# import swarm_bot_simulator.view.visualize as vis

window = pyglet.window.Window(1280, 720, "SimulatedBot Visualizer", resizable=False)


class SimulatedBot:
    def __init__(self,
                 position,
                 direction,
                 center_of_mass,
                 mass,
                 inertia,
                 friction_coef,
                 motor_poz,
                 motor_facing,
                 motor_power,
                 max_force):

        self.direction = Vector(direction)
        self.friction_coef = friction_coef

        self.space = pymunk.Space()
        # self.space.gravity = (0, -2)
        self.body = pymunk.Body()
        self.body.position = position
        self.body.mass = mass
        self.body.moment = inertia
        self.body.angle = direction
        # self.body.rotation_vector = self.direction.get_tuple()

        # self.board = pymunk.Body()
        # self.board.position = (0, 0)

        # self.board_square = pymunk.Poly.create_box(self.board, (100, 100))
        # self.board_square.friction = 1
        # pivot = pymunk.PinJoint(self.body, self.board)

        self.poly = pymunk.Poly.create_box(self.body, size=(25, 25))
        self.poly.friction = 1
        self.space.add(self.body, self.poly)
        # self.space.add(self.body, self.poly, self.board, self.board_square, pivot)
        self.motor_poz = motor_poz
        self.motor_facing = motor_facing
        self.motor_power = motor_power
        self.max_force = max_force
        self.center_of_mass = center_of_mass

        self.window = None
        self.options = DrawOptions()
        self.motor_vector_attachment_points = None
        self.scale = 20

    def friction(self, force, friction_coef):
        # from swarm_bot_simulator.model.bot_components import Vector
        force = Vector(force)

        friction = scipy.constants.g * self.body.mass * friction_coef
        force_friction = Vector(force)
        force_friction.invert()
        force_friction.normalize()
        force_friction.mul_scalar(friction)
        print("force+force_friction: " + str(force) + " + " + str(force_friction))
        force_result = (force+force_friction).get_tuple()
        return force_result

    def calc_motor_force_vector(self, dir, motor_vector):
        print("calc_motor_force_vector args: " + str(dir) + ", " + str(motor_vector))
        dir = Vector(dir)
        motor_vector = Vector(motor_vector)
        motor_vector.turn(dir.get_angle())
        return motor_vector


    def calc_lateral_force(self, speed, motor_facing):
        pass
        # force =

    def calc_speed_force(self, power, speed, motor_facing):
        if speed.length == 0:
            force_mag = self.max_force
        else:
            force_mag = power/speed.length

        if force_mag>self.max_force:
            force_mag = self.max_force

        print("force_mag: " + str(force_mag) + " max_force: " + str(self.max_force))
        force = Vector(motor_facing)
        force.mul_scalar(force_mag)
        return force

    def update(self, dt):
        print("rotation: " + str(self.body.rotation_vector))

        # force2frict = (self.calc_speed_force(self.motor_power[0],
        #                                      self.body.velocity,
        #                                      self.motor_facing[0]),
        #                self.calc_speed_force(self.motor_power[1],
        #                                      self.body.velocity,
        #                                      self.motor_facing[1]))

        force2frict = (self.calc_speed_force(self.motor_power[0],
                                             self.body.velocity,
                                             self.calc_motor_force_vector(-self.body.angle, self.motor_facing[0])),

                       self.calc_speed_force(self.motor_power[1],
                                             self.body.velocity,
                                             self.calc_motor_force_vector(-self.body.angle, self.motor_facing[1])))

        print("force2frict: " + str(force2frict[0]) + str(force2frict[1]))
        force2apply = (self.friction(force2frict[0], self.friction_coef),
                       self.friction(force2frict[1], self.friction_coef))


        print("force2apply: " + str(force2apply))
        print("motor_poz: " + str(self.motor_poz))
        print("force: " + str(self.body._get_force()))
        # self.body.apply_force_at_local_point(force2apply, (0, 0))

        self.body.apply_force_at_local_point(force2apply[0], self.motor_poz[0])
        self.body.apply_force_at_local_point(force2apply[1], self.motor_poz[1])

        world_motor_points = (self.body.local_to_world(self.motor_poz[0]),
                              self.body.local_to_world(self.motor_poz[1]))

        motor_value_vectors = (Vector(force2apply[0]),
                               Vector(force2apply[1]))

        print("motor_value_vectors: " + str(motor_value_vectors[0]) + ", " + str(motor_value_vectors[1]))

        motor_value_vectors[0].normalize()
        motor_value_vectors[1].normalize()
        print("motor_value_vectors normalized: " + str(motor_value_vectors[0]) + ", " + str(motor_value_vectors[1]))
        motor_value_vectors[0].mul_scalar(self.scale)
        motor_value_vectors[1].mul_scalar(self.scale)

        self.motor_vector_attachment_points = (motor_value_vectors[0].get_points_after_attaching_point(world_motor_points[0]),
                                               motor_value_vectors[1].get_points_after_attaching_point(world_motor_points[1]))


        print(self.body.velocity)
        print()
        # time.sleep(0.5)
        self.space.step(dt)

    def visualize(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()

    def calculate(self, speed, force, time):
        pass

    def simulate(self, q=None):
        while True:
            self.update(0.02)
            self.body.apply_force_at_local_point((100, 0), (0, -25))
            print(self.body.position)
            print(self.body.angle)
            print(self.body.force)
            print("\n")

            q.put(self.body)
            # time.sleep(0.5)


simbot = SimulatedBot(position=(500, 250),
                      direction=0,
                      center_of_mass=(0, 0),
                      mass=10,
                      inertia=100000,
                      friction_coef=0.4,
                      motor_poz=((-9, -18), (9, -18)),
                      motor_facing=((0, 1), (0, 1)),
                      motor_power=(1000, 500),
                      max_force=100)

# simbot.body.angle = -math.pi/2
@window.event
def on_draw():
    def flatten(list_of_lists):
        return [y for x in list_of_lists for y in x]

    window.clear()
    simbot.space.debug_draw(options=simbot.options)

    if simbot.motor_vector_attachment_points is not None:
        motor_vector_attachment_points = (flatten(flatten(simbot.motor_vector_attachment_points)))

        pyglet.graphics.draw(4, pyglet.gl.GL_LINES,
                             ('v2f', motor_vector_attachment_points)
                             )


simbot.visualize()
# visualizer = vis.Visualizer()
# q = queue.Queue()
# sim_t = Thread(target=simbot.simulate(), args=q)


# simbot.visualize()
# simbot.simulate()
        # dp = time*speed_right
        # dl = time*speed_left
        #
        # deg = (dp - dl)/(math.pi*self.l)
        # r = dp*self.l/(dp-dl)








