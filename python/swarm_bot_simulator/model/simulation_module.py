import sys
if sys.version_info[0] > 2:
    import numpy as np

from swarm_bot_simulator.utilities.util import Vector
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
        if sys.version_info[0] > 2:
            real_length = self.convert_pix2cm(dist_vec.magnitude())

            vec_forward = Vector(self.count_normal_forward(self.config["real_settings"]["gauss"]["x"],
                                                           self.config["real_settings"]["gauss"]["y"],
                                                           real_length))
            vec_forward.turn(dist_vec.get_angle())
            bot_info.position.add_vector(dist_vec)

        else:
            bot_info.position.add_vector(dist_vec)

        # vector_forward = poz_forward - bot_info.position
        #
        # vec = bot_info.position
        # vec = Vector.create_vec_from_dir_length(bot_info.direction, dist_vec)


    def count_normal_forward(self, x_gauss, y_gauss, real_length):
        real_time = self.convert_cm2pix(real_length)
        x_gauss_corrected = (x_gauss[0] * real_time, x_gauss[1] * real_time)
        y_gauss_corrected = (y_gauss[0] * real_time, y_gauss[1] * real_time)

        return (self.convert_cm2pix(np.random.normal(x_gauss_corrected[0], x_gauss_corrected[1])),
                self.convert_cm2pix(np.random.normal(y_gauss_corrected[0], y_gauss_corrected[1])))

    def convert_cm2pix(self, cm):
        return cm * (1 / self.config["real_settings"]["pixel_2_real_ratio"])

    def convert_pix2cm(self, pix):
        return pix * self.config["real_settings"]["pixel_2_real_ratio"]

    def convert_sec2cm(self, sec):
        return self.config["real_settings"]["cm_per_sec"] * sec

    def convert_cm2sec(self, cm):
        return 1 / self.config["real_settings"]["cm_per_sec"] * cm
# print(np.random.normal(0, 0))

# for x in range(0, 100):
#     print(np.random.normal(1, 11))
