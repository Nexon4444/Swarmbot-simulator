import pygame
# import cairocffi as cairo
import os
from pathlib import Path
import cairo

class Visualizer:
    pygame.init()

    black = (0, 0, 0)
    white = (255, 255, 255)
    size = [800, 600]

    def __init__(self, model):
        self.model = model
        self.game_display = pygame.display.set_mode(Visualizer.size)

    def visualize(self, server):
        x = (800 * 0.45)
        y = (600 * 0.8)
        game_display = pygame.display.set_mode(Visualizer.size)
        pygame.draw.rect(game_display, Visualizer.black, (x, y, 100, 100))
        pygame.display.set_caption('Swarmbot visualization')

        game_display.fill(Visualizer.white)
        clock = pygame.time.Clock()
        crashed = False

        os.chdir(Path(os.getcwd()).parent)
        bot_image = pygame.image.load(os.path.join('resources', 'bot_w_bezruchu.png'))
        # bot_image = pygame.image.load(os.path.join('resources', 'car.png'))
        # bot_image =
        bot1 = BotImage(bot_image, 100, 100, 0, 40, 40, game_display)

        def display_bot(bot_image, x, y, angle):
            bot_image = pygame.transform.rotate(bot_image, angle)
            bot_image = pygame.transform.scale(bot_image, (20, 20))
            game_display.blit(bot_image, (x, y))

        while not crashed:
            clock.tick(10)
            game_display.fill(Visualizer.white)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crashed = True
            # display_bot(bot_image, 200, 200, 100)
            # bot1.draw()
            bot1.change_poz(0, 0, -11)
            bot1.draw()
            x += 2
            pygame.display.update()

        pygame.quit()
        quit()


class BotImage:
    blue = (0, 0, 204)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    def __init__(self, image, poz_x, poz_y, dir, size_x, size_y, game_display):
        self.image_orginal = image
        self.image = self.image_orginal
        self.poz_x = poz_x
        self.poz_y = poz_y
        self.dir = dir
        self.size_x = size_x
        self.size_y = size_y
        self.game_display = game_display

    def change_poz(self, x, y, dir):
        self.poz_x = self.poz_x + x
        self.poz_y = self.poz_y + y
        self.dir = (self.dir + dir) % 360

    def draw(self):
        self.image = pygame.transform.rotozoom(self.image_orginal, self.dir, 0.03)
        # self.image = pygame.transform.scale(self.image, (self.size_x, self.size_y))
        self.game_display.blit(self.image, (self.poz_x, self.poz_y))

    def vectorize(self, dir):
        WIDTH, HEIGHT = 256, 256

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        # cr = cairo.Context(surface)
        # cr.scale(WIDTH, HEIGHT)  # Normalizing the canvas
        # # pat = cairo.LinearGradient(0.0, 0.5, 0.0, 1.0)
        # # pat.add_color_stop_rgba(1, 0.7, 0, 0, 1)  # First stop, 50% opacity
        # # cr.rectangle(0, 0, 1, 1)
        # # cr.set_source(pat)
        # # cr.fill()
        # cr.set_line_width(0.face)
        #         cr2.set_source_rgb(0, 0, 1)
        #         cr2.translate(WIDTH / 2, HEIGHT / 2)
        #         cr2.scale(WIDTH, HEIGHT)
        #         # cr2.transform()
        #         cr2.rotate(dir)
        #         cr2.rectangle(-0.2, -0.3, 0.4, 0.6)
        #         cr2.fill()
        #         cr2.set_source_rgb(1, 0, 0)
        #         cr2.rectangle(0.2, 0.05, 0.1, 0.2)
        #         cr2.fill()
        #         cr2.rectangle(-0.2, 0.05, -0.1, 0.2)
        #         cr2.fill()
        #
        #
        # vis = Visualizer(None)
        # vis.visualize(None)01)
        # cr.set_source_rgb(0, 0, 0)
        # cr.rectangle(0.25, 0.25, 0.5, 0.5)
        # cr.stroke()

        cr2 = cairo.Context(sur
