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
        col = f.color
        text_col = s.text_col_fn(col).drgb
        dark_col = s.darken_fn(col).drgb
        (x, y) = f.pos
        draw.rectangle(
            ((x, y), (x + s.grid_width - 1, y + s.grid_height - 1)),
            fill=col.drgb
        )
        draw.rectangle(
            ((x, y + s.grid_height - s.bar_height - 1), (x + s.grid_width - 1, y + s.grid_height - 1)),
            fill=dark_col
        )
        if col.name:
            draw.text(
                (x + s.grid_width / 2, y + s.grid_height / 2 + s.name_offset),
                col.name,
                font=ImageFont.truetype('renogare.ttf', size=s.name_size),
                fill=text_col,
                anchor='mm'
            )
            draw.text(
                (x + s.grid_width / 2, y + s.grid_height / 2 + s.hex_offset),
                col.hex,
                font=ImageFont.truetype('renogare.ttf', size=s.hex_size),
                fill=text_col,
                anchor='mm'
            )
        else:
            draw.text(
                (x + s.grid_width / 2, y + s.grid_height / 2 + s.hex_offset_noname),
                col.hex,
                font=ImageFont.truetype('renogare.ttf', size=s.hex_size_noname),
                fill=text_col,
                anchor='mm'
            )
        if col.text_left:
            draw.text(
                (x + s.text_left_x, y + s.text_offset_top),
                col.text_left,
                font=ImageFont.truetype('renogare.ttf', size=s.text_size_top),
                fill=text_col,
                anchor='lt'
            )
        if col.text_right:
            draw.text(
                (x + s.grid_width - 1 - s.text_right_x, y + s.text_offset_top),
                col.text_right,
                font=ImageFont.truetype('renogare.ttf', size=s.text_size_top),
                fill=text_col,
                anchor='rt'
            )
    img.save('result.png')
    startfile('result.png')


if __name__ == '__main__':
    main()
