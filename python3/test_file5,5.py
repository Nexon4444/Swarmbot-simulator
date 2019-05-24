import swarm_bot_simulator.model.bot_components as bc
v = bc.Vector(1, 1)
ve = bc.VectorEncoder()
print(ve.encode(v))