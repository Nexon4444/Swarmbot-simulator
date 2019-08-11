import math
import json

from json import JSONEncoder
from math import cos, sin
def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def log_flush(message, start, stop):
    import logging, sys
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s',
                        )
    time = stop - start

    # logging.debug('wat wat')
    sys.stdout.write(str(message) + str(time))
    # logging.debug((str(message) + str(time)))
    sys.stdout.write('\r')
    sys.stdout.flush()

def restart_line():
    import sys
    sys.stdout.write('\r')
    sys.stdout.flush()


class Vector:
    def __init__(self, *args):
        import pymunk
        args = list(args)
        if len(args) == 1 and isinstance(args[0], Vector):
            self.x = args[0].x
            self.y = args[0].y

        elif len(args) == 1 and isinstance(args[0], tuple):
            self.x = args[0][0]
            self.y = args[0][1]

        elif len(args) == 1 and isinstance(args[0], float) or isinstance(args[0], int):
            vec = self.direction2normalized_vector(args[0])
            self.set_xy(vec.x, vec.y)

        elif len(args) == 1 and isinstance(args[0], pymunk.Vec2d):
            self.x = args[0][0]
            self.y = args[0][1]

        elif len(args) == 2:
            self.x = args[0]
            self.y = args[1]

        elif len(args) == 3:
            self.points_direction2vector(args[0], args[1], args[2])
        # self.y = y

    def direction2normalized_vector(self, direction):
        #TODO implementation
        vec = Vector(sin(direction), cos(direction))
        vec.normalize()
        # raise NotImplementedError
        return vec

    def get_points_after_attaching_point(self, point):
        start = Vector(point)
        end = start+self
        return (start.get_tuple(), end.get_tuple())

    def turn(self, angle):
        x1 = self.x
        y1 = self.y
        magnitude = self.magnitude()

        vec = self.direction2normalized_vector(self.get_angle()+angle)
        vec.mul_scalar(magnitude)
        self.x = vec.x
        self.y = vec.y

    def list2vector(self, vector_list):
        self.x = vector_list[0]
        self.y = vector_list[1]

    def points_direction2vector(self, direction, point1, point2):
        x1, y1 = point1
        x2, y2 = point2

        A = y2 - y1
        B = -(x2 - x1)
        C = y1*x2 - x1*y2

        vec = Vector(A, B)

        if Vector.almost_equals(vec.get_angle(), direction, math.pi/2):
            self.set_xy(vec.x, vec.y)
        else:
            vec.invert()
            self.set_xy(vec.x, vec.y)

    def get_perpendicular_line_equation(self, point):
        x = point[0]
        y = point[1]

        A = self.x
        B = self.y
        C = -(A*x + B*y)

        return Line(A, B, C)

    def div_scalar(self, scalar):
        self.x = self.x / scalar
        self.y = self.y / scalar
    # , self.vec.y / scalar)

    def add_vector(self, vec):
        self.x = self.x + vec.x
        self.y = self.y + vec.y

    def normalize(self):
        m = self.magnitude()

        if m > 0:
            self.x = self.x / m
            self.y = self.y / m
        else:
            self.x = 0
            self.y = 0

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def mul_vector(self, vec):
        self.x = self.x * vec.x
        self.y = self.y * vec.y

    def mul_scalar(self, scalar):
        self.x = self.x * scalar
        self.y = self.y * scalar

    def invert(self):
        self.x = -self.x
        self.y = -self.y

    def sub_vector(self, vec):
        self.x = self.x - vec.x
        self.y = self.y - vec.y

    def limit(self, max):
        size = self.magnitude()

        if size is 0:
            return

        if size > max:
            self.x = self.x / size
            self.y = self.y / size

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def get_angle(self):
        """
        Counts the angle between vertical facing vector, and self vector
        :return: returns angle in radians
        """
        return math.atan2(self.x, self.y)

    def substract_vectors(self, vec1, vec2):
        return Vector(vec1.x - vec2.x, vec1.y - vec2.y)

    def distance(self, vec):
        return math.sqrt(math.pow(vec.x - self.x, 2) + math.pow(vec.y - self.y, 2))

    def in_borders(self, border):
        if self.x < 0:
            return False
        elif self.y < 0:
            return False
        elif self.x > border.x:
            return False
        elif self.y > border.y:
            return False
        else:
            return True

    def get_tuple(self):
        return self.x, self.y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __str__(self):
        if math.fabs(self.x) < 0.0000000001:
            x = 0
        else:
            x = self.x

        if math.fabs(self.y) < 0.0000000001:
            y = 0
        else:
            y = self.y

        # x = self.x
        # y = self.y
        return '[' + str(x) + ", " + str(y) + ']'

    @staticmethod
    def almost_equals(val1, val2, span):
        if val1 <= val2 + span and val1 >= val2 - span:
            return True

        else:
            return False

    # def __default(self):
    #     return self.__dict__


class VectorEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Vector):
            return [o.x, o.y]
        else:
            return json.JSONEncoder.default(self, o)


class Line:
    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C

    def turn(self, turn_point, degrees):
        A = self.A
        B = self.B
        C = self.C

        x0 = turn_point[0]
        y0 = turn_point[1]

        x1 = cos(degrees)*x0 - sin(degrees)*y0
        y1 = sin(degrees)*x0 + cos(degrees)*y0


        # theta = math.atan(B/A)
        # beta = theta+degrees
        #
        # p = -C/math.sqrt(A**2 + B**2)
        # pnew = p + x0*(math.cos(beta)-math.cos(theta)) + y0 * (math.sin(beta)-math.sin(theta))
        # x=3


    def get_point_a_length_away_from(self, point, distance):
        xp = point[0]
        yp = point[1]

        r = distance

        A = self.A
        B = self.B90
        C = self.C

        if A != 0:
            a = B**2/A**2+1
            b = 2*C*B/A**2+2*B*xp/A-2*yp
            c = C**2/A**2+2*C*xp/A + xp ** 2 + yp ** 2 - r ** 2

            delta = b**2-4*a*c
            y1 = (-b-math.sqrt(delta))/(2*a)
            y2 = (-b+math.sqrt(delta))/(2*a)

            x1 = -(C+B*y1)/A
            x2 = -(C+B*y2)/A

        else:
            a = 1
            b = -2*xp
            c = xp**2 + C**2/B**2 + 2*C/B*yp + yp**2*(C/B+yp)**2+yp**2-r**2

            delta = b ** 2 - 4 * a * c
            x1 = (-b - math.sqrt(delta)) / (2 * a)
            x2 = (-b + math.sqrt(delta)) / (2 * a)

            y1 = y2 = -C/B

        return [(x1, y1), (x2, y2)]

# print(cos(4*math.pi/2))
vec = Vector(2*math.pi/4)

print(str(vec))
vec.turn(math.pi/2)
print(str(vec))
print(str(math.degrees(vec.get_angle())))
# import time, sys
#
# t = 0
# while True:
#     print('Seconds passed:', t, end='')
#     sys.stdout.flush()
#     time.sleep(1)
#     t += 1
#     # print('\b'*20, end='')