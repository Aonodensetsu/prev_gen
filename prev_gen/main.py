from __future__ import annotations
import colorsys
import os.path
from math import pow, sqrt, floor
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, NamedTuple, Literal, Callable

# some type aliases depend on the presence of classes
# they are declared below their dependencies, spread throughout the file

# used for normalized color representations
#   (R, G, B)
#   (H, S, V)
#   (H, L, S)
#   (Y, I, Q)
f3 = tuple[float, float, float]
# used for denormalized color representations
#   (R: 0-255,  G: 0-255,  B: 0-255)
#   (H: 0-179,  S: 0-255,  V: 0-255)
#   (H: 0-360,  S: 0-100,  L: 0-100)
#   (Y: 0.255,  I: 0-255,  Q: 0-255)
i3 = tuple[int, int, int]


class LazyloadError(AttributeError):
    """Attribute was not assigned a value and does not support lazy loading"""
    def __init__(self, item):
        super().__init__(f'({item}) ' + self.__doc__)


@dataclass(slots=True)
class Color:
    """
    Represents one tile in the image, its color, and any descriptions

    Attributes:
        name:       Color name
        desc_left:  Left corner description
        desc_right: Right corner description
        hex:        Hexadecimal color
        rgb:        RGB normalized color
        hsv:        HSV normalized color
        hls:        HLS normalized color
        yiq:        YIQ normalized color
        rgb_d:      RGB denormalized color
        hsv_d:      HSV denormalized color
        hls_d:      HLS denormalized color
        yiq_d:      YIQ denormalized color
        dark:       Whether the color is dark based on human perception
    """
    name: Optional[str]
    desc_left: Optional[str]
    desc_right: Optional[str]
    hex: str
    rgb: f3
    hsv: f3
    hls: f3
    yiq: f3
    rgb_d: i3
    hsv_d: i3
    hls_d: i3
    yiq_d: i3
    dark: bool

    def __init__(self,
                 color: str | f3 | i3,
                 name: Optional[str] = None,
                 desc_left: Optional[str] = None,
                 desc_right: Optional[str] = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq'] = 'rgb'
                 ) -> None:
        """
        Create a color from a given value

        Parameters:
            color:      The color value to assign
            name:       The name to display
            desc_left:  Left corner description
            desc_right: Right corner description
            mode:       Specifies type of color created
        """
        # hex is allowed regardless of mode
        if isinstance(color, str):
            self.hex = '#' + color.lstrip('#').upper()
            r, g, b = tuple(int(self.hex[i:i + 2], 16) / 255. for i in (1, 3, 5))
            self.rgb = (r, g, b)
        else:
            if all(isinstance(i, int) for i in color):
                match mode:
                    case 'rgb':
                        self.rgb_d = color
                        r, g, b = color
                        color = (r / 255., g / 255., b / 255.)
                    case 'hsv':
                        self.hsv_d = color
                        h, s, v = color
                        color = (h / 179., s / 255., v / 255.)
                    case 'hls':
                        self.hls_d = color
                        h, l, s = color
                        color = (h / 360., l / 100., s / 100.)
                    case 'yiq':
                        self.yiq_d = color
                        y, i, q = color
                        color = (y / 255., i / 255., q / 255.)
            setattr(self, mode, color)
            # always calculate RGB since it is used for conversions
            if not mode == 'rgb':
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
                case 'rgb_d':
                    r, g, b = self.rgb
                    self.rgb_d = (int(r * 255), int(g * 255), int(b * 255))
                case 'hsv_d':
                    h, s, v = self.hsv
                    self.hsv_d = (int(h * 179), int(s * 255), int(v * 255))
                case 'hls_d':
                    h, l, s = self.hls
                    self.hls_d = (int(h * 360), int(l * 100), int(s * 100))
                case 'yiq_d':
                    y, i, q = self.yiq
                    self.yiq_d = (int(y * 255), int(i * 255), int(q * 255))
                case 'hex':
                    self.hex = '#%02X%02X%02X' % self.rgb_d
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
                    self.dark = perc <= 0.4
                case _:
                    raise LazyloadError(item)
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
        file_name:         File name to save into (no extension - png)
        font:              Font used (no extension - true type) if none, will use bundled
        grid_height:       Height of each individual color tile
        grid_width:        Width of each individual color tile
        bar_height:        Height of the darkened bar at the bottom of each tile
        name_offset:       Vertical offset of the color name printed within the tile
        hex_offset:        Vertical offset of the hex value printed below color name
        hex_offset_noname: Vertical offset of the hex value printed if no name given
        desc_offset_x:     Horizontal offset of the corner descriptions
        desc_offset_y:     Vertical offset of the corner descriptions
        name_size:         Text size of the color name
        hex_size:          Text size of the hex value printed under the color name
        hex_size_noname:   Text size of the hex value printed if no name given
        desc_size:         Text size of the corner descriptions
        bar_col_fn:        Function to determine bar color from background color
        text_col_fn:       Function to determine text color from background color
    """
    file_name: str = 'result'
    font: Optional[str] = None
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
                if x.dark
                else x.hsv[2] * 0.6 - (1. - x.hsv[2]) * 0.2
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
u1 = list[Optional[Settings | Color]]
# usage 2
#   list of
#     None to mark an empty row
#     Settings (as the first element)
#     list of
#       None to mark an empty element
#       Color
u2 = list[Optional[Settings | list[Optional[Color]]]]


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
        pos:  Pixel offset from (0,0) to the top left corner
        size: Pixel offset from the top left corner to the bottom right corner
        col:  Color of this field
    """
    pos: Distance
    size: Distance
    col: Color


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
    colors: list[Optional[Color]]
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

    def __init__(self,
                 colors: u1 | u2
                 ) -> None:
        """
        Creates a table from a palette

        Parameters:
             colors: The list of colors to use for this table
        """
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
        self._iter = 0

    def __iter__(self) -> Table:
        self._iter = 0
        return self

    def __next__(self) -> Field:
        i = self._iter
        self._iter += 1
        while i < len(self.colors) - 1 and self.colors[i] is None:
            i += 1
            self._iter += 1
        if i >= len(self.colors) or self.colors[i] is None:
            self._iter = 0
            raise StopIteration
        return Field(
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


class Preview:
    """A wrapper for the main function to allow simpler usage"""
    def __new__(_,
                palette: u1 | u2,
                show: bool = False,
                save: bool = False
                ) -> Image:
        """
        Parameters:
            palette: The palette of colors to generate an image for
            show:    Whether to display the generated image
            save:    Whether to save the generated palette

        Returns:
            (PIL.Image) the created image
        """
        t = Table(palette)
        s = t.settings
        img = Image.new('RGBA', t.size)
        draw = ImageDraw.Draw(img)
        if s.font is None:
            from inspect import currentframe, getabsfile
            font = os.path.dirname(getabsfile(currentframe())) + '/renogare.ttf'
        else:
            font = s.font + '.ttf'
        png = s.file_name + '.png'
        for i in t:
            l, t = i.pos
            w, h = i.size
            col = i.col
            bg_col = col.rgb_d
            bar_col = s.bar_col_fn(col).rgb_d
            text_col = s.text_col_fn(col).rgb_d
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
            img.save(png)
        if show:
            if not save:
                img.show()
            else:
                # a hacky system-agnostic way to try to open the image
                # unlike what the name suggests, it will try to use native apps as well
                from webbrowser import open
                open(png)
        return img


class GUI:
    def __new__(_) -> Image:
        import tkinter as tk
        from inspect import currentframe, getabsfile
        from PIL import ImageTk, ImageOps
        import idlelib.colorizer as ic
        import idlelib.percolator as ip

        def onedit(_):
            editor.unbind('<Key>')
            editor.edited = True

        def preview():
            local = {}
            exec(editor.get('1.0', tk.END), None, local)
            p = local['palette']
            i = Preview(p)
            j = ImageOps.contain(i, (prev.winfo_width()-10, prev.winfo_height()-10))
            img = ImageTk.PhotoImage(j)
            prev.image = img
            prev.config(image=img)
            return i, p

        def save():
            i, p = preview()
            s = p[0]
            if not isinstance(s, Settings):
                s = Settings()
            i.save(s.file_name + '.png')

        def leave():
            _, p = preview()
            if editor.edited:
                with open('gui.py', 'w') as f:
                    f.write(editor.get('1.0', tk.END))
            exit()

        ui = tk.Tk()
        ui.title('Preview Generator GUI')
        ui.rowconfigure(0, weight=1)
        ui.rowconfigure(1, minsize=350)
        ui.columnconfigure(0, weight=1)
        ui.columnconfigure(1, minsize=100)
        ui.config(bg='#282828')
        ui.attributes('-fullscreen', True)
        f_edit = tk.Frame(ui, bg='#282828', border=10)
        f_edit.grid(row=0, column=0, sticky='nsew')
        editor = tk.Text(
            f_edit, bg='#282828', fg='#d4be98', insertbackground='#d4be98', borderwidth=0, font=('Verdana', 13)
        )
        with open(os.path.dirname(getabsfile(currentframe())) + '/example.txt', 'r') as f:
            editor.insert(tk.END, f.read())
        editor.pack(fill='both', expand=True)
        editor.edited = False
        editor.bind('<Key>', onedit)
        col = ic.ColorDelegator()
        col.tagdefs['STRING'] = {'foreground': '#a9b665', 'background': '#282828'}
        col.tagdefs['COMMENT'] = {'foreground': '#5a524c', 'background': '#282828'}
        col.tagdefs['KEYWORD'] = {'foreground': '#ea6962', 'background': '#282828'}
        col.tagdefs['BUILTIN'] = {'foreground': '#d8a657', 'background': '#282828'}
        col.tagdefs['DEFINITION'] = {'foreground': '#7daea3', 'background': '#282828'}
        ip.Percolator(editor).insertfilter(col)
        f_cmd = tk.Frame(ui, bg='#282828')
        f_cmd.grid(row=0, column=1, sticky='nsew')
        tk.Button(f_cmd, text='Preview', command=preview, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(f_cmd, text='Save', command=save, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(f_cmd, text='Exit', command=leave, borderwidth=0, bg='#7daea3').pack(fill='x')
        f_prev = tk.Frame(ui, bg='#282828', border=10)
        f_prev.grid(row=1, column=0, columnspan=2, sticky='nsew')
        prev = tk.Label(f_prev, bg='#282828')
        prev.pack(fill='both', expand=True)
        ui.wait_visibility(prev)
        preview()
        ui.mainloop()
        return preview()[0]
