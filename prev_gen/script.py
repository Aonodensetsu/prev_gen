from argparse import ArgumentParser, Namespace
from os.path import splitext

from .types import config_format, image_format
from .previewer import Previewer
from .reverser import Reverser
from .config import Config


def parse_args() -> tuple[ArgumentParser, Namespace]:
    """
    Parse command line arguments.
    """
    p = ArgumentParser(description='The CLI interface of the prev_gen library')
    p.add_argument('--show', action='store_true', help='preview the result')
    p.add_argument('--unsafe', action='store_true', help='allow loading python files')
    p.add_argument(
        '-o',
        '--out',
        help='output filetype',
        choices=('json', 'png', 'py', 'svg', 'toml', 'yaml')
    )
    p.add_argument('file', help='the filename to convert')
    return p, p.parse_args()


def convert_img(p: ArgumentParser, args: Namespace, ext: image_format, fn: str):
    """
    :param p: arg parser to print errors
    :param args: parsed args
    :param ext: file extension
    :param fn: file name
    """
    if args.out is None:
        args.out = 'yaml'
    if args.out not in ('json', 'py', 'toml', 'yaml'):
        p.error('The out format for this file needs to be yaml, json, toml or py')
    # noinspection PyTypeChecker
    o = Config(Reverser(args.file, output=ext), output=args.out).write(f'{fn}.{args.out}')
    if args.show:
        print(o)


def convert_config(p: ArgumentParser, args: Namespace, ext: config_format):
    """
    :param p: arg parser to print errors
    :param args: parsed args
    :param ext: file extension
    """
    if args.out is None:
        args.out = 'png'
    if args.out not in ('png', 'svg'):
        p.error('The out format for this file needs to be png or svg')
    with open(args.file, 'r') as f:
        fc = f.read()
    if ext == 'yml':
        ext: config_format = 'yaml'
    match ext:
        case 'py':
            if not args.unsafe:
                p.error(
                    'Loading arbitrary python code is unsafe, please review the python file, then use the --unsafe flag'
                )
            try:
                o = Config.read(fc, output=ext).palette
            except Exception as e:
                print(e)
                p.error(
                    'The given file does not contain a palette, this should NEVER happen if you reviewed the file!\n'
                    'Urgently check the file you just loaded for malicious code!'
                )
        case _:
            o = Config.read(fc, output=ext).palette
    # noinspection PyTypeChecker
    Previewer(o, output=args.out, show=args.show, save=True)


def prev_gen():
    """
    The command line tool for conversions
    """
    p, args = parse_args()
    fn, ext = splitext(args.file)
    ext = ext[1:]
    if ext not in ('json', 'png', 'py', 'svg', 'toml', 'yaml', 'yml'):
        p.error('File format not recognized')
    if ext in ('png', 'svg'):
        convert_img(p, args, ext, fn)
        return
    convert_config(p, args, ext)
