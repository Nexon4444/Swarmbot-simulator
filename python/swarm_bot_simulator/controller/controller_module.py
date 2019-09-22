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
        time.sleep(1)
        img_path = "/home/nexon/Projects/Swarmbot-simulator/python/swarm_bot_simulator/resources/trojkat.jpg"

        all_bots_simulated = True
        real_bot_id = None
        for indx, bot in enumerate(self.config["bots"]):
            if bot["is_real"] is True:
                all_bots_simulated = False
                real_bot_id = indx
                break

        if all_bots_simulated is False:
            camera = VideoAnalyzer(config)
            photo_params = camera.load_photo_once()
            # photo_params = camera.load_photo()
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
            # if config["bots"][]["is_real"] is True:
            config["bots"][real_bot_id]["direction"] = marker_direction
            config["bots"][real_bot_id]["poz_x"] = marker_transformed_poz_x
            config["bots"][real_bot_id]["poz_y"] = marker_transformed_poz_y

        else:
            board_width = 800
            board_height = 600
            

        config["real_settings"]["pixel_2_real_ratio"] = board_width / config["board_settings"]["real_width"]
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

