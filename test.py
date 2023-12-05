from prev_gen import (
    Filters, PYTHON, TOML, JSON, YAML, ReverseSVG, PreviewSVG, Reverse, Preview, Table, Settings, Color, Literals
)
from test_helper import Raises, closeEnough
from os.path import exists
from os import remove


def testHelperRaises():
    r = Raises(ValueError)
    with r:
        int('1')
    assert not r.raised
    with r:
        int('raise')
    assert r.raised
    # a non-specified error should still be raised
    try:
        with r:
            _ = int.__dict__['wrong']
        assert False
    except KeyError:
        assert True


def testHelperCloseEnough():
    assert closeEnough((0.,), (0.000001,))
    assert closeEnough((0.,), (0.0001,), digits=3)
    assert not closeEnough((0.,), (0.0001,))


def testLiteralConversion():
    assert Literals.getOrKeep('aliceBlue') == 'F0F8FF'
    assert Literals.getOrKeep('doesNotExist') == 'doesNotExist'


def testInputModes():
    """simply should not raise an error"""
    Color('f00')
    Color('crimson')
    Color(Literals.crimson)
    Color(Literals.crimson.value)
    Color((255, 0, 0))
    Color((1., 0., 0.))


def testInvalidInput():
    r = Raises(ValueError, NotImplementedError)
    # tuple value not long enough
    with r:
        Color((0, 0))
    assert r.raised
    # not implemented for dict
    with r:
        Color({})
    assert r.raised


def testColorCanBeCompared():
    assert Color('crimson') == Color('crimson') == 'dc143c'
    assert Color('crimson') != Color('beige') != 'invalidColor'


def testColorModesWork():
    c = (0.2, 0.5, 0.3)
    assert (
        Color(c, mode='rgb')
        != Color(c, mode='hsv')
        != Color(c, mode='hls')
        != Color(c, mode='yiq')
        != Color(c, mode='lch')
    )


def testHexInputTypes():
    assert (
        Color('00F')
        == Color('00Ff')
        == Color('0000ff')
        == Color('0000FFFF')
        == Color('#00f')
        == Color('#00ff')
        == Color('#0000fF')
        == Color('#0000fFFf')
    )


def testHexIgnoresMode():
    c = 'f00'
    assert (
        Color(c, mode='rgb').rgb
        == Color(c, mode='hsv').rgb
        == Color(c, mode='hls').rgb
        == Color(c, mode='yiq').rgb
        == Color(c, mode='lch').rgb
    )


def testColorsInferProperties():
    c = Color('f00e')
    assert c.hex == 'FF0000'
    assert c.hexa == 'FF0000EE'
    assert c.alphaD == 238
    assert c.rgb == (1., 0., 0.)
    assert c.hsv == (0., 1., 1.)
    assert c.hls == (0., 0.5, 1.)
    assert c.rgbD == (255, 0, 0)
    assert c.hsvD == (0, 255, 255)
    assert c.hlsD == (0, 50, 100)
    assert c.yiqD == (76, 153, 54)
    assert c.lchD == (63, 77, 29)
    assert c.rgbaD == (255, 0, 0, 238)
    assert c.hsvaD == (0, 255, 255, 238)
    assert c.hlsaD == (0, 50, 100, 238)
    assert c.yiqaD == (76, 153, 54, 238)
    assert c.lchaD == (63, 77, 29, 238)
    assert c.dark is False
    assert closeEnough((c.alpha,), (0.9333,))
    assert closeEnough(c.yiq, (0.3, 0.599, 0.213))
    assert closeEnough(c.lch, (0.628, 0.773, 0.0812))
    assert closeEnough(c.rgba, (1., 0., 0., 0.9333))
    assert closeEnough(c.hsva, (0., 1., 1., 0.9333))
    assert closeEnough(c.hlsa, (0., 0.5, 1., 0.9333))
    assert closeEnough(c.yiqa, (0.3, 0.599, 0.213, 0.9333))
    assert closeEnough(c.lcha, (0.628, 0.773, 0.0812, 0.9333))


def testLchIsClipped():
    """this color does not exist in RGB but gets clipped into the range"""
    assert closeEnough(Color((0.725, 0.477, 0.558), mode='lch').rgb, (0.114, 0.737, 0.7707))


def testConversionsAreReversible():
    """colors at extremes may be less accurate (ex. #ff0) but test the general case"""
    c = Color('ed6')
    assert closeEnough(
        c.rgb,
        Color(c.hsv, mode='hsv').rgb,
        Color(c.hls, mode='hls').rgb,
        Color(c.yiq, mode='yiq').rgb,
        Color(c.lch, mode='lch').rgb
    )


def testColorSerializable():
    c = Color('000', 'name', 'descLeft', 'descRight')
    assert c.serializeText() == 'bmFtZQBkZXNjTGVmdABkZXNjUmlnaHQ='


def testColorDeserializable():
    c = Color('f00').deserializeText('bmFtZQBkZXNjTGVmdABkZXNjUmlnaHQ=')
    assert c.name == 'name'
    assert c.descLeft == 'descLeft'
    assert c.descRight == 'descRight'


def testSettingsSerialize():
    assert Settings().serialize() == 'gAR9lC4='
    assert Settings(fileName='nonDefault').serialize() == 'gASVHAAAAAAAAAB9lIwIZmlsZU5hbWWUjApub25EZWZhdWx0lHMu'


def testSettingsDeserialize():
    assert Settings.deserialize('gAR9lC4=') == Settings()
    assert Settings.deserialize('gASVHAAAAAAAAAB9lIwIZmlsZU5hbWWUjApub25EZWZhdWx0lHMu').fileName == 'nonDefault'


def testSettingsSerializeLambda():
    """
    function serials get long quick, I don't like this solution but haven't found a better one
    serializing functions is positional for some reason, I think it keeps the source context when serializing
    it's serialized and deserialized inline to not break when other tests are changed
    """
    assert Settings.deserialize(Settings(barFn=lambda x: x).serialize()).barFn(Color('f00')) == Color('f00')


def testTableInit():
    c = [Color('f00') for _ in range(5)]
    t = Table(c)
    assert t.colors == c
    assert t.settings == Settings()
    # the size is calculated as the rectangle closest to a square whose width >= height
    assert t.width == 3
    assert t.height == 2


def testTableIterable():
    c = [Color('f00') for _ in range(3)]
    c.insert(2, Color('0000'))
    t = Table(c)
    # the color with zero alpha should not get iterated
    it = 0
    for _ in t:
        it += 1
    assert it == 3


def testGeneratePreview():
    assert str(type(Preview([Color('f00')], show=False))) == '<class \'PIL.Image.Image\'>'


def testSavePreview():
    Preview([Settings(fileName='testSavePreview'), Color('f00')], show=False, save=True)
    assert exists('testSavePreview.png')
    remove('testSavePreview.png')


def testReversePreview():
    a = Preview([Settings(fileName='testReversePreview'), Color('f00')], show=False, save=True)
    Reverse('testReversePreview.png')
    remove('testReversePreview.png')
    Reverse(a)


def testGeneratePreviewSVG():
    assert str(type(PreviewSVG([Color('f00')], show=False))) == '<class \'xml.etree.ElementTree.ElementTree\'>'


def testSavePreviewSVG():
    PreviewSVG([Settings(fileName='testSavePreviewSVG'), Color('f00')], show=False, save=True)
    assert exists('testSavePreviewSVG.svg')
    remove('testSavePreviewSVG.svg')


def testReversePreviewSVG():
    a = PreviewSVG([Settings(fileName='testReversePreviewSVG'), Color('f00')], show=False, save=True)
    ReverseSVG('testReversePreviewSVG.svg')
    remove('testReversePreviewSVG.svg')
    ReverseSVG(a)


def testYamlRead():
    assert len(str(YAML.read('palette:\n- - - \'#0000\'\n'))) == 23
    assert len(str(YAML.read('example.yml'))) == 1874


def testYamlWrite():
    assert str(YAML([[Color('0000')]])) == 'palette:\n- - [\'#0000\']\n'


def testJsonRead():
    assert len(str(JSON.read('{"palette": [[["#0000"]]]}'))) == 53
    assert len(str(JSON.read('example.json'))) == 2236


def testJsonWrite():
    assert str(JSON([[Color('0000')]])) == '{\n  "palette": [\n    [\n      [ "#0000" ]\n    ]\n  ]\n}\n'


def testTomlRead():
    assert len(str(TOML.read('palette = [ [ [ "#0000",],],]'))) == 40
    assert len(str(TOML.read('example.toml'))) == 2138


def testTomlWrite():
    assert str(TOML([[Color('0000')]])) == 'palette = [\n  [\n    [ "#0000" ],\n  ],\n]\n'


def testPythonRead():
    assert len(str(PYTHON([[Color('0000')]]))) == 168


def testPythonWrite():
    assert PYTHON.read('palette = [[Color(\'0000\')]]').palette[1][0] == '0000'


def testFilterMonochrome():
    assert Filters(Preview([
        Settings(gridWidth=20, gridHeight=20), Color('f00')
    ], show=False)).monochrome().img.getpixel((0, 0)) == (93, 93, 93, 255)
