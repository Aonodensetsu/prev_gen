from classes import Color

# Usage 1 - 1d list:
#   just place colors in the order you want them to appear
#   the program will make a rectangle big enough to fit them all and just dump them one by one
#   - it actually makes the biggest square *smaller than* required, then extends it horizontally until everything fits
#     meaning it will always make a rectangle that's close to a square in shape
#
# Usage 2 - 2d list:
#  each inner list is a single row, you can treat those lists the same as above (left-to-right)
#  it works pretty much exactly the same as above if you don't take this change into account
#  just make sure all rows are the same length because there is no error checking (oops) - TODO i guess?
#
# you can always place a None in the table to leave one entry transparent
# - use it to tab out the rows to the same length if you need to
#
# the example below is Gruvbox, a really nice color scheme which inspired this project
#
# to make a color you can pass in either RGB: (200, 100, 235), HSV: (0.2, 0.4, 0.7) or HEX: '#52c7a7'
# you can also specify a name for a color or not
# ex:
# without name:
#   Color((200, 100, 235))           <- RGB
#   Color((0.2, 0.4, 0.7))           <- HSV
#   Color('#52c7a7')                 <- HEX
# with name:
#   Color((200, 100, 235), 'purple') <- RGB
#   Color((0.2, 0.4, 0.7), 'green')  <- HSV
#   Color('#52c7a7',       'mint')   <- HEX
palette = [
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
