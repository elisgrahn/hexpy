"""Method to create HexMaps

To create :py:class:`hexpy.HexMap.HexMap` objects, use an appropriate factory
function.
* :py:func:`~hexpy.HexMap.new`              - Create a new empty HexMap
* :py:func:`~hexpy.HexMap.hexagon`          - Create a hexagon shaped HexMap
---
* :py:func:`~hexpy.HexMap.triangle`         - Create a triangle shaped HexMap
* :py:func:`~hexpy.HexMap.star`             - Create a star shaped HexMap (special case of triangle)
---
* :py:func:`~hexpy.HexMap.parallelogram`    - Create a parallelogram shaped HexMap
* :py:func:`~hexpy.HexMap.rhombus`          - Create a rhombus shaped HexMap (special case of parallelogram)
---
* :py:func:`~hexpy.HexMap.rectangle`        - Create a rectangle shaped HexMap
* :py:func:`~hexpy.HexMap.square`           - Create a square shaped HexMap (special case of rectangle)
---
* :py:func:`~hexpy.HexMap.open`             - Open a saved HexMap

Examples:

    Create a HexMap with the six neighbors to Hexigo.

    >>> HexMap.hexagon(radius=1, value=0, hexorigin=Hexigo, hollow=True)
    {Hex(q=-1, r=0, s=1): 0,
     Hex(q=-1, r=1, s=0): 0,
     Hex(q=0, r=-1, s=1): 0,
     Hex(q=0, r=1, s=-1): 0,
     Hex(q=1, r=-1, s=0): 0,
     Hex(q=1, r=0, s=-1): 0}

    Open and plot an already saved hxmp.

    >>> hxmp = HexMap.open("./my_hexmap.pkl")
    >>> hxmp.plot()
    <Figure size 640x480 with 1 Axes>

    Set Hex(1, 2, -3) to '(3, "house") in loaded HexMap,

    >>> hxmp.insert(Hex(1, 2), value=(3, "house"))

    The above is the same as
    >>> hxmp[Hex(1, 2)] = (3, "house")

    Lastly save the HexMap again.

    >>> hxmp.save("./my_updated_hexmap.pkl")
"""


from __future__ import annotations

import builtins
import inspect
import itertools
import pickle
import warnings
from collections.abc import Iterable, Set
from math import floor
from pathlib import Path
from typing import Any, Callable, Generator, Iterator, Optional

from _collections_abc import dict_items, dict_keys, dict_values
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .hexclass import Hex, Hexigo

# import dill # TODO maybe replace pickle with dill


def new(value: Any = None, hexorigin: Hex = Hexigo) -> HexMap:
    """Creates a new empty HexMap

    Args:
        value (Any, optional): Value that will be assigned to new Hexes added to HexMap. Defaults to None.
        hexorigin (Hex, optional): Origin of the HexMap, all new Hexes will be offset by hexorigin. Defaults to Hexigo.

    Returns:
        HexMap: An empty HexMap representing a Hexagonal grid
    """
    return HexMap(default_value=value, origin_offset=hexorigin)


# TODO following functions
def fromdict(
    hexes: dict[Hex, Any], value: Any = None, hexorigin: Hex = Hexigo
) -> HexMap:
    """Create a HexMap from the given dict with Hex as keys

    Args:
        hexes (dict[Hex, Any]): A dict with ``Hex`` as keys
        value (Any, optional): Value that will be assigned to new Hexes added to HexMap. Defaults to None.
        hexorigin (Hex, optional): Origin of the HexMap, all new Hexes will be offset by hexorigin. Defaults to Hexigo.

    Returns:
        HexMap: _description_
    """
    return HexMap(hexes, default_value=value, origin_offset=hexorigin)


def fromiter(
    hexes: Iterable[Hex], value: Any = None, hexorigin: Hex = Hexigo
) -> HexMap:
    """Create a new HexMap from the given iterable of Hex

    Args:
        hexes (dict[Hex, Any]): An iterable of ``Hex``
        value (Any, optional): Value that will be assigned to new Hexes added to HexMap. Defaults to None.
        hexorigin (Hex, optional): Origin of the HexMap, all new Hexes will be offset by hexorigin. Defaults to Hexigo.
    Raises:
        TypeError: _description_

    Returns:
        HexMap: _description_
    """
    if not isinstance(hexes, Iterable):
        # TODO
        raise TypeError("")

    hexes = {hex: value for hex in hexes}

    return HexMap(hexes, default_value=value, origin_offset=hexorigin)


def open(filepath: str) -> HexMap:
    """Open a saved HexMap at filepath

    Args:
        filepath (str): Path to the HexMap ``.pkl`` file

    Returns:
        HexMap: HexMap saved at ``filepath``
    """

    with builtins.open(filepath, "rb") as f:
        return pickle.load(f)


class HexMap(dict):
    """A dict, with ``hexpy.Hex`` as keys, which representing a generic Hexagonal grid

    To create :py:class:`hexpy.HexMap.HexMap` objects, use an appropriate factory
    function. There's hardly ever any reason to call the HexMap constructor directly.

    Examples:
    >>> TODO
    """

    def __init__(
        self,
        hexes: Optional[dict[Hex, Any]] = None,
        default_value: Any = None,
        origin_offset: Hex = Hexigo,
    ) -> None:
        """Create a hexagonal grid map of hexes.

        Args:
            hexes (dict[Hex, Any], optional): If provided it will become the inital HexMap. Defaults to None.
            default_value (Any, optional): Default value that will be assigned to new Hexes added to HexMap. Defaults to None.
            origin_offset (Hex, optional): Origin of the HexMap, all new Hexes will be offset by hexorigin. Defaults to Hexigo.
        """

        self.default = default_value
        self.hexorigin = origin_offset

        if hexes is None:
            super().__init__()

        elif not isinstance(hexes, dict):
            # TODO
            raise TypeError("")

        elif not all(isinstance(hex, Hex) for hex in hexes):
            # TODO
            raise TypeError("")

        else:
            super().__init__(hexes)

    def _new(self, hexes: dict[Hex, Any]) -> HexMap:
        """Create a new HexMap, passing on the default value and hexorigin offset

        Args:
            hexes (dict[Hex, Any]): Hexes for the new HexMap

        Returns:
            HexMap: The new HexMap
        """
        return HexMap(hexes, self.default, self.hexorigin)

    def copy(self) -> HexMap:
        """Create a new identical HexMap

        Returns:
            HexMap: A copy of this HexMap
        """
        return HexMap(dict(self), self.default, self.hexorigin)

    def keys(self) -> dict_keys[Hex, Any]:
        """Wrapper method of .keys() to provide type annotation.

        Returns:
            dict_keys[Hex, Any]: A set-like object providing a view on HexMap Hexes
        """
        return super().keys()

    def hexes(self) -> dict_keys[Hex, Any]:
        """Wrapper method of .keys() to improve readability.

        Returns:
            dict_keys[Hex, Any]: A set-like object providing a view on HexMap Hexes
        """
        return self.keys()

    def items(self) -> dict_items[Hex, Any]:
        """Wrapper method of .items() to provide type annotation.

        Returns:
            dict_items[Hex, Any]: A set-like object providing a view on HexMap items (pairs of Hex and value)
        """
        return super().items()

    def hexes_and_values(self) -> dict_items[Hex, Any]:
        """Wrapper method of .items() to improve readability.

        Returns:
            dict_items[Hex, Any]: A set-like object providing a view on HexMap items (pairs of Hex and value)
        """
        return self.items()

    def values(self) -> dict_values[Hex, Any]:
        """Wrapper method of .values() to provide type annotation.

        Returns:
            dict_values[Hex, Any]: _description_
        """
        return super().values()

    def get_hexes(self, desired_values: Any | Iterable[Any]) -> Iterator[Hex]:
        """Yield all hexes that point to the desired value(s).

        Args:
            desired_values (Any | Iterable[Any]): The value(s) to sort hexes by

        Returns:
            Iterable[Hex]: _description_

        Yields:
            Iterator[Hex]: _description_
        """

        for hex, value in self.items():
            if (
                isinstance(desired_values, Iterable)
                and value in desired_values
                or value == desired_values
            ):
                yield hex

    def __iter__(self) -> Generator[Hex, None, None]:
        yield from super().__iter__()

    def __setitem__(self, __key: Hex | HexMap, __value: Any) -> None:
        """Set ``self[key]`` to ``value``.

        Args:
            __key (Hex | HexMap): If a ``Hex`` is provided only that will be set and if a ``HexMap`` is provided all Hexes in this HexMap will be changed to the provided
            __value (Any): The value to set to

        Raises:
            TypeError: If ``__key`` is not of type ``Hex`` or ``HexMap``
        """

        if isinstance(__key, Hex):
            # When running pickle.load self.hexorigin hasn't been defined yet, therefore the inline if expression
            super().__setitem__(
                __key + self.hexorigin if hasattr(self, "hexorigin") else Hexigo,
                __value,
            )

        elif isinstance(__key, HexMap):
            for hex in __key:
                super().__setitem__(hex, __value)

        else:
            # TODO
            raise TypeError(
                f"Argument __key was provided {__key} of type {type(__key)} which is neither a Hex nor a HexMap"
            )

    def __getitem__(self, __key: Hex | HexMap) -> Any | tuple[Any, ...]:
        """Get value(s) at self[key]

        Args:
            __key (Hex | HexMap): If a ``Hex`` is provided only that Hex assigned value will be returned and if a ``HexMap`` is provided all values from this HexMap that overlap with other will be returned

        Raises:
            TypeError: If ``__key`` is not of type ``Hex`` or ``HexMap``

        Returns:
            Any | tuple[Any, ...]: Either the single value or all the values from the intersecting HexMaps
        """

        if isinstance(__key, Hex):
            return super().__getitem__(__key)

        elif isinstance(__key, HexMap):
            # Return all values in the intersection of self and __key

            return tuple(super().__getitem__(hex) for hex in self & __key)

        else:
            raise TypeError(
                f"Argument __key was provided {__key} of type {type(__key)} which is neither a Hex nor a HexMap"
            )

    def insert(self, hex_or_hexmap: Hex | HexMap, value: Any = None) -> None:
        """Insert a Hex or whole HexMap in this HexMap with an optional value otherwise set to default value

        Args:
            hex_or_hexmap (Hex | HexMap): Set a specific Hex in this HexMap or all Hexes from another HexMap

            value (Any, optional): The value to assign to new Hexes. Defaults to self.default.

        Raises:
            TypeError: If ``hex_or_hexmap`` is not of type ``Hex`` or ``HexMap``
        """
        if isinstance(hex_or_hexmap, (Hex, HexMap)):
            self[hex_or_hexmap] = self.default if value is None else value

        else:
            raise TypeError(
                f"Argument hex_or_hexmap was provided {hex_or_hexmap} of type {type(hex_or_hexmap)} which is neither a Hex nor a HexMap"
            )

    def set_all(self, value: Any = None) -> None:
        """Set all Hexes (keys) to a certain value

        Args:
            value (Any, optional): The value to change Hexes to. Defaults to self.default.
        """

        if value is None:
            value = self.default

        for hex in self.hexes():
            self[hex] = value

    # addition and union

    def __or__(self, other: HexMap) -> HexMap:
        """Get the union of this HexMap and other where values from other will be on the top

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: A union of this HexMap and other where
        """

        if isinstance(other, HexMap):
            return self._new({**other, **self})

        else:
            raise TypeError(
                f"Argument other was provided {other} of type {type(other)} which is not a HexMap"
            )

    def __add__(self, other: Hex | HexMap) -> HexMap:
        """Move all Hexes in this HexMap by another Hex or get the union of this HexMap and other

        Args:
            other (Hex | HexMap): If a Hex is provided all Hexes in this HexMap will be offset by other, but
                if a HexMap is provided all Hexes in other will be added to this HexMap.

        Raises:
            TypeError: If ``other`` is not of type ``Hex`` or ``HexMap``

        Returns:
            HexMap: This HexMap shifted or a union of this HexMap and other
        """

        if isinstance(other, Hex):
            return self._new({hex + other: value for hex, value in self.items()})

        elif isinstance(other, HexMap):
            return self | other

        else:
            raise TypeError(
                f"Argument other was provided {other} of type {type(other)} which is neither a Hex nor a HexMap"
            )

    def union(
        self,
        other: HexMap,
        func: Optional[Callable[[Any, Any], Any]] = None,
    ) -> HexMap:
        """Get union of this HexMap and other,

        The order matters since values from ``other`` will be used for the intersection

        Note:
            This can also be done using the operators ``|`` or ``+`` between two ``HexMap`` objects.

        Args:
            other (HexMap): The other ``HexMap``.
            func (Callable[[Any, Any], Any], optional): A function that will be applied to all values of intersecting Hexes.
                If omitted the values of this HexMap will be preserved. Defaults to None.
        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: The union as a new HexMap

        Examples:

            Creating two hexagonal hexmaps

            >>> hxmp1 = hexmap.hexagon(radius=1, value=1)
            >>> hxmp2 = hexmap.hexagon(radius=1, value=2, hexorigin=Hex(1, 0))

            Using function to add values of intersecting Hexes

            Either lambda:

            >>> inter_func = lambda v1, v2: v1 + v2

            Or function definition:

            >>> def inter_func(v1, v2): return v1 + v2

            Sending in the function to use while creating union

            >>> hxmp3 = hxmp1.union(hxmp2, inter_func)
            >>> hxmp3.plot({1: "b", 2: "r", 3: "m"})
        """
        if func is None:
            return self | other

        # Checking that func is Callable and that it has two arguments, which are values from the first and second HexMap
        elif isinstance(func, Callable) and len(inspect.getfullargspec(func).args) == 2:
            # self explanatory hehe
            def unite(k):
                if k in self and k in other:
                    return func(self[k], other[k])

                return self[k] if k in self else other[k]

            return self._new({k: unite(k) for k in self.keys() | other.keys()})

            # self_copy = self.copy()
            # self_copy.update({k: func(self[k], other[k]) for k in other if self.get(k)})

            # return self._new({**other, **self_copy})

        else:
            # TODO
            raise TypeError("")

    # intersection

    def __and__(self, other: HexMap) -> HexMap:
        """Intersect two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: Intersecting Hexes as a HexMap
        """

        if isinstance(other, HexMap):
            return self._new({k: self[k] for k in self.keys() & other.keys()})

        else:
            raise TypeError(
                f"Argument other was provided {other} of type {type(other)} which is not a HexMap"
            )

    def intersection(
        self,
        other: HexMap,
        func: Optional[Callable[[Any, Any], Any]] = None,
    ) -> HexMap:
        """Get intersection of this HexMap and other.

        Note:
            This can also be done using the operators ``&`` between two ``HexMap`` objects.

        Args:
            other (HexMap): The other ``HexMap``.
            func (Callable[[Any, Any], Any], optional): A function that will be applied to all values of intersecting Hexes.
                If omitted the values of this HexMap will be preserved. Defaults to None.

        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: The intersection as a new HexMap

        Examples:

            Creating two hexagonal hexmaps

            >>> hxmp1 = hexmap.hexagon(radius=1, value=1)
            >>> hxmp2 = hexmap.hexagon(radius=1, value=2, hexorigin=Hex(1, 0))

            Using function to add values of intersecting Hexes

            Either lambda:

            >>> inter_func = lambda v1, v2: v1 + v2

            Or function definition:

            >>> def inter_func(v1, v2): return v1 + v2

            Sending in the function to use while intersecting

            >>> hxmp3 = hxmp1.intersection(hxmp2, inter_func)
            >>> hxmp3.plot({1: "b", 2: "r", 3: "m"})
        """
        if func is None:
            return self & other

        # Checking that func is Callable and that it has two arguments, which are values from the first and second HexMap
        elif isinstance(func, Callable) and len(inspect.getfullargspec(func).args) == 2:
            return self._new(
                {k: func(self[k], other[k]) for k in self.keys() & other.keys()}
            )

        else:
            # TODO
            raise TypeError("")

    # difference

    def __sub__(self, other: Hex | HexMap) -> HexMap:
        """Move all Hexes in this HexMap by another Hex or get the difference of this HexMap and other

        Args:
            other (Hex | HexMap): If a Hex is provided all Hexes in this HexMap will be offset by other, but
                if a HexMap is provided all Hexes that overlap with this HexMap other will be removed.

        Raises:
            TypeError: If ``other`` is not of type ``Hex`` or ``HexMap``

        Returns:
            HexMap: This HexMap shifted or a difference of this HexMap and other
        """

        if isinstance(other, Hex):
            return self._new({hex - other: value for hex, value in self.items()})

        elif isinstance(other, HexMap):
            return self._new({k: self[k] for k in self.keys() - other.keys()})

        else:
            raise TypeError(
                f"Argument other was provided {other} of type {type(other)} which is neither a Hex nor a HexMap"
            )

    def difference(self, other: HexMap) -> HexMap:
        """Get difference between this HexMap and other, order matters.

        Note:
            This can also be done using the operator ``-`` between two ``HexMap`` objects.

        Args:
            other (HexMap): The other ``HexMap``.

        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: The difference as a new HexMap

        """
        return self - other

    # symmetric difference

    def __xor__(self, other: HexMap) -> HexMap:
        """Get symmetric difference of two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: Intersecting Hexes as a HexMap
        """

        if isinstance(other, HexMap):
            return self._new(
                {
                    k: self[k] if k in self else other[k]
                    for k in self.keys() ^ other.keys()
                }
            )

        else:
            raise TypeError(
                f"Argument other was provided {other} of type {type(other)} which is not a HexMap"
            )

    def symmetric_difference(self, other: HexMap) -> HexMap:
        """Get symmetric difference between this HexMap and other.

        Note:
            This can also be done using the operators ``^`` or ``/`` between two ``HexMap`` objects.

        Args:
            other (HexMap): The other ``HexMap``.

        Raises:
            TypeError: If ``other`` is not of type ``HexMap``

        Returns:
            HexMap: The symmetric difference as a new HexMap
        """
        return self ^ other

    # save and plot

    def save(self, filepath: Path | str) -> None:
        """Save a Hexmap at filepath using pickle

        Args:
            filepath (Path | str): Path to where the HexMap ``.pkl`` file should be saved
        """
        with builtins.open(filepath, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def plot(
        self,
        colormap: Optional[dict[Any, Any]] = None,
        draw_axes: bool = False,
        draw_text: bool = False,
        size_factor: float = 1,
        hex_alpha: float = 0.8,
        facecolor: Optional[Any] = None,
        title: str = "Unnamed Hexmap",
        show_directly: bool = True,
    ) -> tuple[Figure, Axes]:
        """Plot the HexMap using matplotlib

        Args:
            colormap (dict[Any, Any], optional): Optional dict to map colors to different values in the HexMap. Defaults to None.
            draw_axes (bool, optional) Wheter to draw the Q, R and S axes. Defaults to True.
            factor (float, optional): Shrink size of Hex by factor. Defaults to 1.
            alpha (float, optional): Alpha value of colors. Defaults to 0.5.
            title (str): Set the title of the HexMap. Defaults to "Unnamed Hexmap".
        """

        # TODO add argument textmap in order to map text onto hexes of certain value
        # Problem atm is scaling of the text, want it relative to the size of hexes so that it fits properly
        # textmap: Optional[dict[Any, str]] = None,
        # textmap (dict[Any, str], optional):   Optional dict to map text to different values in the HexMap. Defaults to None.

        try:
            import matplotlib.pyplot as plt
            import numpy as np
            from matplotlib.collections import PatchCollection
            from matplotlib.patches import Polygon, RegularPolygon

        except ImportError as e:
            warnings.warn(str(e), RuntimeWarning)
            raise

        WHITE = (0.96, 0.96, 0.94)
        GRAY = (0.74, 0.74, 0.74)
        Q = (0.35, 0.7, 0.0, 0.6)
        R = (0.11, 0.64, 0.91, 0.6)
        S = (0.9, 0.1, 0.9, 0.6)

        fig, ax = plt.subplots(num="HexMap Plotter")
        fig.tight_layout()
        ax.invert_yaxis()
        ax.set_aspect("equal")
        ax.set_title(title)

        if facecolor is not None:
            ax.set_facecolor(facecolor)

        # for a nice and bright random coloring haha: np.random.random((1, 3)) * 0.6 + 0.4

        if colormap is None:
            # This draws the hexagons slightly faster since they all get the same appearence
            hex_list = [
                Polygon(tuple(hex.polygon_points(size_factor)))  # type: ignore
                for hex in self.hexes()
            ]
            hexagons = PatchCollection(hex_list, facecolor=WHITE, edgecolor=GRAY)

        else:
            # This draws the hexagons slightly slower but gives individiual colors to the ones with values specified in the colormap
            hex_list = [
                Polygon(
                    tuple(hex.polygon_points(size_factor)),  # type: ignore
                    facecolor=colormap[value] if value in colormap else WHITE,
                    edgecolor=GRAY,
                )
                for hex, value in self.items()
            ]
            hexagons = PatchCollection(hex_list, match_original=True)

        ax.add_collection(hexagons)  # type: ignore

        origin = self.hexorigin.to_point()
        diagonal = self.hexorigin + Hex(2, -1)

        if draw_axes:
            # Draw q, r and s axes

            for col, lbl in zip((Q, R, S), ("Q-axis", "R-axis", "S-axis")):
                ax.axline(origin, diagonal.to_point(), color=col, label=lbl)
                # , zorder=0) Used to set axline behind patches

                # Rotate the diagonal inplace to the right around hex origin two steps
                diagonal >>= (self.hexorigin, 2)

        else:
            # If this is left out, then no patches will be shown!
            ax.plot(origin.x, origin.y)

        # This is used to display q, r and s values in the top right of the window
        def coord_display(x, y):
            x, y = round(x, 1), round(y, 1)
            hexagon = Hex.from_point((x, y)).rounded(1)

            q, r, s = (round(c, 1) for c in hexagon.cube_coords)

            return f"pixel: {x=}, {y=}\nhex: {q=}, {r=}, {s=}"

        # link the coord_display function to the axis object
        ax.format_coord = coord_display

        # TODO make text size relative to ax window size

        if draw_text:
            # phis = np.arange((1 / 2), -(5 / 6), -(2 / 3))
            phis = np.array(((1 / 2), -(1 / 6), -(5 / 6)))

            phis += (1 / 3) * Hex.layout.orientation.start_angle
            phis *= np.pi

            # start_angle = (1 / 3) * np.pi * Hex.layout.orientation.start_angle
            # start_angle -= (1 / 6) * np.pi

            hx_size = Hex.layout.size

            for hx in self:
                coords = "qrs" if hx == Hexigo else (hx.q, hx.r, hx.s)
                center = hx.to_point()

                for phi, coord, color in zip(phis, coords, (Q, R, S)):
                    label_x = center.x + 0.4 * hx_size.x * np.cos(phi)
                    label_y = center.y + 0.4 * hx_size.y * -np.sin(phi)

                    plt.text(
                        label_x,
                        label_y,
                        f"{coord:^3}",
                        va="center",
                        ha="center",
                        color=color,
                        weight="bold",
                        size=hx_size.x,
                    )

        if show_directly:
            plt.show()

        return fig, ax


def show():
    # TODO TELL USER HOW TO USE THIS

    try:
        import matplotlib.pyplot as plt

    except ImportError as e:
        warnings.warn(str(e), RuntimeWarning)
        raise

    plt.show()


# NOTE ALL OF THE BELOW IS STILL WORK IN PROGRESS!


def hexagon(
    radius: int,
    value: Any = None,
    hexorigin: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Hexagon ⬢

    Args:
        radius (int): The number of hexes from the hexorigin
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        hexorigin (Hex, optional): The hexorigin of the shape, all Hexes will be centered around hexorigin. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The hexagon shaped HexMap
    """

    # TODO ADD TYPE CHECKS

    hxmp = HexMap(default_value=value, origin_offset=hexorigin)

    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)

        if not hollow or q == -radius or q == radius:
            for r in range(r1, r2 + 1):
                hxmp.insert(Hex(q, r))

        else:
            hxmp.insert(Hex(q, r1))
            hxmp.insert(Hex(q, r2))

    return hxmp


def _axrange(r: int | tuple[int, int]):
    """Internal TODO

    Args:
        r (int | tuple[int, int]): _description_

    Returns:
        _type_: _description_
    """
    return range(-r, r + 1) if isinstance(r, int) else range(r[0], r[1] + 1)


def parallelogram(
    axes: dict[str, int | tuple[int, int]] = {"q": 2, "r": 1},
    value: Any = None,
    hexorigin: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:  # sourcery skip: default-mutable-arg
    """Create a HexMap in the shape of a Parallelogram ▰

    Args:
        axes (_type_, optional): _description_. Defaults to {"q": 2, "r": 2}.
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        hexorigin (Hex, optional): _description_. Defaults to Hexigo.
        hollow (bool, optional): _description_. Defaults to False.

    Returns:
        HexMap: The parallelogram HexMap
    """

    # TODO type and value checking!

    # elif not isinstance(axes, dict):
    #     raise TypeError("")

    # elif len(axes) != 2:
    #     raise ValueError("")

    # for ax in axes:
    #     if not isinstance(axes[ax], tuple):
    #         raise TypeError("")

    #     elif len(axes[ax]) != 2:
    #         raise ValueError("")

    # Creating a Hex at Hexigo which will effectively be "moved" around the shape
    hx = Hex(0, 0)
    hxmp = HexMap(default_value=value, origin_offset=hexorigin)

    ax1, ax2 = axes
    range1 = _axrange(axes[ax1])
    range2 = _axrange(axes[ax2])

    for c1 in range1:
        if not hollow or c1 == min(range1) or c1 == max(range1):
            for c2 in range2:
                hx[ax1, ax2] = (c1, c2)
                hxmp.insert(hx)

        else:
            hx[ax1, ax2] = (c1, min(range2))
            hxmp.insert(hx)

            hx[ax1, ax2] = (c1, max(range2))
            hxmp.insert(hx)

    return hxmp


def rhombus(
    size: int | tuple[int, int] = 1,
    axes: str | tuple[str, str] = "qs",
    **kwargs,
) -> HexMap:
    """Create a HexMap in the shape of a rhombus (aka diamond) ⬧

    Args:
        size (int, optional): _description_. Defaults to 1.
        axes (str | tuple[str, str], optional): _description_. Defaults to ("q", "s").
        value (Any, optional): The value that should initially be assigned to all Hexagons. Defaults to None.
        hexorigin (Hex, optional): _description_. Defaults to Hexigo.
        hollow (bool, optional): _description_. Defaults to False.

    Returns:
        HexMap: The rhombus HexMap
    """

    return parallelogram({axes[0]: size, axes[1]: size}, **kwargs)


def rectangle(
    axes: dict[str, int | tuple[int, int]] = {"q": (-3, 3), "r": (-2, 2)},
    value: Any = None,
    hexorigin: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:  # sourcery skip: default-mutable-arg
    """Create a HexMap in the shape of a Rectangle ▬
    :param radius: The number of hexes from the center
    :param value: The value that should be assigned to all Hexagons
    :return: The rectangle HexMap"""

    # for (int r = top; r <= bottom; r++) { // pointy top
    #     int r_offset = floor(r/2.0); // or r>>1
    #     for (int q = left - r_offset; q <= right - r_offset; q++) {
    #         map.insert(Hex(q, r, -q-r));
    #     }
    # }

    ax2, ax1 = axes
    # FIXME

    v2, v1 = axes.values()

    left, right = (-v2, v2) if isinstance(v2, int) else v2
    top, bottom = (-v1, v1) if isinstance(v1, int) else v1

    hx = Hex(0, 0)
    hxmp = HexMap(default_value=value, origin_offset=hexorigin)

    range1 = range(top, bottom + 1)

    for c1 in range1:
        range2 = range(left - floor(c1 / 2), right - floor(c1 / 2) + 1)

        if not hollow or c1 == min(range1) or c1 == max(range1):
            for c2 in range2:
                hx[ax1, ax2] = (c1, c2)
                hxmp.insert(hx)

        else:
            hx[ax1, ax2] = (c1, min(range2))
            hxmp.insert(hx)

            hx[ax1, ax2] = (c1, max(range2))
            hxmp.insert(hx)

    return hxmp


def square(
    size: int | tuple[int, int] = 1,
    axes: str | tuple[str, str] = "qr",
    value: Any = None,
    hexorigin: Hex = Hexigo,
    hollow: bool = False,
) -> (
    HexMap
):  # TODO When available remove: value, hexorigin, hollow in favor for type-annotated kwargs
    """Create a HexMap in the shape of a Square ■
    :param radius: The number of hexes from the center
    :param value: The value that should be assigned to all Hexagons
    :return: The square HexMap"""

    return rectangle({axes[0]: size, axes[1]: size}, value, hexorigin, hollow)


def triangle(
    size: int | tuple = 1,
    axes: str | tuple[str, str] = "qr",
    value: Any = None,
    hexorigin: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Triangle ▲
    :param radius: The number of hexes from the center
    :param value: The value that should be assigned to all Hexagons
    :return: The triangle HexMap"""

    # for (int q = 0; q <= map_size; q++) {
    #     for (int r = 0; r <= map_size - q; r++) {
    #         map.insert(Hex(q, r, -q-r));
    #     }
    # }

    hx = Hex(0, 0)
    hxmp = HexMap(default_value=value, origin_offset=hexorigin)

    ax1, ax2 = axes

    if isinstance(size, int):
        r1 = range(-size * 2, size + 1)
        r2 = lambda c: range(-size - c, size + 1)
    else:
        r1 = range(size[0], size[1] + 1)
        r2 = lambda c: range(size[0], size[1] - c + 1)

    for c1 in r1:
        # if not hollow or c1 == min(r) or c1 == max(r):

        for c2 in r2(c1):
            hx[ax1, ax2] = (c1, c2)
            hxmp.insert(-hx)

        # else:
        #     hx[ax1, ax2] = (c1, min(range2))
        #     hxmp.insert(hx)

        #     hx[ax1, ax2] = (c1, max(range2))
        #     hxmp.insert(hx)

    return hxmp


# def star(value: Any = None, axes: str = "qs") -> HexMap:
#     """Create a HexMap in the shape of a Star ★ ✡
#     :param radius: The number of hexes from the center
#     :param value: The value that should be assigned to all Hexagons
#     :return: The star HexMap"""


def polygon(
    hexes: list[Hex] | tuple[Hex, ...],
    value: Any = None,
    hexorigin: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """_summary_

    Args:
        hexes (Iterable[Hex]): The hexes that the polygon will use as corners.

    Returns:
        HexMap: _description_
    """

    def current_and_next(hxs) -> zip[tuple[Hex, Hex]]:
        return zip(hxs, hxs[1:] + hxs[:1])  # type: ignore

    hxmp = HexMap(default_value=value, origin_offset=hexorigin)

    for curr_hx, next_hx in current_and_next(hexes):
        for hx in curr_hx.linedraw_to(next_hx):
            hxmp.insert(hx)

    # for hx in hexes:
    #     last_hex = hx

    #     if first:
    #         first = False
    #         continue

    return hxmp
