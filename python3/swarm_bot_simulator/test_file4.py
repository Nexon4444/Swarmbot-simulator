from swarm_bot_simulator.model.bot_components import *
import math

import pygame
import threading
import time
class Visualizer:

    # width = 20
    # height = 20
    black = (0, 0, 0)
    white = (255, 255, 255)
    size = [800, 600]

    def __init__(self):
        pass

    def visualize(self):
        pygame.init()
        # bot_image = pygame.image.load(os.path.join('resources', 'car.png'))
        x = (800 * 0.45)
        y = (600 * 0.8)
        # game_display = pygame.display.set_mode(Visualizer.size)
        print("visualization started")
        game_display = pygame.display.set_mode(Visualizer.size)
        pygame.draw.rect(game_display, Visualizer.white, (x, y, 100, 100))
        # pygame.display.set_caption('Swarmbot visualization')

        game_display.fill(Visualizer.white)
        clock = pygame.time.Clock()
        crashed = False

        while not crashed:
            clock.tick(10)
            game_display.fill(Visualizer.white)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crashed = True

            x += 2
            pygame.display.update()

        pygame.quit()

        quit()

def graphics():

    vis = Visualizer()
    vis.visualize()

vis_thread = threading.Thread(target=graphics, args=[])
vis_thread.start()
time.sleep(10)
vis_thread.join()
