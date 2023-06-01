# TODO
from __future__ import annotations

from collections.abc import Iterator

# from .hexclock import Clock
from .hexclass import Hex
from .hexlayout import Layout, Orientation, flat_orientation, pointy_orientation


def pointy() -> HexClock:
    """_summary_

    Returns:
        HexClock: _description_
    """
    return HexClock(pointy_orientation)


def flat() -> HexClock:
    """_summary_

    Returns:
        HexClock: _description_
    """
    return HexClock(flat_orientation)


def custom(orientation: Orientation) -> HexClock:
    """_summary_

    Args:
        layout (Layout): _description_

    Returns:
        HexClock: _description_
    """
    return HexClock(orientation)


class HexClock(tuple):
    """Represents a HexClock.

    Note:
        READ THIS: TODO TO GET A BETTER UNDERSTANDNIG

    Examples:
    """

    def __new__(cls, orient: Orientation) -> HexClock:
        """Create a new HexClock from the provided layout

        Args:
            layout (Layout.Layout): _description_

        Returns:
            tuple: A tuple containing the HexClock
        """

        # clock for pointy or custom layout
        hexclock = (
            Hex(1, -2),  # 0/12
            Hex(1, -1),  # 1
            Hex(2, -1),  # 2
            Hex(1, 0),  # 3
            Hex(1, 1),  # 4
            Hex(0, 1),  # 5
            Hex(-1, 2),  # 6
            Hex(-1, 1),  # 7
            Hex(-2, 1),  # 8
            Hex(-1, 0),  # 9
            Hex(-1, -1),  # 10
            Hex(0, -1),  # 11
        )

        # This allows both Orientation or Layout classes to be passed in as input
        if orient == flat_orientation:
            # flat layout,  flat is the same as pointy or custom but shifted a step
            hexclock = hexclock[-1:] + hexclock[:-1]

        return tuple.__new__(cls, hexclock)

    def __init__(self, orient: Orientation) -> None:
        """_summary_

        Args:
            orient (Orientation): _description_
        """
        flat = orient == flat_orientation

        self._directions = slice(0, 12, 2) if flat else slice(1, 13, 2)
        self._diagonals = slice(1, 13, 2) if flat else slice(0, 12, 2)

    def __iter__(self) -> Iterator:
        return super().__iter__()

    def __getitem__(self, given: slice | int | tuple) -> None | Hex | tuple[Hex]:
        if isinstance(given, (slice, int)):
            return super().__getitem__(given)

        elif isinstance(given, tuple):
            return tuple(super(HexClock, self).__getitem__(hour) for hour in given)

    @property
    def directions(self) -> tuple[Hex]:
        """Get all directions on the clock

        Note:
            TODO READ THIS: WITH A LINK

        Raises:
            TypeError: _description_
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: _description_
        """
        return self[self._directions]  # type: ignore

    @property
    def diagonals(self) -> tuple[Hex]:
        """Get all diagonals on the clock

        Note:
            TODO READ THIS: WITH A LINK

        Args:
            hour (int): The hour to get direction in

        Raises:
            TypeError: _description_
            ValueError: If a Layout is not yet defined.

        Returns:
            Hex: _description_
        """
        return self[self._diagonals]  # type: ignore

    # def plot(layout: Layout) -> None:
