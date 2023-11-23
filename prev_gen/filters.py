from __future__ import annotations

from typing import Iterable
from tqdm import tqdm
from PIL import Image

from .color import Color


class Filters:
    """
    Image manipulation functions
    """
    img: Image

    def __init__(self, image: str | Image):
        if isinstance(image, str):
            image = Image.open(image)
        self.img = image

    def iterate(self) -> Iterable[tuple[int, int]]:
        """Returns an iterator of the image that gives you the x, y coordinates"""
        l, u, r, d = self.img.getbbox()
        return tqdm(((x, y) for x in range(l, r) for y in range(u, d)), total=(r - l) * (d - u), leave=False)

    def monochrome(self, chroma: float = 0, hue: float = 0, fileName: str | None = None) -> Image:
        for x, y in self.iterate():
            self.img.putpixel((x, y), Color((Color(self.img.getpixel((x, y))).lch[0], chroma, hue), mode='lch').rgbD)
            if fileName:
                self.img.save(fileName)
        return self.img
