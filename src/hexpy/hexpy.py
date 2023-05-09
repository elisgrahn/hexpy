from __future__ import annotations

import math
from collections.abc import Iterable
from itertools import cycle, islice
from typing import Any

import numpy as np


class Point(tuple):
    "Represents a Point"

    def __new__(cls, x: int | float, y: int | float):
        """
        Create a Point

        :param x: Required point coordinate of type 'int' or 'float'
        :param y: Required point coordinate of type 'int' or 'float'
        """

        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError(
                f"Point got incorrect coordinate types: x and y must be of type 'int' or 'float'"
            )

        return tuple.__new__(cls, (x, y))

    @property
    def x(self) -> int | float:
        return self[0]

    @property
    def y(self) -> int | float:
        return self[1]

    @property
    def coords(self) -> tuple[int | float, int | float]:
        return tuple(self)

    def __repr__(self) -> str:
        "Return a nicely formatted Point representation string"
        x, y = self.coords

        return f"Point({x=}, {y=})"

    def __round__(self, ndigits: int = 0) -> Point:
        return Point(round(self.x), round(self.y))

    def __add__(self, other: Point | tuple | int | float) -> Point:
        "Add a Point with other"

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x + other.x, self.y + other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x + other, self.y + other)

        else:
            raise TypeError(
                f"Cannot add {self} of type {type(self)} to {other} of type {type(other)}"
            )

    def __sub__(self, other: Point | tuple | int | float) -> Point:
        "Subtract a point by other"

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x - other.x, self.y - other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x - other, self.y - other)

        else:
            raise TypeError(
                f"Cannot subtract {self} of type {type(self)} by {other} of type {type(other)}"
            )

    def __mul__(self, other: Point | tuple | int | float) -> Point:
        "Multiplicate a Point"

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x * other.x, self.y * other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)

        else:
            raise TypeError(
                f"Cannot multiplicate {self} of type {type(self)} with {other} of type {type(other)}"
            )

    def __truediv__(self, other: Point | tuple | int | float) -> Point:
        "Divide a Point"

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x / other.x, self.y / other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x / other, self.y / other)

        else:
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {other} of type {type(other)}"
            )

    def __floordiv__(self, other: Point | tuple | int | float) -> Point:
        "Divide a Point while rounding the results"

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return round(Point(self.x / other.x, self.y / other.y))

        elif isinstance(other, (int, float)):
            return round(Point(self.x / other, self.y / other))

        else:
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {other} of type {type(other)}"
            )

    def __neg__(self) -> Point:
        "Negate the values of self, effectively flipping it around Origo"
        return Point(-self.x, -self.y)

    def __eq__(self, other: Point) -> bool:
        "Check if Point equals something"

        if isinstance(other, Point):
            return self.x == other.y and self.x == other.y

        else:
            return False


class Hex:
    """Represents a Hexagon"""

    __slots__ = ("q", "r", "s")

    def __init__(
        self,
        q: int | float,
        r: int | float,
        s: int | float | None = None,
    ) -> None:
        """
        Create a Hexagon

        :param q: Required hex coordinate
        :param r: Required hex coordinate
        :param s: Optional hex coordinate

        q + r + s must be equal to 0
        """

        if s == None:
            s = -(q + r)

        self.q = q
        self.r = r
        self.s = s

        if not all(isinstance(coord, (int, float)) for coord in (q, r, s)):
            raise TypeError(
                f"{self} got incorrect coordinate types: q, r and s must be of type 'int' or 'float'"
            )

        if round(q + r + s) != 0.0:
            raise ValueError(
                f"{self} got incorrect coordinates: q + r + s must be equal to 0"
            )

    # @property
    # def s(self) -> int | float:
    #     return -(self.q + self.r)

    @property
    def cube_coords(self) -> tuple[int | float, ...]:
        "A tuple containing q, r and s"
        return (self.q, self.r, self.s)

    @property
    def axial_coords(self) -> tuple[int | float, int | float]:
        "A tuple containing q and r"
        return (self.q, self.r)

    def __setitem__(self, attrlist, valuelist):
        """
        Used to change q, r and s in a dict like manner

        hex = Hex(1, 2, -3)

        hex['q', 'r'] = (2, 1)

        'hex' will then become Hex(q=2, r=1, s=-3)
        """

        print(f"{attrlist = }, {valuelist = }")

        for attr, value in zip(attrlist, valuelist):
            setattr(self, attr, value)

        # self.__dict__.update(zip(attrlist, valuelist))

    def __round__(self) -> Hex:
        "Round the Hex coordinates to whole integers"

        # Apperently these listcomprehensions are slower... :(
        # (q, dq), (r, dr), (s, ds) = ((round(crd), abs(round(crd) - crd)) for crd in (self.q, self.r, self.s))

        # Walrus flex:
        # (q, dq), (r, dr), (s, ds) = ((rnd := round(crd), abs(rnd - crd)) for crd in (self.q, self.r, self.s))

        # rounded q, r and s
        q = round(self.q)
        r = round(self.r)
        s = round(self.s)

        # diff or delta from rounding
        dq = abs(q - self.q)
        ds = abs(r - self.r)
        dr = abs(s - self.s)

        # in order to avoid getting bad coords, the one with the biggest diff will be calculated from the other two
        if dq > dr and dq > ds:
            q = -(r + s)
        elif dr > ds:
            r = -(q + s)
        else:
            s = -(q + r)

        return Hex(q, r, s)

    def __iter__(self) -> Iterable[int | float]:
        "Iterate through the axial coords"

        for coord in self.axial_coords:
            yield coord

    def __hash__(self) -> int:
        "Return (q, r) as a hash number"

        return hash(self.axial_coords)

    def __repr__(self) -> str:
        "Return a nicely formatted Hex representation string"
        q, r, s = self.cube_coords

        return f"Hex({q=}, {r=}, {s=})"

    def distance_to(self, other: Hex) -> int:
        "Get the Hex distance from self to other Hex"

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot take distance from {self} of type {type(self)} to {other} of type {type(other)}"
            )

        return len(self - other)

    def __add__(self, other: Hex) -> Hex:
        "Add Hex with another Hex"

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot add {self} of type {type(self)} to {other} of type {type(other)}"
            )

        return Hex(self.q + other.q, self.r + other.r)

    def __sub__(self, other: Hex) -> Hex:
        "Subtract Hex by another Hex"

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot subtract {self} of type {type(self)} from {other} of type {type(other)}"
            )

        return Hex(self.q - other.q, self.r - other.r)

    def __mul__(self, k: int | float) -> Hex:
        "Multiplicate Hex by factor k"

        if not isinstance(k, (int, float)):
            raise TypeError(
                f"Cannot multiplicate {self} of type {type(self)} with {k} of type {type(k)}"
            )

        return Hex(self.q * k, self.r * k)

    def __truediv__(self, d: int | float) -> Hex:
        "Divide Hex by divisor d"

        if not isinstance(d, (int, float)):
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {d} of type {type(d)}"
            )

        return Hex(self.q / d, self.r / d)

    def __floordiv__(self, d: int | float) -> Hex:
        "Divide Hex by divisor d and round the results"

        if not isinstance(d, (int, float)):
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {d} of type {type(d)}"
            )

        return round(Hex(self.q / d, self.r / d))

    def __eq__(self, other: Hex | Any) -> bool:
        "Check if Hex is equal to other, we only need to compare axial coords since q + r + s = 0"

        if isinstance(other, Hex):
            return self.axial_coords == other.axial_coords

        return False

    def __len__(self) -> int:
        "Get the distance from Hex to Hexigo"
        return round((abs(self.q) + abs(self.r) + abs(self.s)) / 2)

    def __contains__(self, n: int | float) -> bool:
        "Check if Hex has n as a coord"

        return n in self.cube_coords

    def __neg__(self) -> Hex:
        "Negate the values of self, effectively flipping it around Hexigo"
        return Hex(-self.q, -self.r, -self.s)

    def __lshift__(self, input: int | Hex | tuple[Hex, int]) -> Hex:
        """Convienience function for rotate_left() and rotate_left_around()"""

        # Just steps was provided, rotate around Hexigo
        if isinstance(input, int):
            return self.rotate_left(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            return self.rotate_left_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            return self.rotate_left_around(*input)

        else:
            # TODO
            raise TypeError("")

    def rotate_left(self, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the right around Hexigo
        :param steps: Optional amount of 60 degree steps to rotate
        :returns: Hex rotated around Hexigo
        """
        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the left
        hex = Hex(*islice(cycle(self.cube_coords), 3 - n, 6 - n))

        # Negate the hex values if rotating odd amount of steps
        return -hex if steps % 2 else hex

    def rotate_left_around(self, other: Hex, steps: int = 1):
        """Rotate the Hex 60 * steps degrees to the left around other Hex
        :param other: The other Hex to rotate around
        :param steps: Optional amount of 60 degree steps to rotate
        :returns: Hex rotated around other
        """
        return (self - other).rotate_left(steps) + other

    def __rshift__(self, input: int | Hex | tuple[Hex, int]) -> Hex:
        "Convienience function for rotate_right() and rotate_right_around()"

        # Just steps was provided, rotate around Hexigo
        if isinstance(input, int):
            return self.rotate_left(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            return self.rotate_left_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            return self.rotate_left_around(*input)

        else:
            # TODO
            raise TypeError("")

    def rotate_right(self, steps: int = 1):
        """Rotate Hex 60 * steps degrees to the right around Hexigo
        :param steps: Optional amount of 60 degree steps to rotate
        :returns: Hex rotated around other
        """
        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the right
        hex = Hex(*islice(cycle(self.cube_coords), n, 3 + n))

        # Negate the hex values if rotating odd amount of steps
        return -hex if steps % 2 else hex

    def rotate_right_around(self, other: Hex, steps: int = 1) -> Hex:
        """Rotate Hex 60 * steps degrees to the right around other Hex
        :param other: The other Hex to rotate around
        :param steps: Optional amount of 60 degree steps to rotate
        :returns: Hex rotated around other
        """
        return (self - other).rotate_right(steps) + other

    @classmethod
    def direction(cls, idx: int = 0) -> Hex:
        "Get Hex direction at index idx"

        if not hasattr(cls, "_directions"):
            cls._directions = (
                Hex(1, 0, -1),
                Hex(1, -1, 0),
                Hex(0, -1, 1),
                Hex(-1, 0, 1),
                Hex(-1, 1, 0),
                Hex(0, 1, -1),
            )

        if not isinstance(idx, int):
            raise TypeError(
                f"Direction index got incorrect index type: 'idx' must be of type 'int', got {idx=} of type {type(idx)}"
            )

        if not -6 <= idx < 6:
            raise IndexError(
                f"Directions indexes got incorrect index: All indexes in 'idxs' must be 0 <= 'idx' < 6, got {idx=} of type {type(idx)}"
            )

        return cls._directions[idx]

    @classmethod
    def directions(cls, idxs: Iterable[int] = range(6)) -> Iterable[Hex]:
        "Yield Hex directions at indexes idxs"

        if not hasattr(cls, "_directions"):
            cls._directions = (
                Hex(1, 0, -1),
                Hex(1, -1, 0),
                Hex(0, -1, 1),
                Hex(-1, 0, 1),
                Hex(-1, 1, 0),
                Hex(0, 1, -1),
            )

        if not isinstance(idxs, Iterable):
            raise TypeError(
                f"Directions got incorrect indexes: Idxs must be iterable, got {idxs=} of type {type(idxs)}"
            )

        for idx in idxs:
            if not isinstance(idx, int):
                raise TypeError(
                    f"Directions indexes got incorrect index type: All indexes in 'idxs' must be of type 'int', got {idx=} of type {type(idx)}"
                )

            if not -6 <= idx < 6:
                raise IndexError(
                    f"Directions indexes got incorrect index: All indexes in 'idxs' must be 0 <= 'idx' < 6, got {idx=} of type {type(idx)}"
                )

            yield cls._directions[idx]

    def neighbor(self, idx: int = 0) -> Hex:
        "Return the neighboring Hex at index idx"

        return self + self.direction(idx)

    def neighbors(self, idxs: Iterable[int] = range(6)) -> Iterable[Hex]:
        "Yield the neighboring Hexes at indexes idxs"

        for neighbor in self.directions(idxs):
            yield self + neighbor

    @classmethod
    def diagonal(cls, idx: int = 0) -> Hex:
        "Get Hex diagonal direction at index idx"

        if not hasattr(cls, "_diagonals"):
            cls._diagonals = (
                Hex(2, -1, -1),
                Hex(1, -2, 1),
                Hex(-1, -1, 2),
                Hex(-2, 1, 1),
                Hex(-1, 2, -1),
                Hex(1, 1, -2),
            )

        if not isinstance(idx, int):
            raise TypeError(
                f"Diagonal index got incorrect index type: 'idx' must be of type 'int', got {idx=} of type {type(idx)}"
            )

        if not -6 <= idx < 6:
            raise IndexError(
                f"Diagonal indexes got incorrect index: All indexes in 'idxs' must be 0 <= 'idx' < 6, got {idx=} of type {type(idx)}"
            )

        return cls._diagonals[idx]

    @classmethod
    def diagonals(cls, idxs: Iterable[int] = range(6)) -> Iterable[Hex]:
        "Yield Hex diagonal directions at indexes idxs"

        if not hasattr(cls, "_diagonals"):
            cls._diagonals = (
                Hex(2, -1, -1),
                Hex(1, -2, 1),
                Hex(-1, -1, 2),
                Hex(-2, 1, 1),
                Hex(-1, 2, -1),
                Hex(1, 1, -2),
            )

        if not isinstance(idxs, Iterable):
            raise TypeError(
                f"Diagonal got incorrect indexes: Idxs must be iterable, got {idxs=} of type {type(idxs)}"
            )

        for idx in idxs:
            if not isinstance(idx, int):
                raise TypeError(
                    f"Diagonal indexes got incorrect index type: All indexes in 'idxs' must be of type 'int', got {idx=} of type {type(idx)}"
                )

            if not -6 <= idx < 6:
                raise IndexError(
                    f"Diagonal indexes got incorrect index: All indexes in 'idxs' must be 0 <= 'idx' < 6, got {idx=} of type {type(idx)}"
                )

            yield cls._diagonals[idx]

    def diagonal_neighbor(self, idx: int = 0) -> Hex:
        "Return the diagonally neighboring Hex at index idx"

        return self + self.diagonal(idx)

    def diagonal_neighbors(self, idxs: Iterable[int] = range(6)) -> Iterable[Hex]:
        "Yield the diagonally neighboring Hexes at indexes idxs"

        for neighbor in self.diagonals(idxs):
            yield self + neighbor

    def lerp_to(self, other: Hex, t: float) -> Hex:
        "Lerp from self to other at fraction t"

        return self * (1.0 - t) + other * t

        # return Hex(
        #     self.q * (1.0 - t) + other.q * t,
        #     self.r * (1.0 - t) + other.r * t,
        #     self.s * (1.0 - t) + other.s * t,
        # )

    def linedraw_to(self, other: Hex) -> Iterable[Hex]:
        "Yield all Hexes amongst a line between self and other"

        # Number of hexes that will be reqired
        N = self.distance_to(other)

        nudged_self = Hex(self.q + 1e-06, self.r + 1e-06, self.s - 2e-06)
        nudged_other = Hex(other.q + 1e-06, other.r + 1e-06, other.s - 2e-06)

        step_size = 1.0 / max(N, 1)
        for i in range(0, N + 1):
            yield round(nudged_self.lerp_to(nudged_other, i * step_size))

    def to_pixel(self) -> Point:
        "Return pixel at the center of self"
        return round(self.center_point())

    def center_point(self) -> Point:
        "Return the exact center point of self, without rounding the results"

        # TODO add check to warn if a layout hasn't been defined

        transformed = Point(*np.matmul(self.forward, np.array([self.q, self.r])))

        return round(transformed * self.size + self.origin)

    def corner_offset(self, idx: int) -> Point:
        "Return corner offset from center of hex at index idx"

        angle = 2.0 * math.pi * (self.start_angle - idx) / 6.0
        trig_vec = Point(math.cos(angle), math.sin(angle))

        return trig_vec * self.size

    def polygon_pixels(self, factor: float = 1) -> Iterable[Point]:
        "Yeild all pixels forming self as a polygon"

        center = self.center_point()

        for i in range(6):
            offset = self.corner_offset(i)

            yield round(center + offset * factor)

    @classmethod
    def from_pixel(cls, pixel: Point | tuple[int | float, int | float]) -> Hex:
        "Return the Hex closest to the provided Point"

        pixel = (Point(*pixel) - cls.origin) / cls.size

        transformed = np.matmul(cls.backward, np.array([pixel.x, pixel.y]))
        return round(Hex(*transformed))

    @classmethod
    def set_layout(
        cls,
        size: Point | tuple[int, int] | int,
        origin: Point | tuple[int, int],
        orientation: str = "pointy",
    ) -> None:
        """
        Define a layout containing Hex grid metadata.

        :param size: The pixel size of hexagons. If an int is provided hexagons will be regular, otherwise they can be stretched
        :param origin: The pixel origin, i.e. at what Pixel Hexigo will be
        :param orientation: The orientation of hexagons. Either "pointy" ⬢ or "flat" ⬣.
        """

        cls.origin = Point(*origin)

        if isinstance(size, int):
            cls.size = Point(size, size)

        elif isinstance(size, tuple):
            cls.size = Point(*size)

        elif isinstance(size, Point):
            cls.size = size

        else:
            # TODO
            raise TypeError("")

        if isinstance(orientation, str):
            if orientation == "pointy":
                cls.pointy()

            elif orientation == "flat":
                cls.flat()

            else:
                raise ValueError(
                    'Argument "orientation" needs to be either "pointy" or "flat"'
                )
        else:
            # TODO
            raise TypeError("")

    @classmethod
    def pointy(cls) -> None:
        "Define grid metadata for pointy orientation"

        cls.start_angle = 0.5

        sqrt3 = math.sqrt(3)

        # Used to calculate hex to pixel
        cls.forward = ((sqrt3, sqrt3 / 2), (0, 3 / 2))

        # Used to calculate pixel to hex
        cls.backward = ((sqrt3 / 3, -1 / 3), (0, 2 / 3))

    @classmethod
    def flat(cls) -> None:
        "Define grid metadata for flat orientation"

        cls.start_angle = 0

        sqrt3 = math.sqrt(3)

        # Used to calculate hex to pixel
        cls.forward = ((3 / 2, 0), (sqrt3 / 2, sqrt3))

        # Used to calculate pixel to hex
        cls.backward = ((2 / 3, 0), (-1 / 3, sqrt3 / 3))


class HexMap(dict):
    """Represents a generic Hexagonal grid"""

    def __init__(
        self, map: dict[Hex, Any] | None = None, default_value: Any = None
    ) -> None:
        "Create an empty map of hexes"
        if map == None:
            super().__init__()
        else:
            super().__init__(map)

        # The value that will be assigned to hexagons created with ".add()"
        self.default_value = default_value

    def hexes(self) -> Iterable[Hex]:
        "Wrapper function for .keys() to improve readability"
        return self.keys()

    def get_hexes(self, desired_value: Any) -> Iterable[Hex]:
        "Get all hexes that point to the desired value"

        for hex, value in self.items():
            if value == desired_value:
                yield hex

    def add(self, hex: Hex, value: Any = None) -> None:
        """Add a Hex to the HexMap, reverse of .pop() with optional value"""

        if value == None:
            self[hex] = self.default_value

        else:
            print("adding None")
            self[hex] = value

    def __add__(self, other: Hex) -> HexMap:
        "Add all Hexes in HexMap with another Hex"

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot add {other} of type {type(other)} to Hex in HexMap"
            )

        # for hex in self.keys():
        #    self[hex + other] = self.pop(hex)

        return HexMap(
            {hex + other: value for hex, value in self.items()}, self.default_value
        )

    def __sub__(self, other: Hex) -> HexMap:
        "Subtract all Hexes in HexMap with another Hex"

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot add {other} of type {type(other)} to Hex in HexMap"
            )

        # for hex in self.keys():
        #    self[hex + other] = self.pop(hex)

        return HexMap(
            {hex - other: value for hex, value in self.items()}, self.default_value
        )

    @classmethod
    def hexagon(cls, radius: int, value: Any = None, hollow: bool = False) -> HexMap:
        """Creates a HexMap in the shape of a Hexagon ⬢
        :param radius: The number of hexes from the center
        :param value: The value that should be assigned to all Hexagons
        :return: The hexagon HexMap
        """
        # TODO add bool attribute for if the shape should be filled or hollow

        hexmap = HexMap()

        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)

            for r in range(r1, r2 + 1):
                # skip all inner hexes if hollow is True
                if hollow and not (q == -radius or q == radius or r == r1 or r == r2):
                    continue

                hexmap[Hex(q, r, -(q + r))] = value

        return hexmap

    # @classmethod
    # def parallelogram(cls, value: Any = None, axes) -> HexMap:
    #     """Creates a HexMap in the shape of a Parallelogram ▰
    #     :param radius: The number of hexes from the center
    #     :param value: The value that should be assigned to all Hexagons
    #     :return: The parallelogram HexMap"""

    # @classmethod
    # def rhombus(cls, value: Any = None, radius) -> HexMap:
    #     """Creates a HexMap in the shape of a rhombus (aka diamond) ⬧
    #     :param value: The value that should initially be assigned to all Hexagons
    #     :param axes: jskeow
    #     :return: The rhombus HexMap

    # @classmethod
    # def triangle(cls, value: Any = None, axes: str = "qs") -> HexMap:
    #     """Creates a HexMap in the shape of a Triangle ▲
    #     :param radius: The number of hexes from the center
    #     :param value: The value that should be assigned to all Hexagons
    #     :return: The triangle HexMap"""

    # @classmethod
    # def rectangle(cls, value: Any = None, axes):
    #     """Creates a HexMap in the shape of a Rectangle ▬
    #     :param radius: The number of hexes from the center
    #     :param value: The value that should be assigned to all Hexagons
    #     :return: The rectangle HexMap"""

    # @classmethod
    # def square(cls, value: Any = None, axes):
    #     """Creates a HexMap in the shape of a Square ■
    #     :param radius: The number of hexes from the center
    #     :param value: The value that should be assigned to all Hexagons
    #     :return: The square HexMap"""


Hexigo = Hex(0, 0, 0)


# hex0 = Hex(1, 2, -3)
# hex1 = Hex(10, 10, -20)

# print(hex0 << hex1)


# print(type(HexMap.hexagon(2, (0, 0, 0), True).hexes()))
