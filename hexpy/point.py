from __future__ import annotations


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
