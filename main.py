from dataclasses import dataclass
from typing import Literal, Callable, Generator
from math import pow, sqrt, floor
from os import startfile
from PIL import Image, ImageDraw, ImageFont
import colorsys


@dataclass(slots=True)
class Color:
    # color name
    name: str | None
    # left corner description
    desc_left: str | None
    # right corner description
    desc_right: str | None
    # hexadecimal string '#000000'
    hex: str
    # normalized RGB values 0-1
    rgb: tuple[float, float, float]
    # normalized HSV values 0-1
    hsv: tuple[float, float, float]
    # normalized HLS values 0-1
    hls: tuple[float, float, float]
    # normalized YIQ values 0-1
    yiq: tuple[float, float, float]
    # denormalized RGB values 0-255
    drgb: tuple[int, int, int]
    # based on human perception
    isDark: bool

    def __init__(self,
                 color: str | tuple[float, float, float] | tuple[int, int, int],
                 name: str | None = None,
                 desc_left: str | None = None,
                 desc_right: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq'] = 'rgb'
                 ):
        # hex is allowed regardless of mode
        if isinstance(color, str):
            self.hex = color.upper()
            self.rgb = tuple(int(color.lstrip('#')[i:i + 2], 16) / 255. for i in (0, 2, 4))
            # if mode was passed, precalculate the answer for convenience
            if not mode == 'rgb':
                setattr(self, mode, colorsys.__dict__['rgb_to_' + mode](*self.rgb))
        elif mode == 'rgb':
            # allow passing denormalized RGB
            if all(isinstance(a, int) for a in color):
                self.drgb = color
                color = tuple(i / 255. for i in color)
            setattr(self, mode, color)
        else:
            setattr(self, mode, color)
            # always keep RGB since it is used for conversions
            self.rgb = colorsys.__dict__[mode + '_to_rgb'](*color)
        self.name = name
        self.desc_left = desc_left
        self.desc_right = desc_right

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            # lazyload attributes as needed
            match item:
                case 'hsv' | 'hls' | 'yiq':
                    setattr(self, item, colorsys.__dict__['rgb_to_' + item](*self.rgb))
                case 'drgb':
                    self.drgb = tuple(int(a * 255) for a in self.rgb)
                case 'hex':
                    self.hex = '#%02X%02X%02X' % self.drgb
                case 'isDark':
                    r, g, b = [  # linearized RGB
                        i / 12.92 if i < 0.04045 else pow((i + 0.055) / 1.055, 2.4)
                        for i in self.rgb
                    ]
                    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b  # luminance
                    perc = (  # perceived brightness
                        (lum * 24389 / 27) / 100
                        if lum <= 216 / 24389
                        else (pow(lum, 1 / 3) * 116 - 16) / 100
                    )
                    if perc < 0.4:
                        self.isDark = True
                    else:
                        self.isDark = False
            return object.__getattribute__(self, item)


@dataclass(slots=True)
class Field:
    # x, y position within the image
    pos: tuple[int, int]
    # color that should be drawn
    color: Color | None


@dataclass(kw_only=True, slots=True)
class Settings:
    # file name to save into (no extension - will be png)
    file_name: str = 'result'
    # height of each individual color field
    grid_height: int = 168
    # width of each individual color field
    grid_width: int = 224
    # height of the darkened bar at the bottom of each field
    bar_height: int = 10
    # vertical offset of the name printed within the field
    name_offset: int = -10
    # vertical offset of the hex value printed below name
    hex_offset: int = 35
    # vertical offset of the hex value printed if no name given
    hex_offset_noname: int = 0
    # horizontal offset of the corner descriptions
    desc_offset_x: int = 15
    # vertical offset of the corner descriptions
    desc_offset_y: int = 20
    # text size of the name
    name_size: int = 40
    # text size of the hex value printed under the name
    hex_size: int = 26
    # text size of the hex value printed if no name given
    hex_size_noname: int = 34
    # text size of the corner descriptions
    desc_size: int = 26
    # function to use for the darkened bar
    darken_fn: Callable[[Color], Color] = (
        lambda x:
        Color((x.hsv[0], x.hsv[1] * 1.05, x.hsv[2] * 0.85), mode='hsv')
    )
    # function to determine text color from background color
    text_col_fn: Callable[[Color], Color] = (
        # fix text contrast (using LERP and magic numbers)
        lambda x:
        Color((x.hsv[0], x.hsv[1] * 0.95, x.hsv[2] * 1.1 + (1. - x.hsv[2]) * 0.3), mode='hsv')
        if x.isDark
        else Color((x.hsv[0], x.hsv[1] * 0.95, x.hsv[2] * 0.6 - (1. - x.hsv[2]) * 0.2), mode='hsv')
    )


class Table:
    # list of colors after normalization
    colors: list[Color | None]
    # the settings available to the user
    settings: Settings
    __height: int
    __width: int

    @property
    def height(self) -> int:
        return self.__height

    @property
    def width(self) -> int:
        return self.__width

    def size(self) -> tuple[int, int]:
        return self.__width * self.settings.grid_width, self.__height * self.settings.grid_height

    def fields(self) -> Generator[Field, None, None]:
        i = 0
        h = self.settings.grid_height
        w = self.settings.grid_width
        while i < len(self.colors):
            if self.colors[i] is not None:
                yield Field((i % self.__width * w, i // self.__width * h), self.colors[i])
            i += 1

    def __init__(self,
                 colors: list[Settings | Color | None] | list[Settings | list[Color | None]]
                 ):
        colors = [
            [
                Color(*a) if type(a) == tuple else a
                for a in i
            ]
            if isinstance(i, list)
            else Color(*i)
            if isinstance(i, tuple)
            else i
            for i in colors
        ]
        if type(colors[0]) == Settings:
            self.settings = colors[0]
            colors = colors[1:]
        else:
            self.settings = Settings()
        if type(colors[0]) == list:
            self.__height = len(colors)
            self.__width = max((len(a) for a in colors))
            for i in colors:
                while len(i) < self.__width:
                    i.append(None)
            colors = sum(colors, [])
        self.colors = colors
        try:
            self.__height
        except AttributeError:
            self.__height = floor(sqrt(len(colors)))
            self.__width = self.__height
            while self.__width * self.__height < len(colors):
                self.__width += 1


class App:
    @staticmethod
    def run(p: list[Settings | Color | None] | list[Settings | list[Color | None]]) -> None:
        t = Table(p)
        s = t.settings
        img = Image.new('RGBA', t.size())
        draw = ImageDraw.Draw(img)
        for f in t.fields():
            col = f.color
            text_col = s.text_col_fn(col).drgb
            dark_col = s.darken_fn(col).drgb
            (x, y) = f.pos
            draw.rectangle(
                ((x, y), (x + s.grid_width - 1, y + s.grid_height - 1)),
                fill=col.drgb
            )
            draw.rectangle(
                ((x, y + s.grid_height - s.bar_height - 1), (x + s.grid_width - 1, y + s.grid_height - 1)),
                fill=dark_col
            )
            if col.name:
                draw.text(
                    (x + s.grid_width / 2, y + s.grid_height / 2 + s.name_offset),
                    col.name,
                    font=ImageFont.truetype('renogare.ttf', size=s.name_size),
                    fill=text_col,
                    anchor='mm'
                )
                draw.text(
                    (x + s.grid_width / 2, y + s.grid_height / 2 + s.hex_offset),
                    col.hex,
                    font=ImageFont.truetype('renogare.ttf', size=s.hex_size),
                    fill=text_col,
                    anchor='mm'
                )
            else:
                draw.text(
                    (x + s.grid_width / 2, y + s.grid_height / 2 + s.hex_offset_noname),
                    col.hex,
                    font=ImageFont.truetype('renogare.ttf', size=s.hex_size_noname),
                    fill=text_col,
                    anchor='mm'
                )
            if col.desc_left:
                draw.text(
                    (x + s.desc_offset_x, y + s.desc_offset_y),
                    col.desc_left,
                    font=ImageFont.truetype('renogare.ttf', size=s.desc_size),
                    fill=text_col,
                    anchor='lt'
                )
            if col.desc_right:
                draw.text(
                    (x + s.grid_width - 1 - s.desc_offset_x, y + s.desc_offset_y),
                    col.desc_right,
                    font=ImageFont.truetype('renogare.ttf', size=s.desc_size),
                    fill=text_col,
                    anchor='rt'
                )
        img.save(s.file_name + '.png')
        startfile(s.file_name + '.png')


if __name__ == '__main__':
    from palette import palette
    App.run(palette)
