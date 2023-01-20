from dataclasses import dataclass
from colorsys import hsv_to_rgb
import math
from PIL import ImageColor
from typing import Union


@dataclass
class Color:
    color: tuple[int, int, int]
    name: str

    def __init__(self, color: Union[str, tuple[float, float, float], tuple[int, int, int]], name: str = None):
        self.color = (
            ImageColor.getcolor(color, 'RGB')
            if type(color) == str
            else tuple(int(a*255) for a in hsv_to_rgb(*color))
            if type(color[0]) == float
            else color
        )
        self.name = name


@dataclass
class Table:
    colors: Union[list[Color], list[list[Union[Color, None]]]]
    literalOrder: bool
    height: int
    width: int
    gridHeight: int = 168
    gridWidth: int = 224

    def __init__(self, colors: Union[list[list[Union[Color, None]]], list[Color]]):
        self.colors = colors
        if type(colors[0]) == list:
            self.literalOrder = True
            self.height = len(colors)
            self.width = len(colors[0])
        else:
            self.literalOrder = False
            self.height = math.floor(math.sqrt(len(colors)))
            self.width = self.height
            while self.height * self.width < len(colors):
                self.width += 1
