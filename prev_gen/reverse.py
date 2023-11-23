from __future__ import annotations

from PIL import Image

from .color import Color
from .settings import Settings
from .table import u2


class Reverse:
    def __new__(cls,
                image: Image | str,
                changes: tuple[int, int] = (0, 1)
                ) -> u2:
        """
        Takes an image and returns the palette used to generate it
        :param image: The png image generated with this tool (or compatible)
        :param changes: The amount of color changes in the x/y-axis to ignore per tile (for the darker bar)
        :returns: The palette as a Python list
        """
        if isinstance(image, str):
            image = Image.open(image)
        settings = Settings.deserialize(image.text['colorGen'])
        imageC = image.convert('RGBA')
        imageSize = [imageC.width, imageC.height]
        gridSize = [0, 0]
        chLoc = list(changes)
        # x then y, combined for brevity
        for i in range(2):
            previous = imageC.getpixel((0, 0))
            for j in range(0, imageSize[i]):
                c = imageC.getpixel((0, j) if i else (j, 0))  # here we choose y or x
                if not previous == c:
                    chLoc[i] -= 1
                    if chLoc[i] < 0:
                        break
                gridSize[i] += 1
                previous = c
        ret = [settings]
        index = 0
        for j in range(0, imageSize[1], gridSize[1]):
            row = []
            for i in range(0, imageSize[0], gridSize[0]):
                a = Color('%02X%02X%02X%02X' % imageC.getpixel((i, j)))
                if a.alpha > 0:
                    key = f'color{index}'
                    if key in image.text:
                        a.deserializeText(image.text[key])
                    index += 1
                row.append(a)
            ret.append(row)
        return ret
