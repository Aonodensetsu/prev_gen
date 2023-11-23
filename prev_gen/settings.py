from __future__ import annotations

from typing import Any, TypeAlias, Callable
from base64 import b64decode, b64encode
from dataclasses import dataclass
from dill import loads, dumps

from .color import Color


"""
used for Color transformations
  bar - calculates dark bar color from background color
  text - calculates text color from background color
"""
tf: TypeAlias = Callable[[Color], Color]


@dataclass(kw_only=True, slots=True)
class Settings:
    """
    Image generation settings

    Attributes:
        fileName:          File name to save into (no extension, png)

        fontName:          for png = local file name (no extension, true type)

                           for svg = Google Font name

        fontOpts:          Google Fonts API options (for svg)

        gridHeight:        Height of each individual color tile

        gridWidth:         Width of each individual color tile

        barHeight:         Height of the darkened bar at the bottom of each tile

        nameOffset:        Vertical offset of the color name printed within the tile

        hexOffset:         Vertical offset of the hex value printed below color name

        hexOffsetNameless: Vertical offset of the hex value printed if no name given

        descOffsetX:       Horizontal offset of the corner descriptions

        descOffsetY:       Vertical offset of the corner descriptions

        nameSize:          Text size of the color name

        hexSize:           Text size of the hex value printed under the color name

        hexSizeNameless:   Text size of the hex value printed if no name given

        descSize:          Text size of the corner descriptions

        barFn:             Function to determine bar color from background color

        textFn:            Function to determine text color from background color
    """
    fileName: str = 'result'
    fontName: str = 'Nunito'
    fontOpts: dict | None = None
    gridHeight: int = 168
    gridWidth: int = 224
    barHeight: int = 10
    nameOffset: int = -10
    hexOffset: int = 35
    hexOffsetNameless: int = 0
    descOffsetX: int = 15
    descOffsetY: int = 20
    nameSize: int = 40
    hexSize: int = 26
    hexSizeNameless: int = 34
    descSize: int = 26
    barFn: tf = (
        lambda x:
        Color(
            (
                x.lcha[0] * 0.9,
                x.lcha[1],
                x.lcha[2],
                x.lcha[3]
            ),
            mode='lch'
        )
    )
    textFn: tf = (
        lambda x:
        Color(
            (
                x.lcha[0] * 0.9 + 0.3
                if x.dark
                else x.lcha[0] * 0.75 - 0.15,
                x.lcha[1],
                x.lcha[2],
                x.lcha[3]
            ),
            mode='lch'
        )
    )

    def serialize(self) -> str:
        """
        :return: A base64-encoded representation of the class
        """
        names = Settings.__slots__
        defaultCls = Settings()
        default = {i: getattr(defaultCls, i) for i in names}
        actual = {i: getattr(self, i) for i in names}
        # only serialize non-default values for space-saving
        changed: dict[str, Any] = dict({k: v for k, v in actual.items() if default[k] != v})
        return str(b64encode(dumps(changed, byref=True, recurse=True)), 'latin1')

    @staticmethod
    def deserialize(data: str) -> Settings:
        """
        :param data: The serialized representation to decode into Settings
        :return: The decoded Settings
        """
        return Settings(**loads(b64decode(bytes(data, 'latin1'))))
