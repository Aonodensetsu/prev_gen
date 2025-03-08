from __future__ import annotations

from dataclasses import dataclass, field
from base64 import b64decode, b64encode
from pickle import dumps, loads


@dataclass(kw_only=True, slots=True)
class Settings:
    """
    Image generation settings

    Attributes:
        bar_height:          Height of the darkened bar at the bottom of each tile

        desc_offset_x:       Horizontal offset of the corner descriptions

        desc_offset_y:       Vertical offset of the corner descriptions

        desc_size:           Text size of the corner descriptions

        file_name:           File name to save into (no extension, png)

        font_name:           for png = local file name (no extension, true type)

                             for svg = Google Font name

        font_opts:           Google Fonts API options (for svg)

        grid_height:         Height of each individual color tile

        grid_width:          Width of each individual color tile

        hex_offset:          Vertical offset of the hex value printed below color name

        hex_offset_nameless: Vertical offset of the hex value printed if no name given

        hex_size:            Text size of the hex value printed under the color name

        hex_size_nameless:   Text size of the hex value printed if no name given

        hex_upper:           Should the hex color be uppercase

        name_offset:         Vertical offset of the color name printed within the tile

        name_size:           Text size of the color name

        show_hash:           Display the hash symbol before hex colors
    """
    bar_height: int = 10
    desc_offset_x: int = 15
    desc_offset_y: int = 20
    desc_size: int = 26
    file_name: str = 'result'
    font_name: str = 'Nunito'
    font_opts: dict = field(default_factory=dict)
    grid_height: int = 168
    grid_width: int = 224
    hex_offset: int = 35
    hex_offset_nameless: int = 0
    hex_size: int = 26
    hex_size_nameless: int = 34
    hex_upper: bool = True
    name_offset: int = -10
    name_size: int = 40
    show_hash: bool = False

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

    @classmethod
    def data_serialize(cls, data: dict) -> str:
        return str(b64encode(dumps(data)), 'latin1')

    def serialize(self) -> str:
        """
        :return: A base64-encoded representation of the class
        """
        return self.data_serialize(self.to_dict())

    @classmethod
    def data_deserialize(cls, data: str) -> dict:
        """
        :param data: The serialized representation to decode into a dictionary
        :return: The decoded value
        """
        return loads(b64decode(bytes(data, 'latin1')))

    @classmethod
    def deserialize(cls, data: str) -> Settings:
        """
        :param data: The serialized representation to decode into Settings
        :return: The decoded Settings
        """
        return Settings(**cls.data_deserialize(data))
