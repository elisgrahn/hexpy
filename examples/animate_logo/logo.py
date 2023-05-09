import time

from src.hexpy.hexpy import Hex, Hexigo, HexMap

Q_GREEN = (172, 217, 127)
R_BLUE = (127, 204, 242)
S_PINK = (242, 140, 242)
P_BLUE = (54, 115, 165)
Y_YELLOW = (255, 211, 66)


def animation(
    frame: int, hexmaps: tuple[HexMap, ...] | None = None
) -> tuple[HexMap, ...]:
    """Animate hexpy logo"""

    if frame == 0 or hexmaps == None:
        h = HexMap.hexagon(radius=2, value=Q_GREEN, hollow=True)
        e = HexMap.hexagon(radius=2, value=R_BLUE, hollow=True)
        x = HexMap.hexagon(radius=2, value=S_PINK, hollow=True)
        p = HexMap.hexagon(radius=2, value=P_BLUE, hollow=True)
        y = HexMap.hexagon(radius=2, value=Y_YELLOW, hollow=True)

        h.default_value = Q_GREEN
        e.default_value = R_BLUE
        x.default_value = S_PINK
        p.default_value = P_BLUE
        y.default_value = Y_YELLOW

        h += Hex.diagonal() * 6
        e += Hex.diagonal() * 3
        p -= Hex.diagonal() * 3
        y -= Hex.diagonal() * 6

        # return (h, e, x, p, y)

    else:
        h, e, x, p, y = hexmaps

    frame = frame % 23 - 11

    if frame == -11:
        h -= Hex.diagonal()
        e -= Hex.diagonal()
        p += Hex.diagonal()
        y += Hex.diagonal()

    elif frame == -10:
        h -= Hex.diagonal()
        e -= Hex.diagonal()
        p += Hex.diagonal()
        y += Hex.diagonal()

    elif frame == -9:
        h -= Hex.diagonal()
        y += Hex.diagonal()

    elif frame == -8:
        h -= Hex.diagonal()
        y += Hex.diagonal()

    elif frame == -7:
        h -= Hex.diagonal()
        e -= Hex.diagonal()
        p += Hex.diagonal()
        y += Hex.diagonal()

    elif frame == -6:
        h -= Hex.diagonal()
        y += Hex.diagonal()

    elif frame == -5:
        h.pop(Hex.direction(-1) * 2)

        x.pop(Hex.direction(2) * 2)

        y.pop(Hex.direction(2) * 2)

    elif frame == -4:
        h.pop(Hex.diagonal(-1))
        h.pop(Hex.diagonal(-2))
        h.add(Hex.diagonal() + Hex.direction(-1) * 2)
        h.add(Hex.diagonal(3) + Hex.direction(-1) * 2)
        h.add(Hex.diagonal(3) + Hex.direction(2) * 2)

        e.pop(Hex.diagonal())
        e.add(Hex.direction(1))

        x.pop(Hex.diagonal(1))
        x.pop(Hex.diagonal(2))
        x += Hex.direction(2)
        x.add(Hex.diagonal(-1))
        x.add(Hex.diagonal(-2))

        p.add(Hex.direction(-2) * 2 + Hex.direction(-1))

        y.pop(Hex.diagonal(1))
        y.pop(Hex.diagonal(2))
        y.add(Hex.diagonal() + Hex.direction(2) * 2)
        y.add(Hex.diagonal(3) + Hex.direction(2) * 2)
        y.add(Hex.diagonal() + Hex.direction(-1) * 2)

    elif frame == -3:
        h.add(Hex.diagonal(3) + Hex.direction(2) * 3)

        e.add(Hexigo)

        x.add(Hex.diagonal() + Hex.direction(-1) * 2)
        x.add(Hex.diagonal(3) + Hex.direction(-1) * 2)

        p.add(Hex.diagonal(3) + Hex.direction(-1) * 3)

        y.add(Hex.diagonal() + Hex.direction(-1) * 3)
        y.add(Hex.diagonal() + Hex.direction(-1) * 4)

    elif frame == -2:
        h.add(Hex.diagonal(3) + Hex.direction(2) * 4)

        e.add(Hex.direction(3))

        x.pop(Hex.diagonal() + Hex.direction(2) * 2)
        x.pop(Hex.diagonal(3) + Hex.direction(2) * 2)
        x += Hex.direction(2)
        x.add(Hex.diagonal() + Hex.direction(-1) * 2)
        x.add(Hex.diagonal(3) + Hex.direction(-1) * 2)

        p.add(Hex.diagonal(3) + Hex.direction(-1) * 4)

        y.add(Hex.direction() + Hex.direction(-1) * 4)
        y.add(Hex.direction(-1) * 5)

    # FINISHED LOGO
    elif frame == -1:
        h.add(Hex.diagonal(3) + Hex.direction(2) * 5)

        p.add(Hex.diagonal(3) + Hex.direction(-1) * 5)

        y.add(Hex.direction(-2) + Hex.direction(-1) * 4)
        y.add(Hex.diagonal(3) + Hex.direction(-1) * 4)

    elif frame == 0:
        time.sleep(0.5)
        pass

    elif frame == 1:
        h.pop(Hex.diagonal(3) + Hex.direction(2) * 5)

        p.pop(Hex.diagonal(3) + Hex.direction(-1) * 5)

        y.pop(Hex.direction(-2) + Hex.direction(-1) * 4)
        y.pop(Hex.diagonal(3) + Hex.direction(-1) * 4)

    elif frame == 2:
        h.pop(Hex.diagonal(3) + Hex.direction(2) * 4)

        e.pop(Hex.direction(3))

        x.pop(Hex.diagonal() + Hex.direction(2) * 2)
        x.pop(Hex.diagonal(3) + Hex.direction(2) * 2)
        x += Hex.direction(2)
        x.add(Hex.diagonal() + Hex.direction(-1) * 2)
        x.add(Hex.diagonal(3) + Hex.direction(-1) * 2)

        p.pop(Hex.diagonal(3) + Hex.direction(-1) * 4)

        y.pop(Hex.direction() + Hex.direction(-1) * 4)
        y.pop(Hex.direction(-1) * 5)

    elif frame == 3:
        h.pop(Hex.diagonal(3) + Hex.direction(2) * 3)

        e.pop(Hexigo)

        x.pop(Hex.diagonal() + Hex.direction(2) * 2)
        x.pop(Hex.diagonal(3) + Hex.direction(2) * 2)

        p.pop(Hex.diagonal(3) + Hex.direction(-1) * 3)

        y.pop(Hex.diagonal() + Hex.direction(-1) * 3)
        y.pop(Hex.diagonal() + Hex.direction(-1) * 4)

    elif frame == 4:
        h.add(Hex.diagonal(-1))
        h.add(Hex.diagonal(-2))
        h.pop(Hex.diagonal() + Hex.direction(-1) * 2)
        h.pop(Hex.diagonal(3) + Hex.direction(-1) * 2)
        h.pop(Hex.diagonal(3) + Hex.direction(2) * 2)

        e.add(Hex.diagonal())
        e.pop(Hex.direction(1))

        x.pop(Hex.diagonal(1))
        x.pop(Hex.diagonal(2))
        x += Hex.direction(2)
        x.add(Hex.diagonal(-1))
        x.add(Hex.diagonal(-2))

        p.pop(Hex.direction(-2) * 2 + Hex.direction(-1))

        y.add(Hex.diagonal(1))
        y.add(Hex.diagonal(2))
        y.pop(Hex.diagonal() + Hex.direction(2) * 2)
        y.pop(Hex.diagonal(3) + Hex.direction(2) * 2)
        y.pop(Hex.diagonal() + Hex.direction(-1) * 2)

    elif frame == 5:
        h.add(Hex.direction(-1) * 2)

        x.add(Hex.direction(-1) * 2)

        y.add(Hex.direction(2) * 2)

    elif frame == 6:
        h += Hex.diagonal()
        y -= Hex.diagonal()

    elif frame == 7:
        h += Hex.diagonal()
        e += Hex.diagonal()
        p -= Hex.diagonal()
        y -= Hex.diagonal()

    elif frame == 8:
        h += Hex.diagonal()
        y -= Hex.diagonal()

    elif frame == 9:
        h += Hex.diagonal()
        y -= Hex.diagonal()

    elif frame == 10:
        h += Hex.diagonal()
        e += Hex.diagonal()
        p -= Hex.diagonal()
        y -= Hex.diagonal()

    elif frame == 11:
        h += Hex.diagonal()
        e += Hex.diagonal()
        p -= Hex.diagonal()
        y -= Hex.diagonal()

    return (h, e, x, p, y)
