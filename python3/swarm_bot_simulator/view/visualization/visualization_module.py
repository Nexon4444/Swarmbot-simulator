import pygame
import cairocffi as cairo
import os
from pathlib import Path
# from gi.repository import cairo
from math import pi
from PIL import Image
from threading import Event
import math
from shapely.geometry import Point
from threading import Thread
from swarm_bot_simulator.model.algorithm.algorithm_module import Bot, BotInfo
# from swarm_bot_simulator.model.algorithm import Bot, BotInfo
import logging

class Visualizer:
    log = True
    black = (0, 0, 0)
    white = (255, 255, 255)

    def __init__(self, board_settings, board_activation_event: Event):
        # self.board = board
        self.size = [board_settings["border_x"], board_settings["border_y"]]
        self.game_display = pygame.display.set_mode(self.size)
        self.board_activation_event = board_activation_event

    # def display_bot(self, bot_image, x, y, angle):
    #     bot_image = pygame.transform.rotate(bot_image, angle)
    #     bot_image = pygame.transform.scale(bot_image, (20, 20))
    #     self.game_display.blit(bot_image, (x, y))

        "thread finished...exiting"
    def visualize(self, q):
        pygame.init()
        y = (600 * 0.8)
        x = (800 * 0.45)
        # bot_image = pygame.image.load(os.path.join('resources', 'car.png'))
        logging.debug("visualization started")
        game_display = pygame.display.set_mode(self.size)
        pygame.draw.rect(game_display, Visualizer.black, (x, y, 100, 100))
        pygame.display.set_caption('Swarmbot visualization')

        game_display.fill(Visualizer.white)
        clock = pygame.time.Clock()
        crashed = False

        self.board_activation_event.wait()
        while not crashed:
            board = q.get()
            clock.tick(10)
            game_display.fill(Visualizer.white)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crashed = True
            # display_bot(bot_image, 200, 200, 100)
            # bot1.draw()
            for key, bot_data in board.bots_info.items():
                image = BotImage(bot_data, game_display)
                image.draw()
            # bot1 = BotImage(100, 100, 0, 40, 40, game_display)
            # bot1.change_poz(0, 0, -11)
            x += 2
            self.log("Displaying board: {" + str(board) + "}")
            pygame.display.update()

        pygame.quit()
        return
        # quit()

    def log(self, message):
        if Visualizer.log:
            print(message)


class BotImage:
    COLOURS = {
        "BLACK": (0, 0, 0),
        "WHITE": (1, 1, 1),
        "BLUE": (0, 0, 1),
        "GREEN": (0, 1, 0),
        "RED": (1, 0, 0),
        "YELLOW": (1, 1, 0),
        "ORANGE": (1, 0.6, 0)
    }

    def __init__(self, bot_info, game_display):
        # self.image_orginal = image
        # self.image = self.image_orginal
        self.position = bot_info.position
        # self.poz_y = bot_info.poz_y
        self.dir = bot_info.dir
        self.size_x = BotInfo.size_x
        self.size_y = BotInfo.size_y
        self.game_display = game_display
        self.color = BotImage.COLOURS[bot_info.color]

    def change_poz(self, x, y, dir):
        self.position.x = self.position.x + x
        self.position.y = self.position.y + y
        self.dir = (self.dir + dir) % (2*pi)

    def draw(self):
        self.game_display.blit(self.convert2pygame(self.vectorize(self.dir)), (self.position.x, self.position.y))

    def convert2pygame(self, surface):
        def bgra_surf_to_rgba_string(cairo_surface):
            # We use PIL to do this
            img = Image.frombuffer(
                'RGBA', (cairo_surface.get_width(),
                         cairo_surface.get_height()),
                bytes(cairo_surface.get_data()), 'raw', 'BGRA', 0, 1)
                # cairo_surface.get_data().tobytes(), 'raw', 'BGRA', 0, 1)

            return img.tobytes('raw', 'RGBA', 0, 1)
        return pygame.image.frombuffer(
    bgra_surf_to_rgba_string(surface), (surface.get_width(), surface.get_height()), 'RGBA')


    def vectorize(self, dir):
        WIDTH, HEIGHT = BotInfo.size_x, BotInfo.size_y

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        cr = cairo.Context(surface)
        cr.set_source_rgb(self.color[0], self.color[1], self.color[2])
        cr.translate(WIDTH / 2, HEIGHT / 2)
        cr.scale(WIDTH, HEIGHT)
        cr.rotate(math.radians(180-dir))
        cr.rectangle(-0.2, -0.3, 0.4, 0.6)
        cr.fill()
        cr.set_source_rgb(BotImage.COLOURS["ORANGE"][0], BotImage.COLOURS["ORANGE"][1], BotImage.COLOURS["ORANGE"][2])
        cr.rectangle(0.2, 0.05, 0.1, 0.2)
        cr.fill()
        cr.rectangle(-0.2, 0.05, -0.1, 0.2)
        cr.fill()
        return surface

class ObstacleImage:
    pass
