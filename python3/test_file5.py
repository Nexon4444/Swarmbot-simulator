import pymunk
import time
space = pymunk.Space()
# space.gravity = (0, -200)
mass = 50
poly_square = pymunk.Poly.create_box(None, size=(50, 50))
poly_moment = pymunk.moment_for_poly(mass, poly_square.get_vertices())
poly_body = pymunk.Body()
poly_square = poly_body
poly_body.position = 250, 100

poly_body.mass = 200
poly_body.moment = 500
poly_body.position = 50, 50

space.add(poly_body)



while True:
    space.step(0.02)
    poly_square.apply_force_at_local_point((0, 300), (-10, 0))
    # poly_body.force = 0, 200
    print(poly_body.position)
    print(poly_body.angle)
    print(poly_body.force)
    print("\n")
    time.sleep(0.5)