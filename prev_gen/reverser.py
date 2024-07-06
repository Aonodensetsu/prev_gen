from __future__ import annotations

from xml.etree import ElementTree
from PIL import Image

from .types import config_format
from .settings import Settings
from .config import Config
from .color import Color
from .palette import u2


def _save(ret, save):
    if save is not None:
        Config(ret, output=save).write(f'reverse.{save}')


class Reverser:
    """
    Wrapper for formats, simply returns the appropriate reverser based on chosen mode
    """
    def __new__(cls,
                val: type(ElementTree) | Image | str,
                output: config_format | None = None
                ) -> u2:
        if 'xml.etree.ElementTree.ElementTree' in str(type(val)):
            r = SVGReverser
        elif 'PIL.Image.Image' in str(type(val)):
            r = PNGReverser
        elif 'str' in str(type(val)):
            if '.png' in val:
                r = PNGReverser
            elif '.svg' in val:
                r = SVGReverser
            else:
                raise ValueError('Invalid file type to reverse')
        else:
            raise ValueError('Invalid value type to reverse')
        return r(val, output)


class PNGReverser:
    @staticmethod
    def _calc_grid(image_c, image_size, ch_loc):
        grid_size = [0, 0]
        # x then y, combined for brevity
        for i in range(2):
            previous = image_c.getpixel((0, 0))
            for j in range(0, image_size[i]):
                c = image_c.getpixel((0, j) if i else (j, 0))  # here we choose y or x
                if previous != c:
                    ch_loc[i] -= 1
                    if ch_loc[i] < 0:
                        break
                grid_size[i] += 1
                previous = c
        return grid_size

    @staticmethod
    def _calc_colors(image, image_c, image_size, grid_size):
        ret = []
        index = 0
        for j in range(0, image_size[1], grid_size[1]):
            row = []
            for i in range(0, image_size[0], grid_size[0]):
                px = image_c.getpixel((i, j))
                a = Color('%02X%02X%02X' % px[:3], alpha=px[3])
                if a.alpha > 0.:
                    key = f'color{index}'
                    if key in image.text:
                        a.deserialize_text(image.text[key])
                index += 1
                row.append(a)
            ret.append(row)
        return ret

    def __new__(cls,
                image: Image | str,
                output: config_format | None = None
                ) -> u2:
        """
        Takes an image and returns the palette used to generate it
        :param image: The png image generated with this tool (or compatible)
        :returns: The palette as a Python list
        """
        if isinstance(image, str):
            image = Image.open(image)
        settings = Settings.deserialize(image.text['colorGen'])
        image_c = image.convert('RGBA')
        image_size = [image_c.width, image_c.height]
        ch_loc = [0, 1]
        grid_size = cls._calc_grid(image_c, image_size, ch_loc)
        ret = [settings, *cls._calc_colors(image, image_c, image_size, grid_size)]
        _save(ret, output)
        return ret


class SVGReverser:
    @staticmethod
    def _svg_sift(root, ns, max_x):
        vals = []
        # woo-hoo XML parsing
        for i in root.findall(f'./{ns}*'):
            # only care about marked values
            if 'use' not in i.attrib.keys():
                continue
            # we don't care about the bars and we already parsed metadata
            if i.attrib['use'] in ('meta', 'bar'):
                continue
            # we need the max width to calculate how many tiles horizontally
            if (v := float(i.attrib['x'])) > max_x:
                max_x = v
            vals.append(i)
        return vals

    @staticmethod
    def _val_extract(vals):
        ret = []
        # as long as we have values
        while vals:
            # we get the values until another 'bg'
            cur_val = vals.pop(0)
            while vals and vals[0].attrib['use'] != 'bg':
                cur_val.append(vals.pop(0))
            # we get the text values we need
            col = (
                list(x.text for x in cur_val if x.attrib['use'] == 'hex')[0]
                if any(x.attrib['use'] == 'hex' for x in cur_val)
                else Color('000000', alpha=0.)
            )
            name = (
                list(x.text or '' for x in cur_val if x.attrib['use'] == 'name')[0]
                if any(x.attrib['use'] == 'name' for x in cur_val)
                else ''
            )
            desc_left = (
                list(x.text or '' for x in cur_val if x.attrib['use'] == 'desc_left')[0]
                if any(x.attrib['use'] == 'desc_left' for x in cur_val)
                else ''
            )
            desc_right = (
                list(x.text or '' for x in cur_val if x.attrib['use'] == 'desc_right')[0]
                if any(x.attrib['use'] == 'desc_right' for x in cur_val)
                else ''
            )
            # and remake the color
            ret.append(Color(col, name, desc_left, desc_right))
        return ret

    def __new__(cls,
                tree: ElementTree | str,
                output: config_format | None = None
                ) -> u2:
        """
        This is probably not compatible ith many other generators
        As it uses the non-standard keyword "use" to determine element purpose
        :param tree: The xml.etree.ElementTree or filename to load
        """
        if isinstance(tree, str):
            tree = ElementTree.parse(tree)
        root = tree.getroot()
        ns = root.tag.removesuffix('svg')
        # get the svg element <text use='meta'> which is set by the generator
        settings = Settings.deserialize(list(
            i for i in root.findall(f'./{ns}text') if 'use' in i.attrib and i.attrib['use'] == 'meta')[0].text)
        max_x = -1
        # woo-hoo XML parsing
        vals = cls._svg_sift(root, ns, max_x)
        ret = cls._val_extract(vals)
        # make the result a 2d list and include settings
        n = int(max_x / settings.grid_width) + 1
        ret = [settings] + [ret[i:i + n] for i in range(0, len(ret), n)]
        _save(ret, output)
        return ret
