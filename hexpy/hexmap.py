from __future__ import annotations

import builtins
import os.path as osp
import pickle
import warnings
from collections.abc import Iterable, Set
from pathlib import Path
from typing import Any

from hexpy.point import Point

from .hex import Hex, Hexigo

# import dill # TODO maybe replace pickle with dill


def new(value, origin):
    """Creates a new empty HexMap"""
    return HexMap(default_value=value, origin_offset=origin)


# TODO following functions
# def fromdict():
#     """Create a HexMap from the given dict with Hex as keys"""

# def fromlist():
#     """Create a new HexMap from the given list of Hex"""


def open(filepath: str) -> HexMap:
    """Open a saved HexMap at filepath

    :param filepath: Path to the HexMap ``.pkl`` file
    :returns: HexMap saved at ``filepath``
    """

    with builtins.open(filepath, "rb") as f:
        return pickle.load(f)


class HexMap(dict):
    """Represents a generic Hexagonal grid"""

    """TODO SOMETHING MORE LIKE THIS:
    This class represents an image object.  To create
    :py:class:`~PIL.Image.Image` objects, use the appropriate factory
    functions.  There's hardly ever any reason to call the Image constructor
    directly."""

    def __init__(
        self,
        hexes: dict[Hex, Any] | None = None,
        default_value: Any = None,
        origin_offset: Hex = Hexigo,
    ) -> None:
        """Create an empty map of hexes

        :param default_value: The default value that will be assigned to Hexes inthe  HexMap.
        :param hexmap_origin: Hexigo is moved to hexmap_origin, every Hex that is added will be offset by origin.
        """

        self.default = default_value
        self.origin = origin_offset

        if isinstance(hexes, dict):
            super().__init__(hexes)

        else:
            super().__init__()

    def _new(self, hexes: dict[Hex, Any]):
        """Create a new HexMap with the same default value and origin offset with other hexes"""
        return HexMap(hexes, self.default, self.origin)

    def copy(self):
        """Create a new identical Hexmap

        :returns: A copy of this Hexmap"""
        return HexMap(dict(self), self.default, self.origin)

    def keys(self) -> Set[Hex]:
        """Wrapper function of .keys() to provide type annotation.

        :returns: A set-like object providing a view on HexMap keys"""
        return super().keys()

    def hexes(self) -> Set[Hex]:
        """Wrapper function of .keys() to improve readability.

        :returns: A set-like object providing a view on HexMap keys: hexes"""
        return self.keys()

    def items(self) -> Set[tuple[Hex, Any]]:
        """Wrapper function of .items() to provide type annotation.

        :returns: A set-like object providing a view on HexMap items."""
        return super().items()

    def hexes_and_values(self) -> Set[tuple[Hex, Any]]:
        """Wrapper function of .values() to improve readability.

        :returns: A set-like object providing a view on HexMap items, hex: value."""
        return self.items()

    def get_hexes(self, desired_values: Any | Iterable[Any]) -> Iterable[Hex]:
        """Yield all hexes that point to the desired value(s).

        :param desired_values: The value(s) to sort hexes by
        :returns: Generator of Hexes
        """

        for hex, value in self.items():
            if (
                isinstance(desired_values, Iterable)
                and value in desired_values
                or value == desired_values
            ):
                yield hex

    def __setitem__(self, __key: Hex | HexMap, __value: Any) -> None:
        """Set ``self[key]`` to ``value``.

        :param __key: If a ``Hex`` is provided only that will be set and if a ``HexMap`` is provided all Hexes in the hsexmap will be changed
        """

        if isinstance(__key, Hex):
            # When running pickle.load self.origin hasn't been defined yet
            origin = Hexigo if not hasattr(self, "origin") else self.origin

            super().__setitem__(__key + origin, __value)

        elif isinstance(__key, HexMap):
            for hex in __key:
                super().__setitem__(hex, __value)

        else:
            # TODO
            raise TypeError("")

    def __getitem__(self, __key: Hex | HexMap) -> Any | HexMap:
        """Get value at self[key]"""

        if isinstance(__key, Hex):
            return super().__getitem__(__key)

        elif isinstance(__key, HexMap):
            intersec = HexMap(origin_offset=__key.origin)

            for hex in __key:
                if hex in super().keys():
                    value = super().__getitem__(hex)
                    intersec.set(hex, value)

            return intersec

        else:
            # TODO
            raise TypeError("")

    def set(self, hex_or_hexmap: Hex | HexMap, value: Any = None) -> None:
        """Set a Hex in the HexMap with an optional value otherwise set to default value, inplace"""

        if isinstance(hex_or_hexmap, Hex):
            self[hex_or_hexmap] = self.default if value == None else value

        elif isinstance(hex_or_hexmap, HexMap):
            if value == None:
                self[hex_or_hexmap] = self.default

            else:
                self[hex_or_hexmap] = value

        else:
            # TODO
            raise TypeError("")

    def set_all(self, value: Any = None) -> None:
        """Set all Hexes (keys) to a certain value
        :param value: The value to change Hexes to, if left as None all Hexes will become the default value
        """

        if value == None:
            value = self.default

        for hex in self.hexes():
            self[hex] = value

    def __add__(self, other: Hex | HexMap) -> HexMap:
        """Move all Hexes in this HexMap with another Hex or add Hexes from another HexMap

        :param other: Either a ``Hex`` or a ``HexMap``
            If a Hex is provided all Hexes in this HexMap will be offset by other,
            but if a HexMap is provided all Hexes in other will be added to this HexMap.
        """

        if isinstance(other, Hex):
            return self._new({hex + other: value for hex, value in self.items()})

        elif isinstance(other, HexMap):
            return self._new({**self, **other})

        else:
            # TODO
            raise TypeError(
                f"Cannot add {other} of type {type(other)} to Hex in HexMap"
            )

    # __radd__ is intentionally undefined since it matters which hexmap is first

    def __sub__(self, other: Hex | HexMap) -> HexMap:
        """Move all Hexes in this HexMap with another Hex or remove Hexes from another HexMap

        :param other: Either a ``Hex`` or a ``HexMap``
            If a Hex is provided all Hexes in this HexMap will be offset by other,
            but if a HexMap is provided all Hexes in other will be removed from this HexMap.
        """

        if isinstance(other, Hex):
            return self._new({hex - other: value for hex, value in self.items()})

        elif isinstance(other, HexMap):
            return self._new({k: self[k] for k in self.keys() - other.keys()})

        else:
            # TODO
            raise TypeError(
                f"Cannot subtract {other} of type {type(other)} to Hex in HexMap"
            )

    # __rsub__ is intentinally undefined

    def __and__(self, other: HexMap) -> HexMap:
        """Intersect two HexMaps."""

        if isinstance(other, HexMap):
            return self._new({k: self[k] for k in self.keys() & other.keys()})

        else:
            # TODO
            raise TypeError("")

    def __mul__(self, other: HexMap) -> HexMap:
        """Intersect two HexMaps."""
        return self & other

    def __xor__(self, other: HexMap) -> HexMap:
        """Get difference of two HexMaps."""

        if isinstance(other, HexMap):
            return self._new(
                {
                    k: self[k] if k in self else other[k]
                    for k in self.keys() ^ other.keys()
                }
            )

        else:
            # TODO
            raise TypeError("")

    def __truediv__(self, other: HexMap) -> HexMap:
        """Get difference of two HexMaps."""

        return self ^ other

    def intersection(self, other: HexMap) -> HexMap:
        """Intersect two :ref:`HexMaps` getting all intersecting Hexes as a new HexMap.

        :param other: The other :py:class:`~hexpy.HexMap` object.
        :returns: A :py:class:`~hexpy.HexMap` object.
        """

        return self & other

    def difference(self, other: HexMap) -> HexMap:
        """Differentiate two :ref:`HexMaps` getting all differanting Hexes as a new HexMap.

        :param other: The other :py:class:`~hexpy.HexMap` object.
        :returns: A :py:class:`~hexpy.HexMap` object.
        """

        return self ^ other

    def save(self, filepath: Path | str) -> None:
        """Save a Hexmap at filepath using pickle

        :param filepath: Path to where the HexMap ``.pkl`` file should be saved
        :returns: None
        """

        with builtins.open(filepath, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def plot(
        self,
        colormap: dict[Any, Any] | None = None,
        textmap: dict[Any, str] | None = None,
        factor: float = 1,
        alpha: float = 0.5,
    ) -> None:
        """Plot the HexMap using matplotlib
        :param colormap: Optional dict to map colors to different values in the HexMap
        :param factor: Shrink size of Hex by factor
        :param alpha: Alpha value of colors
        :returns: None
        """

        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Polygon, RegularPolygon

        except ImportError as e:
            warnings.warn(str(e), RuntimeWarning)
            raise

        fig, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.set_title("HexMap")

        # TODO CHECK THE LAYOUT

        size = 1

        Hex.set_layout(size, (0, 0), "flat")

        # Loop through hexes
        for hex, value in self.hexes_and_values():
            # Use the color specified in the colormap
            if colormap != None and value in colormap:
                color = colormap[value]

            else:
                color = "lightgray"

            # point.y = -point.y
            # point = Point(point.x, -point.y)

            # hex_polygon = RegularPolygon(
            #     point,
            #     numVertices=6,
            #     radius=Hex.size.x,
            #     orientation=math.pi * (Hex.start_angle - 0.5),
            #     facecolor=color,
            #     alpha=0.5,
            #     edgecolor="k",
            # )

            # print([Point(p.x, -p.y) for p in hex.polygon_points()])

            polygon = Polygon(
                tuple(Point(p.x, -p.y) for p in hex.polygon_points(factor)),  # type: ignore
                closed=True,
                facecolor=color,
                alpha=alpha,
                edgecolor="k",
            )

            center = hex.to_point()

            ax.add_patch(polygon)
            ax.scatter(center.x, -center.y, c="black", alpha=0)

            # Also add a text label
            # TODO make text size relative to ax window size

            if hex == Hexigo:
                coords = "q,r"

            else:
                coords = f"{hex.q},{hex.r}"

            ax.text(
                center.x,
                -center.y - 0.25,
                coords,
                ha="center",
                va="center",
                size=size * 10 * 2,
            )

            # if

            if textmap != None and value in textmap:
                text = textmap[value]

                ax.text(
                    center.x,
                    -center.y + 0.15,
                    text,
                    ha="center",
                    va="center",
                    size=size * 17 * 2,
                )

        plt.show()


def hexagon(
    radius: int,
    value: Any = None,
    origin: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Hexagon ⬢
    :param radius: The number of hexes from the center
    :param value: The value that should be assigned to all Hexagons
    :param origin: The origin of the shape, all Hexes will be by origin
    :param hollow: Whether or not to make the shape hollow
    :return: The hexagon HexMap
    """

    # TODO ADD TYPE CHECKS

    hexmap = HexMap(default_value=value, origin_offset=origin)

    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)

        if not hollow or q == -radius or q == radius:
            for r in range(r1, r2 + 1):
                hexmap.set(Hex(q, r))

        else:
            hexmap.set(Hex(q, r1))
            hexmap.set(Hex(q, r2))

    return hexmap


# def parallelogram(value: Any = None, axes) -> HexMap:
#     """Create a HexMap in the shape of a Parallelogram ▰
#     :param radius: The number of hexes from the center
#     :param value: The value that should be assigned to all Hexagons
#     :return: The parallelogram HexMap"""

# def rhombus(value: Any = None, radius) -> HexMap:
#     """Create a HexMap in the shape of a rhombus (aka diamond) ⬧
#     :param value: The value that should initially be assigned to all Hexagons
#     :param axes: jskeow
#     :return: The rhombus HexMap

# def triangle(value: Any = None, axes: str = "qs") -> HexMap:
#     """Create a HexMap in the shape of a Triangle ▲
#     :param radius: The number of hexes from the center
#     :param value: The value that should be assigned to all Hexagons
#     :return: The triangle HexMap"""

# def rectangle(value: Any = None, axes):
#     """Create a HexMap in the shape of a Rectangle ▬
#     :param radius: The number of hexes from the center
#     :param value: The value that should be assigned to all Hexagons
#     :return: The rectangle HexMap"""

# def square(value: Any = None, axes):
#     """Create a HexMap in the shape of a Square ■
#     :param radius: The number of hexes from the center
#     :param value: The value that should be assigned to all Hexagons
#     :return: The square HexMap"""
