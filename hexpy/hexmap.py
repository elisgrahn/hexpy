from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from hex import Hex
from point import Point


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
