from swarm_bot_simulator.model.bot_components import *
import math
b = Vector(4, 4)
print(str(math.degrees(b.get_angle())))

p1 = Point(float(0), float(0))
p2 = Point(1.0, 1.0)
p3 = p1.p2
print(str(p3))