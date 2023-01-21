from dataclasses import dataclass
from colorsys import hsv_to_rgb, rgb_to_hsv
import math
from PIL import ImageColor
from typing import Union


@dataclass
class Color:
    name: str
    hex: str
    rgb: tuple[int, int, int]
    hsv: tuple[float, float, float]
    isDark: bool

    def __init__(self, color: Union[str, tuple[float, float, float], tuple[int, int, int]], name: str = None):
        if type(color) == str:
            self.hex = color
            self.rgb = ImageColor.getcolor(color, 'RGB')
            self.hsv = rgb_to_hsv(*(float(a)/255 for a in self.rgb))
        elif type(color[0]) == int:
            self.rgb = color
            self.hex = '#%02x%02x%02x' % color
            self.hsv = rgb_to_hsv(*(float(a)/255 for a in color))
        elif type(color[0]) == float:
            self.hsv = color
            self.rgb = tuple(int(a*255) for a in hsv_to_rgb(*color))
            self.hex = '#%02x%02x%02x' % self.rgb
        self.name = name
        self.isDark = self.hsv[2] < 0.7

    def textCol(self) -> "Color":
        (r, g, b) = [  # normalized RGB
            float(a)/255
            for a in self.rgb
        ]
        (r, g, b) = [  # linearized RGB
            b / 12.92 if b < 0.04045 else math.pow((b + 0.055) / 1.055, 2.4)
            for b in [r, g, b]
        ]
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b  # luminance
        (h, s, v) = self.hsv
        perc = (  # perceived brightness
            (lum*24389/27)/100
            if lum <= 216/24389
            else (math.pow(lum, 1/3)*116-16)/100
        )
        if perc < 0.4:
            return Color((h, s * 0.95, v * 1.2 + (1. - v) * 0.4))  # correct for low contrast (dark)
        else:
            return Color((h, s * 1.05, v * 0.45 + (1. - v) * 0.15))  # correct for low contrast (light)


@dataclass
class Palette:
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
