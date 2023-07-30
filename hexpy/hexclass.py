# Author: Elis Grahn

from __future__ import annotations

import math
from collections.abc import Iterable
from itertools import cycle, islice
from re import A
from typing import TYPE_CHECKING, Iterator, Literal, Optional, overload  # , Self

from .layout import Orientation
from .point import Point

if TYPE_CHECKING:
    from .navigate import HexClock, HexCompass


class Hex:
    """Represents a Hexagon

    Examples:
        Create a new Hex at q = 1 and r = 2
        >>> Hex(1, 2)
        Hex(q=1, r=2, s=-3)

        Add two Hex
        >>> Hex(1, 2) + Hex(3, 4)
        Hex(q=3, r=6, s=-10)

        Multiplicate a Hex by 2
        >>> Hex(1, 2) * 2
        Hex(q=2, r=4, s= -6)

        Divide a Hex by 2
        >>> Hex(1, 2) / 2
        Hex(q=0.5, r=1.0, s=-1.5)

        Divide a Hex by 2 and round the result
        >>> Hex(1, 2) // 2
        Hex(q=0, r=2, s=-2)

        Round a Hex

        >>> round(Hex(1.5, 2.5))
        Hex(q=2, r=2, s=-4)

        Get the length of a Hex
        >>> len(Hex(1, 2))
        3

        >>> Hex(1, 2).length
        3

        Get the distance between two Hexes
        >>> Hex(1, 2).distance(Hex(3, 4))
        4

        >>> len(Hex(1, 2) - Hex(3, 4))
        4

        Rotate a Hex 60 degrees to the left around Hexigo
        >>> Hex(1, 2) << 1
        Hex(q=3, r=-1, s=-2)

        >>> Hex(1, 2).rotated_left(1)
        Hex(q=3, r=-1, s=-2)

        Reflect a Hex over the q-axis
        >>> Hex(1, 2).reflect('q')

    """

    __slots__ = ("q", "r")

    def __init__(
        self,
        q: float,
        r: float,
        s: Optional[float] = None,
    ) -> None:
        """Create a Hex.

        Args:
            q (float): Required hex coordinate.
            r (float): Required hex coordinate.
            s (float, optional): Optional hex coordinate. Defaults to None.

        Raises:
            TypeError: If `q, r or s` are not all of type `int` or `float`
            ValueError: If `q, r and s` does not add upp to `0`
        """

        if not isinstance(q, (int, float)) or not isinstance(r, (int, float)):
            raise TypeError(
                f"{q} and {r} are of incorrect coordinate types: must be of type 'int' or 'float'"
            )

        self.q = q
        self.r = r

        # If the user has provided the unreqired argument s, then it will check that it at least works together with q and r
        # This is intantinal and makes cube coordinates "safer" and less prone to make mistakes in but axial still works
        if s is not None:
            if not isinstance(s, (int, float)):
                raise TypeError(
                    "if s is to be provided it must be of type 'int' or 'float'"
                )
            # Check that s works with q and r
            self.s = s

    @property
    def s(self) -> float:
        return -(self.q + self.r)

    @s.setter
    def s(self, new_s: float) -> None:
        """This will NOT set s to anything, it will however check that the provided s is correct together with both q and r

        Raises:
            ValueError: If q + r + s are not equal up to 0

        Examples:
            Let's say we create a new Hex at q = 1 and r = 2 using axial input:
            >>> Hex(1, 2)
            Hex(q=1, r=2, s=-3)

            The above can and will not check if your provided coords are correct!

            If we instead input using cube coordinates a ValueError will be raised if we accidentally provide incorrect coordinates:
            >>> Hex(q=1, r=2, s=3)
            ValueError: Incorrect coordinates: q + r + s must be equal to 0, but was equal to 6

            This makes cube input safer than axial, due to the double check of coords, but cube input is not required and s will not be stored.
        """
        coord_sum = sum(self.axial_coords) + new_s

        if round(coord_sum) != 0.0:
            raise ValueError(
                f"Incorrect coordinates: q + r + s must be equal to 0, but was equal to {coord_sum}"
            )

    # coords

    @property
    def cube_coords(self) -> tuple[float, float, float]:
        """Get the cube coords of this Hex

        Returns:
            tuple[float, float, float]: The coordinates in cube format
        """
        return (self.q, self.r, self.s)

    @cube_coords.setter
    def cube_coords(self, new_coords: tuple[float, float, float]) -> None:
        """Set the cube coords of this Hex

        Args:
            new_coords (tuple[float, float, float]): The new coords, must be a three long tuple with values of type int or float.
        """
        if (
            not isinstance(new_coords, tuple)
            or len(new_coords) != 3
            or not all(isinstance(c, (int, float)) for c in new_coords)
        ):
            raise TypeError(
                "new_coords must be a 3 long tuple with values of type 'int' or 'float'"
            )

        self.q, self.r, self.s = new_coords

    @property
    def axial_coords(self) -> tuple[float, float]:
        """Get the axial coords of this Hex

        Returns:
            tuple[float, float]: The coordinates in axial format
        """
        return (self.q, self.r)

    @axial_coords.setter
    def axial_coords(self, new_coords: tuple[float, float]) -> None:
        """Set the axial coords of this Hex

        Args:
            new_coords (tuple[float, float]): The new coords, must be a two long tuple with values of type int or float.
        """
        if (
            not isinstance(new_coords, tuple)
            or len(new_coords) != 2
            or not all(isinstance(c, (int, float)) for c in new_coords)
        ):
            raise TypeError(
                "new_coords must be a 2 long tuple with values of type 'int' or 'float'"
            )

        self.q, self.r = new_coords

    @overload
    def __setitem__(
        self, coords: tuple[str, str, str], values: tuple[float, float, float]
    ) -> None:
        ...

    @overload
    def __setitem__(self, coords: tuple[str, str], values: tuple[float, float]) -> None:
        ...

    def __setitem__(self, coords: tuple[str, ...], values: tuple[float, ...]) -> None:
        """Used to change q, r and s in a dict like manner

        Note:
            It is intentionally not possible to just change a single coordinate, since that could result in invalid coordinates.
            If two coords are provided the third will be calculated from the other two.

        Args:
            coords (Iterable[str]): The coords to change
            values (Iterable[float]): The values to coords change to

        Example:
            >>> hx = Hex(1, 2, -3)
            >>> hx['q', 'r'] = (2, 1)
            >>> hx
            Hex(q=2, r=1, s=-3)
        """

        # Tests

        if not isinstance(coords, Iterable) or not isinstance(values, Iterable):
            raise TypeError("Both coords and values must be iterable.")

        if not all(
            coord in {"q", "r", "s"} and isinstance(value, (float, int))
            for coord, value in zip(coords, values)
        ):
            raise TypeError(
                "All coords must be either 'q', 'r' or 's' and all values must be of type 'float' or 'int'"
            )

        if len(coords) == 1 or len(coords) > 3:
            raise ValueError(
                "Must change either two or all three coordinates at the same time, otherwise the hex coordinates will become invalid."
            )

        if len(coords) != len(values):
            raise ValueError(
                "The coords (to change) and the values (to change to) must match in length."
            )

        if len(coords) != len(set(coords)):
            raise ValueError("Cannot reference the same coord twice.")

        # Code

        if len(coords) == 2:
            # When length is 2, get the implicit coord by removing the two provided coords from the set of all coords
            # For instance, if s and r are provided, then q will become implicit and firstly calculated from the other two

            implicit_coord = str(*{"q", "r", "s"} - set(coords))

            if implicit_coord != "s":
                setattr(self, implicit_coord, -sum(values))
        else:
            implicit_coord = "s"

        # create a dict which will access the coords
        coord_dict = dict(zip(coords, values))

        # loop through the coords and values while skipping s and another potential implicit coord
        for coord, value in coord_dict.items():
            if coord not in {"s", implicit_coord}:
                setattr(self, coord, value)

        if "s" in coords:
            # If all three coords were provided, then the provided s will be checked that it works with q and r by calling the s.setter.
            self.s = coord_dict["s"]

    @overload
    def __getitem__(self, coords: str) -> float:
        ...

    @overload
    def __getitem__(self, coords: tuple[str, ...]) -> tuple[float, ...]:
        ...

    def __getitem__(self, coords: str | tuple[str, ...]) -> float | tuple[float, ...]:
        """Used to access q, r and s in a dict like manner

        Args:
            coords (Iterable[str]): The coords to change

        Returns:
            tuple[float, ...]: The values of the coords in the same order as the coords provided

        Example:
            >>> hx = Hex(1, 2, -3)
            >>> hx['r', 'q']
            (2, 1)
        """

        def get_coord(coord: str) -> float:
            if coord not in {"q", "r", "s"}:
                raise ValueError(
                    f"Invalid coordinate: {coord}, must be one of 'q', 'r' or 's'"
                )
            return getattr(self, coord)

        if isinstance(coords, str):
            return get_coord(coords)

        return tuple(get_coord(coord) for coord in coords)

    # directions and neighbors

    @property
    def directions(self) -> HexClock:
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            tuple[Hex]: _description_
        """
        if not hasattr(self, "hexclock"):
            raise RuntimeError(
                "'Layout' has not yet been defined, to define one use 'Hex.flat_layout()', 'Hex.pointy_layout()' or 'Hex.custom_layout()'"
            )
        return self.hexclock.directions(self.hexlayout.orientation)

    @property
    def diagonals(self) -> HexClock:
        """_summary_

        Returns:
            tuple[Hex]: _description_
        """
        if not hasattr(self, "hexclock"):
            raise RuntimeError(
                "'Layout' has not yet been defined, to define one use 'Hex.flat_layout()', 'Hex.pointy_layout()' or 'Hex.custom_layout()'"
            )
        return self.hexclock.diagonals(self.hexlayout.orientation)

    @property
    def direct_neighbors(self) -> HexClock:
        """Return the clock neighbor at hour

        Note:
            TODO READ THIS: WITH A LINK

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: _description_
        """
        if not hasattr(self, "hexclock"):
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.hexlayout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        return self.directions.shifted(self)

        # return self.hexclock.directions + self

    @property
    def diagonal_neighbors(self) -> HexClock:
        """Return the diagonal clock neighbors

        Note:
            TODO READ THIS: WITH A LINK

        Args:
            hour (int): The hour to get neighbor in

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: _description_
        """
        if not hasattr(self, "hexclock"):
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.hexlayout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )
        return self.diagonals.shifted(self)

    @property
    def all_neighbors(self) -> HexClock:
        """Return the all clock neighbors

        Note:
            TODO READ THIS: WITH A LINK

        Args:
            hour (int): The hour to get neighbor in

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: _description_
        """
        if not hasattr(self, "hexclock"):
            raise RuntimeError(
                "'Layout' has not yet been defined, to define one use 'Hex.flat_layout()', 'Hex.pointy_layout()' or 'Hex.custom_layout()'"
            )
        return self.hexclock.shifted(self)

    # rounding

    def round(self, ndigits: Optional[int] = None) -> None:
        """Inplace round the coordinates of this Hex

        Args:
            ndigits (int, optional): The number of digits to round to. Defaults to None.
        """

        # rounded q, r and s
        q = round(self.q, ndigits)
        r = round(self.r, ndigits)
        s = round(self.s, ndigits)

        # diff or delta from rounding
        dq = abs(q - self.q)
        ds = abs(r - self.r)
        dr = abs(s - self.s)

        # in order to avoid getting bad coords, the one with the biggest diff will be calculated from the other two
        if dq > dr and dq > ds:
            q = -r - s
        elif dr > ds:
            r = -q - s
        else:
            s = -q - r

        self.cube_coords = (q, r, s)

    def rounded(self, ndigits: Optional[int] = None) -> Hex:
        """Get the rounded coordinates of this Hex

        Note:
            This can also be done using the function `round()` on a Hex.

        Args:
            ndigits (int, optional): The number of digits to round to. Defaults to None.

        Returns:
            Hex: This Hex with rounded coordinates
        """

        # These listcomprehensions are slower... :(
        # (q, dq), (r, dr), (s, ds) = ((round(crd), abs(round(crd) - crd)) for crd in (self.q, self.r, self.s))

        # Walrus flex:
        # (q, dq), (r, dr), (s, ds) = ((rnd := round(crd), abs(rnd - crd)) for crd in (self.q, self.r, self.s))

        # rounded q, r and s
        q = round(self.q, ndigits)
        r = round(self.r, ndigits)
        s = round(self.s, ndigits)

        # diff or delta from rounding
        dq = abs(q - self.q)
        ds = abs(r - self.r)
        dr = abs(s - self.s)

        # in order to avoid getting bad coords, the one with the biggest diff will be calculated from the other two
        if dq > dr and dq > ds:
            q = -r - s
        elif dr > ds:
            r = -q - s
        else:
            s = -q - r

        return Hex(q, r, s)

    __round__ = rounded

    # representations

    def __repr__(self) -> str:
        """Return a nicely formatted HexMap representation string"""
        q, r, s = self.cube_coords
        return f"Hex({q=}, {r=}, {s=})"

    def __hash__(self) -> int:
        """Return (q, r) as a hash number

        Returns:
            int: hash of this Hex's axial coords
        """
        return hash(self.axial_coords)

    # length

    @property
    def length(self) -> int:
        """Get the displacement from this Hex to Hexigo

        Note:
            This can also be done using `len(thisHex)`.

        Returns:
            int: Length, you can think of this as the least amount of Hexes you have to pass through when walking from this Hex to Hexigo.
        """
        return round((abs(self.q) + abs(self.r) + abs(self.s)) / 2)

    def __len__(self) -> int:
        """Get the displacement from this Hex to Hexigo"""
        return self.length

    def distance(self, other: Hex) -> int:
        """Get the displacement from this Hex to other Hex

        Note:
            This can also be done using `len(thisHex - otherHex)`.

        Args:
            other (Hex, optional): The Hex to get distance to if `other` is omitted `Hexigo` will be used. Defaults to None.

        Raises:
            TypeError: If `other` is not of type `Hex`.

        Returns:
            int: The distance, which can be thought of as the least amount of Hexes you have to pass through when walking from this Hex to other.
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return len(self - other)

    # negation

    def negate(self) -> None:
        """Inplace negate the values of self, effectively reflecting it over Hexigo.

        Note:
            Non inplace version can be done using `thisHex.negated()` or `-thisHex`.
        """
        self.axial_coords = -self.q, -self.r

    def negate_around(self, other: Hex) -> None:
        """Negate the values of self with other as reference, effectively reflecting it over other Hex.

        Args:
            other (Hex): The Hex to reflect over
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        self -= other
        self.negate()
        self += other

    def negated(self) -> Hex:
        """Negate the values of self, effectively reflecting it over Hexigo.

        Note:
            This can also be done using `-thisHex`, for inplace see `thishex.negated()`.

        Returns:
            Hex: This Hex negated
        """
        return Hex(-self.q, -self.r)

    __neg__ = negated

    def negated_around(self, other: Hex) -> Hex:
        """Negate the values of self with other as reference, effectively reflecting it over other Hex.

        Args:
            other (Hex): The Hex to reflect over

        Returns:
            Hex: This Hex negated around other
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return (self - other).negated() + other

    # addition and subtraction

    def add(self, other: Hex) -> Hex:
        """Add this Hex with other Hex

        Note:
            This can also be done using `thisHex + otherHex`.

        Args:
            other (Hex): The Hex to add with

        Raises:
            TypeError: If `other` is not of type `Hex`

        Returns:
            Hex: This Hex added to other Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return Hex(self.q + other.q, self.r + other.r)

    __add__ = add
    __radd__ = add

    def iadd(self, other: Hex):  # -> Self:
        """Add this Hex with other Hex inplace

        Note:
            This can also be done using `thisHex += otherHex`.

        Args:
            other (Hex): The Hex to add with

        Raises:
            TypeError: If `other` is not of type `Hex`

        Returns:
            Hex: This Hex added to other Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        self.axial_coords = (self.q + other.q, self.r + other.q)
        return self

    __iadd__ = iadd

    def sub(self, other: Hex) -> Hex:
        """Subtract this Hex by other Hex

        Args:
            other (Hex): The Hex to subtract by

        Raises:
            TypeError: If `other` is not of type `Hex`

        Returns:
            Hex: This Hex subtracted by other Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return Hex(self.q - other.q, self.r - other.r)

    __sub__ = sub
    # don't need __rsub__ since 'other' is only allowed to be a Hex!

    def isub(self, other: Hex):  # -> Self:
        """Subtract this Hex by other Hex inplace

        Args:
            other (Hex): The Hex to subtract by

        Raises:
            TypeError: If `other` is not of type `Hex`

        Returns:
            Self: This Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        self.axial_coords = (self.q - other.q, self.r - other.r)
        return self

    __isub__ = isub

    # multiplication and division

    def mul(self, k: float) -> Hex:
        """Multiplicate `this Hex` by factor `k`

        Args:
            k (float): The factor to multiply by

        Raises:
            TypeError: If `k` is not of type `int` or `float`

        Returns:
            Hex: This Hex multiplied by k
        """
        if not isinstance(k, (int, float)):
            raise TypeError(f"k must be of type 'float' or 'int', not {type(k)}")

        return Hex(self.q * k, self.r * k)

    __mul__ = mul
    __rmul__ = mul

    def imul(self, k: float):  # -> Self
        """Multiplicate `this Hex` by factor `k`

        Args:
            k (float): The factor to multiply by

        Raises:
            TypeError: If `k` is not of type `int` or `float`

        Returns:
            Hex: This Hex multiplied by k
        """

        if not isinstance(k, (int, float)):
            raise TypeError(f"k must be of type 'float' or 'int', not {type(k)}")

        self.axial_coords = (self.q * k, self.r * k)
        return self

    __imul__ = imul

    def truediv(self, d: float) -> Hex:
        """Divide `this Hex` by divisor `d`

        Args:
            d (float): The divisor to divide by

        Raises:
            TypeError: If `d` is not of type `int` or `float`

        Returns:
            Hex: This Hex divided by d
        """

        if not isinstance(d, (int, float)):
            raise TypeError(f"d must be of type 'float' or 'int', not {type(d)}")

        return Hex(self.q / d, self.r / d)

    __truediv__ = truediv

    def itruediv(self, d: float):  # -> Self
        """Divide `this Hex` by divisor `d`

        Args:
            d (float): The divisor to divide by

        Raises:
            TypeError: If `d` is not of type `int` or `float`

        Returns:
            Hex: This Hex divided by d
        """
        if not isinstance(d, (int, float)):
            raise TypeError(f"d must be of type 'float' or 'int', not {type(d)}")

        self.axial_coords = (self.q / d, self.r / d)
        return self

    __itruediv__ = itruediv

    def floordiv(self, d: float) -> Hex:
        """Divide `this Hex` by divisor `d` and round the result

        Args:
            d (float): The divisor to divide by

        Raises:
            TypeError: If `d` is not of type `int` or `float`

        Returns:
            Hex: This Hex divided by d
        """
        if not isinstance(d, (int, float)):
            raise TypeError(f"d must be of type 'float' or 'int', not {type(d)}")

        return round(Hex(self.q / d, self.r / d))

    __floordiv__ = floordiv

    def ifloordiv(self, d: float):  # -> Self
        """Divide `this Hex` by divisor `d` and round the result inplace

        Args:
            d (float): The divisor to divide by

        Raises:
            TypeError: If `d` is not of type `int` or `float`

        Returns:
            Hex: This Hex divided by d
        """
        if not isinstance(d, (int, float)):
            raise TypeError(f"d must be of type 'float' or 'int', not {type(d)}")

        self.axial_coords = (self.q / d, self.r / d)
        self.round()
        return self

    __ifloordiv__ = ifloordiv

    # comparisons

    def equals(self, other: Hex | object) -> bool:
        """Check if this Hex is equal to other.

        Note:
            This can also be done using equal operator, `Hex1 == Hex2` or `Hex1 == 2`.

        Args:
            other (Hex): The Hex to compare with

        Returns:
            bool: Whether or not the coords of this Hex and other Hex are equal
        """
        if isinstance(other, Hex):
            return self.axial_coords == other.axial_coords

        else:
            return False

    __eq__ = equals

    def __bool__(self) -> bool:
        """Always returns True since it is an object"""
        return True

    def __lt__(self, other: Hex) -> bool:
        """Check if this Hex is closer to Hexigo compared to other Hex"""
        return len(self) < len(other)

    def __le__(self, other: Hex) -> bool:
        """Check if this Hex is closer or equally far to Hexigo compared to other Hex"""
        return len(self) <= len(other)

    def __gt__(self, other: Hex) -> bool:
        """Check if this Hex is farther from Hexigo compared to other Hex"""
        return len(self) > len(other)

    def __ge__(self, other: Hex) -> bool:
        """Check if this Hex is farther or equally far from Hexigo compared to other Hex"""
        return len(self) <= len(other)

    def __contains__(self, c: float) -> bool:
        """Check if this Hex contains the provided coordinate"""
        return c in self.cube_coords

    # left rotation

    def rotate_left(self, steps: int = 1) -> None:
        """Inplace rotate this Hex 60 * steps degrees to the left around Hexigo.

        Note:
            This can also be done using inplace left shift operator, `Hex << steps`.

        Raises:
            TypeError: If `steps` is not of type `int`

        Args:
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.
        """
        if not isinstance(steps, int):
            raise TypeError(f"steps must be of type 'int', not {type(steps)}")

        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Set cube coords of this hex to q, r, s rotated steps % 3 to the left
        self.cube_coords = tuple(islice(cycle(self.cube_coords), 3 - n, 6 - n))

        # Negate the hex values if rotating odd amount of steps
        self = -self if steps % 2 else self

    def rotate_left_around(self, other: Hex, steps: int = 1) -> None:
        """Inplace rotate this Hex 60 * steps degrees to the left around other Hex.

        Note:
            This can also be done using inplace left shift operator, `Hex <<= Hex` or `Hex <<= (Hex, steps)`.

        Raises:
            TypeError: If `other` is not of type `Hex`
            TypeError: If `steps` is not of type `int`

        Args:
            other (Hex): The other Hex to rotate around.
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        self -= other
        self.rotate_left(steps)
        self += other

    def __ilshift__(self, input: int | Hex | tuple[Hex, int]):  # -> Self:
        """Convienience method for both rotate_left() and rotate_left_around().

        Args:
            input (int | Hex | tuple[Hex, int]): If only an `int` is provided that will be used as steps to rotate around `Hexigo`.
                If only a `Hex` is provided that will be used as a centerpoint and rotated 1 step around.
                If a tuple with Hex as first argument and int as second is provided that will be used as centerpoint and steps respectively.

        Raises:
            TypeError: If `input` is not of type `int`, `Hex` or `tuple[Hex, int]`
        """

        # Just steps was provided, rotate around Hexigo
        if isinstance(input, int):
            self.rotate_left(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            self.rotate_left_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            self.rotate_left_around(*input)

        else:
            raise TypeError(
                f"input must be of type 'int', 'Hex' or 'tuple[Hex, int]', not {type(input)}"
            )
        return self

    def rotated_left(self, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the left around Hexigo.

        Note:
            This can also be done using left shift operator, `Hex << steps`.

        Args:
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Raises:
            TypeError: If `steps` is not of type `int`

        Returns:
            Hex: This Hex rotated left around Hexigo.
        """
        if not isinstance(steps, int):
            raise TypeError(f"steps must be of type 'int', not {type(steps)}")

        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the left
        rotated_hex = Hex(*islice(cycle(self.cube_coords), 3 - n, 6 - n))

        # Negate the hex values if rotating odd amount of steps
        return -rotated_hex if steps % 2 else rotated_hex

    def rotated_left_around(self, other: Hex, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the left around other Hex.

        Note:
            This can also be done using left shift operator, `Hex << Hex` or `Hex << (Hex, steps)`.

        Args:
            other (Hex): The other Hex to rotate around.
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Raises:
            TypeError: If `other` is not of type `Hex`
            TypeError: If `steps` is not of type `int`

        Returns:
            Hex: This Hex rotated left around other.
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return (self - other).rotated_left(steps) + other

    def __lshift__(self, input: int | Hex | tuple[Hex, int]) -> Hex:
        """Convienience method for both rotated_left() and rotated_left_around().

        Args:
            input (int | Hex | tuple[Hex, int]): If only an `int` is provided that will be used as steps to rotate around `Hexigo`.
                If only a `Hex` is provided that will be used as a centerpoint and rotated 1 step around.
                If a tuple with Hex as first argument and int as second is provided that will be used as centerpoint and steps respectively.

        Raises:
            TypeError: If `input` is not of type `int`, `Hex` or `tuple[Hex, int]`

        Returns:
            Hex: This Hex rotated

        Examples:
            >>> thisHex = Hex(1, 0, -1)
            >>> otherHex = Hex(-2, 0, 2)

            Rotate this Hex left (around Hexigo) two steps
            >>> thisHex << 2
            Hex(q=0, r=-1, s=1)

            Rotate this Hex left around other Hex (one step)
            >>> thisHex << otherHex
            Hex(q=1, r=-3, s=2)

            Rotate this Hex left around other Hex two steps
            >>> thisHex << (otherHex, 2)
            Hex(q=-2, r=-3, s=5)
        """

        # Just steps was provided, rotate around Hexigo
        if isinstance(input, int):
            return self.rotated_left(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            return self.rotated_left_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            return self.rotated_left_around(*input)

        else:
            raise TypeError(
                f"input must be of type 'int', 'Hex' or 'tuple[Hex, int]', not {type(input)}"
            )

    # right rotation

    def rotate_right(self, steps: int = 1) -> None:
        """Inplace rotate this Hex 60 * steps degrees to the right around Hexigo.

        Args:
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Raises:
            TypeError: If `steps` is not of type `int`.
        """
        if not isinstance(steps, int):
            raise TypeError(f"steps must be of type 'int', not {type(steps)}")

        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the right
        self.cube_coords = tuple(islice(cycle(self.cube_coords), n, 3 + n))

        # Negate the hex values if rotating odd amount of steps
        self = -self if steps % 2 else self

    def rotate_right_around(self, other: Hex, steps: int = 1) -> None:
        """Inplace rotate this Hex 60 * steps degrees to the right around other Hex.

        Args:
            other (Hex): The other Hex to rotate around.
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Raises:
            TypeError: If `other` is not of type `Hex`.
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        self -= other
        self.rotate_right()
        self += other

    def __irshift__(self, input: int | Hex | tuple[Hex, int]):  # -> Self:
        """Convienience method for both rotate_right() and rotate_right_around().

        Args:
            input (int | Hex | tuple[Hex, int]): If only an `int` is provided that will be used as steps to rotate around `Hexigo`.
                If only a `Hex` is provided that will be used as a centerpoint and rotated 1 step around.
                If a tuple with Hex as first argument and int as second is provided that will be used as centerpoint and steps respectively.

        Raises:
            TypeError: TypeError: If `input` is not of type `int`, `Hex` or `tuple[Hex, int]`
        """
        # Just steps was provided, rotate around Hexigo
        if isinstance(input, int):
            self.rotate_right(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            self.rotated_right_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            self.rotate_right_around(*input)

        else:
            raise TypeError(
                f"input must be of type 'int', 'Hex' or 'tuple[Hex, int]', not {type(input)}"
            )
        return self

    def rotated_right(self, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the right around Hexigo.

        Note:
            This can also be done using right shift operator, `Hex >> steps`.

        Args:
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Raises:
            TypeError: If `steps` is not of type `int`.

        Returns:
            Hex: This Hex rotated right around Hexigo.
        """
        if not isinstance(steps, int):
            raise TypeError(f"steps must be of type 'int', not {type(steps)}")

        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the right
        rotated_hex = Hex(*islice(cycle(self.cube_coords), n, 3 + n))

        # Negate the hex values if rotating odd amount of steps
        return -rotated_hex if steps % 2 else rotated_hex

    def rotated_right_around(self, other: Hex, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the right around other Hex.

        Note:
            This can also be done using right shift operator, `Hex >> Hex` or `Hex >> (Hex, steps)`.

        Args:
            other (Hex): The other Hex to rotate around.
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Raises:
            TypeError: If `other` is not of type `Hex`.

        Returns:
            Hex: This Hex rotated right around other.
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return (self - other).rotated_right(steps) + other

    def __rshift__(self, input: int | Hex | tuple[Hex, int]) -> Hex:
        """Convienience method for both rotated_right() and rotated_right_around().

        Args:
            input (int | Hex | tuple[Hex, int]): If only an `int` is provided that will be used as steps to rotate around `Hexigo`.
                If only a `Hex` is provided that will be used as a centerpoint and rotated 1 step around.
                If a tuple with Hex as first argument and int as second is provided that will be used as centerpoint and steps respectively.

        Raises:
            TypeError: TODO

        Returns:
            Hex: This Hex rotated

        Examples:
            >>> thisHex = Hex(1, 0, -1)
            >>> otherHex = Hex(-2, 0, 2)

            Rotate this Hex left (around Hexigo) two steps
            >>> thisHex >> 2
            Hex(q=-1, r=1, s=0)

            Rotate this Hex left around other Hex (one step)
            >>> thisHex >> otherHex
            Hex(q=-2, r=3, s=-1)

            Rotate this Hex left around other Hex two steps
            >>> thisHex >> (otherHex, 2)
            Hex(q=-5, r=3, s=2)
        """

        # Just steps was provided, rotate around Hexigo
        if isinstance(input, int):
            return self.rotated_right(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            return self.rotated_right_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            return self.rotated_right_around(*input)

        else:
            raise TypeError(
                f"input must be of type 'int', 'Hex' or 'tuple[Hex, int]', not {type(input)}"
            )

    # reflection

    def reflect(self, axis: Literal["q", "r", "s"]) -> None:
        """Inplace reflect the Hex over the axis

        Args:
            axis (Literal['q', 'r', 's']): The axis to reflect over, either 'q', 'r' or 's'

        Raises:
            ValueError: _description_
        """
        if axis not in {"q", "r", "s"}:
            raise ValueError("Axis must be either 'q', 'r' or 's'")

        elif axis == "q":
            self.r = self.s

        elif axis == "r":
            self.q = self.s

        elif axis == "s":
            self.axial_coords = self.r, self.q

        # this works but is 10 times slower!
        # coords = tuple({"q", "r", "s"} - {axis})
        # self[coords] = self[coords[::-1]]

    def reflect_around(self, other: Hex, axis: Literal["q", "r", "s"]) -> None:
        """Inplace reflect the Hex over other Hex

        Args:
            other (Hex): The other Hex to reflect over
            axis (Literal['q', 'r', 's']): The axis to reflect over, either 'q', 'r' or 's'
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        self -= other
        self.reflect(axis)
        self += other

    def reflected(self, axis: Literal["q", "r", "s"]) -> Hex:
        """Reflect the Hex over the axis

        Args:
            axis (Literal['q', 'r', 's']): The axis to reflect over, either 'q', 'r' or 's'

        Returns:
            Hex: This Hex reflected over other Hex
        """
        if axis not in {"q", "r", "s"}:
            raise ValueError("Axis must be either 'q', 'r' or 's'")

        elif axis == "q":
            return Hex(self.q, self.s, self.r)

        elif axis == "r":
            return Hex(self.s, self.r, self.q)

        elif axis == "s":
            return Hex(self.r, self.q, self.s)

        # The following works but is less clear and 4 times slower
        # coords = tuple({"q", "r", "s"} - {axis})
        # reflected_hex = Hex(0, 0, 0)
        # reflected_hex[coords] = self[coords[::-1]]
        # return reflected_hex

    def reflected_around(self, other: Hex, axis: Literal["q", "r", "s"]) -> Hex:
        """Reflect the Hex over other Hex

        Args:
            other (Hex): The other Hex to reflect over

        Returns:
            Hex: This Hex reflected over other Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        return (self - other).reflected(axis) + other

    # lerp and linedraw

    def lerp(self, other: Hex, t: float) -> Hex:
        """Lerp from this Hex to other Hex at fraction `t`.

        Args:
            other (Hex): The Hex to lerp to
            t (float): The time fraction of lerp

        Raises:
            TypeError: If `other` is not of type `Hex`
            TypeError: If `t` is not of type `float`
            ValueError: If `t` is outside of range `0 <= t <= 1`

        Returns:
            Hex: The `Hex` coordinate at `t`
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        if not isinstance(t, float):
            raise TypeError(f"t must be of type 'float', not {type(t)}")

        if not 0 <= t <= 1:
            raise ValueError(f"t must be between 0 and 1, not {t}")

        return self * (1.0 - t) + other * t

    def nudge(self, factor: float = 1) -> None:
        """Inplace nudge Hex in a consistent direction.

        This is used get better consistency when, for instance, landing exactly between two cells during lerps.

        Raises:
            TypeError: If `factor` is not of type `float` or `int`
        """
        if not isinstance(factor, (float, int)):
            raise TypeError(f"t must be of type 'float' or 'int', not {type(factor)}")

        self.q -= 1e-06 * factor
        self.r += 1e-06 * factor

    def nudged(self, factor: float = 1) -> Hex:
        """Nudge Hex in a consistent direction.

        This is used have get better consistency when for instance landing between two grid cells in lerps.

        Raises:
            TypeError: If `factor` is not of type `float` or `int`

        Returns:
            Hex: This Hex nudged
        """
        if not isinstance(factor, (float, int)):
            raise TypeError(f"t must be of type 'float' or 'int', not {type(factor)}")

        return Hex(self.q + 1e-06 * factor, self.r + 1e-06 * factor)

    def linedraw(self, other: Hex) -> Iterator[Hex]:
        """Yield all Hexes amongst a line between this Hex and other Hex

        Args:
            other (Hex): The other Hex to linedraw to

        Yields:
            Iterator[Hex]: The Hexes from this Hex to other Hex, in order
        """
        if not isinstance(other, Hex):
            raise TypeError(f"other must be of type 'Hex', not {type(other)}")

        # Number of hexes that will be reqired
        steps = self.distance(other)

        # nudged_self = self.nudged()
        # nudged_other = other.nudged()

        # step_size = 1.0 / max(steps, 1)
        # for i in range(steps + 1):
        #     yield round(nudged_self.lerp_to(nudged_other, i * step_size))

        self.nudge()
        other.nudge()

        step_size = 1.0 / max(steps, 1)

        for i in range(steps + 1):
            yield self.lerp(other, i * step_size).rounded()

    # points and pixels

    def to_point(self) -> Point:
        """Convert this Hex to point based on Layout

        Note:
            `.to_point()` returns the same as `.to_pixel()` but `without rounding` the result.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Point: The exact center point of this Hex.
        """

        if not hasattr(self, "hexlayout"):
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.hexlayout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        O = self.hexlayout.orientation
        size = self.hexlayout.size
        origin = self.hexlayout.origin

        x = (O.f0 * self.q + O.f1 * self.r) * size.x
        y = (O.f2 * self.q + O.f3 * self.r) * size.y

        return Point(x + origin.x, y + origin.y)

        # THIS WORKS BUT IS HARDER TO READ AND A FRACTION SLOWER :(
        # transformed = Point(
        #     *np.matmul(self.hexlayout.orientation.forward, np.array([self.q, self.r]))
        # )
        # return transformed * self.hexlayout.size + self.hexlayout.origin

    def to_pixel(self) -> Point:
        """Convert this Hex to a pixel based on Layout

        Note:
            `.to_pixel()` returns the same as `.to_point()` but `rounds` the result.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Point: The exact center point of this Hex.
        """
        return round(self.to_point())

    def corner_offset(self, idx: int) -> Point:
        """Return corner offset from center of this Hex at index idx

        Args:
            idx (int): The index of the corner to get

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Point: A Point which is the offset from the centerpoint to the corner at idx
        """

        if not hasattr(self, "hexlayout"):
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.hexlayout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        size = self.hexlayout.size
        start_angle = self.hexlayout.orientation.start_angle

        angle = 2.0 * math.pi * (start_angle - idx) / 6.0
        trig_vec = Point(math.cos(angle), math.sin(angle))

        return trig_vec * size

    def polygon_points(self, factor: float = 1) -> Iterable[Point]:
        """Yeild all exact points forming self as a polygon.

        Note:
            `.polygon_points()` returns the same as `.polygon_pixels()` but `without rounding` the result.

        Args:
            factor (float, optional): Shrink size of Hex with factor. Defaults to 1.

        Raises:
            ValueError: If a Layout is not yet defined.

        Yields:
            Iterator[Point]: The pixels forming this Hex as a polygon
        """

        center = self.to_point()

        for i in range(6):
            offset = self.corner_offset(i)

            yield center + offset * factor

    def polygon_pixels(self, factor: float = 1) -> Iterator[Point]:
        """Yeild all pixels forming self as a polygon

        Note:
            `.polygon_pixels()` returns the same as `.polygon_points()` but `rounds` the result.

        Args:
            factor (float, optional): Shrink size of Hex by factor. Defaults to 1.

        Raises:
            ValueError: If a Layout is not yet defined.

        Yields:
            Iterator[Point]: The pixels forming this Hex as a polygon
        """
        for point in self.polygon_points(factor):
            yield round(point)

    @classmethod
    def from_pixel(cls, pixel: Point | tuple[float, float]) -> Hex:
        """Return the rounded Hex closest to the provided pixel based on the Hex layout.

        Note:
            `.from_pixel()` returns the same as `.from_point()` but `rounds` the result.

        Args:
            pixel (Point | tuple[float, float]): The pixel to calculate from.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: The Hex closest to the provided pixel
        """
        return round(cls.from_point(pixel))

    @classmethod
    def from_point(cls, pixel: Point | tuple[float, float]) -> Hex:
        """Return the Hex closest to the provided point based on the Hex layout.

        Note:
            `.from_point()` returns the same as `.from_pixel()` without `rounding` the result.

        Args:
            pixel (Point | tuple[float, float]): The pixel to calculate from.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: The Hex closest to the provided pixel
        """

        if cls.hexlayout is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.hexlayout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        O = cls.hexlayout.orientation
        size = cls.hexlayout.size
        origin = cls.hexlayout.origin

        pt = Point(*pixel)
        pt -= origin
        pt /= size

        q = O.b0 * pt.x + O.b1 * pt.y
        r = O.b2 * pt.x + O.b3 * pt.y

        return Hex(q, r)

    # layouts

    @classmethod
    def pointy_layout(
        cls,
        size: int | tuple[int, int] = 1,
        origin: tuple[int, int] = (0, 0),
    ) -> None:
        """_summary_

        Args:
            size (int | Point | tuple[int, int]): _description_
            origin (Point | tuple[int, int]): _description_
        """
        from . import layout, navigate

        cls.hexlayout = layout.pointy(size, origin)
        cls.hexclock = navigate.pointy_clock()
        cls.hexcompass = navigate.pointy_compass()

    @classmethod
    def flat_layout(
        cls,
        size: int | tuple[int, int] = 1,
        origin: tuple[int, int] = (0, 0),
    ) -> None:
        """_summary_

        Args:
            size (int | Point | tuple[int, int]): _description_
            origin (Point | tuple[int, int]): _description_
        """
        from . import layout, navigate

        cls.hexlayout = layout.flat(size, origin)
        cls.hexclock = navigate.flat_clock()
        cls.hexcompass = navigate.flat_compass()

    @classmethod
    def custom_layout(
        cls,
        orientation: Orientation,
        size: int | tuple[int, int] = 1,
        origin: tuple[int, int] = (0, 0),
        clockdict: Optional[dict[int, Hex]] = None,
        compassdict: Optional[dict[str, Hex]] = None,
    ) -> None:
        """_summary_

        Args:
            orientation (Orientation): _description_
            size (int | tuple[int, int], optional): _description_. Defaults to 1.
            origin (tuple[int, int], optional): _description_. Defaults to (0, 0).
            clockdict (Optional[dict[int, Hex]], optional): _description_. Defaults to None.
            compassdict (Optional[dict[str, Hex]], optional): _description_. Defaults to None.
        """
        from . import layout, navigate

        cls.hexlayout = layout.custom(orientation, size, origin)
        if clockdict is not None:
            cls.hexclock = navigate.custom_clock(clockdict)
        if compassdict is not None:
            cls.hexcompass = navigate.custom_compass(compassdict)

    @classmethod
    @overload
    def o_clock(cls, hours: int) -> Hex:
        ...

    @classmethod
    @overload
    def o_clock(cls, hours: tuple[int, ...]) -> HexClock:
        ...

    @classmethod
    def o_clock(cls, hours: int | tuple[int, ...]) -> Hex | HexClock:
        """_summary_

        Args:
            hours (int | tuple[int, ...]): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            Hex | HexClock: _description_
        """

        if not hasattr(cls, "hexclock"):
            raise RuntimeError(
                "'Layout' has not yet been defined, to define one use 'Hex.flat_layout(*args)', 'Hex.pointy_layout(*args)' or 'Hex.custom_layout(*args)'"
            )

        return cls.hexclock[hours]

    @classmethod
    @overload
    def compass(cls, points: str) -> Hex:
        ...

    @classmethod
    @overload
    def compass(cls, points: tuple[str, ...]) -> HexCompass:
        ...

    @classmethod
    def compass(cls, points: str | tuple[str, ...]) -> Hex | HexCompass:
        """_summary_

        Args:
            points (str | tuple[str, ...]): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            Hex | HexCompass: _description_
        """

        if not hasattr(cls, "hexcompass"):
            raise RuntimeError(
                "'Layout' has not yet been defined, to define one use 'Hex.flat_layout(*args)', 'Hex.pointy_layout(*args)' or 'Hex.custom_layout(*args)'"
            )

        return cls.hexcompass[points]


Hexigo = Hex(0, 0)
