import ctypes
import math
from typing import Iterable

import logo
import pygame as p

from src.hexpy.hexpy import Hex, HexMap

ctypes.windll.user32.SetProcessDPIAware()


def draw(surface: p.Surface, hexmaps: Iterable[HexMap], cover: HexMap) -> None:
    "Draw the hexmaps on surface"

    min_size = min(Hex.size)

    k = 0.9

    width = math.ceil(k * 0.08 * min_size)

    h_map, e_map, x_map, p_map, y_map = hexmaps

    h_map += Hex.diagonal() * -6
    e_map += Hex.diagonal() * -3
    p_map += Hex.diagonal() * 3
    y_map += Hex.diagonal() * 6

    e_cover = cover + Hex.diagonal() * -2
    p_cover = cover + Hex.diagonal() * 2

    ordered_letters = (h_map, y_map, e_cover, e_map, p_cover, p_map, cover, x_map)

    for i, letter in enumerate(ordered_letters):
        for hex, color in letter.items():
            hex: Hex

            polygon = tuple(hex.polygon_pixels(k))

            # print(f"{hex=} {color=}")

            # Draw hexes
            p.draw.polygon(surface, color, polygon)

            edge_color = PY_GRAY if color != WHITE else WHITE
            p.draw.polygon(surface, edge_color, polygon, width)

            # gfxdraw.aapolygon(surface, polygon, GRAY)


Q_GREEN = (172, 217, 127)
R_BLUE = (127, 204, 242)
S_PINK = (242, 140, 242)
P_BLUE = (54, 115, 165)
Y_YELLOW = (255, 211, 66)

PY_GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

p.init()

width, height = 1800, 800
screen = p.display.set_mode((width, height), 0, 32)
p.display.set_caption("Othexo")

# Define our Hexagonal layout
Hex.set_layout(size=40, origin=(width // 2, height // 2), orientation="flat")

# Create a HexMap object in the shape of a hexagon
# bg_map = HexMap.hexagon(radius=20, value=WHITE)

# bg_map[Hexigo] = BLACK

letters = logo.animation(0)

cover = HexMap.hexagon(1, WHITE)

clock = p.time.Clock()
fps = 6

counter = 1
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False
            p.quit()

        # if event.type == p.MOUSEBUTTONDOWN:
        # letters = logo.animation(counter, letters)
        # counter += 1
        # p.image.save(screen, f"logo_gif/frame_{counter}.png")

    if not run:
        break

    # update
    screen.fill(WHITE)

    letters = logo.animation(counter, letters)
    counter += 1

    # draw hexagons
    draw(screen, letters, cover)

    p.display.flip()
    clock.tick(fps)
