from os.path import exists
from math import isclose
from os import remove

from prev_gen import Color, Config, Palette, Previewer, Reverser, Settings
from pytest import raises


def test_input_modes():
    """simply should not raise an error"""
    Color('f00')
    Color('crimson')
    Color((1., 0., 0.))
    Color((1., 0., 0.), model='hsl')


def test_invalid_input():
    # tuple value not long enough
    with raises(ValueError):
        Color((0, 0))
    # not implemented for dict
    with raises(NotImplementedError):
        Color({})


def test_color_can_be_compared():
    assert Color('crimson') == 'crimson'
    assert Color('crimson') == 'dc143c'
    assert Color('crimson') != Color('beige')
    assert Color('beige') != 'invalidColor'


def test_color_modes_work():
    c = (0.2, 0.5, 0.3)
    assert (
        Color(c, model='rgb')
        != Color(c, model='hsl')
        != Color(c, model='hsv')
        != Color(c, model='cmy')
    )


def test_hex_input_types():
    assert (
        Color('0000ff')
        == Color('#0000fF')
    )


def test_hex_ignores_mode():
    c = 'f00'
    assert (
        Color(c, model='rgb').rgb
        == Color(c, model='hsv').rgb
        == Color(c, model='hsl').rgb
        == Color(c, model='cmyk').rgb
    )


def test_colors_infer_properties():
    c = Color('ff0000', alpha=0.93)
    assert c.hexadecimal == '#ff0000'
    assert c.rgb == [1., 0., 0.]
    assert c.hsv == [0., 1., 1.]
    assert c.hsl == [0., 1., 0.5]
    assert c.dark is False
    assert all(isclose(x, y, rel_tol=0.001) for x, y in zip(c.oklch, (0.6279, 0.2577, 0.0812)))


def test_color_serializable():
    c = Color('000000', 'name', 'descLeft', 'descRight')
    des = Color('000000').deserialize_text(c.serialize_text())
    assert c.name == des.name
    assert c.desc_left == des.desc_left
    assert c.desc_right == des.desc_right


def test_settings_serialize():
    assert Settings().serialize() == 'gAR9lC4='
    s = Settings(file_name='nonDefault')
    assert Settings.deserialize(s.serialize()) == s


def test_table_init():
    c = [Color('f00') for _ in range(5)]
    p = Palette(c)
    assert p.colors == c
    assert p.settings == Settings()
    # the size is calculated as the rectangle closest to a square whose width >= height
    assert p.width == 3
    assert p.height == 2


def test_table_iterable():
    c = [Color('ff0000') for _ in range(3)]
    c.insert(2, Color('000000', alpha=0.))
    p = Palette(c)
    it = 0
    for _ in p:
        it += 1
    assert it == 4


def test_generate_png():
    assert str(type(Previewer([Color('f00')], show=False))) == '<class \'PIL.Image.Image\'>'


def test_save_png():
    Previewer([Settings(file_name='testSavePNG'), Color('f00')], show=False, save=True)
    assert exists('testSavePNG.png')
    remove('testSavePNG.png')


def test_reverse_png():
    a = Previewer([Settings(file_name='testReversePNG'), Color('f00')], show=False, save=True)
    Reverser('testReversePNG.png')
    remove('testReversePNG.png')
    Reverser(a)


def test_generate_svg():
    assert str(type(Previewer([Color('f00')], show=False, output='svg'))) == (
        '<class \'xml.etree.ElementTree.ElementTree\'>'
    )


def test_save_svg():
    Previewer([Settings(file_name='testSaveSVG'), Color('f00')], show=False, save=True, output='svg')
    assert exists('testSaveSVG.svg')
    remove('testSaveSVG.svg')


def test_reverse_svg():
    a = Previewer([Settings(file_name='testReverseSVG'), Color('f00')], show=False, save=True, output='svg')
    Reverser('testReverseSVG.svg')
    remove('testReverseSVG.svg')
    Reverser(a)


def test_yaml():
    c = """
palette:
- - color: '#000000'
""".removeprefix('\n')
    assert str(Config.read(c, output='yaml')) == str(Config([[Color('000000')]], output='yaml')) == c


def test_json():
    c = """
{
  "palette": [
    [
      {
        "color": "#000000"
      }
    ]
  ]
}
""".removeprefix('\n')
    assert str(Config.read(c, output='json')) == str(Config([[Color('000000')]], output='json')) == c


def test_toml():
    c = """
palette = [
  [
    { color = "#000000" },
  ],
]
""".removeprefix('\n')
    assert str(Config.read(c, output='toml')) == str(Config([[Color('000000')]], output='toml')) == c


def test_python():
    c = """
palette = [
  [
    {'color': '#000000'},
  ],
]

if __name__ == '__main__':
    from prev_gen import Previewer
    Previewer(palette)
""".removeprefix('\n')
    assert str(Config.read(c, output='py')) == str(Config([[Color('000000')]], output='py')) == c
