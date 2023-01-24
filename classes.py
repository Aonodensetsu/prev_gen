from typing import Union, Literal, Callable
import colorsys
import math


class Color:
    # color name
    name: str
    # hexadecimal string '#000000'
    hex: str
    # left corner description
    desc_left: str
    # right corner description
    desc_right: str
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
                 color: Union[str, tuple[float, float, float], tuple[int, int, int]],
                 name: str = None,
                 desc_left: str = None,
                 desc_right: str = None,
                 *,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq'] = 'rgb'
                 ):
        # hex is allowed regardless of mode
        if type(color) == str:
            self.hex = color.upper()
            self.rgb = tuple(int(color.lstrip('#')[i:i + 2], 16) / 255. for i in (0, 2, 4))
            # if mode was passed, precalculate the answer for convenience
            if not mode == 'rgb':
                setattr(self, mode, colorsys.__dict__['rgb_to_' + mode](*self.rgb))
        elif mode == 'rgb':
            # allow passing denormalized RGB
            if type(color) == tuple[int, int, int]:
                self.drgb = color
                color = tuple(i / 255. for i in color)
            setattr(self, mode, color)
        else:
            setattr(self, mode, color)
            # always keep RGB since it is used for conversions
            setattr(self, 'rgb', colorsys.__dict__[mode + '_to_rgb'](*color))
        self.name = name
        self.desc_left = desc_left
        self.desc_right = desc_right

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            # lazyload attributes as needed
            if item in ['hsv', 'hls', 'yiq']:
                setattr(self, item, colorsys.__dict__['rgb_to_' + item](*self.rgb))
            elif item == 'drgb':
                setattr(self, item, tuple(int(a * 255) for a in self.rgb))
            elif item == 'hex':
                setattr(self, item, ('#%02X%02X%02X' % self.drgb))
            elif item == 'isDark':
                (r, g, b) = [  # linearized RGB
                    i / 12.92 if i < 0.04045 else math.pow((i + 0.055) / 1.055, 2.4)
                    for i in self.rgb
                ]
                lum = 0.2126 * r + 0.7152 * g + 0.0722 * b  # luminance
                perc = (  # perceived brightness
                    (lum * 24389 / 27) / 100
                    if lum <= 216 / 24389
                    else (math.pow(lum, 1 / 3) * 116 - 16) / 100
                )
                if perc < 0.4:
                    setattr(self, item, True)
                else:
                    setattr(self, item, False)
            return object.__getattribute__(self, item)


class Field:
    # x, y position within the image
    pos: tuple[int, int]
    # color that should be drawn
    color: Union[Color, None]

    def __init__(self,
                 pos: tuple[int, int],
                 color: Union[Color, None]
                 ):
        self.pos = pos
        self.color = color


class Settings:
    # file name to save into (no extension - will be png)
    file_name: str
    # height of each individual color field
    grid_height: int
    # width of each individual color field
    grid_width: int
    # height of the darkened bar at the bottom of each field
    bar_height: int
    # vertical offset of the name printed within the field
    name_offset: int
    # vertical offset of the hex value printed below name
    hex_offset: int
    # vertical offset of the hex value printed if no name given
    hex_offset_noname: int
    # horizontal offset of the corner descriptions
    desc_offset_x: int
    # vertical offset of the corner descriptions
    desc_offset_y: int
    # text size of the name
    name_size: int
    # text size of the hex value printed under the name
    hex_size: int
    # text size of the hex value printed if no name given
    hex_size_noname: int
    # text size of the corner descriptions
    desc_size: int
    # function to use for the darkened bar
    darken_fn: Callable[[Color], Color]
    # function to determine text color from background color
    text_col_fn: Callable[[Color], Color]

    def __init__(self,
                 *,
                 file_name: str = 'result',
                 grid_height: int = 168,
                 grid_width: int = 224,
                 bar_height: int = 10,
                 name_offset: int = -10,
                 hex_offset: int = 35,
                 hex_offset_noname: int = 0,
                 desc_offset_x: int = 15,
                 desc_offset_y: int = 20,
                 name_size: int = 40,
                 hex_size: int = 26,
                 hex_size_noname: int = 34,
                 desc_size: int = 24,
                 darken_fn: Callable[[Color], Color] = (
                    lambda x:
                    Color((x.hsv[0], x.hsv[1] * 1.05, x.hsv[2] * 0.85), mode='hsv')
                 ),
                 text_col_fn: Callable[[Color], Color] = (
                         # fix text contrast (using LERP and magic numbers)
                         lambda x:
                         Color((x.hsv[0], x.hsv[1] * 0.95, x.hsv[2] * 1.1 + (1. - x.hsv[2]) * 0.3), mode='hsv')
                         if x.isDark
                         else Color((x.hsv[0], x.hsv[1] * 0.95, x.hsv[2] * 0.6 - (1. - x.hsv[2]) * 0.2), mode='hsv')
                 )
                 ):
        self.file_name = file_name + '.png'
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.bar_height = bar_height
        self.name_offset = name_offset
        self.hex_offset = hex_offset
        self.hex_offset_noname = hex_offset_noname
        self.desc_offset_x = desc_offset_x
        self.desc_offset_y = desc_offset_y
        self.name_size = name_size
        self.hex_size = hex_size
        self.hex_size_noname = hex_size_noname
        self.desc_size = desc_size
        self.darken_fn = darken_fn
        self.text_col_fn = text_col_fn


class Table:
    # list of colors after normalization
    colors: list[Union[Color, None]]
    # the settings available to the user
    settings: Settings
    _height: int
    _width: int

    def size(self):
        return self._width * self.settings.grid_width, self._height * self.settings.grid_height

    def fields(self):
        i = 0
        h = self.settings.grid_height
        w = self.settings.grid_width
        while i < len(self.colors):
            if self.colors[i] is not None:
                yield Field((i % self._width * w, i // self._width * h), self.colors[i])
            i += 1

    def __init__(self,
                 colors: Union[
                     list[Union[Settings, Color, None]],
                     list[Union[Settings, list[Union[Color, None]]]]
                 ]
                 ):
        colors = [
            [
                Color(*a) if type(a) == tuple else a
                for a in i
            ]
            if type(i) == list
            else Color(*i)
            if type(i) == tuple
            else i
            for i in colors
        ]
        if type(colors[0]) == Settings:
            self.settings = colors[0]
            colors = colors[1:]
        else:
            self.settings = Settings()
        if type(colors[0]) == list:
            self._height = len(colors)
            self._width = max((len(a) for a in colors))
            for i in colors:
                while len(i) < self._width:
                    i.append(None)
            colors = sum(colors, [])
        self.colors = colors
        try:
            self._height
        except AttributeError:
            self._height = math.floor(math.sqrt(len(colors)))
            self._width = self._height
            while self._width * self._height < len(colors):
                self._width += 1
