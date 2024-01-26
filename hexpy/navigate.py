# Author: Elis Grahn

from __future__ import annotations

from typing import Any, Generator, Optional, overload

from .hexclass import Hex
from .layout import Orientation, flat_orientation, pointy_orientation


class HexClock(dict):
    """Represents a HexClock.

    Note:
        READ THIS: TODO TO GET A BETTER UNDERSTANDNIG

    Examples:
    """

    __slots__ = ()

    def __init__(self, clockdict: dict[int, Hex]) -> None:
        """Create a HexClock from the provided orientation"""

        super().__init__(clockdict)

    def directions(self, orientation: Orientation) -> HexClock:
        """_summary_

        Returns:
            _type_: _description_
        """
        # TODO test if it is faster to pre calculate and store directions in _directions instead of calculating them every time

        flat = orientation == flat_orientation
        return self[:12:2] if flat else self[1:13:2]

    def diagonals(self, orientation: Orientation) -> HexClock:
        """The diagonals of the HexClock

        Returns:
            HexClock: A new HexClock containing only the diagonals of the original
        """
        # TODO test if it is faster to pre calculate and store diagonals in _diagonals instead of calculating them every time

        flat = orientation == flat_orientation
        return self[1:13:2] if flat else self[:12:2]

    def shifted(self, hx: Hex) -> HexClock:
        """_summary_

        Args:
            hx (Hex): _description_

        Returns:
            HexClock: _description_
        """
        return HexClock({h: hx + clk_hx for h, clk_hx in self.items()})

    @overload
    def __getitem__(self, hours: int) -> Hex:
        ...

    @overload
    def __getitem__(self, hours: slice | tuple[int, ...]) -> HexClock:
        ...

    def __getitem__(self, hours: int | slice | tuple[int, ...]) -> Hex | HexClock:
        """Get Hex at clock hour(s)

        Args:
            __key (str | tuple[str]): _description_

        Returns:
            Hex: _description_
        """

        if isinstance(hours, int):
            if not 0 <= hours <= 12:
                raise KeyError(f"HexClock has no hour '{hours}'")

            return super().__getitem__(hours % 12)

        elif isinstance(hours, tuple):
            if not all(isinstance(h, int) for h in hours):
                raise TypeError(
                    "If a HexClock is provided a tuple, all items must be of type 'int'"
                )

            return HexClock({h % 12: self[h] for h in hours if h % 12 in self})

        elif isinstance(hours, slice):
            return HexClock(
                {h % 12: self[h] for h in range(*hours.indices(13)) if h % 12 in self}
            )

        else:
            raise TypeError("HexClock key must be of type 'int', 'tuple' or 'slice'")

    # Because why not?
    __call__ = __getitem__

    def __iter__(self) -> Generator[Hex, None, None]:
        yield from super().values()

    def __in__(self, value) -> bool:
        return value in self.values()

    def __str__(self) -> str:
        """Return a nicely formatted HexMap representation string"""
        return super().__repr__().replace("), ", "),\n ")

    def __repr__(self) -> str:
        """Return the canonical string representation of HexMap."""
        return f"hexpy.navigate.HexClock({str(self)})"


def flat_clock() -> HexClock:
    """_summary_

    Returns:
        HexClock: _description_
    """
    clockdict = {
        0: Hex(0, -1),  # 0/12
        1: Hex(1, -2),  # 1
        2: Hex(1, -1),  # 2
        3: Hex(2, -1),  # 3
        4: Hex(1, 0),  # 4
        5: Hex(1, 1),  # 5
        6: Hex(0, 1),  # 6
        7: Hex(-1, 2),  # 7
        8: Hex(-1, 1),  # 8
        9: Hex(-2, 1),  # 9
        10: Hex(-1, 0),  # 10
        11: Hex(-1, -1),  # 11
    }
    return HexClock(clockdict)


def pointy_clock() -> HexClock:
    """_summary_

    Returns:
        HexClock: _description_
    """
    clockdict = {
        0: Hex(1, -2),  # 0/12
        1: Hex(1, -1),  # 1
        2: Hex(2, -1),  # 2
        3: Hex(1, 0),  # 3
        4: Hex(1, 1),  # 4
        5: Hex(0, 1),  # 5
        6: Hex(-1, 2),  # 6
        7: Hex(-1, 1),  # 7
        8: Hex(-2, 1),  # 8
        9: Hex(-1, 0),  # 9
        10: Hex(-1, -1),  # 10
        11: Hex(0, -1),  # 11
    }
    return HexClock(clockdict)


def custom_clock(clockdict: dict[int, Hex]) -> HexClock:
    """_summary_

    Args:
        layout (Layout): _description_

    Returns:
        HexClock: _description_
    """
    return HexClock(clockdict)


class HexCompass(dict):
    """_summary_

    Args:
        dict (_type_): _description_

    Raises:
        KeyError: _description_
        TypeError: _description_

    Returns:
        _type_: _description_
    """

    __slots__ = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")

    def __init__(self, compassdict: dict[str, Hex]) -> None:
        """Create a HexCompass from the provided orientation"""

        super().__init__(compassdict)

        for name in compassdict:
            self.__setattr__(name, self[name])

    def shifted(self, hx: Hex) -> HexCompass:
        """_summary_

        Args:
            hx (Hex): _description_

        Returns:
            HexClock: _description_
        """
        return HexCompass({h: hx + cmp_hx for h, cmp_hx in self.items()})

    @overload
    def __getitem__(self, points: str) -> Hex:
        ...

    @overload
    def __getitem__(self, points: tuple[str, ...]) -> HexCompass:
        ...

    def __getitem__(self, points: str | tuple[str, ...]) -> Hex | HexCompass:
        """Get Hex at compass point(s)

        Args:
            __key (str | tuple[str]): _description_

        Returns:
            Hex: _description_
        """
        if isinstance(points, str):
            if points not in self:
                raise KeyError(
                    f"""HexCompass has no point '{points}'
                For pointy layout, valid ones are ('NE', 'E', 'SE', 'SW', 'W', 'NW')
                For flat layout, valid ones are ('N', 'NE', 'SE', 'S', 'SW', 'NW')
                """
                )
            return super().__getitem__(points)

        elif isinstance(points, tuple):
            return HexCompass({p: self[p] for p in points})

        # HexCompass doesn't support slicing

        else:
            raise TypeError("HexCompass key must be of type 'str' or tuple[str, ...]")

    # Because why not?
    __call__ = __getitem__

    def __iter__(self) -> Generator[Hex, None, None]:
        yield from super().values()

    def __in__(self, value) -> bool:
        return value in self.values()

    def __str__(self) -> str:
        """Return a nicely formatted HexMap representation string"""
        return super().__repr__().replace("), '", "),\n '")

    def __repr__(self) -> str:
        """Return the canonical string representation of HexMap."""
        return f"navigate.HexCompass({str(self)})"


def flat_compass() -> HexCompass:
    """_summary_

    Returns:
        HexClock: _description_
    """
    compassdict = {
        "N": Hex(0, -1),  # 0/12
        "NE": Hex(1, -1),  # 2
        "SE": Hex(1, 0),  # 4
        "S": Hex(0, 1),  # 6
        "SW": Hex(-1, 1),  # 8
        "NW": Hex(-1, 0),  # 10
    }
    return HexCompass(compassdict)


def pointy_compass() -> HexCompass:
    """_summary_

    Returns:
        HexClock: _description_
    """
    compassdict = {
        "NE": Hex(1, -1),  # 1
        "E": Hex(1, 0),  # 3
        "SE": Hex(0, 1),  # 5
        "SW": Hex(-1, 1),  # 7
        "W": Hex(-1, 0),  # 9
        "NW": Hex(0, -1),  # 11
    }

    return HexCompass(compassdict)


def custom_compass(
    compassdict: dict[str, Hex],
) -> HexCompass:
    """_summary_

    Args:
        layout (Layout): _description_

    Returns:
        HexClock: _description_
    """
    return HexCompass(compassdict)
