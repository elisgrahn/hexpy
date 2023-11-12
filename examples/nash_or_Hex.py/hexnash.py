from os import path
from queue import Queue
from typing import Optional

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, hexmap
from hexpy.point import Point

# import ctypes
# ctypes.windll.user32.SetProcessDPIAware()

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GRAY = (80, 80, 80)
RED = (200, 0, 0)
DARKRED = (80, 0, 0)
BLUE = (0, 0, 200)
DARKBLUE = (0, 0, 80)


def draw_hex(
    hx: Hex,
    col: tuple[int, int, int],
    factor: float = 1.0,
    edgecolor: Optional[tuple[int, int, int]] = None,
) -> None:
    """Draw a hexagon on the surface using gfxdraw."""
    polygon = hx.polygon_pixels(factor)

    # fill
    gfxdraw.filled_polygon(surface, polygon, col)

    # outline
    gfxdraw.aapolygon(surface, polygon, col if edgecolor is None else edgecolor)


def draw_poly(
    polygon: tuple[tuple[int, int], ...],
    col: tuple[int, int, int] = RED,
) -> None:
    """Draw a general polygon"""
    gfxdraw.filled_polygon(surface, polygon, col)  # fill
    gfxdraw.aapolygon(surface, polygon, col)  # outline


def draw_hexagons(hxmp: hexmap.HexMap, turn: tuple[int, int, int]):
    """Draw the board."""

    for hx, col in hxmp.hexes_and_values():
        draw_hex(hx, col, edgecolor=BLACK)


def draw_border(hxmp: hexmap.HexMap, s: int):
    """Draw the border."""

    def middle(p1: Point, p2: Point) -> tuple[Point]:
        return (p1 + (p2 - p1) / 2,)

    for hx, col in hxmp.hexes_and_values():
        draw_hex(hx, col, 1.5)

        if all(abs(coord) == s for coord in hx.axial_coords):
            corners = hx.polygon_pixels(1.5)

            if hx.axial_coords == (s, s):
                draw_poly(corners[3:] + corners[:1])

            elif hx.axial_coords == (-s, -s):
                draw_poly(corners[:4])

            elif hx.axial_coords == (s, -s):
                draw_poly(middle(*corners[1:3]) + corners[2:5] + middle(*corners[4:]))

            elif hx.axial_coords == (-s, s):
                draw_poly(
                    middle(*corners[4:])
                    + corners[5:]
                    + corners[:2]
                    + middle(*corners[1:3])
                )


def pathify(came_from: dict[Hex, Hex], current: Hex) -> tuple[Hex, ...]:
    path = [current]

    while current := came_from[current]:
        path.append(current)

    return tuple(path)


def sides(turn: tuple[int, int, int], s: int) -> tuple[set[Hex], set[Hex]]:
    """Get the two sides for the given turn.

    Args:
        turn (tuple[int, int, int]): The turn to get the sides for.
        s (int): The size of the board.

    Raises:
        ValueError: If the turn is not valid.

    Returns:
        tuple[set[Hex, ...], set[Hex, ...]]: The two sides.
    """
    if turn == RED:
        starts = set(Hex(-s, -s).linedraw(Hex(s, -s)))
        goals = set(Hex(-s, s).linedraw(Hex(s, s)))

    elif turn == BLUE:
        starts = set(Hex(-s, -s).linedraw(Hex(-s, s)))
        goals = set(Hex(s, -s).linedraw(Hex(s, s)))

    else:
        raise ValueError(f"Invalid turn: {turn}")

    return starts, goals


def check_board(turn: tuple[int, int, int], s: int) -> None | tuple[Hex, ...]:
    """Check if the given turn has won."""
    best_path = None

    frontier = Queue()
    came_from = {}  # path A->B is stored as came_from[B] == A

    starts, goals = sides(turn, s)

    # print(starts, goals)

    for hx in starts:
        if board[hx] == turn:
            frontier.put(hx)
            came_from[hx] = None

    while not frontier.empty():
        current: Hex = frontier.get()

        if current in goals:
            path = pathify(came_from, current)

            if best_path is None or len(path) < len(best_path):
                best_path = path

        for nxt in current.direct_neighbors:
            if nxt in board and board[nxt] == turn and nxt not in came_from:
                frontier.put(nxt)
                came_from[nxt] = current

    return best_path


def highlight(hxmp: hexmap.HexMap, path: tuple[Hex, ...]) -> hexmap.HexMap:
    """Highlight the given path by darkening everything else."""

    for hx, col in hxmp.hexes_and_values():
        if hx in path:
            continue

        if col == RED:
            hxmp[hx] = DARKRED

        elif col == BLUE:
            hxmp[hx] = DARKBLUE

        else:
            hxmp[hx] = GRAY

    return hxmp


# PYGAME
p.init()
p.display.set_caption("Hex / Nash, press SPACE to reset, click first piece to swap")

width, height = 900, 580
size = 5

surface = p.display.set_mode((width, height))
clock = p.time.Clock()

# HEXPY
Hex.pointy_layout(30, (width // 2, height // 2))

board = hexmap.rhombus(size, "qr", WHITE)
border = hexmap.rhombus(size, "qr", RED, hollow=True)

one_side, other_side = sides(BLUE, size)
border[one_side] = BLUE
border[other_side] = BLUE

# for hx in board:
#     board[hx] = random.choice((RED, BLUE))

# board[board == RED] = DARKRED
# board[board == BLUE] = DARKBLUE


# if path := check_board(RED, size):
#     board[path] = DARKRED

# if path := check_board(BLUE, size):
#     board[path] = DARKBLUE

# print(*Hex(5, 5).corner_offsets())
# quit()

# board.plot(title="Hex/Nash", size_factor=0.9, draw_axes=True)

first_piece = True
turn = RED
run = True
while run:
    clock.tick(30)

    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        if event.type == p.MOUSEBUTTONDOWN:
            # TODO WOULD BE NICE USING 'board.from_pixel()' instead!
            clicked = Hex.from_pixel(event.pos)

            if clicked in board:
                if board[clicked] == WHITE:
                    board[clicked] = turn

                    if path := check_board(turn, size):
                        board = highlight(board, path)
                    turn = BLUE if turn == RED else RED

                elif first_piece:
                    board[clicked] = WHITE
                    board[clicked.reflected("s")] = turn
                    turn = BLUE if turn == RED else RED

                if first_piece and turn == RED:
                    first_piece = False

        elif event.type == p.KEYDOWN and event.key == p.K_SPACE:
            # If space is pressed, reset
            board = hexmap.rhombus(size, "qr", WHITE)
            first_piece = True
            turn = RED

    surface.fill(DARKRED if turn == RED else DARKBLUE)

    draw_border(border, size)
    draw_hexagons(board, turn)

    p.display.update()
