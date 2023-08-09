"""Demo of hexagonal game of life."""
import math

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, hexmap

# import ctypes
# ctypes.windll.user32.SetProcessDPIAware()

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


def draw(surface: p.Surface, hexmap: hexmap.HexMap, k: float = 0.85) -> None:
    """Draw the hexmap on the surface."""

    # min_size = min(Hex.layout.size)

    for hx, col in hexmap.hexes_and_values():
        polygon = hx.polygon_pixels(k)

        gfxdraw.filled_polygon(surface, polygon, col)  # fill
        gfxdraw.aapolygon(surface, polygon, col)  # outline

        # p.draw.polygon(surface, col, polygon)


def click(
    hexmap: hexmap.HexMap, clicked_hex: Hex, initial: tuple[int, int, int]
) -> hexmap.HexMap:
    """Flip the clicked Hex in hexmap"""

    # Flip the color
    if clicked_hex in hexmap:
        hexmap[clicked_hex] = WHITE if initial == BLACK else BLACK

    return hexmap


def update(board: hexmap.HexMap) -> hexmap.HexMap:
    """Update the game of life HexMap"""

    new_hexmap = board.copy()
    new_hexmap.update_all(BLACK)

    for hx in board.hexes():
        ctr = sum(
            neighbor in board and board[neighbor] == WHITE
            for neighbor in hx.direct_neighbors
        )

        if ctr == 2:
            new_hexmap.insert(hx, WHITE)

    return new_hexmap


width = 1000
height = round((math.sqrt(3) / 2) * width)

r = 20
s = round((height / ((r + 1) * 2)) * 2 / 3)

# PYGAME
p.init()
screen = p.display.set_mode((width, height), 0, 32)
p.display.set_caption(
    "Hexagonal Game of Life, SPACE to play/pause, C to clear, CLICK to add/remove cells"
)

# HEXPY
Hex.pointy_layout(size=s, origin=(width // 2, height // 2))

# Create a HexMap object in the shape of a hexagon
board = hexmap.hexagon(radius=r, value=BLACK)

# Add a hollow hexagon of white hexes
board[hexmap.hexagon(radius=r, hollow=True)] = WHITE

# Plot the board using the default plot function
# board.plot(factor=0.85)

clock = p.time.Clock()
fps = 60

initial = BLACK
frame = 0
clicking = False
play = False
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        if event.type == p.KEYDOWN:
            if event.key == p.K_SPACE:
                play = not play

            elif event.key == p.K_c:
                board.update_all(value=BLACK)

        elif not play:
            if event.type == p.MOUSEBUTTONDOWN:
                clicked = Hex.from_pixel(p.mouse.get_pos())

                if clicked in board:
                    initial = board[clicked]
                    board = click(board, clicked, initial)
                    clicking = True

            elif clicking and event.type == p.MOUSEMOTION:
                clicked = Hex.from_pixel(p.mouse.get_pos())

                board = click(board, clicked, initial)

            if event.type == p.MOUSEBUTTONUP:
                clicking = False

    if play and frame % 6 == 0:
        board = update(board)
        frame = 1

    # update
    screen.fill(GRAY)

    # draw hexagons
    draw(screen, board)

    p.display.flip()
    clock.tick(fps)
    frame += 1
