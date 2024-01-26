"""Created just for fun because I wanted to draw in hexagonal grids on paper while sketching the logo"""

from hexpy import Hex, hexmap

# Define our Hexagonal layout
Hex.pointy_layout(10)

# Create a hexmap object in the shape of a hexagon
hexrect = hexmap.rectangle(axes={"q": (-29, 30), "r": (-20, 21)})
hexrect.plot(title="Hexagonal grid for A4 paper")
