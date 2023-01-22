from palette import *
from classes import *
from os import startfile
from PIL import Image, ImageDraw, ImageFont


def main():
    t = Table(palette)
    s = t.settings
    img = Image.new('RGBA', t.size())
    draw = ImageDraw.Draw(img)
    for f in t.fields():
        text_col = s.text_col_fn(f.color).drgb
        (x, y) = f.pos
        draw.rectangle(
            ((x, y), (x + s.grid_width - 1, y + s.grid_height - 1)),
            fill=f.color.drgb
        )
        draw.rectangle(
            ((x, y + s.grid_height - s.bar_height - 1), (x + s.grid_width - 1, y + s.grid_height - 1)),
            fill=s.darken_fn(f.color).drgb
        )
        if f.color.name:
            draw.text(
                (x + s.grid_width / 2, y + s.grid_height / 2 + s.name_offset),
                f.color.name,
                font=ImageFont.truetype('renogare.ttf', size=s.name_size),
                fill=text_col,
                anchor='mm'
            )
            draw.text(
                (x + s.grid_width / 2, y + s.grid_height / 2 + s.hex_offset),
                f.color.hex,
                font=ImageFont.truetype('renogare.ttf', size=s.hex_size),
                fill=text_col,
                anchor='mm'
            )
        else:
            draw.text(
                (x + s.grid_width / 2, y + s.grid_height / 2 + s.hex_offset_noname),
                f.color.hex,
                font=ImageFont.truetype('renogare.ttf', size=s.hex_size_noname),
                fill=text_col,
                anchor='mm'
            )
    img.save('result.png')
    startfile('result.png')


if __name__ == '__main__':
    main()
