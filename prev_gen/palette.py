from __future__ import annotations

from typing import TypeAlias, Sequence
from dataclasses import dataclass

from .util import Distance, Tile
from .settings import Settings
from .color import Color


"""
usage 1
  list of
    Settings (as the first element) (or dict)
    Color (or dict or list)
"""
u1: TypeAlias = list[Settings | Color | dict | list]
"""
usage 2
  list of
    Settings (as the first element) (or dict) 
    list of Color (or dict or list)
"""
u2: TypeAlias = list[Settings | dict | list[Color | dict | list]]


@dataclass(slots=True)
class Palette:
    # noinspection PyUnresolvedReferences
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
            self.width * self.settings.grid_width,
            self.height * self.settings.grid_height
        )

    def _get_settings(self, colors):
        if isinstance(colors[0], Settings):
            self.settings = colors[0]
            colors: u2 = colors[1:]
        elif isinstance(colors[0], dict):
            self.settings = Settings(**colors[0])
            colors: u2 = colors[1:]
        else:
            self.settings = Settings()
        return colors

    def _calc_size(self, colors):
        # get the explicitly given size and flatten list
        if isinstance(colors[0], list):
            self.height = len(colors)
            self.width = max(len(i) for i in colors)
            for i in colors:
                while len(i) < self.width:
                    i.append(Color('000000', alpha=0.))
            colors: u1 = [
                Color(**j) if isinstance(j, dict)
                else Color(*j) if isinstance(j, Sequence)
                else j
                for i in colors
                for j in i
            ]
        # calculate the correct size
        else:
            self.height = int(len(colors) ** (1 / 2))
            self.width = self.height
            # extend the square until everything fits
            while self.width * self.height < len(colors):
                self.width += 1
        return colors

    def __init__(self, colors: u1 | u2) -> None:
        """
        :param colors: The list of colors to parse
        """
        colors = self._get_settings(colors)
        colors = self._calc_size(colors)
        self.colors = colors
        self._iter = 0

    def __iter__(self) -> Palette:
        self._iter = 0
        return self

    def __next__(self) -> Tile:
        i = self._iter
        self._iter += 1
        if i >= len(self.colors):
            self._iter = 0
            raise StopIteration
        return Tile(
            Distance(
                i % self.width * self.settings.grid_width,
                i // self.width * self.settings.grid_height
            ),
            # the size is decreased by one because the tiles would overlap
            # which you can see if you have an empty tile somewhere
            Distance(
                self.settings.grid_width - 1,
                self.settings.grid_height - 1
            ),
            self.colors[i]
        )
