import math

import pygame as p
from pygame import gfxdraw
from utils import make_move, start

from hexpy import Hex, Hexigo, hexmap

# import ctypes
# ctypes.windll.user32.SetProcessDPIAware()


def draw(
    surface: p.Surface,
    hxmp: hexmap.HexMap,
    red_highlight: Hex | None,
    size_factor: float = 1,
) -> None:
    """Draw the hexmap on surface while highlighting red_highlight"""

    min_size = Hex.hexlayout.size.x * size_factor

    # width = math.ceil(0.04 * min_size)
    radius = math.ceil(0.78 * min_size)

    for hx, value in hxmp.items():
        polygon = hx.polygon_pixels(size_factor)

        # Draw board hex
        gfxdraw.filled_polygon(surface, polygon, GREEN)
        gfxdraw.aapolygon(surface, polygon, DARKGREEN)

        # p.draw.polygon(surface, GREEN, polygon)  # fill
        # p.draw.polygon(surface, DARKGREEN, polygon, width)  # outline

        if value != 0:
            center = hx.to_pixel()

            if value == 1:
                gfxdraw.filled_circle(surface, center.x, center.y, radius, WHITE)
                # p.draw.circle(surface, WHITE, center, radius)

            elif value == -1:
                gfxdraw.filled_circle(surface, center.x, center.y, radius, BLACK)
                # p.draw.circle(surface, BLACK, center, radius)

            gfxdraw.aacircle(surface, center.x, center.y, radius, GRAY)
            # p.draw.circle(surface, GRAY, center, radius, width)

        if red_highlight != None and hx == red_highlight:
            red_center = red_highlight.to_pixel()
            gfxdraw.filled_circle(
                surface, red_center.x, red_center.y, round(0.2 * radius), RED
            )
            gfxdraw.aacircle(
                surface, red_center.x, red_center.y, round(0.2 * radius), RED
            )
            # p.draw.circle(surface, RED, red_highlight.to_pixel(), 0.2 * radius)


GREEN = (57, 140, 61)
DARKGREEN = (43, 103, 46)
GRAY = (78, 78, 78)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BEIGE = (227, 195, 159)
RED = (255, 0, 0)

# PYGAME
p.init()

fps = 30
clock = p.time.Clock()

# width, height = 1280, 960
width, height = 1000, 750
screen = p.display.set_mode((width, height))
p.display.set_caption("Othexo")

# HEXPY
Hex.pointy_layout(size=50, origin=(width // 2, height // 2))

# Create a HexMap object in the shape of a hexagon
hxmp = hexmap.hexagon(radius=4, value=0)
# hxmp = hexmap.rhombus(3, "qr", value=0)

# Remove Hexigo from the map
hxmp.pop(Hexigo)

# Set every even neighbor to white and odd to black
for i, direction in enumerate(Hexigo.directions):
    hxmp[direction] = -1 if i % 2 else 1

for i, direction in enumerate(Hex.o_clock((9, 3))):
    hxmp[direction * 2] = 1 if i % 2 else -1

# Initialise othexo
start(hxmp)

# plot the board
# hxmp.plot(
#     {0: "green", 1: "white", -1: "black", 2: "gray", -2: "gray"}, facecolor="brown"
# )
latest_move = None
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        elif event.type == p.MOUSEBUTTONDOWN:
            clicked = Hex.from_pixel(p.mouse.get_pos())

            if make_move(hxmp, clicked):
                latest_move = clicked

    # update the game
    screen.fill(BEIGE)

    # draw hexagons
    draw(screen, hxmp, latest_move)

    p.display.flip()
    clock.tick(fps)
