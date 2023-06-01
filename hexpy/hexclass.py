from __future__ import annotations

import math
from collections.abc import Iterable
from itertools import cycle, islice
from typing import Iterator, Optional  # , Self

# This is to avoid circular imports, "Hex" is for instance used in hexclock
from . import hexclock, hexlayout
from .point import Point


class Hex:
    """Represents a Hexagon

    Examples:
        Create a new Hex at q = 1 and r = 2
        >>> Hex(1, 2)
        Hex(q=1, r=2, s=-3)

        Add two Hex
        >>> Hex(-1, 2) + Hex(1, 2)
        Hex(q=0, r=4, s=-4)

        Multiplicate a Hex by 3
        >>> Hex(1, 2) * 3
        Hex(q=3, r=6, s= -9)
    """

    __slots__ = ("q", "r")

    layout: hexlayout.Layout
    clock: hexclock.HexClock

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
            TypeError: If ``q, r or s`` are not all of type ``int`` or ``float``
            ValueError: If ``q, r and s`` does not add upp to ``0``
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

            This makes cube input safer compared to axial, due to the additional coord checking, but cube is not required and will not be stored.
        """
        coord_sum = sum(self.axial_coords) + new_s

        if round(coord_sum) != 0.0:
            raise ValueError(
                f"Incorrect coordinates: q + r + s must be equal to 0, but was equal to {coord_sum}"
            )

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

    @property
    def all_neighbors(self) -> tuple[Hex]:
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
        if self.clock is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        return tuple(self + direction for direction in self.clock)

    @property
    def directions(self) -> tuple[Hex]:
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            tuple[Hex]: _description_
        """
        if self.clock is None:
            # TODO
            raise ValueError(
                "'clock' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        return self.clock.directions

    @property
    def direct_neighbors(self) -> tuple[Hex]:
        """Return the clock neighbor at hour

        Note:
            TODO READ THIS: WITH A LINK

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: _description_
        """
        if self.clock is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )
        return tuple(self + direction for direction in self.clock.directions)

    @property
    def diagonals(self) -> tuple[Hex]:
        """_summary_

        Returns:
            tuple[Hex]: _description_
        """
        if self.clock is None:
            # TODO
            raise ValueError(
                "'clock' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        return self.clock.diagonals

    @property
    def diagonal_neighbors(self) -> tuple[Hex]:
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
        if self.clock is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        return tuple(self + diagonal for diagonal in self.clock.diagonals)

    def __setitem__(self, coords: Iterable[str], values: Iterable[float]):
        """Used to change q, r and s in a dict like manner

        Args:
            coords (Iterable[str]): The coords to change
            values (Iterable[float]): The values to coords change to

        Example:
            >>> hex = Hex(1, 2, -3)
            >>> hex['q', 'r'] = (2, 1)
            >>> hex
            Hex(q=2, r=1, s=-3)
        """

        # TODO if not 2 <= len(coords) <= 3: raise ValueError()

        for coord, value in zip(coords, values):
            # TODO if coord not in self.__slots__: raise ValueError()

            setattr(self, coord, value)

        # self.__dict__.update(zip(attrlist, valuelist))

    def __round__(self, ndigits: Optional[int] = None) -> Hex:
        """Round the Hex coordinates to whole integers

        Args:
            ndigits (int, optional): The number of digits to round to. Defaults to None.. Defaults to None.

        Returns:
            Hex: This Hex with rounded coordinates
        """

        # Apperently these listcomprehensions are slower... :(
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

    def round(self, ndigits: Optional[int] = None) -> Hex:
        """Round the coordinates of this Hex

        Note:
            This can also be done using the function ``round()`` on a Hex.

        Args:
            ndigits (int, optional): The number of digits to round to. Defaults to None.

        Returns:
            Hex: This Hex with rounded coordinates
        """
        return round(self, ndigits)

    def inplace_round(self, ndigits: Optional[int] = None) -> Hex:
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

        return self

    def __iter__(self) -> Iterator[float]:
        """Iterate through this Hex's axial coords

        Yields:
            Iterator[float]: _description_
        """

        yield from self.axial_coords

    def __hash__(self) -> int:
        """Return (q, r) as a hash number

        Returns:
            int: hash of this Hex's axial coords
        """

        return hash(self.axial_coords)

    def __repr__(self) -> str:
        """Return a nicely formatted Hex representation string"""
        q, r, s = self.cube_coords

        return f"Hex({q=}, {r=}, {s=})"

    def __len__(self) -> int:
        """Get the displacement from this Hex to Hexigo"""
        return round((abs(self.q) + abs(self.r) + abs(self.s)) / 2)

    def length(self, other: Optional[Hex] = None) -> int:
        """Get the displacement from this Hex to other Hex

        Note:
            This can also be done using ``len(thisHex - otherHex)``.

        Args:
            other (Hex, optional): The Hex to get distance to if ``other`` is omitted ``Hexigo`` will be used. Defaults to None.

        Raises:
            TypeError: If ``other`` is not of type ``Hex``.

        Returns:
            int: The length, which can be thought of as the least amount of Hexes you have to pass through when walking from this Hex to other.
        """

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot get length from {self} of type {type(self)} to {other} of type {type(other)}"
            )

        return len(self) if other is None else len(self - other)

    def __neg__(self) -> Hex:
        """Negate the values of self, effectively flipping it around Hexigo

        Returns:
            Hex: This Hex but negated
        """
        return Hex(-self.q, -self.r)

    def __add__(self, other: Hex) -> Hex:
        """Add this Hex with other Hex

        Args:
            other (Hex): The Hex to add with

        Raises:
            TypeError: If ``other`` is not of type ``Hex``

        Returns:
            Hex: This Hex added to other Hex
        """

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot add {self} of type {type(self)} to {other} of type {type(other)}"
            )

        return Hex(self.q + other.q, self.r + other.r)

    __radd__ = __add__

    def __iadd__(self, other: Hex):  # -> Self:
        """Add this Hex with other Hex inplace

        Args:
            other (Hex): The Hex to add with

        Raises:
            TypeError: If ``other`` is not of type ``Hex``

        Returns:
            Hex: This Hex added to other Hex
        """

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot add {self} of type {type(self)} to {other} of type {type(other)}"
            )

        self.axial_coords = (self.q + other.q, self.r + other.q)

        return self

    def __sub__(self, other: Hex) -> Hex:
        """Subtract this Hex by other Hex

        Args:
            other (Hex): The Hex to subtract by

        Raises:
            TypeError: If ``other`` is not of type ``Hex``

        Returns:
            Hex: This Hex subtracted by other Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot subtract {self} of type {type(self)} from {other} of type {type(other)}"
            )

        return self + -other

    def __rsub__(self, other: Hex) -> Hex:
        """Subtract other Hex by this Hex

        Args:
            other (Hex): The Hex to subtract from

        Raises:
            TypeError: If ``other`` is not of type ``Hex``

        Returns:
            Hex: The other Hex subtracted by this Hex
        """

        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot subtract {self} of type {type(self)} from {other} of type {type(other)}"
            )

        return other + -self

    def __isub__(self, other: Hex):  # -> Self:
        """Subtract this Hex by other Hex inplace

        Args:
            other (Hex): The Hex to subtract by

        Raises:
            TypeError: If ``other`` is not of type ``Hex``

        Returns:
            Hex: This Hex subtracted by other Hex
        """
        if not isinstance(other, Hex):
            raise TypeError(
                f"Cannot subtract {self} of type {type(self)} from {other} of type {type(other)}"
            )

        self.axial_coords = (self.q - other.q, self.r - other.s)

        return self

    def __mul__(self, k: float) -> Hex:
        """Multiplicate ``this Hex`` by factor ``k``

        Args:
            k (float): The factor to multiply by

        Raises:
            TypeError: If ``k`` is not of type ``int`` or ``float``

        Returns:
            Hex: This Hex multiplied by k
        """

        if not isinstance(k, (int, float)):
            raise TypeError(
                f"Cannot multiplicate {self} of type {type(self)} with {k} of type {type(k)}"
            )

        return Hex(self.q * k, self.r * k)

    __rmul__ = __mul__

    def __imul__(self, k: float):  # -> Self
        """Multiplicate ``this Hex`` by factor ``k``

        Args:
            k (float): The factor to multiply by

        Raises:
            TypeError: If ``k`` is not of type ``int`` or ``float``

        Returns:
            Hex: This Hex multiplied by k
        """

        if not isinstance(k, (int, float)):
            raise TypeError(
                f"Cannot multiplicate {self} of type {type(self)} with {k} of type {type(k)}"
            )

        self.axial_coords = (self.q * k, self.r * k)

        return self

    def __truediv__(self, d: float) -> Hex:
        """Divide ``this Hex`` by divisor ``d``

        Args:
            d.(float): The divisor to divide by

        Raises:
            TypeError: If ``d`` is not of type ``int`` or ``float``

        Returns:
            Hex: This Hex divided by d
        """

        if not isinstance(d, (int, float)):
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {d} of type {type(d)}"
            )

        return Hex(self.q / d, self.r / d)

    def __itruediv__(self, d: float):  # -> Self
        """Divide ``this Hex`` by divisor ``d``

        Args:
            d.(float): The divisor to divide by

        Raises:
            TypeError: If ``d`` is not of type ``int`` or ``float``

        Returns:
            Hex: This Hex divided by d
        """

        if not isinstance(d, (int, float)):
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {d} of type {type(d)}"
            )

        self.axial_coords = (self.q / d, self.r / d)
        return self

    def __floordiv__(self, d: float) -> Hex:
        """Divide ``this Hex`` by divisor ``d`` and round the result

        Args:
            d.(float): The divisor to divide by

        Raises:
            TypeError: If ``d`` is not of type ``int`` or ``float``

        Returns:
            Hex: This Hex divided by d
        """

        if not isinstance(d, (int, float)):
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {d} of type {type(d)}"
            )

        return round(Hex(self.q / d, self.r / d))

    def __ifloordiv__(self, d: float):  # -> Self
        """Divide ``this Hex`` by divisor ``d`` and round the result inplace

        Args:
            d.(float): The divisor to divide by

        Raises:
            TypeError: If ``d`` is not of type ``int`` or ``float``

        Returns:
            Hex: This Hex divided by d
        """

        if not isinstance(d, (int, float)):
            raise TypeError(
                f"Cannot divide {self} of type {type(self)} with {d} of type {type(d)}"
            )

        self.axial_coords = (self.q / d, self.r / d)
        self.inplace_round()

        return self

    def __eq__(self, other: Hex) -> bool:
        """Check if this Hex is equal to other.

        Args:
            other (Hex): The Hex to compare with

        Returns:
            bool: Whether or not the coords of this Hex and other Hex are equal
        """
        if isinstance(other, Hex):
            return self.axial_coords == other.axial_coords

        return False

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
        """Check if Hex has c as a cube coord"""

        return c in self.cube_coords

    def rotate_left(self, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the left around Hexigo.

        Note:
            This can also be done using left shift operator, ``Hex << steps``.

        Args:
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Returns:
            Hex: This Hex rotated left around Hexigo.
        """

        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the left
        rotated_hex = Hex(*islice(cycle(self.cube_coords), 3 - n, 6 - n))

        # Negate the hex values if rotating odd amount of steps
        return -rotated_hex if steps % 2 else rotated_hex

    def rotate_left_around(self, other: Hex, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the left around other Hex.

        Note:
            This can also be done using left shift operator, ``Hex << Hex`` or ``Hex << (Hex, steps)``.

        Args:
            other (Hex): The other Hex to rotate around.
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Returns:
            Hex: This Hex rotated left around other.
        """
        return (self - other).rotate_left(steps) + other

    def __lshift__(self, input: int | Hex | tuple[Hex, int]) -> Hex:
        """Convienience method for both rotate_left() and rotate_left_around().

        Args:
            input (int | Hex | tuple[Hex, int]): If only an ``int`` is provided that will be used as steps to rotate around ``Hexigo``.
                If only a ``Hex`` is provided that will be used as a centerpoint and rotated 1 step around.
                If a tuple with Hex as first argument and int as second is provided that will be used as centerpoint and steps respectively.

        Raises:
            TypeError: TODO

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
        """Rotate the Hex 60 * steps degrees to the right around Hexigo.

        Note:
            This can also be done using right shift operator, ``Hex >> steps``.

        Args:
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Returns:
            Hex: This Hex rotated right around Hexigo.
        """
        n = steps % 3 if steps >= 0 else -(abs(steps) % 3)

        # Get a new hex with q, r, s rotated steps % 3 to the right
        rotated_hex = Hex(*islice(cycle(self.cube_coords), n, 3 + n))

        # Negate the hex values if rotating odd amount of steps
        return -rotated_hex if steps % 2 else rotated_hex

    def rotate_right_around(self, other: Hex, steps: int = 1) -> Hex:
        """Rotate the Hex 60 * steps degrees to the right around other Hex.

        Note:
            This can also be done using right shift operator, ``Hex >> Hex`` or ``Hex >> (Hex, steps)``.

        Args:
            other (Hex): The other Hex to rotate around.
            steps (int, optional): Amount of 60 degree steps to rotate. Defaults to 1.

        Returns:
            Hex: This Hex rotated right around other.
        """
        return (self - other).rotate_right(steps) + other

    def __rshift__(self, input: int | Hex | tuple[Hex, int]) -> Hex:
        """Convienience method for both rotate_right() and rotate_right_around().

        Args:
            input (int | Hex | tuple[Hex, int]): If only an ``int`` is provided that will be used as steps to rotate around ``Hexigo``.
                If only a ``Hex`` is provided that will be used as a centerpoint and rotated 1 step around.
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
            return self.rotate_right(input)

        # Just other Hex was provided, rotate 1 step around other Hex
        elif isinstance(input, Hex):
            return self.rotate_right_around(input)

        # Both other Hex and steps was provided
        elif (
            isinstance(input, tuple)
            and isinstance(input[0], Hex)
            and isinstance(input[1], int)
        ):
            return self.rotate_right_around(*input)

        else:
            # TODO
            raise TypeError("")

    def coordinate_range(self, radius: int) -> Iterator[Hex]:
        """Get all Hexes within a certain radius from this Hex

        Args:
            radius (int): The radius of the range

        Yields:
            Iterator[Hex]: The Hexes
        """

        for q in range(-radius, radius + 1):
            start = max(-radius, -q - radius)
            stop = min(+radius, -q + radius)

            for r in range(start, stop + 1):
                yield self + Hex(q, r)

    def lerp_to(self, other: Hex, t: float) -> Hex:
        """Lerp from this Hex to other Hex at fraction ``t``.

        Args:
            other (Hex): The Hex to lerp to
            t (float): The time fraction of lerp

        Raises:
            ValueError: If ``t`` is outside of range ``0 <= t <= 1``

        Returns:
            Hex: The ``Hex`` coordinate at ``t``
        """
        # TODO if not isinstance(other, Hex): raise TypeError("")

        # TODO if not isinstance(t, floatS): raise TypeError("")

        if not 0 <= t <= 1:
            raise ValueError("Fraction t of lerp was out of range 0 <= t <= 1")

        return self * (1.0 - t) + other * t

    def nudge(self) -> Hex:
        """Nudge Hex in a consistent direction.

        This is used have get better consistency when for instance landing between two grid cells in lerps.

        Returns:
            Hex: This Hex nudged
        """

        return Hex(self.q + 1e-06, self.r + 1e-06)

    def linedraw_to(self, other: Hex) -> Iterator[Hex]:
        """Yield all Hexes amongst a line between this Hex and other Hex

        Args:
            other (Hex): The other Hex to linedraw to

        Yields:
            Iterator[Hex]: The Hexes from this Hex to other Hex, in order
        """

        # Number of hexes that will be reqired
        steps = self.length(other)

        nudged_self = self.nudge()
        nudged_other = other.nudge()

        step_size = 1.0 / max(steps, 1)
        for i in range(steps + 1):
            yield round(nudged_self.lerp_to(nudged_other, i * step_size))

    def to_point(self) -> Point:
        """Convert this Hex to point based on Layout

        Note:
            ``.to_point()`` returns the same as ``.to_pixel()`` but ``without rounding`` the result.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Point: The exact center point of this Hex.
        """

        if self.layout is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        O = self.layout.orientation
        size = self.layout.size
        origin = self.layout.origin

        x = (O.f0 * self.q + O.f1 * self.r) * size.x
        y = (O.f2 * self.q + O.f3 * self.r) * size.y

        return Point(x + origin.x, y + origin.y)

        # THIS WORKS BUT IS HARDER TO READ AND A FRACTION SLOWER :(
        # transformed = Point(
        #     *np.matmul(self.layout.orientation.forward, np.array([self.q, self.r]))
        # )
        # return transformed * self.layout.size + self.layout.origin

    def to_pixel(self) -> Point:
        """Convert this Hex to point based on Layout

        Note:
            ``.to_pixel()`` returns the same as ``.to_point()`` but ``rounds`` the result.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Point: The exact center point of this Hex.
        """
        return round(self.to_point())

    def corner_offset(self, idx: int) -> Point:
        """Return corner offset from center of this Hex at index idx

        Args:
            idx (int): The corner index

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Point: A Point which is the offset from the centerpoint to the corner at idx
        """

        if self.layout is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        size = self.layout.size
        start_angle = self.layout.orientation.start_angle

        angle = 2.0 * math.pi * (start_angle - idx) / 6.0
        trig_vec = Point(math.cos(angle), math.sin(angle))

        return trig_vec * size

    def polygon_points(self, factor: float = 1) -> Iterable[Point]:
        """Yeild all exact points forming self as a polygon.

        Note:
            ``.polygon_points()`` returns the same as ``.polygon_pixels()`` but ``without rounding`` the result.

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
            ``.polygon_pixels()`` returns the same as ``.polygon_points()`` but ``rounds`` the result.

        Args:
            factor (float, optional): Shrink size of Hex with factor. Defaults to 1.

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
            ``.from_pixel()`` returns the same as ``.from_point()`` but ``rounds`` the result.

        Args:
            pixel (Point | tuple[float, float]): The pixel to calculate from.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: The Hex closest to the provided pixel
        """
        return round(cls.from_point(pixel))

        # pixel = (Point(*pixel) - origin) / size

        # transformed = np.matmul(cls.orientation.backward, np.array([pixel.x, pixel.y]))
        # return round(Hex(*transformed))

    @classmethod
    def from_point(cls, pixel: Point | tuple[float, float]) -> Hex:
        """Return the Hex closest to the provided point based on the Hex layout.

        Note:
            ``.from_point()`` returns the same as ``.from_pixel()`` without ``rounding`` the result.

        Args:
            pixel (Point | tuple[float, float]): The pixel to calculate from.

        Raises:
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: The Hex closest to the provided pixel
        """

        if cls.layout is None:
            raise ValueError(
                "'Layout' has not yet been defined, use Hex.layout = 'Layout.pointy()' or 'Layout.flat()' to define a layout."
            )

        origin = cls.layout.origin
        size = cls.layout.size

        pt = Point(*pixel)
        pt -= origin
        pt /= size

        O = cls.layout.orientation
        size = cls.layout.size
        origin = cls.layout.origin

        q = O.b0 * pt.x + O.b1 * pt.y
        r = O.b2 * pt.x + O.b3 * pt.y

        return Hex(q, r)

    @classmethod
    def pointy_layout(
        cls,
        size: int | Point | tuple[int, int],
        origin: Point | tuple[int, int],
    ) -> None:
        """_summary_

        Args:
            size (int | Point | tuple[int, int]): _description_
            origin (Point | tuple[int, int]): _description_
        """
        cls.layout = hexlayout.pointy(size, origin)
        cls.clock = hexclock.pointy()

    @classmethod
    def flat_layout(
        cls,
        size: int | Point | tuple[int, int],
        origin: Point | tuple[int, int],
    ) -> None:
        """_summary_

        Args:
            size (int | Point | tuple[int, int]): _description_
            origin (Point | tuple[int, int]): _description_
        """
        cls.layout = hexlayout.flat(size, origin)
        cls.clock = hexclock.flat()

    @classmethod
    def custom_layout(
        cls,
        size: int | Point | tuple[int, int],
        origin: Point | tuple[int, int],
        orientation: hexlayout.Orientation,
    ) -> None:
        """_summary_

        Args:
            size (int | Point | tuple[int, int]): _description_
            origin (Point | tuple[int, int]): _description_
            orientation (hexlayout.Orientation): _description_
        """
        cls.layout = hexlayout.custom(size, origin, orientation)
        cls.clock = hexclock.pointy()


Hexigo = Hex(0, 0)
