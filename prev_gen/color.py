from __future__ import annotations

from typing import Literal, Any, TypeAlias, Sequence
from math import pi, cos, sin, degrees, atan2
from base64 import b64decode, b64encode
from multimethod import multidispatch
from dataclasses import dataclass

from .lazyloadError import LazyloadError
from .literals import Literals

import colorsys

"""
used for normalized color representations
     (R, G, B)
     (H, S, V)
     (H, L, S)
     (Y, I, Q)
(OK) (L, C, H)
"""
f3: TypeAlias = tuple[float, float, float]
# with alpha
f4: TypeAlias = tuple[float, float, float, float]
"""
used for denormalized color representations
     (R: 0-255,  G: 0-255,  B: 0-255)
     (H: 0-179,  S: 0-255,  V: 0-255)
     (H: 0-360,  S: 0-100,  L: 0-100)
     (Y: 0.255,  I: 0-255,  Q: 0-255)
(OK) (L: 0-100   C: 0-100   H: 0-360)
"""
i3: TypeAlias = tuple[int, int, int]
# with alpha (A: 0-255)
i4: TypeAlias = tuple[int, int, int, int]


@dataclass(slots=True)
class Color:
    """
    Represents one color tile in the image, any descriptions it may have - and facilitates color conversions
    Parameters are calculated lazily for efficiency

    :param color:     The color value to assign
    :param name:      The name to display
    :param descLeft:  Left corner description
    :param descRight: Right corner description
    :param mode:      Specifies type of color created

    Attributes:
        *Optional suffixes, in square brackets*
            *a - with alpha*

            *D - denormalized*

        name:      Color name

        descLeft:  Left corner description

        descRight: Right corner description

        dark:      Whether the color is dark based on human perception

        alpha[D]:  Transparency value

        hex[a]:    Hexadecimal color

        rgb[aD]:   rgb normalized color

        hsv[aD]:   hsv normalized color

        hls[aD]:   hls normalized color

        yiq[aD]:   yiq normalized color

        lch[aD]:   (ok)lch normalized color
    """
    name: str | None
    descLeft: str | None
    descRight: str | None
    dark: bool
    hex: str
    hexa: str
    alpha: float
    alphaD: int
    rgb: f3
    rgba: f4
    rgbD: i3
    rgbaD: i4
    hsv: f3
    hsva: f4
    hsvD: i3
    hsvaD: i4
    hls: f3
    hlsa: f4
    hlsD: i3
    hlsaD: i4
    yiq: f3
    yiqa: f4
    yiqD: i3
    yiqaD: i4
    lch: f3
    lcha: f4
    lchD: i3
    lchaD: i4

    """
    multidispatch changes type annotations into type checks
    methods that get ".register"-ed under the same name are treated like overloaded versions
    i keep the default version (annotated by @multidispatch itself) unimplemented to catch incorrect types
    """
    def __new__(cls, *args, **kwargs):
        """
        Allow passing a Color to Color's init, and instead of returning a new object, simply keep the old one
        This allows for some additional flexibility in complex call stacks
        """
        if len(args) >= 1 and isinstance(args[0], Color):
            return args[0]
        return object.__new__(cls)

    @multidispatch
    def __init__(self,
                 color,
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        # arguments are ignored for the unimplemented type
        _ = color, name, descLeft, descRight, mode
        raise NotImplementedError('Color cannot be specified as this type')

    @__init__.register
    def __init__(self,
                 color: Color,
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        # ignore all elements since this case is handled by __new__
        _ = color, name, descLeft, descRight, mode

    @__init__.register
    def __init__(self,
                 color: str,
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        # mode is ignored for hex values
        _ = mode
        self.name = name
        self.descLeft = descLeft
        self.descRight = descRight
        color = Literals.getOrKeep(color).lstrip('#').upper()
        if len(color) < 6:
            color = ''.join(i * 2 for i in color)
        if len(color) not in (6, 8):
            raise ValueError('Hex value of incorrect length')
        if len(color) == 8:
            self.alpha = int(color[6:8], 16) / 255
            color = color[:6]
        else:
            self.alpha = 1
        self.hex = color
        # this raises if an incorrect value was passed, so we know we have a valid RGB color
        r, g, b = (
            int(color[i * 2:(i + 1) * 2], 16) / 255
            for i in range(3)
        )
        self.rgb = (r, g, b)

    @__init__.register
    def __init__(self,
                 color: Literals,
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        self.__init__(color.value, name, descLeft, descRight, mode)

    @__init__.register
    def __init__(self,
                 color: Sequence[float],
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        self.name = name
        self.descLeft = descLeft
        self.descRight = descRight
        if len(color) < 3 or len(color) > 4:
            raise ValueError('Color sequence is of wrong length')
        if len(color) == 4:
            self.alpha = color[3]
            color = color[:3]
        else:
            self.alpha = 1
        setattr(self, mode, color)
        # always calculate RGB since it is used for conversions
        match mode:
            case 'hsv' | 'hls' | 'yiq':
                self.rgb = getattr(colorsys, mode + '_to_rgb')(*color)
            case 'lch':
                """
                Based on https://bottosson.github.io/posts/oklab/
                Some colors don't exist in RGB, so we clip their chroma

                I would like to implement https://bottosson.github.io/posts/gamutclipping/#adaptive-%2C-hue-dependent
                    because it looks better but I am too stupid
                    please make a PR if you know how to
                """
                L, C, H = color
                """
                chroma max is ~0.32, we use a normalized value for the user
                but still need the true value for conversion
                """
                C /= 3
                h = 2 * pi * H
                r, g, b = 0, 0, 0
                for _ in range(200):
                    """
                    the first iteration sets the initial RGB color
                    if it is outside the range, chroma is slightly decreased and another loop is performed
                    it will decrease chroma until a valid RGB color is produced
                    try a maximum of 200 times for performance, which should be enough for any color anyway
                    """
                    a = C * cos(h)
                    b = C * sin(h)
                    l_, m_, s_ = (
                        (L + 0.3963377774 * a + 0.2158037573 * b) ** 3,
                        (L - 0.1055613458 * a - 0.0638541728 * b) ** 3,
                        (L - 0.0894841775 * a - 1.291485548 * b) ** 3
                    )
                    # linear RGB
                    rl, gl, bl = (
                        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
                        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
                        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.707614701 * s_
                    )
                    # sRGB
                    r, g, b = (
                        1.055 * x ** (1 / 2.4) - 0.055
                        if x > 0.0031308
                        else 12.92 * x
                        for x in (rl, gl, bl)
                    )
                    if all(0 <= x <= 1 for x in (r, g, b)):
                        break
                    C -= 0.005
                # clamp just in case
                r, g, b = (
                    max(0, min(x, 1))
                    for x in (r, g, b)
                )
                self.rgb = (r, g, b)

    @__init__.register
    def __init__(self,
                 color: Sequence[int],
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        if len(color) < 3 or len(color) > 4:
            raise ValueError('Color sequence is of wrong length')
        if len(color) == 3:
            color = (*color, None)
        v1, v2, v3, v4 = color
        match mode:
            case 'rgb' | 'yiq':
                color = (v1 / 255, v2 / 255, v3 / 255)
            case 'hsv':
                color = (v1 / 179, v2 / 255, v3 / 255)
            case 'hls':
                color = (v1 / 360, v2 / 100, v3 / 100)
            case 'lch':
                color = (v1 / 100, v2 / 100, v3 / 360)
        # if alpha was passed, normalize it
        if v4 is not None:
            color = (*color, v4 / 255)
        # pass it along to the normalized init
        self.__init__(color, name, descLeft, descRight, mode)

    @multidispatch
    def __eq__(self, other) -> bool:
        return NotImplemented

    @__eq__.register
    def __eq__(self, other: Color) -> bool:
        return self.rgba == other.rgba

    @__eq__.register
    def __eq__(self, other: str) -> bool:
        try:
            return Color(other).rgba == self.rgba
        except ValueError:
            return False

    @__eq__.register
    def __eq__(self, other: Literals) -> bool:
        return other == Literals(self.hex)

    @__eq__.register
    def __eq__(self, other: tuple[float, float, float, float]) -> bool:
        return other == self.rgba

    @__eq__.register
    def __eq__(self, other: tuple[float, float, float]) -> bool:
        return self.alpha == 1. and other == self.rgb

    @__eq__.register
    def __eq__(self, other: tuple[int, int, int, int]) -> bool:
        return other == self.rgbaD

    @__eq__.register
    def __eq__(self, other: tuple[int, int, int]) -> bool:
        return self.alpha == 1. and other == self.rgbD

    def __getattribute__(self, item) -> Any:
        """
        python attribute magic
        this gets called to return a class attribute
        i capture it to calculate values on demand
        """
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            """
            not cached, calculate and store
            rgb and alpha don't get loaded lazily since we ensure they're always available
            """
            match item:
                case 'rgba' | 'hsva' | 'hlsa' | 'yiqa' | 'lcha' | 'rgbaD' | 'hsvaD' | 'hlsaD' | 'yiqaD' | 'lchaD':
                    """
                    some suffix magic to handle all cases with alpha simultaneously
                    we get the value of attribute without alpha and merge it with alpha
                    """
                    base = item.removesuffix('D').removesuffix('a')
                    suffix = 'D' if 'D' in item else ''
                    setattr(self, item, (*getattr(self, base + suffix), getattr(self, 'alpha' + suffix)))
                case 'rgbD' | 'hsvD' | 'hlsD' | 'yiqD' | 'lchD':
                    v1, v2, v3 = getattr(self, item.removesuffix('D'))
                    # denormalization table
                    mult = (255, 255, 255)
                    match item:
                        case 'hsvD':
                            mult = (179, 255, 255)
                        case 'hlsD':
                            mult = (360, 100, 100)
                        case 'lchD':
                            mult = (100, 100, 360)
                    setattr(self, item, (round(v1 * mult[0]), round(v2 * mult[1]), round(v3 * mult[2])))
                case 'hsv' | 'hls' | 'yiq':
                    setattr(self, item, getattr(colorsys, 'rgb_to_' + item)(*self.rgb))
                case 'lch':
                    # linear rgb
                    r, g, b = (
                        ((x + 0.055) / 1.055) ** 2.4
                        if x > 0.0404482362771082
                        else x / 12.92
                        for x in self.rgb
                    )
                    l_, m_, s_ = (
                        x ** (1 / 3)
                        for x in (
                            0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
                            0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
                            0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
                        )
                    )
                    a = 1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_
                    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_
                    L, C, H = (
                        0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_,
                        (a ** 2 + b ** 2) ** 0.5,
                        degrees(atan2(b, a)) % 360 / 360
                    )
                    self.lch = (L, C * 3, H)  # normalize for the user
                case 'hex':
                    self.hex = '%02X%02X%02X' % self.rgbD
                case 'hexa':
                    self.hexa = self.hex + '%02X' % self.alphaD
                case 'alphaD':
                    self.alphaD = round(self.alpha * 255)
                case 'dark':
                    # lch is perception-based - so lightness also matches perception
                    # 0.483 is a magic number
                    self.dark = self.lch[0] <= 0.483
                case _:
                    raise LazyloadError(item)
            return object.__getattribute__(self, item)

    def dict(self) -> list:
        """
        :return:  A lossless list of parameters
        """
        if self.alpha == 0:
            return ['#0000']
        else:
            col = '(' + ', '.join(f'{round(y, 4)}' for y in self.lcha) + ')'
            return [x for x in [col, self.name, self.descLeft, self.descRight, 'lch'] if x]

    def serializeText(self) -> str:
        """
        :return: A base64-encoded representation of the text values
        """
        return str(b64encode(bytes(f'{self.name}\0{self.descLeft}\0{self.descRight}', 'utf-8')), 'latin1')

    def deserializeText(self, text: str) -> Color:
        """
        :param text: The serialized text to decode into name, descLeft and descRight
        :return: self for chaining
        """
        self.name, self.descLeft, self.descRight = str(b64decode(bytes(text, 'latin1')), 'utf-8').split('\0')
        return self
