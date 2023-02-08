# Palette:
#   with either option you can put "None" in the table instead of a Color to leave one field transparent
#
#   Usage 1 - "it just works" (1d list):
#     place colors in the order you want them to appear in the generated image
#     the program will make a rectangle big enough to fit them all
#     - it actually makes the biggest square *smaller than* required
#       then extends it horizontally until everything fits
#     - it will always make a rectangle that's close to a square in shape
#       in my opinion it's the most useful shape
#
#   Usage 2 - "literal mode" (2d list):
#     each inner list will be treated as a single row of colors, left-to-right
#     use this for full control over the placement of colors in the final image
#     inner lists will have their lengths automatically equalized
#     - this means that a shorter row will end with transparent spaces by default
#     - you can even leave entire rows transparent if you pass an empty list
#
# Color:
#   an object that represents a single color
#   Available parameters:
#     color: str | tuple[float, float, float] | tuple[int, int, int]
#       The color value to assign, you need to include this value
#     name: str | None = None
#       The name to display
#     desc_left: str | None = None
#       Left corner description
#     desc_right: str | None = None
#       Right corner description
#     mode: Literal['rgb', 'hsv', 'hls', 'yiq'] = 'rgb'
#       Specifies type of color to convert from
#
#   in the default mode you make a color that uses RGB:
#     RGB: Color((0., 0., 0.))     <- normalized
#          Color((1., 1., 1.))     <- make sure to include the dots (type: float)
#          Color((0, 0, 0))        <- denormalized
#          Color((255, 255, 255))  <- this is the option without dots (type: int)
#
#   you can change the mode by specifying the type of color you want
#     HSV: Color((0.2, 0.4, 0.7), mode='hsv')
#     HLS: Color((0.2, 0.4, 0.7), mode='hls')
#     YIQ: Color((0.2, 0.4, 0.7), mode='yiq')
#
#   all the modes support normalized and denormalized values
#   but make sure to look at the ranges of values if you want to use denormalized ones
#     (R: 0-255,  G: 0-255,  B: 0-255)
#     (H: 0-179,  S: 0-255,  V: 0-255)
#     (H: 0-360,  S: 0-100,  L: 0-100)
#     (Y: 0.255,  I: 0-255,  Q: 0-255)
#
#   you can also specify a name for a color or not
#     Color((200, 100, 235), 'purple')    <- RGB with name
#     Color((0.2, 0.4, 0.7), mode='hsv')  <- HSV without name
#
#   HEX works regardless of mode specified
#     Color('#52c7a7', 'mint', mode='hls')  <- HEX with name (mode ignored*)
#       *HLS values will be generated when creating the color for later use
#
# Settings:
#   an object that controls the behavior of the program
#   you pass a Settings object as the first thing in the palette
#   - if you don't want to overwrite any settings just omit it
#   Available settings:
#     file_name: str = 'result'
#       File name to save into (no extension - png)
#     font:str = None
#       Font used (no extension - true type) - if none, will use bundled
#     grid_height: int = 168
#       Height of each individual color field
#     grid_width: int = 224
#       Width of each individual color field
#     bar_height: int = 10
#       Height of the darkened bar at the bottom of each field
#     name_offset: int = -10
#       Vertical offset of the color name printed within the field
#     hex_offset: int = 35
#       Vertical offset of the hex value printed below color name
#     hex_offset_noname: int = 0
#       Vertical offset of the hex value printed if no name given
#     desc_offset_x: int = 15
#       Horizontal offset of the corner descriptions
#     desc_offset_y: int = 20
#       Vertical offset of the corner descriptions
#     name_size: int = 40
#       Text size of the color name
#     hex_size: int = 26
#       Text size of the hex value printed under the color name
#     hex_size_noname: int = 34
#       Text size of the hex value printed if no name given
#     desc_size: int = 26
#       Text size of the corner descriptions
#     bar_col_fn: Callable[[Color], Color] = (default omitted)
#       Function to determine bar color from background color
#       You probably shouldn't touch this
#     text_col_fn: Callable[[Color], Color] = (default omitted)
#       Function to determine text color from background color
#       You probably shouldn't touch this
#
# App:
#   the entrypoint that starts the program
#   it always returns the generated image, even if you choose to also save it
#   Available settings:
#     save: bool = False
#       Whether to save the image to disk
#     show: bool = False
#        Whether to display the generated image to the user
#
# the example below is Gruvbox, a really nice color scheme which inspired this project
# - changes the file name to gruvbox.png
# - usage 2: literal mode
#
from prev_gen import Color as C, Settings
palette = [
    Settings(file_name='gruvbox'),
    [
        C('#282828', 'bg',     '235', '0'),  C('#cc241d', 'red',    '124', '1'),  C('#98971a', 'green',  '106', '2'),
        C('#d79921', 'yellow', '172', '3'),  C('#458588', 'blue',   '66',  '4'),  C('#b16286', 'purple', '132', '5'),
        C('#689d6a', 'aqua',   '72',  '6'),  C('#a89984', 'gray',   '246', '7')
    ],
    [
        C('#928374', 'gray',   '245', '8'),  C('#fb4934', 'red',    '167', '9'),  C('#b8bb26', 'green',  '142', '10'),
        C('#fabd2f', 'yellow', '214', '11'), C('#83a598', 'blue',   '109', '12'), C('#d3869b', 'purple', '175', '13'),
        C('#8ec07c', 'aqua',   '108', '14'), C('#ebdbb2', 'fg',     '223', '15')
    ],
    [
        C('#1d2021', 'bg0_h',  '234', '0'),  C('#282828', 'bg0',    '235', '0'),  C('#3c3836', 'bg1',    '237', '-'),
        C('#504945', 'bg2',    '239', '-'),  C('#665c54', 'bg3',    '241', '-'),  C('#7c6f64', 'bg4',    '243', '-'),
        C('#928374', 'gray',   '245', '8'),  C('#d65d0e', 'orange', '166', '-')
    ],
    [
        None,                               C('#32302f', 'bg0_s',  '236', '0'),  C('#a89984', 'fg4',    '246', '7'),
        C('#bdae93', 'fg3',    '248', '-'),  C('#d5c4a1', 'fg2',    '250', '-'),  C('#ebdbb2', 'fg1',    '223', '15'),
        C('#fbf1c7', 'fg0',    '229', '-'),  C('#fe8019', 'orange', '208', '-')
    ]
]

# start the program
if __name__ == '__main__':
    # you can use these same two lines in your own code
    # to use this as a library
    from prev_gen import Preview
    Preview(palette, save=True, show=True)
