from argparse import ArgumentParser
from os.path import splitext

from .preview import Preview
from .previewSvg import PreviewSVG
from .reverse import Reverse
from .reverseSvg import ReverseSVG
from .formats import YAML, JSON, TOML, PYTHON
from .gui import GUI


def prev_gen() -> None:
    """
    The command line tool for conversions
    """
    p = ArgumentParser(
        description='The CLI interface of the prev_gen library'
    )
    p.add_argument('--show', action='store_true', help='preview the result')
    p.add_argument('--unsafe', action='store_true', help='allow loading python files')
    p.add_argument('-o', '--out', help='output filetype', choices=('py', 'yml', 'json', 'toml', 'png', 'svg'))
    p.add_argument('file', help='the filename to convert (can also be \'gui\')')
    args = p.parse_args()
    fn, ext = splitext(args.file)
    if not ext and fn == 'gui':
        GUI()
        return
    ext = ext[1:]
    if ext not in ('yml', 'yaml', 'json', 'toml', 'py', 'png', 'svg'):
        p.error('File format not recognized')
    if ext in ('png', 'svg'):
        if args.out is None:
            args.out = 'py'
        if args.out in ('png', 'svg'):
            p.error('The out format for this file needs to be yml, json, toml or py')
        match ext:
            case 'png':
                p = Reverse(args.file)
            case 'svg':
                p = ReverseSVG(args.file)
        match args.out:
            case 'py':
                o = PYTHON(p).write(fn + '.py')
            case 'yml':
                o = YAML(p).write(fn + '.yml')
            case 'json':
                o = JSON(p).write(fn + '.json')
            case 'toml':
                o = TOML(p).write(fn + '.toml')
            case _:
                o = 'Error :('
        if args.show:
            print(o)
        return
    if args.out is None:
        args.out = 'png'
    if args.out not in ('png', 'svg'):
        p.error('The out format for this file needs to be png or svg')
    with open(args.file, 'r') as f:
        fc = f.read()
    match ext:
        case 'yml' | 'yaml':
            p = YAML.read(fc).palette
        case 'json':
            p = JSON.read(fc).palette
        case 'toml':
            p = TOML.read(fc).palette
        case 'py':
            loc = {}
            if not args.unsafe:
                p.error(
                    'Running arbitrary python code is unsafe, please review the python file, then use the --unsafe flag'
                )
            exec(fc, None, loc)
            if 'palette' not in loc:
                p.error('The given file does not contain a palette')
            p = loc['palette']
    match args.out:
        case 'svg':
            PreviewSVG(p, show=args.show, save=True)
        case 'png':
            Preview(p, show=args.show, save=True)
    return
