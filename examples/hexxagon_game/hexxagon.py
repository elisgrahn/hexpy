from typing import Any, Optional

import pygame as p

from hexpy import Hex, Hexigo, hexmap

BLACK = (0, 0, 0)
RED = (200, 0, 0)
DARKRED = (80, 0, 0)
BLUE = (0, 0, 200)
DARKBLUE = (0, 0, 80)
ORANGE = (200, 100, 0)
GREEN = (0, 200, 0)
GRAY = (70, 70, 70)


def draw_hex(hx: Hex, c: tuple[int, int, int], w: int = 0, factor: float = 0.9):
    polygon = tuple(hx.polygon_pixels(factor))

    if w != 0:
        p.draw.polygon(surface, GRAY, polygon, 0)

    p.draw.polygon(surface, c, polygon, w)


def draw(board: hexmap.HexMap, moves: Optional[hexmap.HexMap], turn):
    # surface.fill(BLACK)

    surface.fill(DARKRED if turn == "p1" else DARKBLUE)

    func = lambda v1, v2: v2 if v1 == "" else v1

    hxmp = board.union(moves, func) if moves is not None else board

    for hx, val in hxmp.hexes_and_values():
        draw_hex(hx, BLACK, 0, 1.05)

        if val == "p1":
            draw_hex(hx, RED)

        elif val == "p2":
            draw_hex(hx, BLUE)

        elif val == "spread":
            draw_hex(hx, GREEN, 3, 0.85)

        elif val == "jump":
            draw_hex(hx, ORANGE, 3, 0.85)

        else:
            color = GRAY
            draw_hex(hx, color)

    p.display.flip()


def click(hxmp: hexmap.HexMap, pos: tuple[int, int]) -> Hex | None:
    clicked = Hex.from_pixel(pos)

    return clicked if clicked in hxmp else None


def get_moves(hxmp: hexmap.HexMap, clicked: Hex, turn: str):
    if hxmp[clicked] == turn:
        move_func = lambda v1, v2: v2 if v1 == "" else None
        return hxmp.intersection(move_mask + clicked, move_func)

        # The following does the same, but is IMO harder to read
        # return (move_mask + clicked).intersection(hxmp[hxmp == ""])


def make_move(
    hxmp: hexmap.HexMap, moves: hexmap.HexMap, clicked: Hex, origin: Hex, turn: str
):
    if moves[clicked] == "spread":
        hxmp[clicked] = turn

    elif moves[clicked] == "jump":
        hxmp[clicked] = turn
        hxmp[origin] = ""

    else:
        return hxmp

    for hx in clicked.direct_neighbors:
        if hx in hxmp and hxmp[hx] not in {"", turn}:
            hxmp[hx] = turn

    return hxmp


def count(hxmp: hexmap.HexMap):
    p1 = len(hxmp[hxmp == "p1"])
    p2 = len(hxmp[hxmp == "p2"])

    # p1 = len(tuple(v for v in hxmp.values() if v == "p1"))
    # p2 = len(tuple(v for v in hxmp.values() if v == "p2"))

    p.display.set_caption(f"Hexxagon      YOU: {p1}      ENEMY: {p2}")


#     if moves is not None and clicked in moves:
#         if moves[clicked] == "spread":
#             spread(board)

# PYGAME
p.init()
p.display.set_caption("Hexxagon")
surface = p.display.set_mode((600, 600))
clock = p.time.Clock()


# HEXPY
Hex.flat_layout(size=int(45 * 1.1), origin=(300, 300))

r = 3

board = hexmap.hexagon(r, "")

board[Hex(0, r, -r)] = "p1"
board[Hex(0, -r, r)] = "p2"

direct_neighbors = hexmap.hexagon(1, "spread", hollow=True)
second_neighbors = hexmap.hexagon(2, "jump", hollow=True)

move_mask = direct_neighbors | second_neighbors

# test_move_mask = eval(repr(move_mask))


# print(move_mask == test_move_mask)
# move_mask.plot({1: "g", 2: "orange"})

# moves = board.intersection(move_mask + Hex(0, 3, -3), move_func)

# moveboard = board | moves

# print(moveboard)

# move_mask.plot({"p1": "r", "p2": "b", "spread": "g", "jump": "orange"})

turn = "p1"
clicked: Hex | None
origin: Hex = Hexigo
moves = None
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        if event.type == p.MOUSEBUTTONDOWN:
            if clicked := click(board, p.mouse.get_pos()):
                #
                if moves is None or board[clicked] == turn:
                    moves = get_moves(board, clicked, turn)
                    origin = clicked

                elif clicked in moves and board[clicked] == "":
                    board = make_move(board, moves, clicked, origin, turn)
                    turn = "p1" if turn == "p2" else "p2"
                    moves = None

            count(board)

    draw(board, moves, turn)

    clock.tick(60)
