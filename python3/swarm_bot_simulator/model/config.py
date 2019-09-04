from swarm_bot_simulator.model.algorithm import *
# from swarm_bot_simulator.model.board import BotDataContainer

# class Config:
#     def __init__(self, app_config):
#         self.bot_n = len(app_config["bots"])
#         self.communication_settings = CommunicationSettings(app_config["communication_settings"])
#         self.bot_settings = BotSettings(app_config["bot_settings"])
#         self.view_settings = ViewSettings(app_config["view_settings"])
#         self.board_settings = BoardSettings(app_config["board_settings"])
#         # self.bot_infos = [BotInfoSettings(parsed_bot) for parsed_bot in app_config["bots"]]
#
# class CommunicationSettings:
#     def __init__(self, communication_settings):
#         self.broker = communication_settings["broker"]
#         self.port = communication_settings["port"]
#         self.method = communication_settings["method_is_direct"]
#
# class BoardSettings:
#     def __init__(self, board_settings):
#         self.border_x = board_settings["border_x"]
#         self.border_y = board_settings["border_y"]
#
# class BotSettings:
#     def __init__(self, bot_settings):
#         self.view_is_omni = bot_settings["view_mode_is_omni"]
#         self.separation_distance = bot_settings["separation_distance"]
#         self.cohesion_distance = bot_settings["cohesion_distance"]
#         self.alignment_distance = bot_settings["alignment_distance"]
#
#         self.sep_mul = bot_settings["sep_mul"]
#         self.ali_mul = bot_settings["ali_mul"]
#         self.coh_mul = bot_settings["coh_mul"]
#
#         self.max_speed = bot_settings["max_speed"]
#         self.max_force = bot_settings["max_force"]
#
# class ViewSettings:
#     def __init__(self, view_settings):
#         self.launch = view_settings["launch"]
#
# class BotInfoSettings:
#     def __init__(self, bots):
#         self.bot_id = bots["bot_id"]
#         self.poz_x = bots["poz_x"]
#         self.poz_y = bots["poz_y"]
#         self.is_real = bots["is_real"]
#         self.speed = bots["speed"]
#         self.direction = bots["direction"]