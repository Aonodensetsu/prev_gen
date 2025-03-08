from inspect import currentframe, getabsfile
from urllib.error import HTTPError
from xml.etree import ElementTree
from webbrowser import open
from os.path import dirname
from time import sleep
from os import remove

from drawsvg import Drawing, DrawingElement, Rectangle, Text
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

from .palette import Palette, u1, u2
from .types import image_format
from .distance import Distance
from .settings import Settings
from .color import Color


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


class Previewer:
    """
    Wrapper for formats, simply returns the appropriate previewer based on chosen mode
    """
    def __new__(cls, palette: u1 | u2, show: bool = True, save: bool = False, output: image_format = 'png'):
        try:
            return {'png': PNGPreviewer, 'svg': SVGPreviewer}[output](palette, show, save)
        except KeyError:
            raise ValueError(f'Invalid previewer mode: <{output}>')


class PNGPreviewer:
    @classmethod
    def _get_font(cls, s: Settings) -> str:
        if s.font_name == 'Nunito':
            font = dirname(getabsfile(currentframe())) + '/nunito.ttf'
        else:
            font = s.font_name + '.ttf'
        return font

    @classmethod
    def _get_hex_word(cls, col: Color, s: Settings) -> str:
        hx = col.hexadecimal
        if col.alpha < 1:
            hx += f'{col.alpha:2X}'
        if not s.show_hash:
            hx = hx[1:]
        if s.hex_upper:
            hx = hx.upper()
        return hx

    @classmethod
    def _draw_bg(cls, draw: ImageDraw.Draw, pos: Distance, size: Distance, col: Color, s: Settings):
        l, p = pos
        w, h = size
        bg_col = tuple([int(x * 255) for x in col.srgb] + [int(col.alpha * 255)])
        bar_col = tuple([int(x * 255) for x in bar_color(col).srgb] + [int(col.alpha * 255)])
        draw.rectangle(
            (
                (l, p),
                (l + w, p + h - s.bar_height - 1)
            ),
            fill=bg_col
        )
        draw.rectangle(
            (
                (l, p + h - s.bar_height),
                (l + w, p + h)
            ),
            fill=bar_col
        )

    @classmethod
    def _draw_text_name(cls, draw: ImageDraw.Draw, pos: Distance, size: Distance, col: Color, s: Settings):
        l, p = pos
        w, h = size
        font = cls._get_font(s)
        hx = cls._get_hex_word(col, s)
        text_col = tuple([int(x * 255) for x in text_color(col).srgb] + [int(col.alpha * 255)])
        if col.name:
            draw.text(
                (l + w / 2, p + h / 2 + s.name_offset),
                col.name,
                font=ImageFont.truetype(font, size=s.name_size),
                fill=text_col,
                anchor='mm'
            )
            draw.text(
                (l + w / 2, p + h / 2 + s.hex_offset),
                hx,
                font=ImageFont.truetype(font, size=s.hex_size),
                fill=text_col,
                anchor='mm'
            )
        else:
            draw.text(
                (l + w / 2, p + h / 2 + s.hex_offset_nameless),
                hx,
                font=ImageFont.truetype(font, size=s.hex_size_nameless),
                fill=text_col,
                anchor='mm'
            )

    @classmethod
    def _draw_text_desc(cls, draw: ImageDraw.Draw, pos: Distance, size: Distance, col: Color, s: Settings):
        l, p = pos
        w, _ = size
        font = cls._get_font(s)
        text_col = tuple([int(x * 255) for x in text_color(col).srgb] + [int(col.alpha * 255)])
        if col.desc_left:
            draw.text(
                (l + s.desc_offset_x, p + s.desc_offset_y),
                col.desc_left,
                font=ImageFont.truetype(font, size=s.desc_size),
                fill=text_col,
                anchor='lt'
            )
        if col.desc_right:
            draw.text(
                (l + w - 1 - s.desc_offset_x, p + s.desc_offset_y),
                col.desc_right,
                font=ImageFont.truetype(font, size=s.desc_size),
                fill=text_col,
                anchor='rt'
            )

    def __new__(cls, palette: u1 | u2, show: bool = True, save: bool = False) -> Image.Image:
        """
        :param palette: The palette of colors to generate an image for
        :param show:    Whether to display the generated image
        :param save:    Whether to save the generated palette
        :returns:       (PIL.Image) The created image
        """
        p = Palette(palette)
        s = p.settings
        img = Image.new('RGBA', tuple[int, int](p.size))
        draw = ImageDraw.Draw(img, 'RGBA')
        img.text = {'colorGen': s.serialize()}
        for i, v in enumerate(p):
            if v.col.alpha < 0.005:
                continue
            if v.col.name or v.col.desc_left or v.col.desc_right:
                img.text[f'color{i}'] = v.col.serialize_text()
            cls._draw_bg(draw, v.pos, v.size, v.col, s)
            cls._draw_text_name(draw, v.pos, v.size, v.col, s)
            cls._draw_text_desc(draw, v.pos, v.size, v.col, s)
        # despite setting the text dict, we need to explicitly write it as a PngInfo
        meta = PngInfo()
        for k, v in img.text.items():
            meta.add_text(k, v)
        if save:
            img.save(s.file_name + '.png', pnginfo=meta)
        if show:
            if not save:
                img.show()
            else:
                open(s.file_name + '.png')
        return img


class SVGMeta(DrawingElement):
    """
    For whatever reason custom elements get written twice
    Keep track of this to return nothing the second time
    """
    written = False

    def __init__(self, s: Settings):
        super().__init__()
        self.gen_s = s

    def write_svg_element(self, id_map, is_duplicate, output_file, lcontext, dry_run, force_dup: bool = False):
        if not self.written:
            output_file.write(f'<text use="meta" display="none">{self.gen_s.serialize()}</text>')
            self.written = True


class SVGPreviewer:
    @classmethod
    def _get_hex_word(cls, col: Color, s: Settings) -> str:
        hx = col.hexadecimal
        if col.alpha < 1:
            hx += f'{col.alpha:2X}'
        if not s.show_hash:
            hx = hx[1:]
        if s.hex_upper:
            hx = hx.upper()
        return hx

    @classmethod
    def _draw_bg(cls, draw: Drawing, pos: Distance, size: Distance, col: Color, s: Settings):
        l, p = pos
        w, h = size
        b_col = bar_color(col)
        draw.append(Rectangle(
            l,
            p,
            w + 1,
            h - s.bar_height + 1,
            use='bg',
            fill=col.hexadecimal,
            fill_opacity=col.alpha,
            stroke=col.hexadecimal
        ))
        draw.append(Rectangle(
            l,
            p + h - s.bar_height + 1,
            w + 1,
            s.bar_height,
            use='bar',
            fill=b_col.hexadecimal,
            fill_opacity=col.alpha,
            stroke=b_col.hexadecimal
        ))

    @classmethod
    def _draw_text_name(cls, draw: Drawing, pos: Distance, size: Distance, col: Color, s: Settings):
        l, p = pos
        w, h = size
        t_col = text_color(col)
        hx = cls._get_hex_word(col, s)
        if col.name is not None:
            draw.append(Text(
                col.name,
                use='name',
                x=l + w / 2,
                y=p + h / 2 + s.name_offset,
                fill=t_col.hexadecimal,
                fill_opacity=col.alpha,
                center=True,
                font_size=s.name_size,
                font_family=s.font_name
            ))
            draw.append(Text(
                hx,
                use='hex',
                x=l + w / 2,
                y=p + h / 2 + s.hex_offset,
                fill=t_col.hexadecimal,
                fill_opacity=col.alpha,
                center=True,
                font_size=s.hex_size,
                font_family=s.font_name
            ))
        else:
            draw.append(Text(
                hx,
                use='col',
                x=l + w / 2,
                y=p + h / 2 + s.hex_offset_nameless,
                fill=t_col.hexadecimal,
                fill_opacity=col.alpha,
                center=True,
                font_size=s.hex_size_nameless,
                font_family=s.font_name
            ))

    @classmethod
    def _draw_text_desc(cls, draw: Drawing, pos: Distance, size: Distance, col: Color, s: Settings):
        l, p = pos
        w, _ = size
        t_col = text_color(col)
        if col.desc_left is not None:
            draw.append(Text(
                col.desc_left,
                use='desc_left',
                x=l + s.desc_offset_x,
                y=p + s.desc_size / 2 + s.desc_offset_y,
                center=True,
                text_anchor='start',
                fill=t_col.hexadecimal,
                fill_opacity=col.alpha,
                font_size=s.desc_size,
                font_family=s.font_name
            ))
        if col.desc_right is not None:
            draw.append(Text(
                col.desc_right,
                use='desc_right',
                x=l + w - 1 - s.desc_offset_x,
                y=p + s.desc_size / 2 + s.desc_offset_y,
                center=True,
                text_anchor='end',
                fill=t_col.hexadecimal,
                fill_opacity=col.alpha,
                font_size=s.desc_size,
                font_family=s.font_name
            ))

    def __new__(cls, palette: u1 | u2, show: bool = True, save: bool = False) -> ElementTree.ElementTree:
        """
        :param palette: The palette of colors to generate an image for
        :param show:    Whether to display the generated image
        :param save:    Whether to save the generated palette
        :returns:       (drawsvg.Drawing) The created image
        """
        p = Palette(palette)
        s = p.settings
        draw = Drawing(*p.size, origin=(0, 0), id_prefix='prevgen')
        draw.append(SVGMeta(s))
        font_opts = s.font_opts or {'wght': 700}
        if 'wght' in font_opts:
            draw.append_css(f'text{{font-family:{s.font_name},Calibri,sans-serif;font-weight:{font_opts["wght"]};}}')
        else:
            draw.append_css(f'text{{font-family:{s.font_name},Calibri,sans-serif;}}')
        # embed google font in svg for correct previews
        try:
            draw.embed_google_font(s.font_name, **font_opts)
        except HTTPError:
            raise ValueError(
                f'\033[31;1mError: \'{s.font_name}\' with opts \'{font_opts}\' is not available in Google Fonts'
            )
        for i in p:
            w, h = i.size
            if i.col.alpha < 0.005:
                draw.append(Rectangle(
                    *i.pos,
                    w + 1,
                    h - s.bar_height + 1,
                    use='bg',
                    fill_opacity=i.col.alpha
                ))
                continue
            cls._draw_bg(draw, i.pos, i.size, i.col, s)
            cls._draw_text_name(draw, i.pos, i.size, i.col, s)
            cls._draw_text_desc(draw, i.pos, i.size, i.col, s)
        fn = s.file_name + '.svg' if save else 'randomFileNameThatShouldNotExistOnYourSystemYet.svg'
        draw.save_svg(fn)
        tree = ElementTree.parse(fn)
        if show:
            """
            a hacky system-agnostic way to try to open the image
            unlike what the library name suggests, it will try to use native apps as well
            """
            open(fn)
        # had to save temporarily to display in browser, remove if user did not intend to keep the file
        if not save:
            sleep(2)
            remove(fn)
        return tree
