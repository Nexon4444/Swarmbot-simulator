from swarm_bot_simulator.model.bot_components import *

md = MovementData(poz=Vector(0, 0), direction=0.0, time=1, command=Movement.MOVE_PRIM)
me = MovementDataEncoder()
json_command = me.encode(md)
print(json_command)