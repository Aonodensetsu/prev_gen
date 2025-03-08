from __future__ import annotations

from typing import Callable, Sequence
from abc import ABC, abstractmethod
from os.path import exists
from copy import deepcopy

from .types import config_format
from .settings import Settings
from .color import Color
from .palette import u2


class Config:
    def __new__(cls, palette: u2, output: config_format = 'yaml') -> BaseConfig:
        try:
            return {'yaml': YamlConfig, 'json': JsonConfig, 'toml': TomlConfig, 'py': PythonConfig}[output](palette)
        except KeyError:
            raise ValueError(f'Invalid config mode: <{output}>')

    @classmethod
    def read(cls, file: str, output: config_format | None = None) -> BaseConfig:
        if output is None and exists(file):
            output = file.split('.')[-1]
        try:
            return {'yaml': YamlConfig, 'json': JsonConfig, 'toml': TomlConfig, 'py': PythonConfig}[output].read(file)
        except KeyError:
            raise ValueError(f'Invalid config mode: <{output}>')


class BaseConfig(ABC):
    """
    A class to allow loading configuration from arbitrary (supported) formats

    Attributes:
        palette: The common palette representation
        data:    The multiline string of data
    """
    palette: u2
    data: str

    @classmethod
    @abstractmethod
    def _serialize(cls) -> Callable[[dict], str]:
        """
        :return: A function to change the settings DICT! into a format string
        """
        return lambda x: str(x) if x is not None else ''

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        """
        Override if not correct
        :param prev: The previous output, make sure to include it in the processing
        :return: A function to change the u2 color DICTs! into a format string
        """
        return lambda x: prev + cls._serialize()(x)

    @classmethod
    @abstractmethod
    def _deserialize(cls) -> Callable[[str], dict]:
        """
        :return: A function to change the format string into a python dictionary
        """
        ...

    def __init__(self, palette: u2):
        """
        :param palette: The palette to transform to a formatted string
        """
        self.palette = deepcopy(palette)
        if isinstance(palette[0], Settings):
            s = palette[0].to_dict()
            c: list[list] = palette[1:]
        elif isinstance(palette[0], dict):
            s = Settings(**palette[0]).to_dict()
            c: list[list] = palette[1:]
        else:
            s = {}
            c: list[list] = palette
        for i, x in enumerate(c):
            for j, y in enumerate(x):
                c[i][j] = y.to_dict()
        data = self._serialize()({'settings': s})
        data = self._serialize2(data)({'palette': c})
        self.data = data

    def __repr__(self) -> str:
        """
        :return: The format string
        """
        return self.data

    @classmethod
    def read(cls, file: str) -> BaseConfig:
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
                if isinstance(b, str):
                    colors[i][j] = Color([float(x) for x in b[0].strip('()').split(', ')], *b[1:])
                elif isinstance(b, dict):
                    colors[i][j] = Color(**b)
                elif isinstance(b, Sequence):
                    colors[i][j] = Color(*b)
                elif isinstance(b, Color):
                    colors[i][j] = b
        return cls([Settings(**settings), *colors])

    def write(self, file: str) -> BaseConfig:
        """
        :param file: The filename to write to
        :return: Self, for method chaining
        """
        with open(file, 'w') as f:
            f.write(self.data)
        return self


class YamlConfig(BaseConfig):
    @classmethod
    def _serialize(cls) -> Callable[[dict], str]:
        from yaml import safe_dump
        return lambda val: (
            safe_dump(val, sort_keys=False)
            if val.get('settings', None)
            or val.get('palette')
            else ''
        )

    @classmethod
    def _deserialize(cls) -> Callable[[str], dict]:
        from yaml import safe_load
        return safe_load


class JsonConfig(BaseConfig):
    @classmethod
    def _serialize(cls) -> Callable[[dict], str]:
        from json import dumps
        return lambda val: '{\n' + (
            dumps(val, indent=2).removeprefix('{\n').removesuffix('\n}') + ',\n'
            if val.get('settings')
            else ''
        )

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        from json import dumps
        return lambda val: prev + (
            dumps(val, indent=2).removeprefix('{\n') + '\n'
            if val.get('palette')
            else ''
        )

    @classmethod
    def _deserialize(cls) -> Callable[[str], dict]:
        from json import loads
        return loads


class TomlConfig(BaseConfig):
    @classmethod
    def _serialize(cls) -> Callable[[dict], str]:
        def f(val):
            if not val.get('settings'):
                return ''
            s = val['settings']
            a = '\n[settings]\n'
            for k, v in s.items():
                a += f'{k} = {v}\n'
            return a
        return f

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        def f(val):
            if not val.get('palette'):
                return prev
            p = val['palette']
            a = 'palette = [\n'
            for ln in p:
                a += '  [\n'
                for c in ln:
                    a += f'    {{ color = "{c["color"]}"'
                    for x in ('name', 'desc_left', 'desc_right'):
                        if x in c:
                            a += f', {x} = "{c[x]}"'
                    if 'alpha' in c:
                        a += f', alpha = {c["alpha"]}'
                    a += ' },\n'
                a += '  ],\n'
            a += ']\n'
            return a + prev
        return f

    @classmethod
    def _deserialize(cls) -> Callable[[str], dict]:
        from tomlkit import parse
        return lambda x: parse(x).unwrap()


class PythonConfig(BaseConfig):
    @classmethod
    def _serialize(cls) -> Callable[[dict], str]:
        def f(val):
            if not val.get('settings'):
                return 'palette = [\n'
            val = val['settings']
            t = 'palette = [\n  {\n'
            for k, v in val.items():
                t += f'    \'{k}\': '
                if isinstance(v, str):
                    t += f'\'{v}\',\n'
                else:
                    t += f'{v},\n'
            t += '  },\n'
            return t
        return f

    @classmethod
    def _serialize2(cls, prev: str) -> Callable[[dict], str]:
        def f(val):
            if not val.get('palette'):
                return prev
            s = ''
            a = val['palette']
            for ln in a:
                s += '  ['
                for c in map(lambda x: Color(**x), ln):
                    s += f'\n    {{\'color\': \'{c.hexadecimal}\''
                    for i in ('name', 'desc_left', 'desc_right'):
                        if v := getattr(c, i):
                            s += f', \'{i}\': \'{v}\''
                    if (v := c.alpha) < 1.:
                        s += f', \'alpha\': {v}'
                    s += '},'
                s += '\n  ],\n'
            s += ']\n\nif __name__ == \'__main__\':\n    from prev_gen import Previewer\n    Previewer(palette)\n'
            return prev + s
        return f

    @classmethod
    def _deserialize(cls) -> Callable[[str], dict]:
        def f(val):
            ret = {}
            loc = {}
            exec(val, None, loc)
            if 'palette' in loc:
                if isinstance(loc['palette'][0], Settings):
                    ret['settings'] = loc['palette'][0].to_dict()
                    ret['palette'] = loc['palette'][1:]
                if isinstance(loc['palette'][0], dict):
                    ret['settings'] = Settings(**loc['palette'][0]).to_dict()
                    ret['palette'] = loc['palette'][1:]
                else:
                    ret['palette'] = loc['palette']
            return ret
        return f
