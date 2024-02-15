from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import Callable
from os.path import exists

from .color import Color
from .settings import Settings
from .table import u2


class Format(ABC):
    """
    A class to allow loading configuration from arbitrary (supported) formats

    Attributes:
        data: The multiline string of data
    """
    palette: u2
    data: str

    @staticmethod
    def _prefix() -> str:
        """
        Added to the beginning of the output
        """
        return ''

    @staticmethod
    @abstractmethod
    def _serialize(prev: str) -> Callable[[dict], str]:
        """
        :param prev: The previous output, make sure to include it in the processing
        :return: A function to change the settings DICT! into a format string
        """
        ...

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        """
        Override if not correct
        :param prev: The previous output, make sure to include it in the processing
        :return: A function to change the u2 color DICTs! into a format string
        """
        return cls._serialize(prev)

    @staticmethod
    @abstractmethod
    def _deserialize() -> Callable[[str], dict]:
        """
        :return: A function to change the format string into a python dictionary
        """
        ...

    def __init__(self, palette: u2) -> None:
        """
        :param palette: The palette to transform to a formatted string
        """
        self.palette = copy.deepcopy(palette)
        if isinstance(palette[0], Settings):
            s = palette[0].dict()
            c = palette[1:]
        else:
            s = {}
            c = palette
        for i, x in enumerate(c):
            for j, y in enumerate(x):
                c[i][j] = y.dict()
        data = self._prefix()
        if s:
            data = self._serialize(data)({'settings': s})
        data = self._serialize2(data)({'palette': c})
        self.data = data

    def __repr__(self):
        """
        :return: The format string
        """
        return self.data

    @classmethod
    def read(cls, file: str) -> Format:
        """
        :param file: The filename or loaded Format-data to use
        :return: The loaded Format instance
        """
        if exists(file):
            with open(file, 'r') as f:
                file = f.read()
        data = cls._deserialize()(file)
        if 'settings' not in data:
            data['settings'] = {}
        colors, settings = data['palette'], data['settings']
        for i, a in enumerate(colors):
            for j, b in enumerate(a):
                try:
                    # parse '(0.2, 0.2, 0.2)' as a  tuple first
                    colors[i][j] = Color([float(x) for x in b[0].strip('()').split(', ')], *b[1:])
                except (ValueError, TypeError):
                    try:
                        colors[i][j] = Color(*b)
                    except TypeError:
                        colors[i][j] = Color(b)
        return cls([Settings(**settings), *colors])

    def write(self, file: str) -> Format:
        """
        :param file: The filename to write to
        :return: Self, for method chaining
        """
        with open(file, 'w') as f:
            f.write(self.data)
        return self


class YAML(Format):
    @staticmethod
    def _serialize(prev: str) -> Callable[[dict], str]:
        from yaml import safe_dump
        return lambda val: prev + safe_dump(val, sort_keys=False)

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        from yaml import safe_dump
        return lambda val: prev + safe_dump(val, sort_keys=False, default_flow_style=None)

    @staticmethod
    def _deserialize() -> Callable[[str], dict]:
        from yaml import safe_load
        return safe_load


class JSON(Format):
    @staticmethod
    def _prefix() -> str:
        return '{\n'

    @staticmethod
    def _serialize(prev: str) -> Callable[[dict], str]:
        from json import dumps
        return lambda val: prev + dumps(val, indent=2).removeprefix('{\n').removesuffix('\n}') + ',\n'

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        from json import dumps

        def f(val):
            a = prev + dumps(val, indent=2).removeprefix('{\n') + '\n'
            a = a.replace('\n        ', ' ')
            a = a.replace('\n      ]', ' ]')
            return a
        return f

    @staticmethod
    def _deserialize() -> Callable[[str], dict]:
        from json import loads
        return loads


class TOML(Format):
    @staticmethod
    def _serialize(prev: str) -> Callable[[dict], str]:
        from toml import dumps
        return lambda val: prev + dumps(val)

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        from toml import dumps

        def f(val):
            a = dumps(val)
            a = a.replace('palette = [ [ [', 'palette = [\n  [\n    [')
            a = a.replace('], ', '],\n    ')
            a = a.replace('],],', '],\n  ],')
            a = a.replace('  [ [ ', '[\n    [ ')
            a = a.replace('],]', '],\n]')
            a = a.replace(',],', ' ],')
            if prev:
                a += '\n' + prev
            return a

        return f

    @staticmethod
    def _deserialize() -> Callable[[str], dict]:
        from toml import loads
        return loads


class PYTHON(Format):
    @staticmethod
    def _prefix() -> str:
        return 'from prev_gen import Preview, Color, Settings\n\npalette = [\n'

    @staticmethod
    def _serialize(prev: str) -> Callable[[dict], str]:
        def f(val):
            val = val['settings']
            t = prev + '    Settings(\n'
            for k, v in val.items():
                t += f'        {k}='
                if isinstance(v, str):
                    t += f'\'{v}\',\n'
                else:
                    t += f'{v},\n'
            t += '    ),\n'
            return t
        return f

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        def f(val):
            val = val['palette']
            height = len(val)
            width = len(val[0])
            val = [y for x in val for y in x]
            t = prev
            tbl = [[], [], [], []]
            for i in range(len(val)):
                c = val[i]
                try:
                    # parse '(0.2, 0.2, 0.2)' as a  tuple first
                    v = Color([float(x) for x in c[0].strip('()').split(', ')], *c[1:])
                    c[0] = '0000' if v.alpha == 0 else v.hexa if v.alpha < 1 else v.hex
                except ValueError:
                    pass
                for j in range(4):
                    try:
                        tbl[j].append(c[j])
                    except IndexError:
                        tbl[j].append(None)
            mx = [max(len(x) if x else 4 for x in tbl[i]) for i in range(4)]
            mx[0] += 4
            mx[1] += 4
            mx[2] += 3
            for i in range(height):
                t += '    [\n'
                for j in range(width):
                    inx = width * i + j
                    v = [tbl[x][inx] for x in range(4)]
                    v[0] = ('\'' + v[0] + '\',').ljust(mx[0])
                    for k in range(1, 4):
                        if not v[k]:
                            v[k] = 'None,'.ljust(mx[k])
                        else:
                            v[k] = ('\'' + v[k] + '\',').ljust(mx[k])
                    v[3] = v[3].replace(',', '')
                    if 'None' in v[3]:
                        v[3] = ''
                        if 'None' in v[2]:
                            v[2] = ''
                            if 'None' in v[1]:
                                v[1] = ''
                    t += '        Color({}{}{}{}'.format(*v).rstrip(', ')
                    t = t.replace('#0000', '0000')
                    t = t.replace('\'None\'', 'None')
                    t += '),\n'
                t += '    ],\n'
            t += ']\n\nif __name__ == \'__main__\':\n    Preview(palette, save=True, show=True)\n'
            return t
        return f

    @staticmethod
    def _deserialize() -> Callable[[str], dict]:
        def f(val):
            ret = {}
            loc = {}
            exec(val, None, loc)
            if 'palette' in loc:
                if isinstance(loc['palette'][0], Settings):
                    ret['settings'] = loc['palette'][0]
                    ret['palette'] = loc['palette'][1:]
                else:
                    ret['palette'] = loc['palette']
            return ret
        return f
