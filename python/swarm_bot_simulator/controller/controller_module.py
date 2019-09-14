import time
from threading import Event
class MainController:
    def __init__(self):
        self.q = None
        self.config = None
        self.bot_manager = None
        self.quit_event = Event()
        self.quit_event.clear()

    def start_serwer(self):
        # -*- coding: utf-8 -*-
        import warnings
        import subprocess
        from swarm_bot_simulator.model.bot_manager_module import Bot_manager
        from swarm_bot_simulator.model.image_analyzer_module import VideoAnalyzer
        from swarm_bot_simulator.resources.config import config

        self.config = config

        def launch_mosquitto(port):
            subprocess.Popen(["mosquitto", "-p", str(port)])

        launch_mosquitto(config["communication_settings"]["port"])

        img_path = "/home/nexon/Projects/Swarmbot-simulator/python/swarm_bot_simulator/resources/trojkat.jpg"

        for bots in self.config.
        camera = VideoAnalyzer(config)
        photo_params = camera.load_photo(img_path)
        board_params = photo_params[0]
        board_width = board_params[1][0]
        board_height = board_params[1][1]

        marker_params = photo_params[1]
        marker_poz_x = marker_params[0][0]
        marker_poz_y = marker_params[0][1]
        marker_direction = marker_params[1]
        marker_transformed = photo_params[2]
        marker_transformed_poz_x = marker_transformed[0][0]
        marker_transformed_poz_y = marker_transformed[0][1]

        config["real_settings"]["pixel_2_real_ratio"] = board_width / config["board_settings"]["real_width"]

        if config["bots"][0]["is_real"] is True:
            config["bots"][0]["direction"] = marker_direction
            config["bots"][0]["poz_x"] = marker_transformed_poz_x
            config["bots"][0]["poz_y"] = marker_transformed_poz_y

        config["board_settings"] = {}
        config["board_settings"]["border_x"] = board_width
        config["board_settings"]["border_y"] = board_height

        try:
            self.bot_manager = Bot_manager(config, self)
            self.bot_manager.simulate()

        except ConnectionRefusedError as e:
            warnings.warn("Have you started mosquitto.exe?")
            raise e

        while not self.quit_event.is_set():
            time.sleep(0.1)


    def quit_program(self):
        self.quit_event.set()
        quit()

