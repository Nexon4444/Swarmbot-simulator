from swarm_bot_simulator.model.server import Server


class Board:
    def __init__(self, config):
        self.bot_n = config.bot_n
        self.all_bots = config.config["bots"]
        self.server = Server(config)
        x= 3

    def calibrate(self):
        pass

    def run(self):
        pass


