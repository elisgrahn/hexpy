"""Created just for fun because I wanted to draw in hexagonal grids on paper while sketching the logo"""

from hexpy import Hex, hexmap

# Define our Hexagonal layout
Hex.pointy_layout(size=10)

# Create a hexmap object in the shape of a hexagon
hxmp = hexmap.rectangle(axes={"q": (-29, 30), "r": (-20, 21)}, value=0)

# Plot the hexmap
hxmp.plot(draw_axes=False, title="A4 paper grid of hexagons")
