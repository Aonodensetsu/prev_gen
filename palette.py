# Palette:
#   with either option below you can always put None in the table instead of a Color to leave one field transparent
#
#   Usage 1 - "it just works" (1d list):
#     place colors in the order you want them to appear in the generated image
#     the program will make a rectangle big enough to fit them all
#     - it actually makes the biggest square *smaller than* required, then extends it horizontally until everything fits
#     - it will always make a rectangle that's close to a square in shape (in my opinion it's the most useful option)
#
#   Usage 2 - "literal mode" (2d list):
#     each inner list will be treated as a single row of colors, left-to-right
#     use this for full control over the placement of colors in the final image
#     inner lists will have their lengths automatically equalized
#     - this means that a shorter row will end with transparent spaces by default
#     - you can even leave entire rows transparent if you pass an empty list
#
# Colors:
#   in the default mode you can make a color using RGB:
#     RGB: Color((0.2, 0.4, 0.7))          <- normalized
#          Color((0., 0., 0.), 'black')    <- make sure to include the dots (type: float)
#          Color((200, 100, 235))          <- denormalized
#          Color((0, 0, 0), 'still black') <- this is the option without dots (type: int)
#
#   you can change the mode by specifying the type of color you want
#   all the modes other than RGB do not currently allow denormalized values
#     HSV: Color((0.2, 0.4, 0.7), mode='hsv')
#     HLS: Color((0.2, 0.4, 0.7), mode='hls')
#     YIQ: Color((0.2, 0.4, 0.7), mode='yiq')
#
#   you can also specify a name for a color or not
#     Color((200, 100, 235))                       <- RGB without name
#     Color((0.2, 0.4, 0.7), 'green', mode='hsv')  <- HSV with name
#
#   HEX works regardless of mode specified
#     Color('#52c7a7', 'mint', mode='yiq') <- HEX with name (mode ignored)
#
#   there is a special syntax which allows you to omit the Color keyword
#   but you need to adhere to the order of parameters that create a Color
#   (color, name, desc_left, desc_right, mode)
#     HEX: ('#000000',)                                      <- comma at the end if only one element
#          ('#ffffff', 'white')                              <- name is the second parameter
#          ('#ffffff', 'white', None, None, 'hls')           <- HEX still works regardless of mode
#     RGB: ((0., 0., 1.), 'blue')                         <- RGB is the default mode
#     HSV: ((0., 1., 1.), None, None, None, 'hsv')        <- HSV without a name or descriptions
#          ((0., 0., 0.), 'black', None, None, 'yiq') <- YIQ with a name but no comments
#
# Settings:
#   an object that controls the behavior of the program
#   you pass a Settings object as the first thing in the palette
#   - if you don't want to overwrite any settings just omit it
#   Available settings:
#     file_name: str = 'result'
#       file name to save into (no extension - will be png)
#     grid_height: int = 168
#       height of each individual color field
#     grid_width: int = 224
#       width of each individual color field
#     bar_height: int = 10
#       height of the darkened bar at the bottom of each field
#     name_offset: int = -10
#       vertical offset of the name printed within the field
#     hex_offset: int = 35
#       vertical offset of the hex value printed below name
#     hex_offset_noname: int = 0
#       vertical offset of the hex value printed if no name given
#     desc_offset_x: int = 15
#       horizontal offset for the corner descriptions
#     desc_offset_y: int = 20
#       vertical offset for the corner descriptions
#     name_size: int = 40
#       text size of the name
#     hex_size: int = 27
#       text size of the hex value printed under the name
#     hex_size_noname: int = 30
#       text size of the hex value printed if no name given
#     desc_size: int = 25
#       text size of the corner descriptions
#     darken_fn: Callable[[Color], Color] = (
#         lambda x:
#         Color((x.hsv[0], x.hsv[1] * 1.05, x.hsv[2] * 0.85), mode='hsv')
#     )
#       function to use for the darkened bar
#       don't touch this unless you know what the default value means
#     text_col_fn: Callable[[Color], Color] = (
#         lambda x:
#         Color((x.hsv[0], x.hsv[1] * 0.95, x.hsv[2] * 1.1 + (1. - x.hsv[2]) * 0.3), mode='hsv')
#         if x.isDark
#         else Color((x.hsv[0], x.hsv[1] * 0.95, x.hsv[2] * 0.6 - (1. - x.hsv[2]) * 0.2), mode='hsv')
#     )
#       function to determine text color from background color
#       don't touch this unless you know what the default value means
#
# the example below is Gruvbox, a really nice color scheme which inspired this project
# - uses the special syntax
# - literal mode (each array is one row)
# - changes the file name to gruvbox.png
from main import Color, Settings
palette = [
    Settings(file_name='gruvbox'),
    [
        ('#282828', 'bg', '235', '0'),     ('#cc241d', 'red', '124', '1'),  ('#98971a', 'green', '106', '2'),
        ('#d79921', 'yellow', '172', '3'), ('#458588', 'blue', '66', '4'),  ('#b16286', 'purple', '132', '5'),
        ('#689d6a', 'aqua', '72', '6'),    ('#a89984', 'gray', '246', '7')
    ],
    [
        ('#928374', 'gray', '245', '8'),    ('#fb4934', 'red', '167', '9'),   ('#b8bb26', 'green', '142', '10'),
        ('#fabd2f', 'yellow', '214', '11'), ('#83a598', 'blue', '109', '12'), ('#d3869b', 'purple', '175', '13'),
        ('#8ec07c', 'aqua', '108', '14'),   ('#ebdbb2', 'fg', '223', '15')
    ],
    [
        ('#1d2021', 'bg0_h', '234', '0'), ('#282828', 'bg0', '235', '0'),    ('#3c3836', 'bg1', '237', '-'),
        ('#504945', 'bg2', '239', '-'),   ('#665c54', 'bg3', '241', '-'),    ('#7c6f64', 'bg4', '243', '-'),
        ('#928374', 'gray', '245', '8'),  ('#d65d0e', 'orange', '166', '-')
    ],
    [
        None,                           ('#32302f', 'bg0_s', '236', '0'),  ('#a89984', 'fg4', '246', '7'),
        ('#bdae93', 'fg3', '248', '-'), ('#d5c4a1', 'fg2', '250', '-'),    ('#ebdbb2', 'fg1', '223', '15'),
        ('#fbf1c7', 'fg0', '229', '-'), ('#fe8019', 'orange', '208', '-')
    ]
]

# start the program
if __name__ == '__main__':
    from run import run
    run()
