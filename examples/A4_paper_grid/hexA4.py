"""Created just for fun because I wanted to draw in hexagonal grids on paper while sketching the logo"""

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, hexmap

# Following line is for windows not to duplicate window size
# ctypes.windll.user32.SetProcessDPIAware()


def draw(surface: p.Surface, hexmap: hexmap.HexMap, k: int = 1) -> None:
    """Draw the hexmap on surface
    :param surface: The pygame surface to draw on
    :param hexmap: The HexMap object to draw
    :optional k: Factor to mulptiply hexagon size with
    """

    for hex in hexmap.hexes():
        polygon = tuple(hex.polygon_pixels(k))

        # Using pygames gfxdraw in order to get antialiasing, turned out rastery otherwise
        gfxdraw.aapolygon(surface, polygon, GRAY)


GRAY = (78, 78, 78)
WHITE = (255, 255, 255)

p.init()

fps = 1
clock = p.time.Clock()

# A4 ratio
width, height = 297 * 5, 210 * 5
screen = p.display.set_mode((width, height))
p.display.set_caption("Hexagonal A4")

# Define our Hexagonal layout
Hex.set_layout(size=12, origin=(width // 2, height // 2), orientation="pointy")

# Create a HexMap object in the shape of a hexagon
hexmap = hexmap.hexagon(radius=50, value=0)

run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        elif event.type == p.MOUSEBUTTONDOWN:
            p.image.save(screen, f"A4_paper_grid.png")

    # update the game
    screen.fill(WHITE)

    # draw hexagons
    draw(screen, hexmap)

    p.display.flip()
    clock.tick(fps)
