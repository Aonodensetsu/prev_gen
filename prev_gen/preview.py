from inspect import currentframe, getabsfile
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
from webbrowser import open
from os.path import dirname

from .table import u1, u2, Table


class Preview:
    def __new__(cls,
                palette: u1 | u2,
                show: bool = True,
                save: bool = False
                ) -> Image:
        """
        :param palette: The palette of colors to generate an image for
        :param show:    Whether to display the generated image
        :param save:    Whether to save the generated palette
        :returns:       (PIL.Image) The created image
        """
        t = Table(palette)
        s = t.settings
        img = Image.new('RGBA', tuple(t.size))
        draw = ImageDraw.Draw(img, 'RGBA')
        if s.fontName == 'Nunito':
            font = dirname(getabsfile(currentframe())) + '/nunito.ttf'
        else:
            font = s.fontName + '.ttf'
        # the text dict is only created when reading from a file, create it ourselves
        img.text = {'colorGen': s.serialize()}
        for i, v in enumerate(t):
            l, t = v.pos
            w, h = v.size
            col = v.col
            if col.name or col.descLeft or col.descRight:
                img.text[f'color{i}'] = col.serializeText()
            bgCol = col.rgbaD
            barCol = s.barFn(col).rgbaD
            textCol = s.textFn(col).rgbaD
            hx = col.hexa if col.alpha < 1 else col.hex
            if s.showHash:
                hx = '#' + hx
            draw.rectangle(
                (
                    (l, t),
                    (l + w, t + h - s.barHeight - 1)
                ),
                fill=bgCol
            )
            draw.rectangle(
                (
                    (l, t + h - s.barHeight),
                    (l + w, t + h)
                ),
                fill=barCol
            )
            if col.name is not None:
                draw.text(
                    (l + w / 2, t + h / 2 + s.nameOffset),
                    col.name,
                    font=ImageFont.truetype(font, size=s.nameSize),
                    fill=textCol,
                    anchor='mm'
                )
                draw.text(
                    (l + w / 2, t + h / 2 + s.hexOffset),
                    hx,
                    font=ImageFont.truetype(font, size=s.hexSize),
                    fill=textCol,
                    anchor='mm'
                )
            else:
                draw.text(
                    (l + w / 2, t + h / 2 + s.hexOffsetNameless),
                    hx,
                    font=ImageFont.truetype(font, size=s.hexSizeNameless),
                    fill=textCol,
                    anchor='mm'
                )
            if col.descLeft is not None:
                draw.text(
                    (l + s.descOffsetX, t + s.descOffsetY),
                    col.descLeft,
                    font=ImageFont.truetype(font, size=s.descSize),
                    fill=textCol,
                    anchor='lt'
                )
            if col.descRight is not None:
                draw.text(
                    (l + w - 1 - s.descOffsetX, t + s.descOffsetY),
                    col.descRight,
                    font=ImageFont.truetype(font, size=s.descSize),
                    fill=textCol,
                    anchor='rt'
                )
        # despite setting the text dict, we need to explicitly write it as a PngInfo
        meta = PngInfo()
        for k, v in img.text.items():
            meta.add_text(k, v)
        if save:
            img.save(s.fileName + '.png', pnginfo=meta)
        if show:
            if not save:
                img.show()
            else:
                """
                a hacky system-agnostic way to try to open the image
                unlike what the name suggests, it will try to use native apps as well
                """
                open(s.fileName + '.png')
        return img
