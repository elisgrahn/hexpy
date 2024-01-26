import warnings
from typing import TYPE_CHECKING, Any, Optional

from .hexclass import Hex, Hexigo

if TYPE_CHECKING:
    from .hexmap import HexMap

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.axes import Axes
    from matplotlib.collections import PatchCollection
    from matplotlib.figure import Figure
    from matplotlib.patches import Polygon, RegularPolygon

except ImportError as e:
    warnings.warn(str(e), RuntimeWarning)
    raise

raise NotImplementedError(
    "This module is work in progress, hexmap.plot() will utilize this in order to modularize plotting.!"
)  # sourcery skip: remove-unreachable-code

# Global colors
WHITE = (0.96, 0.96, 0.94)
GRAY = (0.74, 0.74, 0.74)
Q = (0.35, 0.7, 0.0, 0.6)
R = (0.11, 0.64, 0.91, 0.6)
S = (0.9, 0.1, 0.9, 0.6)


def draw_hexaxes(ax: Axes, hxmp: HexMap) -> None:
    """Draw q, r and s axes in the HexMap plot"""

    origin = hxmp.origin_offset.to_point()
    diagonal = hxmp.origin_offset + Hex(2, -1)

    for col, lbl in zip((Q, R, S), ("Q-axis", "R-axis", "S-axis")):
        ax.axline(origin, diagonal.to_point(), color=col, label=lbl)
        # , zorder=0) Used to set axline behind patches

        # Rotate the diagonal inplace to the right around origin_offset two steps
        diagonal >>= (hxmp.origin_offset, 2)


def draw_text(ax: Axes, x: float, y: float, text: str, color: Any, size: int = 20):
    """Draw text in the HexMap plot"""

    ax.text(
        x,
        y,
        text,
        va="center",
        ha="center",
        color=color,
        weight="bold",
        size=size,  # HOW TO DO THIS RELATIVE TO HEX SIZE?
    )


def draw_hexcoords(ax: Axes, hxmp: HexMap) -> None:
    """Draw the q, r and s coords for each Hex in the HexMap plot"""
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

            draw_text(ax, label_x, label_y, f"{coord:^3}", color=color)


def hexcoord_display(x, y):
    """Display the q, r and s coordinates of the cursor together with the pixel coordinate in the top right of the window"""

    x, y = round(x, 1), round(y, 1)
    hx = Hex.from_point((x, y)).rounded(1)

    q, r, s = hx.cube_coords

    return f"pixel: {x=}, {y=}\nhex: {q=}, {r=}, {s=}"


def hexmap_plot(
    hxmp: HexMap,
    colormap: Optional[dict[Any, Any]] = None,
    textmap: Optional[dict[Any, str]] = None,
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
        hex_list = [Polygon(hx.polygon_points(size_factor)) for hx in hxmp.hexes()]  # type: ignore
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

    # if textmap is not None:
    #     TODO add textmap support

    # hexagons.set_alpha(hex_alpha)
    # hexagons.set_facecolor("none")

    ax.add_collection(hexagons)  # type: ignore

    if draw_axes:
        draw_hexaxes(ax, hxmp)
    else:
        # If this is left out, then no patches will be shown!
        origin = hxmp.origin_offset.to_point()
        ax.plot(origin.x, origin.y)

    # link the hexcoord_display function to the axis object
    ax.format_coord = hexcoord_display

    # TODO make text size relative to ax window size

    if draw_coords:
        draw_hexcoords(ax, hxmp)

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
