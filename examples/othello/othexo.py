import ctypes
import math

import othexo_functions as othexo
import pygame as p

from hexpy import Hex, Hexigo, HexMap

# ctypes.windll.user32.SetProcessDPIAware()


def draw(surface: p.Surface, hexmap: HexMap, red_highlight: Hex | None) -> None:
    "Draw the hexmap on surface while highlighting red_highlight"

    min_size = min(Hex.size)

    k = 1  # 0.92

    width = math.ceil(k * 0.05 * min_size)
    radius = math.ceil(k * 0.78 * min_size)

    for hex, value in hexmap.items():
        hex: Hex

        polygon = tuple(hex.polygon_pixels(k))

        # Draw board hex
        p.draw.polygon(surface, GREEN, polygon)
        p.draw.polygon(surface, DARKGREEN, polygon, width)

        if value != 0:
            center = hex.to_pixel()

            if value == 1:
                p.draw.circle(surface, WHITE, center, radius)
                p.draw.circle(surface, GRAY, center, radius, width)

            elif value == -1:
                p.draw.circle(surface, BLACK, center, radius)
                p.draw.circle(surface, GRAY, center, radius, width)

            else:  # if value is -2 or 2
                p.draw.circle(surface, GRAY, center, radius, width)

        if red_highlight != None and hex == red_highlight:
            p.draw.circle(surface, RED, red_highlight.to_pixel(), 0.2 * radius)


GREEN = (57, 140, 61)
DARKGREEN = (43, 103, 46)
GRAY = (78, 78, 78)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BEIGE = (227, 195, 159)
RED = (255, 0, 0)

p.init()

fps = 30
clock = p.time.Clock()

width, height = 1280, 960
screen = p.display.set_mode((width, height))
p.display.set_caption("Othexo")

# Define our Hexagonal layout
Hex.set_layout(size=60, origin=(width // 2, height // 2), orientation="pointy")

# Create a HexMap object in the shape of a hexagon
hexmap = HexMap.hexagon(radius=4, value=0)
# hexmap = HexMap.diamond(value=0)

# Remove Hexigo from the map
hexmap.pop(Hexigo)

# Set every even neighbor to white and odd to black
for i, direction in enumerate(Hex.directions()):
    hexmap[direction] = -1 if i % 2 else 1

for i, direction in enumerate(Hex.directions((0, 3))):
    hexmap[direction * 2] = 1 if i % 2 else -1

# Initialise othexo
othexo.hexboard = hexmap
othexo.start()

latest_move = None
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False
            p.quit()

        elif event.type == p.MOUSEBUTTONDOWN:
            clicked = Hex.from_pixel(p.mouse.get_pos())

            if othexo.make_move(clicked):
                latest_move = clicked

    if not run:
        break

    # update the game
    screen.fill(BEIGE)

    # draw hexagons
    draw(screen, hexmap, latest_move)

    p.display.flip()
    clock.tick(fps)
