# Author: Elis Grahn

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

    >>> HexMap.hexagon(radius=1, value=0, origin_offset=Hexigo, hollow=True)
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

import builtins  # type: ignore
import inspect
import pickle
import warnings
from collections.abc import Iterable
from math import floor
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Iterator,
    Literal,
    Optional,
    TypeAlias,
    overload,
)

from numpy import empty

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from pathlib import Path

from _collections_abc import dict_items, dict_keys, dict_values

from .hexclass import Hex, Hexigo
from .navigate import HexClock, HexCompass

hexcoord: TypeAlias = Literal["q", "r", "s"]

# import dill # TODO maybe replace pickle with dill


def new(value: Any = None, origin_offset: Hex = Hexigo) -> HexMap:
    """Creates a new empty HexMap

    Args:
        value (Any, optional): Value that will be assigned to new Hexes added to HexMap. Defaults to None.
        origin_offset (Hex, optional): Origin of the HexMap, all new Hexes will be offset by origin_offset. Defaults to Hexigo.

    Returns:
        HexMap: An empty HexMap representing a Hexagonal grid
    """
    return HexMap(default_value=value, origin_offset=origin_offset)


def fromdict(
    hexdict: dict[Hex, Any], value: Any = None, origin_offset: Hex = Hexigo
) -> HexMap:
    """Create a HexMap from the given dict with Hex as keys

    Args:
        hexdict (dict[Hex, Any]): A dict with `Hex` as keys
        value (Any, optional): Value that will be assigned to new Hexes added to HexMap. Defaults to None.
        origin_offset (Hex, optional): Origin of the HexMap, all new Hexes will be offset by origin_offset. Defaults to Hexigo.

    Returns:
        HexMap: _description_
    """
    return HexMap(hexdict, default_value=value, origin_offset=origin_offset)


def fromkeys(
    hexiter: Hex | Iterable[Hex], value: Any = None, origin_offset: Hex = Hexigo
) -> HexMap:
    """Create a new HexMap from a single Hex or the given iterable of Hex

    Args:
        hexiter (Hex | Iterable[Hex]): An iterable of `Hex`
        value (Any, optional): Value that will be assigned to new Hexes added to HexMap. Defaults to None.
        origin_offset (Hex, optional): Origin of the HexMap, all new Hexes will be offset by origin_offset. Defaults to Hexigo.
    Raises:
        TypeError: _description_

    Returns:
        HexMap: _description_
    """
    if isinstance(hexiter, Hex):
        hexdict = dict.fromkeys((hexiter,), value)

    elif isinstance(hexiter, Iterable):
        hexdict = dict.fromkeys(hexiter, value)

    else:
        raise TypeError(
            f"hexiter must be of type 'Hex' or 'Iterable[Hex]', not {type(hexiter)}"
        )

    return HexMap(hexdict, default_value=value, origin_offset=origin_offset)


def open(filepath: str) -> HexMap:
    """Open a saved HexMap at filepath

    Args:
        filepath (str): Path to the HexMap `.pkl` file

    Returns:
        HexMap: HexMap saved at `filepath`
    """

    with builtins.open(filepath, "rb") as f:
        return pickle.load(f)


class HexMap(dict):
    """A dict, with `hexpy.Hex` as keys, which representing a generic Hexagonal grid

    To create :py:class:`hexpy.HexMap.HexMap` objects, use an appropriate factory
    function. There's hardly ever any reason to call the HexMap constructor directly.

    Examples:
    >>> TODO
    """

    def __init__(
        self,
        hexdict: Optional[dict[Hex, Any]] = None,
        default_value: Any = None,
        origin_offset: Hex = Hexigo,
    ) -> None:
        """Create a hexagonal grid map of hexes.

        Args:
            hexdict (dict[Hex, Any], optional): If provided it will become the inital HexMap. Defaults to None.
            default_value (Any, optional): Default value that will be assigned to new Hexes added to HexMap. Defaults to None.
            origin_offset (Hex, optional): Origin of the HexMap, all new Hexes will be offset by origin_offset. Defaults to Hexigo.
        """

        self.default_value = default_value
        self.origin_offset = origin_offset

        if hexdict is None:
            super().__init__()

        elif not isinstance(hexdict, dict):
            raise TypeError(
                "HexMaps can only be created initiated from dicts, if you need to create a HexMap from another Hex iterable use 'hexmap.fromkeys()'"
            )

        elif not all(isinstance(hx, Hex) for hx in hexdict):
            raise TypeError("All keys in a HexMap must be of type Hex")

        else:
            super().__init__(hexdict)

    @property
    def empty(self) -> bool:
        """Check if HexMap is empty.

        Note:
            This is the same as taking `len(HexMap) == 0` or `bool(self)`

        Returns:
            bool: True if HexMap is empty, False otherwise
        """
        return bool(self)

    # creation

    def _new(self, hexdict: dict[Hex, Any]) -> HexMap:
        """Internally create a new HexMap, passing on the default value and origin_offset offset

        Args:
            hexdict (dict[Hex, Any]): Dict with Hex as keys to use for the new HexMap

        Returns:
            HexMap: The new HexMap
        """
        return HexMap(hexdict, self.default_value, self.origin_offset)

    def copy(self) -> HexMap:
        """Create a new identical HexMap

        Returns:
            HexMap: A copy of this HexMap
        """
        return HexMap(dict(self), self.default_value, self.origin_offset)

    # representations

    def __str__(self) -> str:
        """Return a nicely formatted HexMap representation string"""

        # Following comments technically work, but don't add '' to strings so 'eval(repr(obj))' will not work in that case
        # return "{" + ",\n".join(f"{hx}: '{v}'" for hx, v in self.items()) + "}"
        # return ("{"+ ",\n".join(str(item)[1:-1].replace("), ", "): ") for item in self.items())+ "}")

        # This is the most hacky yet elegant solution :)
        return super().__repr__().replace(", Hex", ",\n Hex")

    def __repr__(self) -> str:
        """Return the canonical string representation of HexMap."""
        return f"hexpy.hexmap.HexMap({str(self)})"

    # keys and values

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
        return super().keys()

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
        return super().items()

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

        for hx, value in self.items():
            if (
                isinstance(desired_values, Iterable)
                and value in desired_values
                or value == desired_values
            ):
                yield hx

    def __iter__(self) -> Generator[Hex, None, None]:
        yield from super().__iter__()

    # get and set

    @overload
    def __getitem__(self, __key: Hex) -> Any:
        ...

    @overload
    def __getitem__(self, __key: Iterable[Hex]) -> tuple[Any, ...]:
        ...

    @overload
    def __getitem__(self, __key: Generator[bool, None, None]) -> HexMap:
        ...

    def __getitem__(self, __key: Hex | Iterable[Hex] | Generator[bool, None, None]):
        """Get value(s) at self[key]

        Args:
            __key (Hex | Iterable[Hex]): If a Hex is provided only it's value will be returned and
        if an Iterable of Hex is provided all values from the Hex in the Iterable will be returned as a tuple

        Raises:
            TypeError: If `__key` is not of type `Hex` or `HexMap`

        Returns:
            Any | tuple[Any, ...]: Either the single value or all the values from the intersecting HexMaps
        """

        if isinstance(__key, Hex):
            return super().__getitem__(__key)

        elif isinstance(__key, Generator):
            return self._new({hx: v for b, (hx, v) in zip(__key, self.items()) if b})

        elif isinstance(__key, Iterable):
            # This is to handle HexClock or HexCompass in hexpy.navigate
            # NOTE that both if you iterate on a HexClock or HexCompass you will iterate through the Hexagons and not the keys
            return tuple(super().__getitem__(hx) for hx in __key if isinstance(hx, Hex))

        else:
            raise TypeError(
                f"Argument __key was provided {__key} of type {type(__key)} which is neither a Hex nor a HexMap"
            )

    def __setitem__(
        self, __key: Hex | Iterable[Hex] | Generator[bool, None, None], __value: Any
    ) -> None:
        """Set `self[key]` to `value`.

        Args:
            __key (Hex | HexMap): If a `Hex` is provided only that will be set and if a `HexMap` is provided all Hexes in this HexMap will be changed to the provided
            __value (Any): The value to set to

        Raises:
            TypeError: If `__key` is not of type `Hex`, `Iterable` or `Generator`
            TypeError: If `__key` is of type `Iterable` but contains items that are not of type `Hex`
        """

        if isinstance(__key, Hex):
            # When running pickle.load self.origin_offset hasn't been defined yet, therefore the inline if expression
            offset = self.origin_offset if hasattr(self, "origin_offset") else Hexigo

            super().__setitem__(__key + offset, __value)

        elif isinstance(__key, Generator):
            for b, hx in zip(__key, self.keys()):
                if b:
                    self[hx] = __value

        elif isinstance(__key, Iterable):
            for hx in __key:
                # Check that the items in iterable are of type Hex
                if not isinstance(hx, Hex):
                    raise TypeError(
                        f"Items of iterable provided to HexMap.__setitem__ should be of type Hex, not {type(hx)}"
                    )

                self[hx] = __value

        else:
            raise TypeError(
                f"Argument __key was provided {__key} of type {type(__key)} which is neither a Hex, a tuple of Hex, a HexMap or a boolean mask."
            )

    # update

    def pop(self, hexiter: Hex | Iterable[Hex], default: Any = None) -> Any:
        """Pop a Hex from the HexMap and return its value

        Args:
            hexiter (Hex | Iterable[Hex]): The Hex or Iterable of Hex to pop
            default (Any): The value to return if the Hex is not in the HexMap

        Returns:
            Any: The value of the popped Hex
        """
        if isinstance(hexiter, Hex):
            return super().pop(hexiter, None)

        elif isinstance(hexiter, Iterable):
            return tuple(self.pop(hx) for hx in hexiter)

        else:
            raise TypeError(
                f"hexiter must be of type 'Hex' or 'Iterable[Hex]', not {type(hexiter)}"
            )

    def insert(self, hexiter: Hex | Iterable[Hex], value: Optional[Any] = None) -> None:
        """Insert a Hex or whole HexMap in this HexMap with an optional value otherwise set to default value

        Args:
            hexiter (Hex | Iterable[Hex]): Insert a specific Hex or an iterable of Hex
            value (Any, optional): The value to assign to new Hexes. Defaults to self.default_value.

        Raises:
            TypeError: If `hex_or_hexmap` is not of type `Hex` or `HexMap`
        """
        if isinstance(hexiter, (Hex, Iterable)):
            self[hexiter] = value or self.default_value

        else:
            raise TypeError(
                f"Argument hexiter was provided {hexiter} of type {type(hexiter)} which is neither a Hex nor an iterable of Hex"
            )

    # changing

    def update_all(self, value: Any = None) -> None:
        """Update all Hexes (keys) to a certain value

        Args:
            value (Any, optional): The value to change Hexes to. Defaults to self.default_value.
        """
        self.update(self.fromkeys(self.keys(), value or self.default_value))

    def apply(self, func: Callable[[Any], Any], *args, **kwargs) -> HexMap:
        """Apply a function to all values in this HexMap

        Args:
            func (Callable[[Any], Any]): Function to apply, takes and returns one value.
            *args: Arguments to pass along to func
            **kwargs: Keyword arguments to pass along to func

        Returns:
            HexMap: A new HexMap where values have been passed through the function

        Example:
            Multiply all values in the HexMap by three

            >>> hxmp = hexmap.fromdict({Hex(1, 2): 1, Hex(3, 4): 3})
            >>> hxmp.apply(func=lambda v: 3 * v)
            {Hex(q=1, r=2, s=-3): 3,
             Hex(q=3, r=4, s=-7): 9}
        """
        return self._new(
            {hx: func(value, *args, **kwargs) for hx, value in self.items()}
        )

    def apply_inplace(self, func: Callable[[Any], Any], *args, **kwargs) -> None:
        """Inplace apply a function to all values in this HexMap

        Args:
            func (Callable[[Any], Any]): Function to apply, takes and returns one value.
            *args: Arguments to pass along to func
            **kwargs: Keyword arguments to pass along to func

        Example:
            Inplace multiply all values in the HexMap by three

            >>> hxmp = hexmap.fromdict({Hex(1, 2): 1, Hex(3, 4): 3})
            >>> hxmp.apply_inplace(func=lambda v: 3 * v)
            >>> hxmp
            {Hex(q=1, r=2, s=-3): 3,
             Hex(q=3, r=4, s=-7): 9}
        """

        self.update({hx: func(value, *args, **kwargs) for hx, value in self.items()})

    def transform(self, func: Callable[[Hex], Hex], *args, **kwargs) -> HexMap:
        """Transform the HexMap by applying a function to all hexes.

        Args:
            func (Callable[[Hex], Hex]): Function to apply, takes and returns one Hex.
            *args: Arguments to pass along to func
            **kwargs: Keyword arguments to pass along to func

        Returns:
            HexMap: A new HexMap where hexes have been passed through the function

        Example:
            Multiply all hexes in the HexMap by 3

            >>> hxmp = hexmap.fromdict({Hex(1, 2): 1, Hex(3, 4): 3})
            >>> hxmp.transform(func=lambda hx: 3 * hx)
            {Hex(q=3, r=6, s=-9): 1,
             Hex(q=9, r=12, s=-21): 3}
        """
        return self._new(
            {func(hx, *args, **kwargs): value for hx, value in self.items()}
        )

    def clear(self) -> None:
        """Clear the HexMap"""
        super().clear()

    def cleared(self) -> HexMap:
        """Get a cleared copy of the HexMap"""
        return self._new({})

    # comparison

    def __bool__(self) -> bool:
        """True if the HexMap is not empty

        Returns:
            bool: True if the HexMap is not empty
        """
        return bool(self.values())

    def __eq__(self, other: HexMap | object) -> Generator[bool, None, None]:
        """Boolean mask

        Args:
            other (HexMap | object): _description_

        Returns:
            Generator[bool, None, None]: _description_
        """

        return (v == other for v in self.values())

    def __lt__(self, other: HexMap | object) -> Generator[bool, None, None]:
        """Boolean mask

        Args:
            other (HexMap | object): _description_

        Returns:
            Generator[bool, None, None]: _description_
        """
        return (v < other for v in self.values())

    def __le__(self, other: HexMap | object) -> Generator[bool, None, None]:
        """Boolean mask

        Args:
            other (HexMap | object): _description_

        Returns:
            Generator[bool, None, None]: _description_
        """
        return (v <= other for v in self.values())

    def __gt__(self, other: HexMap | object) -> Generator[bool, None, None]:
        """Boolean mask

        Args:
            other (HexMap | object): _description_

        Returns:
            Generator[bool, None, None]: _description_
        """
        return (v > other for v in self.values())

    def __ge__(self, other: HexMap | object) -> Generator[bool, None, None]:
        """Boolean mask

        Args:
            other (HexMap | object): _description_

        Returns:
            Generator[bool, None, None]: _description_
        """
        return (v >= other for v in self.values())

    # addition and union

    def __or__(self, other: HexMap) -> HexMap:
        """Get the union of this HexMap and other where values from other will be on the top

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: A union of this HexMap and other where
        """

        if isinstance(other, HexMap):
            return self._new({**self, **other})

        else:
            raise TypeError(f"other must be of type 'HexMap', not {type(other)}")

    def __add__(self, other: Hex | HexMap) -> HexMap:
        """Move all Hexes in this HexMap by other Hex or get the union of this HexMap and other

        Args:
            other (Hex | HexMap): If a Hex is provided all Hexes in this HexMap will be offset by other, but
                if a HexMap is provided all Hexes in other will be added to this HexMap.

        Raises:
            TypeError: If `other` is not of type `Hex` or `HexMap`

        Returns:
            HexMap: This HexMap shifted or a union of this HexMap and other
        """

        if isinstance(other, Hex):
            return self._new({hx + other: value for hx, value in self.items()})

        elif isinstance(other, HexMap):
            return self | other

        else:
            raise TypeError(
                f"other must be of type 'Hex' or 'HexMap', not {type(other)}"
            )

    __radd__ = __add__

    def union(
        self,
        other: HexMap,  # TODO ALLOW MULTIPLE HEXMAPS TO BE UNIONED SIMULTANIOUSLY
        func: Optional[Callable[[Any, Any], Any]] = None,
    ) -> HexMap:
        """Return the union of this HexMap and other.

        The order matters since values from `other` will be used for the intersection

        Note:
            This can also be done using the operators `|` or `+` between two `HexMap` objects.

        Args:
            other (HexMap): The other `HexMap`.
            func (Callable[[Any, Any], Any], optional): A function that will be applied to all values of intersecting Hexes.
                If omitted the values of this HexMap will be preserved. Defaults to None.
        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: The union as a new HexMap

        Examples:

            Creating two hexagonal hexmaps

            >>> hxmp1 = hexmap.hexagon(radius=1, value=1)
            >>> hxmp2 = hexmap.hexagon(radius=1, value=2, origin_offset=Hex(1, 0))

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

            return self._new({hx: unite(hx) for hx in self.keys() | other.keys()})

            # self_copy = self.copy()
            # self_copy.update({k: func(self[k], other[k]) for k in other if self.get(k)})

            # return self._new({**other, **self_copy})

        else:
            raise TypeError(f"func must be a Callable with two arguments, not {func}")

    def __ior__(self, other: HexMap):  # -> Self:
        """Get the union of this HexMap and other where values from other will be on the top

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: A union of this HexMap and other where
        """

        if not isinstance(other, HexMap):
            raise TypeError(f"other must be of type 'HexMap', not {type(other)}")

        super().update({**self, **other})
        return self

    def __iadd__(self, other: Hex | HexMap):  # -> Self:
        """Move all Hexes in this HexMap by other Hex or get the union of this HexMap and other

        Args:
            other (Hex | HexMap): If a Hex is provided all Hexes in this HexMap will be offset by other, but
                if a HexMap is provided all Hexes in other will be added to this HexMap.

        Raises:
            TypeError: If `other` is not of type `Hex` or `HexMap`

        Returns:
            HexMap: This HexMap shifted or a union of this HexMap and other
        """

        if isinstance(other, Hex):
            for hx in self.keys():
                self[hx] += other

        elif isinstance(other, HexMap):
            self |= other

        else:
            raise TypeError(
                f"other must be of type 'Hex' or 'HexMap', not {type(other)}"
            )

        return self

    def update(
        self,
        other: dict[Hex, Any] | HexMap,
        func: Optional[Callable[[Any, Any], Any]] = None,
    ) -> None:
        """Update the HexMap with the Hex/value pairs from other, overwriting existing Hex.

        Args:
            other (dict[Hex, Any] | HexMap): The other HexMap or dict to update this HexMap with
            func (Optional[Callable[[Any, Any], Any]], optional): What to do with the intersecting hexes. Defaults to None.

        Raises:
            TypeError: If `hexes` is not of type `HexMap` or `dict`
        """
        if func is None:
            super().update(other)

        elif isinstance(func, Callable) and len(inspect.getfullargspec(func).args) == 2:
            for hx in other.keys() | self.keys():
                if hx in other:
                    self[hx] = func(self[hx], other[hx]) if hx in self else other[hx]
        else:
            raise TypeError(f"func must be a Callable with two arguments, not {func}")

    # intersection

    def __and__(self, other: HexMap) -> HexMap:
        """Intersect two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: Intersecting Hexes as a HexMap
        """

        if isinstance(other, HexMap):
            return self._new({k: other[k] for k in self.keys() & other.keys()})

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
            This can also be done using the operators `&` between two `HexMap` objects.

        Args:
            other (HexMap): The other `HexMap`.
            func (Callable[[Any, Any], Any], optional): A function that will be applied to all values of intersecting Hexes.
                If omitted the values of this HexMap will be preserved. Defaults to None.

        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: The intersection as a new HexMap

        Examples:

            Creating two hexagonal hexmaps

            >>> hxmp1 = hexmap.hexagon(radius=1, value=1)
            >>> hxmp2 = hexmap.hexagon(radius=1, value=2, origin_offset=Hex(1, 0))

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
            raise TypeError(f"func must be a Callable with two arguments, not {func}")

    def __iand__(self, other: HexMap):  # -> Self:
        """Intersect two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: Intersecting Hexes as a HexMap
        """

        if not isinstance(other, HexMap):
            raise TypeError(f"other must be of type 'HexMap', not {type(other)}")

        for k in self.keys() - other.keys():
            self.pop(k)

        return self

    def intersection_update(
        self, other: HexMap, func: Optional[Callable[[Any, Any], Any]] = None
    ):  # -> Self:
        """Update the HexMap with the intersection of itself and other, overwriting existing Hex."""

        if func is None:
            self &= other

        elif isinstance(func, Callable) and len(inspect.getfullargspec(func).args) == 2:
            # Remove all Hexes that are other
            self -= other

            self.update(other - self, func)
        else:
            raise TypeError(f"func must be a Callable with two arguments, not {func}")

    # difference

    def __sub__(self, other: Hex | HexMap) -> HexMap:
        """Move all Hexes in this HexMap by other Hex or get the difference of this HexMap and other

        Args:
            other (Hex | HexMap): If a Hex is provided all Hexes in this HexMap will be offset by other, but
                if a HexMap is provided all Hexes that overlap with this HexMap other will be removed.

        Raises:
            TypeError: If `other` is not of type `Hex` or `HexMap`

        Returns:
            HexMap: This HexMap shifted or a difference of this HexMap and other
        """

        if isinstance(other, Hex):
            return self._new({hx - other: value for hx, value in self.items()})

        elif isinstance(other, HexMap):
            return self._new({k: self[k] for k in self.keys() - other.keys()})

        else:
            raise TypeError(
                f"Argument other was provided {other} of type {type(other)} which is neither a Hex nor a HexMap"
            )

    def difference(self, other: HexMap) -> HexMap:
        """Return the difference of two HexMaps as a new HexMap.

        TODO "or more"

        Get difference between this HexMap and other, order matters.

                Note:
                    This can also be done using the operator `-` between two `HexMap` objects.

                Args:
                    other (HexMap): The other `HexMap`.

                Raises:
                    TypeError: If `other` is not of type `HexMap`

                Returns:
                    HexMap: The difference as a new HexMap
        """
        return self - other

    def __isub__(self, other: Hex | HexMap):  # -> Self
        """Remove all elements of another set from this set.

        Args:
            other (HexMap): The other `HexMap`.

        Raises:
            TypeError: If `other` is not of type `Hex` or `HexMap`

        Returns:
            HexMap: This HexMap shifted or a difference of this HexMap and other
        """

        if isinstance(other, Hex):
            # Move all Hexes in this HexMap by other Hex
            new_dict = {k: self[k] - other for k in self.keys()}
            self.update(new_dict)

        elif isinstance(other, HexMap):
            # Remove all Hexes that overlap with other
            for k in self.keys() & other.keys():
                self.pop(k)
        else:
            raise TypeError(
                f"other must be of type 'Hex' or 'HexMap', not {type(other)}"
            )
        return self

    def difference_update(self, other: HexMap):  # -> Self
        """Remove all elements of another set from this set.

        Args:
            other (HexMap): The other `HexMap`.

        Raises:
            TypeError: If `other` is not of type `HexMap`
        """
        if not isinstance(other, HexMap):
            raise TypeError("other must be of type 'HexMap'")

        self -= other

    # symmetric difference

    def __xor__(self, other: HexMap) -> HexMap:
        """Get symmetric difference of two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`

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
            This can also be done using the operators `^` between two `HexMap` objects.

        Args:
            other (HexMap): The other `HexMap`.

        Raises:
            TypeError: If `other` is not of type `HexMap`

        Returns:
            HexMap: The symmetric difference as a new HexMap
        """
        return self ^ other

    def __ixor__(self, other: HexMap):  # -> Self:
        """Get symmetric difference of two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`
        """

        if not isinstance(other, HexMap):
            raise TypeError(f"other must be of type 'HexMap', not {type(other)}")

        for k in other.keys() - self.keys():
            self[k] = other[k]

        return self

    def symmetric_difference_update(self, other: HexMap):  # -> Self:
        """Get symmetric difference of two HexMaps.

        Args:
            other (HexMap): The other HexMap

        Raises:
            TypeError: If `other` is not of type `HexMap`
        """
        self ^= other

    # save and plot

    def save(self, filepath: Path | str) -> None:
        """Save a Hexmap at filepath using pickle

        Args:
            filepath (Path | str): Path to where the HexMap `.pkl` file should be saved
        """
        with builtins.open(filepath, "wb") as f:  # type: ignore
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def plot(
        self,
        colormap: Optional[dict[Any, Any]] = None,
        draw_axes: bool = False,
        draw_coords: bool = False,
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

        # TODO CHANGE PLOT TO USE *args, **kwargs instead and maybe a separate module for it
        return plot(
            self,
            colormap,
            draw_axes,
            draw_coords,
            size_factor,
            hex_alpha,
            facecolor,
            title,
            show_directly,
        )


def plot(
    hxmp: HexMap,
    colormap: Optional[dict[Any, Any]] = None,
    # textmap: Optional[dict[Any, str]] = None,
    draw_axes: bool = False,
    draw_coords: bool = False,
    size_factor: float = 1,
    hex_alpha: float = 0.8,
    facecolor: Optional[Any] = None,
    title: str = "Unnamed Hexmap",
    show_directly: bool = False,
    fig: Optional[Figure] = None,
    ax: Optional[Axes] = None,
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

    # TODO add support for adding this plot as an ax to a prior figure!
    # if fig is not None and ax is None:
    #     ax = fig.add_subplot(2, 2, len(fig.get_axes()))

    if ax is None:
        fig, ax = plt.subplots(num="HexMap plot")
        ax.invert_yaxis()

    else:
        fig = ax.get_figure()

    fig.tight_layout()
    ax.set_aspect("equal")
    ax.set_title(title)

    if facecolor is not None:
        ax.set_facecolor(facecolor)

    # for a nice and bright random coloring haha: np.random.random((1, 3)) * 0.6 + 0.4

    if colormap is None:
        # This draws the hexagons slightly faster since they all get the same appearence
        hex_list = [
            Polygon(hx.polygon_points(size_factor))  # type: ignore
            for hx in hxmp.hexes()
        ]
        hexagons = PatchCollection(hex_list, facecolor=WHITE, edgecolor=GRAY)

    else:
        # This draws the hexagons slightly slower but gives individiual colors to the ones with values specified in the colormap
        hex_list = [
            Polygon(
                hx.polygon_points(size_factor),  # type: ignore
                facecolor=colormap[value] if value in colormap else WHITE,
                edgecolor=GRAY,
            )
            for hx, value in hxmp.items()
        ]
        hexagons = PatchCollection(hex_list, match_original=True)

    # hexagons.set_alpha(hex_alpha)
    # hexagons.set_facecolor("none")

    ax.add_collection(hexagons)  # type: ignore

    origin = hxmp.origin_offset.to_point()
    diagonal = hxmp.origin_offset + Hex(2, -1)

    if draw_axes:
        # Draw q, r and s axes

        for col, lbl in zip((Q, R, S), ("Q-axis", "R-axis", "S-axis")):
            ax.axline(origin, diagonal.to_point(), color=col, label=lbl)
            # , zorder=0) Used to set axline behind patches

            # Rotate the diagonal inplace to the right around origin_offset two steps
            diagonal >>= (hxmp.origin_offset, 2)

    else:
        # If this is left out, then no patches will be shown!
        ax.plot(origin.x, origin.y)

    # This is used to display q, r and s values in the top right of the window
    def coord_display(x, y):
        x, y = round(x, 1), round(y, 1)
        hexagon = Hex.from_pixel((x, y), False).rounded(1)

        q, r, s = (round(c, 1) for c in hexagon.cube_coords)

        return f"pixel: {x=}, {y=}\nhex: {q=}, {r=}, {s=}"

    # link the coord_display function to the axis object
    ax.format_coord = coord_display

    # TODO make text size relative to ax window size

    if draw_coords:
        # phis = np.arange((1 / 2), -(5 / 6), -(2 / 3))
        phis = np.array(((1 / 2), -(1 / 6), -(5 / 6)))

        phis += (1 / 3) * Hex.hexlayout.orientation.start_angle
        phis *= np.pi

        # start_angle = (1 / 3) * np.pi * Hex.layout.orientation.start_angle
        # start_angle -= (1 / 6) * np.pi

        hx_size = Hex.hexlayout.size

        for hx in hxmp:
            coords = "qrs" if hx == Hexigo else (hx.q, hx.r, hx.s)
            center = hx.to_point()

            for phi, coord, color in zip(phis, coords, (Q, R, S)):
                label_x = center.x + 0.4 * hx_size.x * np.cos(phi)
                label_y = center.y + 0.4 * hx_size.y * -np.sin(phi)

                ax.text(
                    label_x,
                    label_y,
                    f"{coord:^3}",
                    va="center",
                    ha="center",
                    color=color,
                    weight="bold",
                    size=20,
                )

    if show_directly:
        plt.show()

    return fig, ax


def show(*args, **kwargs):
    # TODO TELL USER HOW TO USE THIS

    try:
        import matplotlib.pyplot as plt

    except ImportError as e:
        warnings.warn(str(e), RuntimeWarning)
        raise

    plt.show(*args, **kwargs)


# NOTE ALL OF THE BELOW IS STILL WORK IN PROGRESS!
# TODO WHEN SIZE OR RADIUS IS 0, THEN RETURN EMPTY HEXMAP


def hexagon(
    radius: int,
    value: Any = None,
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Hexagon ⬢

    Args:
        radius (int): The number of hexes from the origin_offset
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The hexagon shaped HexMap
    """

    # TODO ADD TYPE CHECKS

    hxmp = HexMap(default_value=value, origin_offset=origin_offset)

    for q in range(-radius, radius + 1):
        r1 = max(-radius, -q - radius)
        r2 = min(radius, -q + radius)

        if not hollow or q == -radius or q == radius:
            for r in range(r1, r2 + 1):
                # print(f"{q=}, {r=}")

                hxmp.insert(Hex(q, r))
        else:
            hxmp.insert(Hex(q, r1))
            hxmp.insert(Hex(q, r2))

    return hxmp


def parallelogram(
    axes: dict[str, int | tuple[int, int]] = {"q": 2, "r": 1},
    value: Any = None,
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:  # sourcery skip: default-mutable-arg
    """Create a HexMap in the shape of a Parallelogram ▰

    Args:
        axes (_type_, optional): _description_. Defaults to {"q": 2, "r": 2}.
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

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
    hxmp = HexMap(default_value=value, origin_offset=origin_offset)

    ax1, ax2 = axes
    v1, v2 = axes.values()
    range1 = range(-v1, v1 + 1) if isinstance(v1, int) else range(v1[0], v1[1] + 1)
    range2 = range(-v2, v2 + 1) if isinstance(v2, int) else range(v2[0], v2[1] + 1)

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
    value: Any = None,
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a rhombus (aka diamond) ⬧

    Note:
        This is a special case of parallelogram, where both axes are the same size.

    Args:
        size (int, optional): _description_. Defaults to 1.
        axes (str | tuple[str, str], optional): _description_. Defaults to ("q", "s").
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The rhombus HexMap
    """
    # TODO When available remove: value, origin_offset, hollow in favor for type-annotated kwargs
    return parallelogram({axes[0]: size, axes[1]: size}, value, origin_offset, hollow)


def rectangle(
    axes: dict[str, int | tuple[int, int]] = {"q": (-3, 3), "r": (-2, 2)},
    value: Any = None,
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:  # sourcery skip: default-mutable-arg
    """Create a HexMap in the shape of a Rectangle ▬

    Args:
        axes (_type_, optional): _description_. Defaults to {"q": (-3, 3), "r": (-2, 2)}.
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The rectangle HexMap
    """

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
    hxmp = HexMap(default_value=value, origin_offset=origin_offset)

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
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Square ■

    Note:
        This is a special case of rectangle, where both axes are the same size.

    Args:
        size (int | tuple[int, int], optional): _description_. Defaults to 1.
        axes (str | tuple[str, str], optional): _description_. Defaults to "qr".
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The square HexMap
    """

    # TODO When available remove: value, origin_offset, hollow in favor for type-annotated kwargs
    return rectangle({axes[0]: size, axes[1]: size}, value, origin_offset, hollow)


def triangle(
    size: int | tuple = 1,
    axes: str | tuple[str, str] = "qr",
    value: Any = None,
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Triangle ▲

    Args:
        size (int | tuple, optional): _description_. Defaults to 1.
        axes (str | tuple[str, str], optional): _description_. Defaults to "qr".
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The triangle HexMap
    """
    # for (int q = 0; q <= map_size; q++) {
    #     for (int r = 0; r <= map_size - q; r++) {
    #         map.insert(Hex(q, r, -q-r));
    #     }
    # }

    hx = Hex(0, 0)
    hxmp = HexMap(default_value=value, origin_offset=origin_offset)

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


def star(
    # size: Any = None,
    # value: Any = None,
    # origin_offset: Hex = Hexigo,
    # hollow: bool = False,
) -> HexMap:
    """Create a HexMap in the shape of a Star ★ ✡

    NOT YET IMPLEMENTED

    Note:
        This is a combination of hexmap.hexagon() and six hexmap.triangle().

    Args:
        value (Any, optional): _description_. Defaults to None.
        axes (str, optional): _description_. Defaults to "qs".
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The star HexMap
    """

    raise NotImplementedError(
        "Not yet implemented, plan is to make it a special case of 'triangle'"
    )


def polygon(
    hexiter: Iterable[Hex],
    value: Any = None,
    origin_offset: Hex = Hexigo,
    hollow: bool = False,
) -> HexMap:
    """Create a general shape polygon from an iterable of Hexes

    PLAN ON ALLOWING FILLED GENERAL POLYGONS, BUT AS OF NOW THEY WILL BE HOLLOW

    Args:
        hexiter (Iterable[Hex]) The Hex to use as corners for the polygon.
        value (Any, optional): The value that should be assigned to all Hexagons. Defaults to None.
        origin_offset (Hex, optional): The origin_offset of the shape, all Hexes will be centered around origin_offset. Defaults to Hexigo.
        hollow (bool, optional):  NOT SUPPORTED YET: Whether or not to make the shape hollow. Defaults to False.

    Returns:
        HexMap: The general polygon HexMap
    """

    def current_and_next(hxs) -> zip[tuple[Hex, Hex]]:
        return zip(hxs, hxs[1:] + hxs[:1])  # type: ignore

    hxmp = HexMap(default_value=value, origin_offset=origin_offset)

    for curr_hx, next_hx in current_and_next(hexiter):
        for hx in curr_hx.linedraw(next_hx):
            hxmp.insert(hx)

    # for hx in hexiter:
    #     last_hex = hx

    #     if first:
    #         first = False
    #         continue

    return hxmp
