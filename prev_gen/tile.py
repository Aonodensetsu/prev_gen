from dataclasses import dataclass

from .distance import Distance
from .color import Color


@dataclass(slots=True)
class Tile:
    """
    A single tile in the table, which contains a color and its positioning
    Used as a container of data when drawing tiles

    Attributes:
        pos:  Pixel offset from (0,0) to the top left corner

        size: Pixel offset from the top left corner to the bottom right corner

        col:  Color of this tile
    """
    pos: Distance
    size: Distance
    col: Color
