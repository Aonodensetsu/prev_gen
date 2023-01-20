from classes import *
from PIL import Image, ImageDraw, ImageFont

palette = [ #gruvbox as example
    [
        Color('#282828', 'bg'),   Color('#cc241d', 'red'),    Color('#98971a', 'green'), Color('#d79921', 'yellow'),
        Color('#458588', 'blue'), Color('#b16286', 'purple'), Color('#689d6a', 'aqua'),  Color('#a89984', 'gray')
    ],
    [
        Color('#928374', 'gray'), Color('#fb4934', 'red'),    Color('#b8bb26', 'green'), Color('#fabd2f', 'yellow'),
        Color('#83a598', 'blue'), Color('#d3869b', 'purple'), Color('#8ec07c', 'aqua'),  Color('#ebdbb2', 'fg')
    ],
    [
        Color('#1d2021', 'bg0_h'), Color('#282828', 'bg0'), Color('#3c3836', 'bg1'),  Color('#504945', 'bg2'),
        Color('#665c54', 'bg3'),   Color('#7c6f64', 'bg4'), Color('#928374', 'gray'), Color('#d65d0e', 'orange')
    ],
    [
        None,                    Color('#32302f', 'bg0_s'), Color('#a89984', 'fg4'), Color('#bdae93', 'fg3'),
        Color('#d5c4a1', 'fg2'), Color('#ebdbb2', 'fg1'),   Color('#fbf1c7', 'fg0'), Color('#fe8019', 'orange')
    ]
]


def main():
    t = Table(palette)
    img = Image.new('RGBA', (t.width * t.gridWidth, t.height * t.gridHeight))
    imgd = ImageDraw.Draw(img)
    for i in range(t.height):
        for j in range(t.width):
            left = j * t.gridWidth
            top = i * t.gridHeight
            color = t.colors[i][j] if t.literalOrder else t.colors[t.width * i + j]
            if color:
                imgd.rectangle(
                    ((left, top), (left + t.gridWidth - 1, top + t.gridHeight - 1)),
                    fill=color.color
                )
                isDark = True if sum(color.color)/3 <= 127 else False
                textCol = tuple([int(a+127) for a in color.color]) if isDark else tuple([int(a-127) for a in color.color])
                if color.name:
                    imgd.text(
                        (left + t.gridWidth / 2, top + t.gridHeight / 2),
                        color.name,
                        font=ImageFont.truetype('arial.ttf', size=30),
                        fill=textCol,
                        anchor='mm'
                    )
                    imgd.text(
                        (left + t.gridWidth / 2, top + t.gridHeight / 2 + 50),
                        '#%02x%02x%02x' % color.color,
                        font=ImageFont.truetype('arial.ttf', size=20),
                        fill=textCol,
                        anchor='mm'
                    )
                else:
                    imgd.text(
                        (left + t.gridWidth/2, top + t.gridHeight/2),
                        '#%02x%02x%02x' % color.color,
                        font=ImageFont.truetype('arial.ttf', size=30),
                        fill=textCol,
                        anchor='mm'
                    )
    img.save('result.png')
    img.show()


if __name__ == '__main__':
    main()
