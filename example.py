# the instruction is now available in Markdown format in WIKI.md
#
# the example below is Gruvbox, a really nice color scheme which inspired this project
# Color is imported under the name "Cl" to avoid writing "Color" this many times
from prev_gen import Preview, Settings, Color as Cl
palette = [
    Settings(file_name='gruvbox'),
    [
        Cl('#282828', 'bg',     '235', '0'),
        Cl('#cc241d', 'red',    '124', '1'),
        Cl('#98971a', 'green',  '106', '2'),
        Cl('#d79921', 'yellow', '172', '3'),
        Cl('#458588', 'blue',   '66',  '4'),
        Cl('#b16286', 'purple', '132', '5'),
        Cl('#689d6a', 'aqua',   '72',  '6'),
        Cl('#a89984', 'gray',   '246', '7')
    ],
    [
        Cl('#928374', 'gray',   '245', '8'),
        Cl('#fb4934', 'red',    '167', '9'),
        Cl('#b8bb26', 'green',  '142', '10'),
        Cl('#fabd2f', 'yellow', '214', '11'),
        Cl('#83a598', 'blue',   '109', '12'),
        Cl('#d3869b', 'purple', '175', '13'),
        Cl('#8ec07c', 'aqua',   '108', '14'),
        Cl('#ebdbb2', 'fg',     '223', '15')
    ],
    [
        Cl('#1d2021', 'bg0_h',  '234', '0'),
        Cl('#282828', 'bg0',    '235', '0'),
        Cl('#3c3836', 'bg1',    '237', '-'),
        Cl('#504945', 'bg2',    '239', '-'),
        Cl('#665c54', 'bg3',    '241', '-'),
        Cl('#7c6f64', 'bg4',    '243', '-'),
        Cl('#928374', 'gray',   '245', '8'),
        Cl('#d65d0e', 'orange', '166', '-')
    ],
    [
        Cl('0000'),
        Cl('#32302f', 'bg0_s',  '236', '0'),
        Cl('#a89984', 'fg4',    '246', '7'),
        Cl('#bdae93', 'fg3',    '248', '-'),
        Cl('#d5c4a1', 'fg2',    '250', '-'),
        Cl('#ebdbb2', 'fg1',    '223', '15'),
        Cl('#fbf1c7', 'fg0',    '229', '-'),
        Cl('#fe8019', 'orange', '208', '-')
    ]
]

# start the program
if __name__ == '__main__':
    Preview(palette, save=True, show=True)
