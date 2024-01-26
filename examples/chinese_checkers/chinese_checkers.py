import ctypes

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, Hexigo, hexmap

ctypes.windll.user32.SetProcessDPIAware()


# DARKBROWN = (37, 26, 20)
GRAY = (120, 120, 120)
WHITE = (220, 220, 220)

RED = (201, 4, 21)
BLUE = (0, 112, 176)
BLACK = (33, 29, 30)
YELLOW = (214, 202, 20)
PURPLE = (89, 61, 112)
GREEN = (3, 136, 71)


def create_board() -> hexmap.HexMap:
    """Create a HexMap with the initial Chinese Checkers board layout"""

    def rotate(hxmp: hexmap.HexMap) -> hexmap.HexMap:
        """Rotate the HexMap around Hexigo"""

        return hxmp.transform(lambda hx: hx.rotated_left())

    hexagon = hexmap.hexagon(4)
    triangle = hexmap.triangle(1, origin_offset=Hex(-3, 6))

    for color in (RED, BLUE, BLACK, YELLOW, PURPLE, GREEN):
        hexagon.insert(triangle, color)

        triangle = rotate(triangle)

    return hexagon


def draw(surface: p.Surface, board: hexmap.HexMap, moves: hexmap.HexMap) -> None:
    """Draw the board using pygame.gfxdraw."""

    def draw_hex(
        hx: Hex,
        col: tuple[int, int, int],
        factor: float = 1,
    ) -> None:
        polygon = hx.polygon_pixels(factor)

        gfxdraw.filled_polygon(surface, polygon, col)  # fill
        gfxdraw.aapolygon(surface, polygon, BLACK)  # outline

    def draw_circle(
        hx: Hex,
        col: tuple[int, int, int],
        factor: float = 1,
    ) -> None:
        pixel = hx.to_pixel()
        x, y = round(pixel)
        r = int(Hex.hexlayout.size.x * factor)

        gfxdraw.filled_circle(surface, x, y, r, col)
        gfxdraw.aacircle(surface, x, y, r, BLACK)

    surface.fill(GRAY)

    # if moves is not None:
    #     for hx in moves:
    #         draw_hex(hx, BLACK, 0.9)

    for hx, color in board.hexes_and_values():
        if color is None:
            if moves and hx in moves:
                draw_circle(hx, BLACK, 0.5)

            else:
                draw_circle(hx, WHITE, 0.5)

        else:
            draw_circle(hx, color, 0.7)

        if moves and hx == moves.origin_offset:
            draw_circle(hx, BLACK, 0.2)

        # draw_hex(hx, color)


def get_moves(board: hexmap.HexMap, clicked: Hex) -> hexmap.HexMap:
    """_summary_

    Args:
        board (hexmap.HexMap): _description_
        clicked (Hex): _description_

    Returns:
        hexmap.HexMap: moves
    """

    moves = hexmap.new(origin_offset=clicked)

    if clicked not in board or board[clicked] is None:
        return moves

    for dir in Hexigo.directions:
        hx = clicked + dir

        if hx in board:
            if board[hx] is None:
                moves.insert(dir)

            elif hx + dir in board and board[hx + dir] is None:
                moves.insert(2 * dir)

    return moves


def move(
    board: hexmap.HexMap,
    moves: hexmap.HexMap,
    clicked: Hex,
) -> tuple[hexmap.HexMap, hexmap.HexMap]:
    """Move to the clicked Hex if it is a valid move.

    Args:
        board (hexmap.HexMap): _description_
        moves (hexmap.HexMap): _description_
        clicked (Hex): _description_

    Returns:
        tuple[hexmap.HexMap, hexmap.HexMap]: board, moves
    """
    held = moves.origin_offset

    if clicked == held:
        # We clicked on the origin, finish the move
        return board, moves.cleared()

    if clicked not in moves:
        # Clicked is not a valid move
        return board, moves

    board[clicked] = board[held]
    board[held] = None

    if clicked.distance(held) == 2:
        # We jumped, get new moves from the new position

        new_moves = get_moves(board, clicked)

        if new_moves:
            non_jumps = tuple(hx for hx in new_moves if hx.distance(clicked) != 2)
            new_moves.pop(non_jumps)

        return board, new_moves

    # If we didn't jump, we're done

    return board, moves.cleared()


p.init()

fps = 30
clock = p.time.Clock()

width, height = 1000, 1000
screen = p.display.set_mode((width, height))
p.display.set_caption("Chinese Checkers")

Hex.pointy_layout(35, (width // 2, height // 2))

board = create_board()

run: bool = True
moves: hexmap.HexMap = hexmap.new()
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        elif event.type == p.MOUSEBUTTONDOWN:
            clicked = Hex.from_pixel(p.mouse.get_pos())

            if moves:
                board, moves = move(board, moves, clicked)

            else:
                moves = get_moves(board, clicked)

    draw(screen, board, moves)
    p.display.update()
