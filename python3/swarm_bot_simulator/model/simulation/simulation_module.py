import numpy as np

class PhysicsSimulator:
    def __init__(self, config):
        self.config = config

    def predict_params(self, vector, bot_info):
        pass

    def count_turn(self, rel_dir):
        return rel_dir/self.config["real_settings"]["deg_per_sec"]

    def simulate_turn(self, bot_info, t):
        bot_info.dir = self.config["real_settings"]["deg_per_sec"] * t

    def count_forward(self, dist_vec):
        return dist_vec.magnitude()/self.config["real_settings"]["cm_per_sec"]

    def simulate_forward(self, bot_info, dist_vec):
        bot_info.position.add_vector(dist_vec)

    def count_normal_forward(self, avg, dev, l):
        pass


# for x in range(0, 100):
#     print(np.random.normal(1, 11))
