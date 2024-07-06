from __future__ import annotations

from typing import ClassVar

# noinspection PyProtectedMember
from colour.graph.conversion import _build_graph
from base64 import b64decode, b64encode
from multimethod import multidispatch
from collections.abc import Sequence
from dataclasses import dataclass
from numpy.typing import NDArray
from colour import convert
from numpy import ndarray
from math import isclose

from .types import color_format


@dataclass
class Color:
    """
    Represents one color tile in the image, any descriptions it may have - and facilitates color conversions
    Attributes are calculated lazily for efficiency

    Attributes:
        name:       Color name

        desc_left:  Left corner description

        desc_right: Right corner description

        alpha:      Transparency value

        dark:       Whether the color is perceptibly dark

        original:   The mode this color was created in, conversions can cause imprecision

        srgb:       The most popular color model

        oklch:      The recommended color model, based on human perception

        <model>:    Normalized color in a specific model
                    github.com/colour-science/colour?tab=readme-ov-file#31automatic-colour-conversion-graph---colourgraph

    :param color:      The color value to assign
    :param name:       The name to display
    :param desc_left:  Left corner description
    :param desc_right: Right corner description
    :param model:      Specifies type of color created
    :param alpha:      The transparency value to assign
    """
    _conversions: ClassVar = _build_graph()
    name: str
    desc_left: str
    desc_right: str
    alpha: float
    dark: bool
    original: str
    srgb: NDArray
    oklch: NDArray

    @multidispatch
    def __init__(self,
                 color,
                 name: str = '',
                 desc_left: str = '',
                 desc_right: str = '',
                 model: color_format = 'srgb',
                 alpha: float | None = 1.
                 ) -> None:
        """
        multidispatch changes type annotations into type checks
        methods that get registered under the same name are treated like overloaded versions
        I keep the default version (annotated by @multidispatch itself) unimplemented to catch incorrect types
        """
        _ = color, name, desc_left, desc_right, model, alpha
        raise NotImplementedError('Color cannot be specified as this type')

    @__init__.register
    def __init__(self,
                 color: Color,
                 name: str = '',
                 desc_left: str = '',
                 desc_right: str = '',
                 model: color_format = 'srgb',
                 alpha: float | None = None
                 ) -> None:
        _ = model
        self.original = color.original
        setattr(self, color.original, getattr(color, color.original))
        self.rgb = color.rgb
        self.name = name or color.name
        self.desc_left = desc_left or color.desc_left
        self.desc_right = desc_right or color.desc_right
        if alpha is not None:
            self.alpha = sorted((0., alpha, 1.))[1]
        else:
            self.alpha = color.alpha

    @__init__.register
    def __init__(self,
                 color: str,
                 name: str = '',
                 desc_left: str = '',
                 desc_right: str = '',
                 model: color_format = 'srgb',
                 alpha: float | None = None,
                 ) -> None:
        _ = model
        try:
            color = convert(color, 'css color 3', 'hexadecimal')
            setattr(self, 'css color 3', color)
            self.original = 'css color 3'
        except AssertionError:
            self.original = 'hexadecimal'
        if len(color) == 3:
            color = ''.join(x * 2 for x in color)
        elif len(color) == 4:
            color = ''.join(x * 2 for x in color[:3])
            alpha = int(color[3] * 2, 16)
        elif len(color) == 8:
            color = color[:6]
            alpha = int(color[6:8], 16)
        self.hexadecimal = '#' + color.removeprefix('#').lower()
        self.rgb = convert(color, 'hexadecimal', 'rgb')
        self.alpha = sorted((0., alpha if alpha is not None else 1., 1.))[1]
        self.name = name
        self.desc_left = desc_left
        self.desc_right = desc_right

    @__init__.register
    def __init__(self,
                 color: NDArray | Sequence,
                 name: str = '',
                 desc_left: str = '',
                 desc_right: str = '',
                 model: color_format = 'srgb',
                 alpha: float | None = None
                 ) -> None:
        model = model.lower()
        self.original = model
        setattr(self, model, color)
        # catch conversion errors early by doing one conversion greedily
        # also always have RGB set because it converts well
        if model != 'rgb':
            self.rgb = convert(color, model, 'rgb')
        else:
            self.oklch = convert(color, model, 'oklch')
        self.alpha = sorted((0., alpha if alpha is not None else 1., 1.))[1]
        self.name = name
        self.desc_left = desc_left
        self.desc_right = desc_right

    def __eq__(self, other) -> bool:
        try:
            return all(isclose(x, y, rel_tol=0.01) for x, y in zip(self.srgb, Color(other).srgb))
        except ValueError:
            return False

    def __getattribute__(self, item):
        """
        this is overriden to allow loading attributes lazily
        """
        try:
            v = object.__getattribute__(self, item)
        except AttributeError:
            match item:
                case 'dark':
                    v = self.oklab[0] <= 0.483
                    self.dark = v
                case _ if item.lower() == 'rgb':
                    # this should always be calculated greedily, but might as well make sure it exists
                    v = convert(getattr(self, self.original), self.original, item)
                    setattr(self, 'rgb', v)
                case _ if item.lower() in Color._conversions:
                    v = convert(self.rgb, 'rgb', item)
                    setattr(self, item.lower(), v)
                case x:
                    raise AttributeError(f'Attribute <{x}> not found and not loaded lazily.')
        if isinstance(v, ndarray):
            return v.tolist()
        return v

    def to_dict(self) -> dict:
        """
        Converts the Color into a list of non-default parameters
        """
        if self.alpha < 0.005:
            return {'color': '0000'}
        names = ['alpha', 'name', 'desc_left', 'desc_right']
        default_cls = Color('000000')
        default = {i: getattr(default_cls, i) for i in names}
        actual = {i: getattr(self, i) for i in names}
        changed = {k: v for k, v in actual.items() if default[k] != v}
        # always store color
        changed['color'] = self.hexadecimal
        return changed

    def serialize_text(self) -> str:
        """
        :return: A base64-encoded representation of the text values
        """
        return str(b64encode(bytes(f'{self.name}\0{self.desc_left}\0{self.desc_right}', 'utf-8')), 'latin1')

    def deserialize_text(self, text: str) -> Color:
        """
        :param text: The serialized text to decode into name, desc_left and desc_right
        :return: self for chaining
        """
        self.name, self.desc_left, self.desc_right = str(b64decode(bytes(text, 'latin1')), 'utf-8').split('\0')
        return self
