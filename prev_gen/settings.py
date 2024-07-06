from __future__ import annotations

from dataclasses import dataclass, field
from base64 import b64decode, b64encode
from pickle import loads, dumps


@dataclass(kw_only=True, slots=True)
class Settings:
    """
    Image generation settings

    Attributes:
        file_name:           File name to save into (no extension, png)

        font_name:           for png = local file name (no extension, true type)

                             for svg = Google Font name

        font_opts:           Google Fonts API options (for svg)

        grid_height:         Height of each individual color tile

        grid_width:          Width of each individual color tile

        bar_height:          Height of the darkened bar at the bottom of each tile

        name_offset:         Vertical offset of the color name printed within the tile

        hex_offset:          Vertical offset of the hex value printed below color name

        hex_offset_nameless: Vertical offset of the hex value printed if no name given

        desc_offset_x:       Horizontal offset of the corner descriptions

        desc_offset_y:       Vertical offset of the corner descriptions

        name_size:           Text size of the color name

        hex_size:            Text size of the hex value printed under the color name

        hex_size_nameless:   Text size of the hex value printed if no name given

        desc_size:           Text size of the corner descriptions

        show_hash:           Display the hash symbol before hex colors

        hex_upper:           Should the hex color be uppercase
    """
    file_name: str = 'result'
    font_name: str = 'Nunito'
    font_opts: to_dict = field(default_factory=dict)
    grid_height: int = 168
    grid_width: int = 224
    bar_height: int = 10
    name_offset: int = -10
    hex_offset: int = 35
    hex_offset_nameless: int = 0
    desc_offset_x: int = 15
    desc_offset_y: int = 20
    name_size: int = 40
    hex_size: int = 26
    hex_size_nameless: int = 34
    desc_size: int = 26
    show_hash: bool = False
    hex_upper: bool = True

    def to_dict(self) -> dict:
        """
        :return: The dictionary of non-default values
        """
        # noinspection PyUnresolvedReferences
        names = Settings.__slots__
        default_cls = Settings()
        default = {i: getattr(default_cls, i) for i in names}
        actual = {i: getattr(self, i) for i in names}
        return {k: v for k, v in actual.items() if default[k] != v}

    def serialize(self) -> str:
        """
        :return: A base64-encoded representation of the class
        """
        return str(b64encode(dumps(self.to_dict())), 'latin1')

    @staticmethod
    def deserialize(data: str) -> Settings:
        """
        :param data: The serialized representation to decode into Settings
        :return: The decoded Settings
        """
        return Settings(**loads(b64decode(bytes(data, 'latin1'))))
