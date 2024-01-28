import random

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, Hexigo, hexmap

COLOR_MAP = {
    0: (120, 120, 120),
    2: (0, 0, 255),
    4: (0, 255, 0),
    8: (255, 0, 0),
    16: (255, 0, 255),
    32: (0, 128, 255),
}


class Hex2028:
    def __init__(self, surface: p.Surface = None, size: int = 2):
        self.size = size
        self.hxmp = hexmap.hexagon(radius=size, value=0)
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
            for i in range(1, self.size + 1)
            for hx in (start + i * dir1, start + i * dir2)
        )

        for hx in init_hexes:
            self._traverse(hx, -Hex.o_clock(hour))

        self.place_random()

    def draw_hex(
        self,
        hx: Hex,
        col: tuple[int, int, int],
        factor: float = 1,
        filled: bool = True,
    ) -> None:
        polygon = tuple(hx.polygon_pixels(factor))

        if filled:
            gfxdraw.filled_polygon(self.surface, polygon, col)  # fill
            gfxdraw.aapolygon(self.surface, polygon, (0, 0, 0))  # outline
        else:
            gfxdraw.aapolygon(self.surface, polygon, col)  # outline

    def draw(self):
        self.surface.fill((70, 70, 70))

        for hx, val in self.hxmp.hexes_and_values():
            self.draw_hex(hx, COLOR_MAP[val])

        p.display.flip()


def main():
    fps = 30
    clock = p.time.Clock()

    width, height = 800, 800
    Hex.pointy_layout(90, (width // 2, height // 2))

    screen = p.display.set_mode((width, height))
    p.display.set_caption("Hexagonal 2048")

    game = Hex2028(screen)

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
