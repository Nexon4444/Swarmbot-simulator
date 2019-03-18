import math
import cairo

WIDTH, HEIGHT = 256, 256

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
# cr = cairo.Context(surface)
# cr.scale(WIDTH, HEIGHT)  # Normalizing the canvas
# # pat = cairo.LinearGradient(0.0, 0.5, 0.0, 1.0)
# # pat.add_color_stop_rgba(1, 0.7, 0, 0, 1)  # First stop, 50% opacity
# # cr.rectangle(0, 0, 1, 1)
# # cr.set_source(pat)
# # cr.fill()
# cr.set_line_width(0.01)
# cr.set_source_rgb(0, 0, 0)
# cr.rectangle(0.25, 0.25, 0.5, 0.5)
# cr.stroke()

cr2 = cairo.Context(surface)
cr2.set_source_rgb(0, 0, 1)
cr2.translate(WIDTH/2, HEIGHT/2)
cr2.scale(WIDTH, HEIGHT)
# cr2.transform()
cr2.rotate(0.8)
cr2.rectangle(-0.2, -0.3, 0.4, 0.6)
cr2.fill()
cr2.set_source_rgb(1, 0, 0)
cr2.rectangle(0.2, 0.05, 0.1, 0.2)
cr2.fill()
cr2.rectangle(-0.2, 0.05, -0.1, 0.2)
cr2.fill()

#
# pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
# pat.add_color_stop_rgba(1, 0.7, 0, 0, 1)  # First stop, 50% opacity
# pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity
# pat.add_color_stop_rgba(0, 1, 1, 1, 1)
# # pat.add_color_stop_rgba(0, 1, 0, 0, 1)
# # ctx.translate(0.1, 0.3)
# ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
# ctx.set_source(pat)
# ctx.fill()
#
# ctx.set_line_width(0.1)
# ctx.set_source_rgb(0, 0, 0)
# ctx.rectangle(0.25, 0.25, 0.5, 0.5)
# ctx.stroke()
#
# ctx.translate(0.1, 0.1)  # Changing the current transformation matrix
#
# ctx.move_to(0, 0)
# # Arc(cx, cy, radius, start_angle, stop_angle)
# ctx.arc(0.2, 0.1, 0.1, -math.pi / 2, 0)
# ctx.line_to(0.5, 0.1)  # Line to (x,y)
# # Curve(x1, y1, x2, y2, x3, y3)
# ctx.curve_to(0.5, 0.2, 0.5, 0.4, 0.2, 0.8)
# ctx.close_path()
#
# ctx.set_source_rgb(0.3, 0.2, 0.5)  # Solid color
# ctx.set_line_width(0.02)
# ctx.stroke()

surface.write_to_png("example.png")  # Output to PNG

#
# radial = cairo.RadialGradient(0.25, 0.25, 0.1,  0.5, 0.5, 0.5)
# radial.add_color_stop_rgb(0,  1.0, 0.8, 0.8)
# radial.add_color_stop_rgb(1,  0.9, 0.0, 0.0)

# for i in range(1, 10):
#     for j in range(1, 10):
#         cr.rectangle(i/10.0 - 0.04, j/10.0 - 0.04, 0.08, 0.08)
# cr.set_source(radial)
# cr.fill()
#
# linear = cairo.LinearGradient(0.25, 0.35, 0.75, 0.65)
# linear.add_color_stop_rgba(0.00,  1, 1, 1, 0)
# linear.add_color_stop_rgba(0.25,  0, 1, 0, 0.5)
# linear.add_color_stop_rgba(0.50,  1, 1, 1, 0)
# linear.add_color_stop_rgba(0.75,  0, 0, 1, 0.5)
# linear.add_color_stop_rgba(1.00,  1, 1, 1, 0)
#
# cr.rectangle(0.0, 0.0, 1, 1)
# cr.set_source(linear)
# cr.fill()