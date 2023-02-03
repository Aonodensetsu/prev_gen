from typing import NamedTuple, Literal, Callable, Generator
from PIL import Image, ImageDraw, ImageFont
from math import pow, sqrt, floor
from dataclasses import dataclass
from os import startfile
import colorsys


# type aliases are declared as needed, so they are spread throughout the file
# some depend on the presence of classes, so they cannot be moved to the top of the file

# used for normalized color representations
#   (R, G, B)
#   (H, S, V)
#   (H, L, S)
#   (Y, I, Q)
f3 = tuple[float, float, float]
# used for denormalized color representations
#   (R, G, B) - currently only RGB supports denormalized values
i3 = tuple[int, int, int]


class LazyloadError(AttributeError):
    """Attribute was not assigned a value and does not support lazyloading"""
    def __init__(self):
        super().__init__(self.__doc__)


@dataclass(slots=True)
class Color:
    """
    Represents one tile in the image, its color, and any descriptions

    Attributes:
        name: Color name
        desc_left: Left corner description
        desc_right: right corner description
        hex: Hexadecimal color
        rgb: RGB normalized color
        hsv: HSV normalized color
        hls: HLS normalized color
        yiq: YIQ normalized color
        drgb: RGB denormalized color
        dark: Whether the color is dark based on human perception
    """
    name: str | None
    desc_left: str | None
    desc_right: str | None
    hex: str
    rgb: f3
    hsv: f3
    hls: f3
    yiq: f3
    drgb: i3
    dark: bool

    def __init__(self,
                 color: str | f3 | i3,
                 name: str | None = None,
                 desc_left: str | None = None,
                 desc_right: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq'] = 'rgb'
                 ) -> None:
        """
        Create a color from a given value

        Parameters:
            color: The color value to assign
            name: The name to display
            desc_left: Left corner description
            desc_right: Right corner description
            mode: Specifies type of color to convert from
        """
        # hex is allowed regardless of mode
        if isinstance(color, str):
            self.hex = '#'+color.lstrip('#').upper()
            self.rgb = tuple(int(self.hex[i:i + 2], 16) / 255. for i in (1, 3, 5))
            # precalculate the given mode if not default, the user probably intends to use it
            if not mode == 'rgb':
                setattr(self, mode, colorsys.__dict__['rgb_to_' + mode](*self.rgb))
        else:
            # always calculate RGB since it is used for conversions
            if not mode == 'rgb':
                self.rgb = colorsys.__dict__[mode + '_to_rgb'](*color)
            # allow passing denormalized RGB
            if mode == 'rgb' and all(isinstance(i, int) for i in color):
                self.drgb = color
                color = tuple(i / 255. for i in color)
            setattr(self, mode, color)
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
                    self.drgb = tuple(int(i * 255) for i in self.rgb)
                case 'hex':
                    self.hex = '#%02X%02X%02X' % self.drgb
                case 'dark':
                    r, g, b = [  # linearized RGB
                        i / 12.92
                        if i < 0.04045
                        else pow((i + 0.055) / 1.055, 2.4)
                        for i in self.rgb
                    ]
                    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b  # luminance
                    perc = (  # perceived brightness
                        (lum * 24389 / 27) / 100
                        if lum <= 216 / 24389
                        else (pow(lum, 1 / 3) * 116 - 16) / 100
                    )
                    if perc <= 0.4:
                        self.dark = True
                    else:
                        self.dark = False
                case _:
                    raise LazyloadError
            return object.__getattribute__(self, item)


# used for Color transformations
#   bar - calculates dark bar color from background color
#   text - calculates text color from background color
tf = Callable[[Color], Color]


@dataclass(kw_only=True, slots=True)
class Settings:
    """
    Image generation settings

    Attributes:
        file_name: File name to save into (no extension - png)
        font: Font used (no extension - true type)
        grid_height: Height of each individual color field
        grid_width: Width of each individual color field
        bar_height: Height of the darkened bar at the bottom of each field
        name_offset: Vertical offset of the color name printed within the field
        hex_offset: Vertical offset of the hex value printed below color name
        hex_offset_noname: Vertical offset of the hex value printed if no name given
        desc_offset_x: Horizontal offset of the corner descriptions
        desc_offset_y: Vertical offset of the corner descriptions
        name_size: Text size of the color name
        hex_size: Text size of the hex value printed under the color name
        hex_size_noname: Text size of the hex value printed if no name given
        desc_size: Text size of the corner descriptions
        bar_col_fn: Function to determine bar color from background color
        text_col_fn: Function to determine text color from background color
    """
    file_name: str = 'result'
    font: str = 'renogare'
    grid_height: int = 168
    grid_width: int = 224
    bar_height: int = 10
    name_offset: int = -10
    hex_offset: int = 35
    hex_offset_noname: int = 0
    desc_offset_x: int = 15
    desc_offset_y: int = 20
    name_size: int = 40
    hex_size: int = 26
    hex_size_noname: int = 34
    desc_size: int = 26
    bar_col_fn: tf = (
        lambda x:
        Color(
            (
                x.hsv[0],
                x.hsv[1] * 1.05,
                x.hsv[2] * 0.85
            ),
            mode='hsv'
        )
    )
    text_col_fn: tf = (
        lambda x:
        Color(
            (
                x.hsv[0],
                x.hsv[1] * 0.95,
                x.hsv[2] * 1.1 + (1. - x.hsv[2]) * 0.3
            ),
            mode='hsv'
        )
        if x.dark
        else Color(
            (
                x.hsv[0],
                x.hsv[1] * 0.95,
                x.hsv[2] * 0.6 - (1. - x.hsv[2]) * 0.2
            ),
            mode='hsv'
        )
    )


# used to typehint palettes
# usage 1
#   list of
#     None to mark an empty element
#     Settings (as the first element)
#     Color
#     tuple representing a color in special syntax
u1 = list[None | Settings | Color | tuple]
# usage 2
#   list of
#     None to mark an empty row
#     Settings (as the first element)
#     list of
#       None to mark an empty element
#       Color
#       tuple representing a color in special syntax
u2 = list[None | Settings | list[None | Color | tuple]]


# used for position and size when placing tiles in an image
# and for the size of the image itself
class Distance(NamedTuple):
    """
    Absolute distance in pixels

    Attributes:
        x: Horizontal offset
        y: Vertical offset
    """
    x: int
    y: int


# used as a container of data when drawing tiles
class Field(NamedTuple):
    """
    A single field in the table, which contains a tile (color) and its geometry

    Attributes:
        pos: Pixel offset from (0,0) to the top left corner
        size: Pixel offset from the top left corner to the bottom right corner
        col: Color of this field
    """
    pos: Distance
    size: Distance
    col: Color


@dataclass(slots=True)
class Table:
    """
    A table of colors

    Attributes:
        colors: List of colors, flattened
        settings: The settings available to the user
        height: Height of the table in fields
        width: Width of the table in fields
        size: Size of table in pixels
        fields: Iterable of Fields within the table
    """
    colors: list[Color | None]
    settings: Settings
    height: int
    width: int

    @property
    def size(self) -> Distance:
        """Size of table in pixels"""
        return Distance(
            self.width * self.settings.grid_width,
            self.height * self.settings.grid_height
        )

    @property
    def fields(self) -> Generator[Field, None, None]:
        """Iterable of Fields within the table"""
        i = 0
        while i < len(self.colors):
            if self.colors[i] is not None:
                yield Field(
                    Distance(
                        i % self.width * self.settings.grid_width,
                        i // self.width * self.settings.grid_height
                    ),
                    Distance(
                        self.settings.grid_width - 1,
                        self.settings.grid_height - 1
                    ),
                    self.colors[i]
                )
            i += 1

    def __init__(self, colors: u1 | u2) -> None:
        """
        Creates a table from a palette

        Parameters:
             colors: The list of colors to use for this table
        """
        # special syntax handling, converts tuples to Colors
        # kinda complicated because supports both usage types
        colors = [
            [
                Color(*j)
                if isinstance(j, tuple)
                else j
                for j in i
            ]
            if isinstance(i, list)
            else Color(*i)
            if isinstance(i, tuple)
            else i
            for i in colors
        ]
        # extract settings from palette
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
                    i.append(None)
            colors = [j for i in colors for j in i]
        # calculate the correct size
        else:
            self.height = floor(sqrt(len(colors)))
            self.width = self.height
            while self.width * self.height < len(colors):
                self.width += 1
        self.colors = colors


class App:
    """A wrapper for the main function to allow simpler usage"""
    def __new__(cls,
                palette: u1 | u2,
                show: bool = True,
                save: bool = True
                ) -> Image:
        """
        Parameters:
            palette: The palette of colors to generate an image for
            show: Whether to display the generated image
            save: Whether to save the generated palette

        Returns:
            (PIL.Image) the created image
        """
        t = Table(palette)
        s = t.settings
        img = Image.new('RGBA', t.size)
        draw = ImageDraw.Draw(img)
        font = s.font+'.ttf'
        for i in t.fields:
            l, t = i.pos
            w, h = i.size
            col = i.col
            bg_col = col.drgb
            bar_col = s.bar_col_fn(col).drgb
            text_col = s.text_col_fn(col).drgb
            draw.rectangle(
                (
                    (l, t),
                    (l + w, t + h)
                ),
                fill=bg_col
            )
            draw.rectangle(
                (
                    (l, t + h - s.bar_height),
                    (l + w, t + h)
                ),
                fill=bar_col
            )
            if col.name is not None:
                draw.text(
                    (l + w / 2, t + h / 2 + s.name_offset),
                    col.name,
                    font=ImageFont.truetype(font, size=s.name_size),
                    fill=text_col,
                    anchor='mm'
                )
                draw.text(
                    (l + w / 2, t + h / 2 + s.hex_offset),
                    col.hex,
                    font=ImageFont.truetype(font, size=s.hex_size),
                    fill=text_col,
                    anchor='mm'
                )
            else:
                draw.text(
                    (l + w / 2, t + h / 2 + s.hex_offset_noname),
                    col.hex,
                    font=ImageFont.truetype(font, size=s.hex_size_noname),
                    fill=text_col,
                    anchor='mm'
                )
            if col.desc_left is not None:
                draw.text(
                    (l + s.desc_offset_x, t + s.desc_offset_y),
                    col.desc_left,
                    font=ImageFont.truetype(font, size=s.desc_size),
                    fill=text_col,
                    anchor='lt'
                )
            if col.desc_right is not None:
                draw.text(
                    (l + w - 1 - s.desc_offset_x, t + s.desc_offset_y),
                    col.desc_right,
                    font=ImageFont.truetype(font, size=s.desc_size),
                    fill=text_col,
                    anchor='rt'
                )
        if save:
            img.save(s.file_name + '.png')
        if show:
            img.show() if not save else startfile(s.file_name + '.png')
        return img


# start the program
if __name__ == '__main__':
    from run import run
    run()
