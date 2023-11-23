from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .color import Color
from .settings import Settings
from .distance import Distance
from .tile import Tile


"""
usage 1
  list of
    Settings (as the first element)
    Color
"""
u1: TypeAlias = list[Settings | Color]
"""
usage 2
  list of
    None to mark an empty row
    Settings (as the first element)
    list of Color
"""
u2: TypeAlias = list[Settings | list[Color]]


@dataclass(slots=True)
class Table:
    """
    A table of colors, which you can iterate over

    Attributes:
        colors:   List of colors, flattened

        settings: The settings available to the user

        height:   Height of the table in fields

        width:    Width of the table in fields

        size:     Size of table in pixels
    """
    colors: list[Color]
    settings: Settings
    height: int
    width: int
    _iter: int

    @property
    def size(self) -> Distance:
        """Size of table in pixels"""
        return Distance(
            self.width * self.settings.gridWidth,
            self.height * self.settings.gridHeight
        )

    def __init__(self,
                 colors: u1 | u2
                 ) -> None:
        """
        :param colors: The list of colors to parse
        """
        if isinstance(colors[0], Settings):
            self.settings = colors[0]
            colors = colors[1:]
        else:
            self.settings = Settings()
        # get the explicitly given size and flatten list
        if isinstance(colors[0], list):
            self.height = len(colors)
            self.width = max(len(i) for i in colors)
            for i in colors:
                while len(i) < self.width:
                    i.append(Color('0000'))
            colors = [j for i in colors for j in i]
        # calculate the correct size
        else:
            self.height = int(len(colors) ** (1 / 2))
            self.width = self.height
            # extend the square until everything fits
            while self.width * self.height < len(colors):
                self.width += 1
        self.colors = colors
        self._iter = 0

    def __iter__(self) -> Table:
        self._iter = 0
        return self

    def __next__(self) -> Tile:
        i = self._iter
        self._iter += 1
        while i < len(self.colors) - 1 and self.colors[i].alpha == 0:
            i += 1
            self._iter += 1
        if i >= len(self.colors) or self.colors[i].alpha == 0:
            self._iter = 0
            raise StopIteration
        return Tile(
            Distance(
                i % self.width * self.settings.gridWidth,
                i // self.width * self.settings.gridHeight
            ),
            # the size is decreased by one because the tiles would overlap
            # which you can see if you have an empty tile somewhere
            Distance(
                self.settings.gridWidth - 1,
                self.settings.gridHeight - 1
            ),
            self.colors[i]
        )
