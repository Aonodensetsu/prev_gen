from palette import palette
from classes import *
from PIL import Image, ImageDraw, ImageFont


def main():
    t = Palette(palette)
    img = Image.new('RGBA', (t.width * t.gridWidth, t.height * t.gridHeight))
    imgd = ImageDraw.Draw(img)
    for i in range(t.height):
        for j in range(t.width):
            left = j * t.gridWidth
            top = i * t.gridHeight
            if t.width * i + j >= len(t.colors) and not t.literalOrder:
                break
            color = t.colors[i][j] if t.literalOrder else t.colors[t.width * i + j]
            if color:
                textcol = color.text().rgb
                imgd.rectangle(
                    ((left, top), (left + t.gridWidth - 1, top + t.gridHeight - 1)),
                    fill=color.rgb
                )
                imgd.rectangle(
                    ((left, top + t.gridHeight - 11), (left + t.gridWidth - 1, top + t.gridHeight - 1)),
                    fill=color.darker().rgb
                )
                if color.name:
                    imgd.text(
                        (left + t.gridWidth / 2, top + t.gridHeight / 2 - 5),
                        color.name,
                        font=ImageFont.truetype('renogare.ttf', size=40),
                        fill=textcol,
                        anchor='mm'
                    )
                    imgd.text(
                        (left + t.gridWidth / 2, top + t.gridHeight / 2 + 40),
                        '#%02x%02x%02x' % color.rgb,
                        font=ImageFont.truetype('renogare.ttf', size=27),
                        fill=textcol,
                        anchor='mm'
                    )
                else:
                    imgd.text(
                        (left + t.gridWidth/2, top + t.gridHeight/2),
                        '#%02x%02x%02x' % color.rgb,
                        font=ImageFont.truetype('renogare.ttf', size=30),
                        fill=textcol,
                        anchor='mm'
                    )
    img.save('result.png')
    img.show()


if __name__ == '__main__':
    main()
