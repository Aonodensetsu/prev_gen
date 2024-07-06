from __future__ import annotations

from typing import Generator, Any, Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from tqdm import tqdm
from PIL import Image

from .color import Color


@dataclass(slots=True)
class Distance:
    """
    Absolute distance in pixels
    used for position and size when placing tiles in an image
    and for the size of the image itself

    Attributes:
        x: Horizontal offset

        y: Vertical offset
    """
    x: int
    y: int

    def __iter__(self) -> Generator[int, Any, None]:
        """
        Allows conversion to a tuple
        """
        for i in (self.x, self.y):
            yield i


@dataclass(slots=True)
class Tile:
    """
    A single tile in the table, which contains a color and its positioning
    Used as a container of data when drawing tiles

    Attributes:
        pos:  Pixel offset from (0,0) to the top left corner

        size: Pixel offset from the top left corner to the bottom right corner

        col:  Color of this field
    """
    pos: Distance
    size: Distance
    col: Color


@dataclass(slots=True)
class Filters:
    """
    Image manipulation functions
    These honestly probably shouldn't be in this library
    But I have an image processing class, so they are here either way

    Attributes:
        img: The used image, mutable
    """
    img: Image

    def __init__(self, image: str | Image) -> None:
        """
        :param image: The image to use filters for
        """
        if isinstance(image, str):
            image = Image.open(image)
        self.img = image

    def iterate(self) -> Iterable[Sequence[int]]:
        """Returns an iterator of the image that gives you the x, y coordinates"""
        l, u, r, d = self.img.getbbox()
        return tqdm(((x, y) for x in range(l, r) for y in range(u, d)), total=(r - l) * (d - u), leave=False)

    def monochrome(self, chroma: float = 0, hue: float = 0, file_name: str | None = None) -> Filters:
        """
        :param chroma: The color intensity
        :param hue: The color hue
        :param file_name: The filename to save to
        :return: Self for method chaining
        """
        for x, y in self.iterate():
            px = tuple(float(x)/255. for x in self.img.getpixel((x, y)))
            c = Color(px[:3], alpha=px[3])
            nc = Color((float(c.oklab[0]), chroma, hue), model='oklch', alpha=c.alpha)
            npx = tuple(int(x*255) for x in [*nc.RGB, nc.alpha])
            self.img.putpixel((x, y), npx)
            if file_name:
                self.img.save(file_name)
        return self


class Raises:
    """
    Catch a specific exception type and keep the result

    All other types still get raised

    :param catch: the chosen exception type(s)

    Attributes:
        raised: whether the chosen exception was raised
    """
    catch: tuple
    raised: bool

    def __init__(self, *catch):
        self.catch = catch

    def __enter__(self) -> Raises:
        self.raised = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type in self.catch:
            self.raised = True
            return True
        return False


def bar_color(c: Color) -> Color:
    return Color(
        (
            c.Oklab[0] * 0.9,
            c.Oklab[1],
            c.Oklab[2]
        ),
        model='oklab',
        alpha=c.alpha
    )


def text_color(c: Color) -> Color:
    return Color(
        (
            c.Oklab[0] * 0.9 + 0.3
            if c.dark
            else c.Oklab[0] * 0.75 - 0.15,
            c.Oklab[1],
            c.Oklab[2]
        ),
        model='oklab',
        alpha=c.alpha
    )
