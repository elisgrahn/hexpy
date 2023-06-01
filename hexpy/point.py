from __future__ import annotations

from typing import Optional


class Point(tuple):
    """Represents a Point"""

    def __new__(cls, x: float, y: float):
        """Create a Point

        Args:
            x (float): Required point coordinate
            y (float): Required point coordinate

        Raises:
            TypeError: If x or y is not of type ``int`` or ``float``

        Returns:
            Point: The point at (x, y)
        """

        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError(
                "Point got incorrect coordinate types: x and y must be of type 'int' or 'float'"
            )

        return tuple.__new__(cls, (x, y))

    @property
    def x(self) -> float:
        """Get the x coordinate of the Point"""
        return self[0]

    @property
    def y(self) -> float:
        """Get the y coordinate of the Point"""
        return self[1]

    @property
    def coords(self) -> tuple[float, float]:
        return tuple(self)

    def __repr__(self) -> str:
        """Return a nicely formatted Point representation string"""
        x, y = self.coords

        return f"Point({x=}, {y=})"

    def __round__(self, ndigits: Optional[int] = None) -> Point:
        """Round the coordinates of this Point

        Args:
            ndigits (int, optional): The number of digits to round to. Defaults to None.

        Returns:
            Point: This Point with rounded coordinates as a new Point
        """

        return Point(round(self.x, ndigits), round(self.y, ndigits))

    def __neg__(self) -> Point:
        "Negate the values of self, effectively flipping it around Origo"
        return Point(-self.x, -self.y)

    def __add__(self, other: Point | tuple | float) -> Point:
        """Add this Point with another Point or number

        Args:
            other (Point | tuple | float): If a ``Point`` or ``tuple`` is provided the addition will be elementwise,
                and if an ``int`` or a ``float`` is provided both x and y will be added by that number

        Raises:
            TypeError: If ``other`` is not of type ``Point``, ``tuple``, ``int`` or ``float``

        Returns:
            Point: The added point
        """

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x + other.x, self.y + other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x + other, self.y + other)

        else:
            raise TypeError(
                f"Cannot add {self} of type {type(self)} to {other} of type {type(other)}"
            )

    __radd__ = __add__

    def __sub__(self, other: Point | tuple | float) -> Point:
        """Subtract this Point by another Point or number

        Args:
            other (Point | tuple | float): If a ``Point`` or ``tuple`` is provided the subtraction will be elementwise,
                and if an ``int`` or a ``float`` is provided both x and y will be subtracted by that number

        Raises:
            TypeError: If ``other`` is not of type ``Point``, ``tuple``, ``int`` or ``float``

        Returns:
            Point: The subtracted point
        """
        if isinstance(other, tuple):
            other = Point(*other)

        return self + -other

    def __mul__(self, other: Point | tuple | float) -> Point:
        """Multiplicate this Point by another Point or number

        Args:
            other (Point | tuple | float): If a ``Point`` or ``tuple`` is provided the multiplication will be elementwise,
                and if an ``int`` or a ``float`` is provided both x and y will be multiplied by that number

        Raises:
            TypeError: If ``other`` is not of type ``Point``, ``tuple``, ``int`` or ``float``

        Returns:
            Point: The multiplicated point
        """

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x * other.x, self.y * other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x * other, self.y * other)

        else:
            raise TypeError(
                f"Cannot multiplicate {self} of type {type(self)} with {other} of type {type(other)}"
            )

    def __truediv__(self, other: Point | tuple | float) -> Point:
        """Divide this Point by another Point or number

        Args:
            other (Point | tuple | float): If a ``Point`` or ``tuple`` is provided the divsion will be elementwise,
                and if an ``int`` or a ``float`` is provided both x and y will be divided by that number

        Raises:
            TypeError: If ``other`` is not of type ``Point``, ``tuple``, ``int`` or ``float``

        Returns:
            Point: The divided point
        """

        if isinstance(other, (Point, tuple)):
            other = Point(*other)
            return Point(self.x / other.x, self.y / other.y)

        elif isinstance(other, (int, float)):
            return Point(self.x / other, self.y / other)

        else:
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {other} of type {type(other)}"
            )

    def __floordiv__(self, other: Point | tuple | float) -> Point:
        """Divide this Point by another Point or number and round the result

        Args:
            other (Point | tuple | float): If a ``Point`` or ``tuple`` is provided the division will be elementwise,
                and if an ``int`` or a ``float`` is provided both x and y will be divided by that number

        Raises:
            TypeError: If ``other`` is not of type ``Point``, ``tuple``, ``int`` or ``float``

        Returns:
            Point: The divided and rounded point
        """
        return round(self / other)

    def __eq__(self, other: Point | tuple) -> bool:
        """Check if Point coords are equal equals something

        Args:
            other (Point | tuple): Accepts a tuple, compares the coordinates elementwise

        Returns:
            bool: Wheter or not the coordinates are equal
        """
        if not isinstance(other, (tuple, Point)):
            return False

        elif isinstance(other, tuple):
            other = Point(*other)

        return self.x == other.y and self.x == other.y
