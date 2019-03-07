from swarm_bot_simulator.model.bot_components import Bot


class Config:
    def __init__(self, app_config):
        self.bot_n = len(app_config["bots"])
        self.communication_settings = CommunicationSettings(app_config["communication_settings"])
        self.start_bots = [Bot(b, self.communication_settings) for b in (app_config["bots"])]


class CommunicationSettings:
    def __init__(self, communication_settings):
        self.broker = communication_settings["broker"]
        self.port = communication_settings["port"]

