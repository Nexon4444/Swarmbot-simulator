#!/usr/bin/env python
# Copyleft 2010 Niels Serup, WTFPL 2.0. Free software.

### Imports ###
import math
import pygame
import cairo
import numpy
import image

### Constants ###
width, height = 640, 480


### Functions ###
def draw(ctx):
    ctx.set_line_width(15)
    ctx.arc(320, 240, 200, 0, 2 * math.pi)

    #                   r    g  b    a
    ctx.set_source_rgba(0.6, 0, 0.4, 1)
    ctx.fill_preserve()

    #                   r  g     b    a
    ctx.set_source_rgba(0, 0.84, 0.2, 0.5)
    ctx.stroke()

def bgra_surf_to_rgba_string(cairo_surface):
    # We use PIL to do this
    img = image.frombuffer(
        'RGBA', (cairo_surface.get_width(),
                 cairo_surface.get_height()),
        cairo_surface.get_data(), 'raw', 'BGRA', 0, 1)

    return img.tostring('raw', 'RGBA', 0, 1)


### Body ###
# Init PyGame
pygame.display.init()
screen = pygame.display.set_mode((width, height), 0, 32)

# Create raw surface data (could also be done with something else than
# NumPy)
data = numpy.empty(width * height * 4, dtype=numpy.int8)

# Create Cairo surface
cairo_surface = cairo.ImageSurface.create_for_data(
    data, cairo.FORMAT_ARGB32, width, height, width * 4)

# Draw with Cairo on the surface
ctx = cairo.Context(cairo_surface)
draw(ctx)


##### SVG LOADING EXAMPLE #####
# Using rsvg it is possible to render an SVG file onto a Cairo
# surface. Uncomment the following lines to make it work.
#import rsvg # This will probably not work in Windows. As far as I
# know, only GNU/Linux distibutions package this Python
# module. Nevertheless, it should be easy to create a small wrapper;
# see http://www.cairographics.org/cairo_rsvg_and_python_in_windows/

# Load the file
#svg_graphics = rsvg.Handle('path/to/file.svg')

# Render the graphics onto your Cairo context
#svg_graphics.render_cairo(ctx)

# To get the SVG file's dimensions before you create a Cairo surface,
# use the following function:
#print svg_graphics.get_dimension_data()
###############################

# On little-endian machines (and perhaps big-endian, who knows?),
# Cairo's ARGB format becomes a BGRA format. PyGame does not accept
# BGRA, but it does accept RGBA, which is why we have to convert the
# surface data. You can check what endian-type you have by printing
# out sys.byteorder
data_string = bgra_surf_to_rgba_string(cairo_surface)

# Create PyGame surface
pygame_surface = pygame.image.frombuffer(
    data_string, (width, height), 'RGBA')

# Show PyGame surface
screen.blit(pygame_surface, (0,0))
pygame.display.flip()

clock = pygame.time.Clock()
while not pygame.QUIT in [e.type for e in pygame.event.get()]:
    clock.tick(30)

# This method allows Cairo to use the same block of memory for the surface as pygame does. This is most likely the fastest method of the ones listed here, since it doesn't use an extra buffer. (Tested on Python 2.6.4, pycairo 1.8.6, Cairo 1.8.8, pygame 1.8.1, numpy 1.3.0.) (note: does not work, if numeric is installed)

#!/usr/bin/env python
import cairo
import pygame
import math

size = 400, 400

# Initialize pygame with 32-bit colors. This setting stores the pixels
# in the format 0x00rrggbb.
pygame.init()
screen = pygame.display.set_mode(size, 0, 32)

# Get a reference to the memory block storing the pixel data.
pixels = pygame.surfarray.pixels2d(screen)

# Set up a Cairo surface using the same memory block and the same pixel
# format (Cairo's RGB24 format means that the pixels are stored as
# 0x00rrggbb; i.e. only 24 bits are used and the upper 16 are 0).
cairo_surface = cairo.ImageSurface.create_for_data(
	pixels.data, cairo.FORMAT_RGB24, size[0], size[1])

# Draw a white circle to the screen using pygame.
radius = int(min(size)/2*0.7)
pos = [int(a/2) for a in size]
pygame.draw.circle(screen, (255,255,255), pos, radius)

# Draw a smaller black circle to the screen using Cairo.
context = cairo.Context(cairo_surface)
context.set_source_rgb(0, 0, 0)
context.arc(size[0]/2, size[1]/2, min(size)/2*0.5, 0, 2*math.pi)
context.fill()

# Flip the changes into view.
pygame.display.flip()

# Wait for the user to quit.
while pygame.QUIT not in [e.type for e in pygame.event.get()]:
	pass
