import ctypes

import pygame as p

from hexpy import Hex, hexmap

ctypes.windll.user32.SetProcessDPIAware()

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


def draw(surface: p.Surface, hexmap: hexmap) -> None:
    "Draw the hexmaps on surface"

    min_size = min(Hex.size)

    k = 0.95

    for hex, color in hexmap.hexes_and_values():
        polygon = tuple(hex.polygon_pixels(k))

        p.draw.polygon(surface, color, polygon)


def click(hexmap: hexmap, clicked_hex: Hex, initial: tuple[int, int, int]) -> hexmap:
    """Flip the clicked Hex in hexmap"""

    # Flip the color
    if clicked_hex in hexmap:
        hexmap[clicked_hex] = WHITE if initial == BLACK else BLACK

    return hexmap


def update(hexmap: hexmap) -> hexmap:
    """Update the game of life HexMap"""

    new_hexmap = hexmap.hexagon(radius=5, value=BLACK)

    for hex in hexmap.hexes():
        # Count the number of living neighbors
        ctr = 0
        for neighbor in hex.neighbors():
            if neighbor in hexmap and hexmap[neighbor] == WHITE:
                ctr += 1

        if ctr == 2:
            new_hexmap.set(hex, WHITE)

    return new_hexmap


p.init()

width, height = 1280, 960
screen = p.display.set_mode((width, height), 0, 32)
p.display.set_caption("Othexo")

# Define our Hexagonal layout
Hex.set_layout(size=50, origin=(width // 2, height // 2), orientation="pointy")

# Create a HexMap object in the shape of a hexagon
board = hexmap.hexagon(radius=5, value=BLACK)

clock = p.time.Clock()
fps = 30

initial = BLACK
frame = 0
clicking = False
play = False
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False
            p.quit()

        if event.type == p.KEYDOWN:
            if event.key == p.K_SPACE:
                play = not play

        elif not play:
            if event.type == p.MOUSEBUTTONDOWN:
                clicked = Hex.from_pixel(p.mouse.get_pos())
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
