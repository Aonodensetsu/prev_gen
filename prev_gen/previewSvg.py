from drawsvg import Drawing, DrawingElement, Rectangle, Text
from urllib.error import HTTPError
from xml.etree import ElementTree
from webbrowser import open
from time import sleep
from os import remove

from .settings import Settings
from .table import u1, u2, Table


class SVGMeta(DrawingElement):
    """
    For whatever reason custom elements get written twice
    Keep track of this to return nothing the second time
    """
    written = False

    def __init__(self, s: Settings):
        super().__init__()
        self.genS = s

    def write_svg_element(self, id_map, is_duplicate, output_file, lcontext, dry_run, force_dup=False):
        if not self.written:
            output_file.write(f'<text use="meta" display="none">{self.genS.serialize()}</text>')
            self.written = True


class PreviewSVG:
    def __new__(cls,
                palette: u1 | u2,
                show: bool = True,
                save: bool = False
                ) -> ElementTree:
        """
        :param palette: The palette of colors to generate an image for
        :param show:    Whether to display the generated image
        :param save:    Whether to save the generated palette
        :returns:       (drawsvg.Drawing) The created image
        """
        t = Table(palette)
        s = t.settings
        draw = Drawing(*t.size, origin=(0, 0), id_prefix='prevgen')
        draw.append(SVGMeta(s))
        fontOpts = s.fontOpts or {'wght': 700}
        if 'wght' in fontOpts:
            draw.append_css(f'text{{font-family:{s.fontName},Calibri,sans-serif;font-weight:{fontOpts["wght"]};}}')
        else:
            draw.append_css(f'text{{font-family:{s.fontName},Calibri,sans-serif;}}')
        # embed google font in svg for correct previews
        try:
            draw.embed_google_font(s.fontName, **fontOpts)
        except HTTPError:
            print(f'\033[31;1mError: \'{s.fontName}\' with opts \'{fontOpts}\' is not available in Google Fonts')
            exit(1)
        for i in t:
            l, t = i.pos
            w, h = i.size
            col = i.col
            bCol = s.barFn(col)
            tCol = s.textFn(col)
            bgCol = f'oklch({col.lch[0]} {col.lch[1] / 3} {col.lchD[2]})'
            barCol = f'oklch({bCol.lch[0]} {bCol.lch[1] / 3} {bCol.lchD[2]})'
            textCol = f'oklch({tCol.lch[0]} {tCol.lch[1] / 3} {tCol.lchD[2]})'
            hx = col.hexa if col.alpha < 1 else col.hex
            draw.append(Rectangle(
                l,
                t,
                w + 1,
                h - s.barHeight + 1,
                use='bg',
                fill=bgCol,
                fill_opacity=col.alpha,
                stroke=bgCol
            ))
            draw.append(Rectangle(
                l,
                t + h - s.barHeight + 1,
                w + 1,
                s.barHeight,
                use='bar',
                fill=barCol,
                fill_opacity=col.alpha,
                stroke=barCol
            ))
            if col.name is not None:
                draw.append(Text(
                    col.name,
                    use='name',
                    x=l + w / 2,
                    y=t + h / 2 + s.nameOffset,
                    fill=textCol,
                    fill_opacity=col.alpha,
                    center=True,
                    font_size=s.nameSize,
                    font_family=s.fontName
                ))
                draw.append(Text(
                    hx,
                    use='hex',
                    x=l + w / 2,
                    y=t + h / 2 + s.hexOffset,
                    fill=textCol,
                    fill_opacity=col.alpha,
                    center=True,
                    font_size=s.hexSize,
                    font_family=s.fontName
                ))
            else:
                draw.append(Text(
                    hx,
                    use='hex',
                    x=l + w / 2,
                    y=t + h / 2 + s.hexOffsetNameless,
                    fill=textCol,
                    fill_opacity=col.alpha,
                    center=True,
                    font_size=s.hexSizeNameless,
                    font_family=s.fontName
                ))
            if col.descLeft is not None:
                draw.append(Text(
                    col.descLeft,
                    use='descLeft',
                    x=l + s.descOffsetX,
                    y=t + s.descSize / 2 + s.descOffsetY,
                    center=True,
                    text_anchor='start',
                    fill=textCol,
                    fill_opacity=col.alpha,
                    font_size=s.descSize,
                    font_family=s.fontName
                ))
            if col.descRight is not None:
                draw.append(Text(
                    col.descRight,
                    use='descRight',
                    x=l + w - 1 - s.descOffsetX,
                    y=t + s.descSize / 2 + s.descOffsetY,
                    center=True,
                    text_anchor='end',
                    fill=textCol,
                    fill_opacity=col.alpha,
                    font_size=s.descSize,
                    font_family=s.fontName
                ))
        fn = s.fileName + '.svg' if save else 'randomFileNameThatShouldNotExistOnYourSystemYet.svg'
        draw.save_svg(fn)
        tree = ElementTree.parse(fn)
        if show:
            # a hacky system-agnostic way to try to open the image
            # unlike what the name suggests, it will try to use native apps as well
            open(fn)
        # had to save temporarily to display in browser, remove if user did not intend to keep the file
        if not save:
            sleep(2)
            remove(fn)
        return tree
