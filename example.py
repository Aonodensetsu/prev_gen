# the instruction is now available in Markdown format in WIKI.md
#
# the example below is Gruvbox, a really nice color scheme which inspired this project
# Color is imported under the name "C" to avoid repeating "Color" this many times
from prev_gen import Preview, Settings, Color as C
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
        None,                                C('#32302f', 'bg0_s',  '236', '0'),  C('#a89984', 'fg4',    '246', '7'),
        C('#bdae93', 'fg3',    '248', '-'),  C('#d5c4a1', 'fg2',    '250', '-'),  C('#ebdbb2', 'fg1',    '223', '15'),
        C('#fbf1c7', 'fg0',    '229', '-'),  C('#fe8019', 'orange', '208', '-')
    ]
]

# start the program
if __name__ == '__main__':
    Preview(palette, save=True, show=True)
