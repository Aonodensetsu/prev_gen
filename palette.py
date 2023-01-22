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
#     inner lists will have their lengths automatically equalized with None
#     - this means that a shorter row will end with transparent spaces by default
#     - you can even leave entire rows transparent if you pass an empty inner list
#
# Colors:
#   in the default mode you can make a color using HEX or RGB:
#     HEX: Color('#52c7a7')
#     RGB: Color((0.2, 0.4, 0.7))          <- normalized
#          Color((0., 0., 0.), 'black')    <- make sure to include the dots (type: float)
#          Color((200, 100, 235))          <- denormalized
#          Color((0, 0, 0), 'still black') <- this is the option without dots (type: int)
#
#   the default mode has a "special" mode
#   which enables you to not write Color(...) every single time
#   you can use it whenever the color you create does not take keyword arguments (which implies default mode)
#   - which means it only works with HEX and RGB
#   simply omit the name of the class
#     HEX: ('#52c7a7',)              <- notice the comma at the end (type: tuple)
#     RGB: ((0.2, 0.4, 0.7),)        <- double parentheses and a comma
#          ((200, 100, 235), 'name') <- names work too
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
# Settings:
#   an object that controls the behavior of the program
#   you pass a Settings object as the first thing in the palette
#   - if you don't want to overwrite any settings just omit it
#   Available settings:
#     grid_height: int = 168
#       height of each individual color field
#     grid_width: int = 224
#       width of each individual color field
#     bar_height: int = 10
#       height of the darkened bar at the bottom of each field
#     name_offset: int = -20
#       vertical offset of the name printed within the field
#     hex_offset: int = 25
#       vertical offset of the hex value printed below name
#     hex_offset_noname: int = 0
#       vertical offset of the hex value printed if no name given
#     name_size: int = 40
#       text size of the name
#     hex_size: int = 27
#       text size of the hex value printed under the name
#     hex_size_noname: int = 30
#       text size of the hex value printed if no name given
#     darken_fn: Callable[[Color], Color] = (default omitted, you really shouldn't touch this)
#       function to use for the darkened bar
#     text_col_fn: Callable[[Color], Color] = (default omitted, you really shouldn't touch this)
#       function to determine text color from background color
#
# the example below is Gruvbox, a really nice color scheme which inspired this project
# - uses the special default mode with HEX
# - literal mode (each array is one row)
palette = [
    [
        ('#282828', 'bg'),   ('#cc241d', 'red'),    ('#98971a', 'green'), ('#d79921', 'yellow'),
        ('#458588', 'blue'), ('#b16286', 'purple'), ('#689d6a', 'aqua'),  ('#a89984', 'gray')
    ],
    [
        ('#928374', 'gray'), ('#fb4934', 'red'),    ('#b8bb26', 'green'), ('#fabd2f', 'yellow'),
        ('#83a598', 'blue'), ('#d3869b', 'purple'), ('#8ec07c', 'aqua'),  ('#ebdbb2', 'fg')
    ],
    [
        ('#1d2021', 'bg0_h'), ('#282828', 'bg0'), ('#3c3836', 'bg1'),  ('#504945', 'bg2'),
        ('#665c54', 'bg3'),   ('#7c6f64', 'bg4'), ('#928374', 'gray'), ('#d65d0e', 'orange')
    ],
    [
        None,               ('#32302f', 'bg0_s'), ('#a89984', 'fg4'), ('#bdae93', 'fg3'),
        ('#d5c4a1', 'fg2'), ('#ebdbb2', 'fg1'),   ('#fbf1c7', 'fg0'), ('#fe8019', 'orange')
    ]
]
