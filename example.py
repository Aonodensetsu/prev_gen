"""
the instruction is now available in Markdown format in WIKI.md

the example below is Gruvbox, a really nice color scheme which inspired this project
"""
from prev_gen import PreviewSVG, Settings, Color
palette = [
    Settings(fileName='gruvbox'),
    [
        Color('282828', 'bg',     '235', '0'),
        Color('CC241D', 'red',    '124', '1'),
        Color('98971A', 'green',  '106', '2'),
        Color('D79921', 'yellow', '172', '3'),
        Color('458588', 'blue',   '66',  '4'),
        Color('B16286', 'purple', '132', '5'),
        Color('689D6A', 'aqua',   '72',  '6'),
        Color('A89984', 'gray',   '246', '7'),
    ],
    [
        Color('928374', 'gray',   '245', '8'),
        Color('FB4934', 'red',    '167', '9'),
        Color('B8BB26', 'green',  '142', '10'),
        Color('FABD2F', 'yellow', '214', '11'),
        Color('83A598', 'blue',   '109', '12'),
        Color('D3869B', 'purple', '175', '13'),
        Color('8EC07C', 'aqua',   '108', '14'),
        Color('EBDBB2', 'fg',     '223', '15'),
    ],
    [
        Color('1D2021', 'bg0_h',  '234', '0'),
        Color('282828', 'bg0',    '235', '0'),
        Color('3C3836', 'bg1',    '237', '-'),
        Color('504945', 'bg2',    '239', '-'),
        Color('665C54', 'bg3',    '241', '-'),
        Color('7C6f64', 'bg4',    '243', '-'),
        Color('928374', 'gray',   '245', '8'),
        Color('D65D0E', 'orange', '166', '-'),
    ],
    [
        Color('0000'),
        Color('32302F', 'bg0_s',  '236', '0'),
        Color('A89984', 'fg4',    '246', '7'),
        Color('BDAE93', 'fg3',    '248', '-'),
        Color('D5C4A1', 'fg2',    '250', '-'),
        Color('EBDBB2', 'fg1',    '223', '15'),
        Color('FBF1C7', 'fg0',    '229', '-'),
        Color('FE8019', 'orange', '208', '-'),
    ],
]

if __name__ == '__main__':
    PreviewSVG(palette, save=False, show=True)
