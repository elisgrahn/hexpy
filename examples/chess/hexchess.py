"""Still WIP demo of hexagonal chess."""
import ctypes
import math
from typing import Optional

import pygame as p
from pieces import Bishop, King, Knight, Pawn, Queen, Rook, opponent
from pygame import gfxdraw
from utils import get_pieces, paint_board

from hexpy import Hex, Hexigo, hexmap

ctypes.windll.user32.SetProcessDPIAware()

TRUEBLACK = (0, 0, 0)
TRUEWHITE = (255, 255, 255)

BLACK = (35, 35, 35)
WHITE = (220, 220, 220)

GRAY = (120, 120, 120)
GREEN = (255, 0, 255)
DARKBROWN = (37, 26, 20)
# Copilot's DARKBROWN = (50, 25, 0)

# RGB values for colors
LIGHT = (210, 140, 69)
LIGHTER = (233, 173, 112)
LIGHTEST = (255, 207, 159)

# LIGHT, LIGHTER, LIGHTEST = tuple(
#     tuple(round(val / 255, 2) for val in col) for col in (LIGHT, LIGHTER, LIGHTEST)
# )

# FLOAT values for colors
# LIGHT = (0.82, 0.55, 0.27)
# LIGHTER = (0.91, 0.68, 0.44)
# LIGHTEST = (1.0, 0.81, 0.62)


def draw(
    surface: p.Surface,
    board: hexmap.HexMap,
    pieces: dict[str, set[Bishop | King | Knight | Pawn | Queen | Rook]],
    held: Optional[Bishop | King | Knight | Pawn | Queen | Rook] = None,
) -> None:
    """Draw the board and pieces using pygame.gfxdraw."""

    def draw_hex(
        hx: Hex,
        col: tuple[int, int, int],
        factor: float = 1,
        filled: bool = True,
    ) -> None:
        polygon = tuple(hx.polygon_pixels(factor))

        if filled:
            gfxdraw.filled_polygon(surface, polygon, col)  # fill
            gfxdraw.aapolygon(surface, polygon, TRUEBLACK)  # outline
        else:
            gfxdraw.aapolygon(surface, polygon, col)  # outline

    surface.fill(DARKBROWN)

    for hx, color in board.hexes_and_values():
        draw_hex(hx, color)

    for piece in pieces["white"] | pieces["black"]:
        # Add sprite drawing here

        # sprite_path = f"pieces-basic-png/{piece.team}-{str(piece.__class__).lower()}.png"

        # Use pygame to load the image
        # piece.image = p.image.load(sprite_path).convert_alpha()

        piece.rect.center = piece.pos.to_pixel()

        screen.blit(piece.image, piece.rect)

        # draw_hex(piece.pos, BLACK if piece.team == "black" else WHITE)

    if held is not None:
        draw_hex(held.pos, GREEN, filled=False)

        # TODO fix this
        for move in held.possible_moves(board, pieces):  # held.movemap:
            draw_hex(move, GRAY, 0.25)

        # else:
        #     surface.blit(piece.image, hx.to_pixel())

    p.display.flip()


def kill(
    pos: Hex,
) -> None:
    """Kill the piece at the given position"""

    for piece in pieces[opponent(turn)]:
        if piece.pos == pos:
            pieces[opponent(turn)].discard(piece)
            del piece
            break


# PYGAME
p.init()

fps = 30
clock = p.time.Clock()

width, height = 1300, 1300
screen = p.display.set_mode((width, height))
p.display.set_caption("Hexagonal Chess")

# HEXPY
# TODO layout should take a "from_height" or "from_width" argument alongside the size
Hex.flat_layout(65, (width // 2, height // 2))

# board contains color information while pieces contains piece information
board = paint_board(hexmap.hexagon(5), (LIGHT, LIGHTER, LIGHTEST))
pieces = get_pieces()

turn = "white"  # White starts

# piece = Knight
# team = "white"

# hx = tuple(getattr(piece, f"{team}_positions"))[1]

# board |= board & piece(pos=hx, team=team).movemap

# fig, ax = hexmap.plot(pieces + Hex(12, -6), {0: "k"})
# fig, ax = hexmap.plot(
#     board,
#     {0: "r", LIGHT: LIGHT, LIGHTER: LIGHTER, LIGHTEST: LIGHTEST},
#     ax=ax,
# )

# hexmap.show()

# board.plot()

# quit()
held = None
run = True
ctr = 0
while run:
    clock.tick(fps)

    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
            clicked = Hex.from_pixel(p.mouse.get_pos())

            p.image.save(screen, f"tmp/{(ctr := ctr + 1):03d}.png")
            print(ctr)

            if held and clicked == held.pos:
                held = None

            elif held and clicked in held.possible_moves(board, pieces):
                kill(clicked)
                held.move(clicked)
                held = None
                turn = opponent(turn)

            else:
                for piece in pieces[turn]:
                    if clicked == piece.pos:
                        held = piece

    draw(screen, board, pieces, held)

    p.display.update()
