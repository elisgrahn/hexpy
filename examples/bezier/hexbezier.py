"""Demo of plotting a hexagonal bezier curve using hexpy and pygame"""
from collections.abc import Iterable

import pygame as p
from pygame import gfxdraw

from hexpy import Hex, hexmap

# Following line is for windows not to duplicate window size
# ctypes.windll.user32.SetProcessDPIAware()

RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)


def blend(color1: tuple[int, int, int], color2: tuple[int, int, int], ratio: float):
    """Blend two colors together at the given ratio"""

    return tuple(round(c1 * ratio + c2 * (1 - ratio)) for c1, c2 in zip(color1, color2))


def draw(
    surface: p.Surface,
    bezier_curve: Iterable[Hex],
    bezier_control: list[Hex],
    steps: int = 10,
) -> None:
    """Draw the bezier curve on the surface

    Args:
        surface (p.Surface): The pygame surface to draw on
        bezier_curve (tuple[Hex, ...]): The bezier curve to draw
        bezier_control (list[Hex]): The control points of the bezier curve
        steps (Iterator[Hex]): The number of hexes in the curve
    """
    screen.fill(WHITE)

    # for hx in hexmap.hexes():
    #     polygon = tuple(hx.polygon_pixels())

    #     # Using pygames gfxdraw in order to get antialiasing, turned out rastery otherwise
    #     gfxdraw.aapolygon(surface, polygon, GRAY)

    for i, hx in enumerate(bezier_curve):
        polygon = tuple(hx.polygon_pixels())

        color = blend(RED, BLUE, i / steps)

        gfxdraw.filled_polygon(surface, polygon, color)
        gfxdraw.aapolygon(surface, polygon, BLACK)

    prior_point = ()

    for i, hx in enumerate(bezier_control):
        color = YELLOW if i % 4 in {0, 3} else RED

        point = round(hx.to_pixel())

        if prior_point and i != 2:
            gfxdraw.line(surface, prior_point.x, prior_point.y, point.x, point.y, BLACK)  # type: ignore

        gfxdraw.filled_circle(surface, point.x, point.y, 5, color)  # type: ignore
        gfxdraw.aacircle(surface, point.x, point.y, 5, BLACK)  # type: ignore

        prior_point = point

    p.display.flip()


def cubic_bezier(
    hx0: Hex, hx1: Hex, hx2: Hex, hx3: Hex, steps: int = 10
) -> Iterable[Hex]:
    # steps = sum(
    #     h1.distance(h2) for h1, h2 in zip([hx0, hx1, hx2], [hx1, hx2, hx3])
    # )

    # The following is neccessary to minimize the risk of hexes landing directly in between two grid positions
    hx0_ngd = hx0.nudged()
    hx1_ngd = hx1.nudged()
    hx2_ngd = hx2.nudged()
    hx3_ngd = hx3.nudged()

    step_size = 1.0 / max(steps - 1, 1)
    for i in range(steps - 1):
        A = hx0_ngd.lerp(hx1_ngd, i * step_size)
        B = hx1_ngd.lerp(hx2_ngd, i * step_size)
        C = hx2_ngd.lerp(hx3_ngd, i * step_size)
        D = A.lerp(B, i * step_size)
        E = B.lerp(C, i * step_size)
        F = D.lerp(E, i * step_size)

        yield round(F.nudged())

    yield hx3


GRAY = (78, 78, 78)
WHITE = (255, 255, 255)

p.init()

fps = 60
clock = p.time.Clock()

width, height = 297 * 4, 210 * 4
screen = p.display.set_mode((width, height))
p.display.set_caption("Bezier")

# Define our Hexagonal layout
Hex.pointy_layout(size=12, origin=(width // 2, height // 2))

# h0 = Hex(-3, 0, 3)
# h1 = Hex(-1, -4, 5)
# h2 = Hex(10, -20, 10)
# h3 = Hex(3, 0, -3)

h0 = Hex(q=-38, r=22, s=16)
h1 = Hex(q=-15, r=19, s=-4)
h2 = Hex(q=3, r=-19, s=16)
h3 = Hex(q=37, r=-21, s=-16)
bezcontrol = [h0, h1, h2, h3]

steps = 100
bezcurve = cubic_bezier(*bezcontrol, steps=steps)

# drawing once before the loop to avoid a blank screen
draw(screen, bezcurve, bezcontrol, steps)

held = None
holding = False
run = True
while run:
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False

        elif not holding and event.type == p.MOUSEBUTTONDOWN:
            pressed = Hex.from_pixel(p.mouse.get_pos())

            for i, control_hex in enumerate(bezcontrol):
                if pressed == control_hex:
                    held = i
                    holding = True

        elif holding and event.type == p.MOUSEMOTION:
            moved = Hex.from_pixel(p.mouse.get_pos())

            if held is not None:
                bezcontrol[held] = moved

            bezcurve = cubic_bezier(*bezcontrol, steps=steps)
            draw(screen, bezcurve, bezcontrol, steps)

        elif holding and p.MOUSEBUTTONUP:
            holding = False

    # I don't draw here since I keep the bezcurve as a generator,
    # otherwice just make it into a tuple and draw here

    clock.tick(fps)
