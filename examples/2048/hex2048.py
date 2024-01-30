import random

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, Hexigo, hexmap

BACKGROUND = (185, 173, 161)
LINES = (65, 60, 55)
TEXT = (121, 114, 104)
COLOR_MAP = {
    0: (213, 204, 199),
    2: (236, 227, 218),
    4: (235, 225, 200),
    8: (232, 180, 130),
    16: (232, 154, 108),
    32: (230, 131, 102),
    64: (228, 103, 71),
    128: (240, 215, 146),
    256: (232, 206, 113),
    512: (231, 202, 102),
    1024: (240, 208, 109),
    2048: (230, 195, 79),
}


class Hex2028:
    def __init__(
        self,
        surface: p.Surface,
        hx_size: int,
        hx_origin: tuple[int, int],
        board_size: int = 2,
    ):
        self.board_size = board_size
        self.hx_size = hx_size

        Hex.pointy_layout(hx_size, hx_origin)
        self.hxmp = hexmap.hexagon(radius=board_size, value=0)

        self.hxmp.pop(Hexigo)
        self.surface = surface
        self.keybinds = {
            p.K_e: 1,
            p.K_d: 3,
            p.K_x: 5,
            p.K_z: 7,
            p.K_a: 9,
            p.K_w: 11,
        }
        self.font = p.font.SysFont("arial", hx_size)

    def _move_fwd(self, hx: Hex, direc: Hex, val: int):
        while hx + direc in self.hxmp and self.hxmp[hx + direc] in {0, val}:
            self.hxmp[hx + direc] = 2 * val if self.hxmp[hx + direc] == val else val
            self.hxmp[hx] = 0

            hx = hx + direc

    def _traverse(self, hx: Hex, direc: Hex):
        while hx in self.hxmp or hx == Hexigo:
            if hx != Hexigo and self.hxmp[hx] != 0:
                self._move_fwd(hx, -direc, self.hxmp[hx])

            hx = hx + direc

    def place_random(self):
        placed = 0
        while placed < 2:
            rndm_hx = random.choice(tuple(self.hxmp.hexes()))

            if self.hxmp[rndm_hx] == 0:
                self.hxmp[rndm_hx] = 2
                placed += 1

    def make_move(self, key: str):
        hour = self.keybinds.get(key)

        if not hour:
            return

        start = 2 * Hex.o_clock(hour)

        dir1 = Hex.o_clock((hour - 4) % 12)
        dir2 = Hex.o_clock((hour + 4) % 12)

        init_hexes = (start,) + tuple(
            hx
            for i in range(1, self.board_size + 1)
            for hx in (start + i * dir1, start + i * dir2)
        )

        for hx in init_hexes:
            self._traverse(hx, -Hex.o_clock(hour))

        self.place_random()

    def draw_text(
        self,
        hx: Hex,
        text: str,
    ):
        rendered = self.font.render(text, True, TEXT)
        rect = rendered.get_rect(center=hx.to_pixel())
        self.surface.blit(rendered, rect)

    def draw_circle(
        self,
        hx: Hex,
        color: tuple[int, int, int],
        radius: float = 0.6,
    ):
        pos = hx.to_pixel()
        rad = round(self.hx_size * radius)

        gfxdraw.filled_circle(self.surface, pos.x, pos.y, rad, color)  # fill
        gfxdraw.aacircle(self.surface, pos.x, pos.y, rad, LINES)  # outline

    def draw_hex(
        self,
        hx: Hex,
        color: tuple[int, int, int],
        factor: float = 1,
    ):
        polygon = tuple(hx.polygon_pixels(factor))

        gfxdraw.filled_polygon(self.surface, polygon, color)  # fill
        gfxdraw.aapolygon(self.surface, polygon, LINES)  # outline

    def draw(self):
        self.surface.fill(BACKGROUND)

        for hx, val in self.hxmp.hexes_and_values():
            self.draw_hex(hx, COLOR_MAP[0])

            if val != 0:
                self.draw_circle(hx, COLOR_MAP[val])
                self.draw_text(hx, str(val))

        p.display.flip()


def main():
    fps = 30
    clock = p.time.Clock()

    width, height = 800, 800

    p.init()
    screen = p.display.set_mode((width, height))
    p.display.set_caption("Hexagonal 2048")

    game = Hex2028(screen, 90, (width // 2, height // 2))

    game.hxmp[Hex.o_clock(3)] = 2
    game.hxmp[Hex.o_clock(6)] = 2

    # game.hxmp.plot({2: "b", 4: "g", 8: "pink", 16: "purple"})

    run = True
    while run:
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False

            if event.type == p.KEYDOWN:
                game.make_move(event.key)
                # game.hxmp.plot({2: "b", 4: "g", 8: "pink", 16: "purple"})

        game.draw()
        clock.tick(fps)


if __name__ == "__main__":
    main()
