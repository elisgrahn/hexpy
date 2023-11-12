# Author: Elis Grahn

"""_summary_

Raises:
    TypeError: _description_
    TypeError: _description_
    TypeError: _description_

Returns:
    _type_: _description_
"""  # TODO
from __future__ import annotations

from math import sqrt

import numpy as np

from .point import Point


class Orientation:
    __slots__ = ("forward", "backward", "start_angle")

    def __init__(self, forward: np.ndarray | tuple | list, start_angle: float):
        """Create an Orientation.

        Args:
            forward (np.ndarray | tuple | list): The matrix used to get points from Hexess
            start_angle (float): The angle in radians which hexes are rotated
        """

        # Used to calculate hex to pixel
        self.forward = np.array(forward)

        # Used to calculate pixel to hex
        self.backward = np.linalg.inv(forward)

        # The angle that Hexes will be rotated
        self.start_angle = start_angle

    def __repr__(self) -> str:
        """Return a nicely formated string of Orientation"""

        forward = [[round(n, 2) for n in sublist] for sublist in self.forward]
        backward = [[round(n, 2) for n in sublist] for sublist in self.backward]
        start_angle = self.start_angle

        return f"Orientation({forward=},\n            {backward=},\n            {start_angle=})"

    @property
    def f0(self):
        return self.forward[0, 0]

    @property
    def f1(self):
        return self.forward[0, 1]

    @property
    def f2(self):
        return self.forward[1, 0]

    @property
    def f3(self):
        return self.forward[1, 1]

    @property
    def b0(self):
        return self.backward[0, 0]

    @property
    def b1(self):
        return self.backward[0, 1]

    @property
    def b2(self):
        return self.backward[1, 0]

    @property
    def b3(self):
        return self.backward[1, 1]


class Layout:
    __slots__ = ("size", "origin", "orientation")

    def __init__(
        self,
        size: int | Point | tuple[int, int],
        origin: Point | tuple[int, int],
        orientation: int | Orientation,
    ) -> None:
        """_summary_

        Args:
            size (int | Point | tuple[int, int]): _description_
            origin (Point | tuple[int, int]): _description_
            orientation (Orientation): _description_

        Raises:
            TypeError: _description_
            TypeError: _description_
            TypeError: _description_
        """

        """Create a layout containing Hex grid metadata.

        :param size: The pixel size of hexagons. If an int is provided hexagons will be regular, otherwise they can be stretched
        :param origin: The pixel origin, i.e. at what Pixel Hexigo will be
        :param orientation: The orientation of hexagons. Either ``pointy`` ⬢ or ``flat`` ⬣.
        """

        if isinstance(origin, (Point, tuple)):
            self.origin = Point(*origin)

        else:
            # TODO
            raise TypeError("")

        if isinstance(size, int):
            self.size = Point(size, size)

        elif isinstance(size, (Point, tuple)):
            self.size = Point(*size)

        else:
            # TODO
            raise TypeError("")

        if isinstance(orientation, Orientation):
            self.orientation = orientation

        else:
            # TODO
            raise TypeError("")
    
    @property
    def width(self) -> int:
        """Returns the width of the hexes in pixels based on the size and orientation"""
        if self.orientation == flat_orientation:
            return self.size.x * 2
        
        elif self.orientation == pointy_orientation:
            return sqrt(3) * self.size.x

        else: 
            raise TypeError("Width is not defined for custom orientations")
    
    @property
    def height(self) -> int:
        """Returns the height of the hexes in pixels based on the size and orientation"""
        if self.orientation == flat_orientation:
            return sqrt(3) * self.size.y
        
        elif self.orientation == pointy_orientation:
            return 2 * self.size.y

        else: 
            raise TypeError("Width is not defined for custom orientations")
    
    @property
    def horizontal_spacing(self) -> int:
        """Returns the horizontal spacing between hexes in pixels based on the size and orientation"""
        if self.orientation == flat_orientation:
            return 3/2 * self.size.x
        
        elif self.orientation == pointy_orientation:
            return sqrt(3) * self.size.x

        else: 
            raise TypeError("horizontal_spacing is not defined for custom orientations")
        
    @property
    def vertical_spacing(self) -> int:
        """Returns the vertical spacing between hexes in pixels based on the size and orientation"""
        if self.orientation == flat_orientation:
            return sqrt(3) * self.size.y

        elif self.orientation == pointy_orientation:
            return 3/2 * self.size.y

        else: 
            raise TypeError("vertical_spacing is not defined for custom orientations")
        

    def __repr__(self) -> str:
        """Return a nicely formated string of Layout"""

        size, origin = self.size, self.origin
        orientation = self.orientation

        return (
            f"Layout({size=},\n       {origin=},\n       orientation=\n{orientation})"
        )


pointy_orientation = Orientation(
    ((sqrt(3), sqrt(3) / 2), (0, 3 / 2)),
    start_angle=0.5,
)
flat_orientation = Orientation(
    ((3 / 2, 0), (sqrt(3) / 2, sqrt(3))),
    start_angle=0,
)


def pointy(
    size: int | tuple[int, int],
    origin: tuple[int, int],
) -> Layout:
    """_summary_

    Args:
        size (int | Point | tuple[int, int]): _description_
        origin (Point | tuple[int, int]): _description_

    Returns:
        Layout: _description_
    """
    return Layout(size, origin, pointy_orientation)


def flat(
    size: int | tuple[int, int],
    origin: tuple[int, int],
) -> Layout:
    """_summary_

    Args:
        size (int | Point | tuple[int, int]): _description_
        origin (Point | tuple[int, int]): _description_

    Returns:
        Layout: _description_
    """
    return Layout(size, origin, flat_orientation)


def custom(
    orientation: Orientation,
    size: int | tuple[int, int],
    origin: tuple[int, int],
) -> Layout:
    """_summary_

    Args:
        orientation (Orientation): _description_
        size (int | Point | tuple[int, int]): _description_
        origin (Point | tuple[int, int]): _description_

    Returns:
        Layout: _description_
    """
    return Layout(size, origin, orientation)
