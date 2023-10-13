from __future__ import annotations
from drawsvg import Drawing, Rectangle, Text, DrawingElement
from typing import NamedTuple, Literal, Callable
from math import degrees, atan2, pi, cos, sin
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
from urllib.error import HTTPError
from dataclasses import dataclass
from os.path import dirname
from os import remove
from enum import Enum
import colorsys

# some type aliases depend on the presence of classes
# they are declared below their dependencies, spread throughout the file

# used for normalized color representations
#    (R, G, B)
#    (H, S, V)
#    (H, L, S)
#    (Y, I, Q)
# OK (L, C, H)
f3 = tuple[float, float, float]
# with alpha
f4 = tuple[float, float, float, float]
# used for denormalized color representations
#    (R: 0-255,  G: 0-255,  B: 0-255)
#    (H: 0-179,  S: 0-255,  V: 0-255)
#    (H: 0-360,  S: 0-100,  L: 0-100)
#    (Y: 0.255,  I: 0-255,  Q: 0-255)
# OK (L: 0-100   C: 0-100   H: 0-360)
i3 = tuple[int, int, int]
# with alpha (A: 0-255)
i4 = tuple[int, int, int, int]


class LazyloadError(AttributeError):
    """
    Attribute was not assigned a value during object creation and does not support lazy loading
    """
    def __init__(self, item):
        super().__init__(f'({item}) ' + self.__doc__)


# represents all CSS literals and their corresponding HEX value
class Literals(Enum):
    aliceblue = 'F0F8FF'
    antiquewhite = 'FAEBD7'
    antiquewhite1 = 'FFEFDB'
    antiquewhite2 = 'EEDFCC'
    antiquewhite3 = 'CDC0B0'
    antiquewhite4 = '8B8378'
    aqua = '0FF'
    aquamarine1 = '7FFFD4'
    aquamarine2 = '76EEC6'
    aquamarine3 = '66CDAA'
    aquamarine4 = '458B74'
    azure1 = 'F0FFFF'
    azure2 = 'E0EEEE'
    azure3 = 'C1CDCD'
    azure4 = '838B8B'
    banana = 'E3CF57'
    beige = 'F5F5DC'
    bisque1 = 'FFE4C4'
    bisque2 = 'EED5B7'
    bisque3 = 'CDB79E'
    bisque4 = '8B7D6B'
    black = '000'
    blanchedalmond = 'FFEBCD'
    blue = '00F'
    blue2 = '00E'
    blue3 = '0000CD'
    blue4 = '00008B'
    blueviolet = '8A2BE2'
    brick = '9C661F'
    brown = 'A52A2A'
    brown1 = 'FF4040'
    brown2 = 'EE3B3B'
    brown3 = 'CD3333'
    brown4 = '8B2323'
    burlywood = 'DEB887'
    burlywood1 = 'FFD39B'
    burlywood2 = 'EEC591'
    burlywood3 = 'CDAA7D'
    burlywood4 = '8B7355'
    burntsienna = '8A360F'
    burntumber = '8A3324'
    cadetblue = '5F9EA0'
    cadetblue1 = '98F5FF'
    cadetblue2 = '8EE5EE'
    cadetblue3 = '7AC5CD'
    cadetblue4 = '53868B'
    cadmiumorange = 'FF6103'
    cadmiumyellow = 'FF9912'
    carrot = 'ED9121'
    chartreuse1 = '7FFF00'
    chartreuse2 = '76EE00'
    chartreuse3 = '66CD00'
    chartreuse4 = '458B00'
    chocolate = 'D2691E'
    chocolate1 = 'FF7F24'
    chocolate2 = 'EE7621'
    chocolate3 = 'CD661D'
    chocolate4 = '8B4513'
    cobalt = '3D59AB'
    cobaltgreen = '3D9140'
    coldgrey = '808A87'
    coral = 'FF7F50'
    coral1 = 'FF7256'
    coral2 = 'EE6A50'
    coral3 = 'CD5B45'
    coral4 = '8B3E2F'
    cornflowerblue = '6495ED'
    cornsilk1 = 'FFF8DC'
    cornsilk2 = 'EEE8CD'
    cornsilk3 = 'CDC8B1'
    cornsilk4 = '8B8878'
    crimson = 'DC143C'
    cyan2 = '0EE'
    cyan3 = '00CDCD'
    cyan4 = '008B8B'
    darkgoldenrod = 'B8860B'
    darkgoldenrod1 = 'FFB90F'
    darkgoldenrod2 = 'EEAD0E'
    darkgoldenrod3 = 'CD950C'
    darkgoldenrod4 = '8B6508'
    darkgray = 'A9A9A9'
    darkgreen = '006400'
    darkkhaki = 'BDB76B'
    darkolivegreen = '556B2F'
    darkolivegreen1 = 'CAFF70'
    darkolivegreen2 = 'BCEE68'
    darkolivegreen3 = 'A2CD5A'
    darkolivegreen4 = '6E8B3D'
    darkorange = 'FF8C00'
    darkorange1 = 'FF7F00'
    darkorange2 = 'EE7600'
    darkorange3 = 'CD6600'
    darkorange4 = '8B4500'
    darkorchid = '9932CC'
    darkorchid1 = 'BF3EFF'
    darkorchid2 = 'B23AEE'
    darkorchid3 = '9A32CD'
    darkorchid4 = '68228B'
    darksalmon = 'E9967A'
    darkseagreen = '8FBC8F'
    darkseagreen1 = 'C1FFC1'
    darkseagreen2 = 'B4EEB4'
    darkseagreen3 = '9BCD9B'
    darkseagreen4 = '698B69'
    darkslateblue = '483D8B'
    darkslategray = '2F4F4F'
    darkslategray1 = '97FFFF'
    darkslategray2 = '8DEEEE'
    darkslategray3 = '79CDCD'
    darkslategray4 = '528B8B'
    darkturquoise = '00CED1'
    darkviolet = '9400D3'
    deeppink1 = 'FF1493'
    deeppink2 = 'EE1289'
    deeppink3 = 'CD1076'
    deeppink4 = '8B0A50'
    deepskyblue1 = '00BFFF'
    deepskyblue2 = '00B2EE'
    deepskyblue3 = '009ACD'
    deepskyblue4 = '00688B'
    dimgray = '696969'
    dodgerblue1 = '1E90FF'
    dodgerblue2 = '1C86EE'
    dodgerblue3 = '1874CD'
    dodgerblue4 = '104E8B'
    eggshell = 'FCE6C9'
    emeraldgreen = '00C957'
    firebrick = 'B22222'
    firebrick1 = 'FF3030'
    firebrick2 = 'EE2C2C'
    firebrick3 = 'CD2626'
    firebrick4 = '8B1A1A'
    flesh = 'FF7D40'
    floralwhite = 'FFFAF0'
    forestgreen = '228B22'
    gainsboro = 'DCDCDC'
    ghostwhite = 'F8F8FF'
    gold1 = 'FFD700'
    gold2 = 'EEC900'
    gold3 = 'CDAD00'
    gold4 = '8B7500'
    goldenrod = 'DAA520'
    goldenrod1 = 'FFC125'
    goldenrod2 = 'EEB422'
    goldenrod3 = 'CD9B1D'
    goldenrod4 = '8B6914'
    gray = '808080'
    gray1 = '030303'
    gray10 = '1A1A1A'
    gray11 = '1C1C1C'
    gray12 = '1F1F1F'
    gray13 = '212121'
    gray14 = '242424'
    gray15 = '262626'
    gray16 = '292929'
    gray17 = '2B2B2B'
    gray18 = '2E2E2E'
    gray19 = '303030'
    gray2 = '050505'
    gray20 = '333'
    gray21 = '363636'
    gray22 = '383838'
    gray23 = '3B3B3B'
    gray24 = '3D3D3D'
    gray25 = '404040'
    gray26 = '424242'
    gray27 = '454545'
    gray28 = '474747'
    gray29 = '4A4A4A'
    gray3 = '080808'
    gray30 = '4D4D4D'
    gray31 = '4F4F4F'
    gray32 = '525252'
    gray33 = '545454'
    gray34 = '575757'
    gray35 = '595959'
    gray36 = '5C5C5C'
    gray37 = '5E5E5E'
    gray38 = '616161'
    gray39 = '636363'
    gray4 = '0A0A0A'
    gray40 = '666'
    gray42 = '6B6B6B'
    gray43 = '6E6E6E'
    gray44 = '707070'
    gray45 = '737373'
    gray46 = '757575'
    gray47 = '787878'
    gray48 = '7A7A7A'
    gray49 = '7D7D7D'
    gray5 = '0D0D0D'
    gray50 = '7F7F7F'
    gray51 = '828282'
    gray52 = '858585'
    gray53 = '878787'
    gray54 = '8A8A8A'
    gray55 = '8C8C8C'
    gray56 = '8F8F8F'
    gray57 = '919191'
    gray58 = '949494'
    gray59 = '969696'
    gray6 = '0F0F0F'
    gray60 = '999'
    gray61 = '9C9C9C'
    gray62 = '9E9E9E'
    gray63 = 'A1A1A1'
    gray64 = 'A3A3A3'
    gray65 = 'A6A6A6'
    gray66 = 'A8A8A8'
    gray67 = 'ABABAB'
    gray68 = 'ADADAD'
    gray69 = 'B0B0B0'
    gray7 = '121212'
    gray70 = 'B3B3B3'
    gray71 = 'B5B5B5'
    gray72 = 'B8B8B8'
    gray73 = 'BABABA'
    gray74 = 'BDBDBD'
    gray75 = 'BFBFBF'
    gray76 = 'C2C2C2'
    gray77 = 'C4C4C4'
    gray78 = 'C7C7C7'
    gray79 = 'C9C9C9'
    gray8 = '141414'
    gray80 = 'CCC'
    gray81 = 'CFCFCF'
    gray82 = 'D1D1D1'
    gray83 = 'D4D4D4'
    gray84 = 'D6D6D6'
    gray85 = 'D9D9D9'
    gray86 = 'DBDBDB'
    gray87 = 'DEDEDE'
    gray88 = 'E0E0E0'
    gray89 = 'E3E3E3'
    gray9 = '171717'
    gray90 = 'E5E5E5'
    gray91 = 'E8E8E8'
    gray92 = 'EBEBEB'
    gray93 = 'EDEDED'
    gray94 = 'F0F0F0'
    gray95 = 'F2F2F2'
    gray97 = 'F7F7F7'
    gray98 = 'FAFAFA'
    gray99 = 'FCFCFC'
    green = '008000'
    green1 = '0F0'
    green2 = '0E0'
    green3 = '00CD00'
    green4 = '008B00'
    greenyellow = 'ADFF2F'
    honeydew1 = 'F0FFF0'
    honeydew2 = 'E0EEE0'
    honeydew3 = 'C1CDC1'
    honeydew4 = '838B83'
    hotpink = 'FF69B4'
    hotpink1 = 'FF6EB4'
    hotpink2 = 'EE6AA7'
    hotpink3 = 'CD6090'
    hotpink4 = '8B3A62'
    indianred = 'CD5C5C'
    indianred1 = 'FF6A6A'
    indianred2 = 'EE6363'
    indianred3 = 'CD5555'
    indianred4 = '8B3A3A'
    indigo = '4B0082'
    ivory1 = 'FFFFF0'
    ivory2 = 'EEEEE0'
    ivory3 = 'CDCDC1'
    ivory4 = '8B8B83'
    ivoryblack = '292421'
    khaki = 'F0E68C'
    khaki1 = 'FFF68F'
    khaki2 = 'EEE685'
    khaki3 = 'CDC673'
    khaki4 = '8B864E'
    lavender = 'E6E6FA'
    lavenderblush1 = 'FFF0F5'
    lavenderblush2 = 'EEE0E5'
    lavenderblush3 = 'CDC1C5'
    lavenderblush4 = '8B8386'
    lawngreen = '7CFC00'
    lemonchiffon1 = 'FFFACD'
    lemonchiffon2 = 'EEE9BF'
    lemonchiffon3 = 'CDC9A5'
    lemonchiffon4 = '8B8970'
    lightblue = 'ADD8E6'
    lightblue1 = 'BFEFFF'
    lightblue2 = 'B2DFEE'
    lightblue3 = '9AC0CD'
    lightblue4 = '68838B'
    lightcoral = 'F08080'
    lightcyan1 = 'E0FFFF'
    lightcyan2 = 'D1EEEE'
    lightcyan3 = 'B4CDCD'
    lightcyan4 = '7A8B8B'
    lightgoldenrod1 = 'FFEC8B'
    lightgoldenrod2 = 'EEDC82'
    lightgoldenrod3 = 'CDBE70'
    lightgoldenrod4 = '8B814C'
    lightgoldenrodyellow = 'FAFAD2'
    lightgrey = 'D3D3D3'
    lightpink = 'FFB6C1'
    lightpink1 = 'FFAEB9'
    lightpink2 = 'EEA2AD'
    lightpink3 = 'CD8C95'
    lightpink4 = '8B5F65'
    lightsalmon1 = 'FFA07A'
    lightsalmon2 = 'EE9572'
    lightsalmon3 = 'CD8162'
    lightsalmon4 = '8B5742'
    lightseagreen = '20B2AA'
    lightskyblue = '87CEFA'
    lightskyblue1 = 'B0E2FF'
    lightskyblue2 = 'A4D3EE'
    lightskyblue3 = '8DB6CD'
    lightskyblue4 = '607B8B'
    lightslateblue = '8470FF'
    lightslategray = '778899'
    lightsteelblue = 'B0C4DE'
    lightsteelblue1 = 'CAE1FF'
    lightsteelblue2 = 'BCD2EE'
    lightsteelblue3 = 'A2B5CD'
    lightsteelblue4 = '6E7B8B'
    lightyellow1 = 'FFFFE0'
    lightyellow2 = 'EEEED1'
    lightyellow3 = 'CDCDB4'
    lightyellow4 = '8B8B7A'
    limegreen = '32CD32'
    linen = 'FAF0E6'
    magenta = 'FF00FF'
    magenta2 = 'E0E'
    magenta3 = 'CD00CD'
    magenta4 = '8B008B'
    manganeseblue = '03A89E'
    maroon = '800000'
    maroon1 = 'FF34B3'
    maroon2 = 'EE30A7'
    maroon3 = 'CD2990'
    maroon4 = '8B1C62'
    mediumorchid = 'BA55D3'
    mediumorchid1 = 'E066FF'
    mediumorchid2 = 'D15FEE'
    mediumorchid3 = 'B452CD'
    mediumorchid4 = '7A378B'
    mediumpurple = '9370DB'
    mediumpurple1 = 'AB82FF'
    mediumpurple2 = '9F79EE'
    mediumpurple3 = '8968CD'
    mediumpurple4 = '5D478B'
    mediumseagreen = '3CB371'
    mediumslateblue = '7B68EE'
    mediumspringgreen = '00FA9A'
    mediumturquoise = '48D1CC'
    mediumvioletred = 'C71585'
    melon = 'E3A869'
    midnightblue = '191970'
    mint = 'BDFCC9'
    mintcream = 'F5FFFA'
    mistyrose1 = 'FFE4E1'
    mistyrose2 = 'EED5D2'
    mistyrose3 = 'CDB7B5'
    mistyrose4 = '8B7D7B'
    moccasin = 'FFE4B5'
    navajowhite1 = 'FFDEAD'
    navajowhite2 = 'EECFA1'
    navajowhite3 = 'CDB38B'
    navajowhite4 = '8B795E'
    navy = '000080'
    oldlace = 'FDF5E6'
    olive = '808000'
    olivedrab = '6B8E23'
    olivedrab1 = 'C0FF3E'
    olivedrab2 = 'B3EE3A'
    olivedrab3 = '9ACD32'
    olivedrab4 = '698B22'
    orange = 'FF8000'
    orange1 = 'FFA500'
    orange2 = 'EE9A00'
    orange3 = 'CD8500'
    orange4 = '8B5A00'
    orangered1 = 'FF4500'
    orangered2 = 'EE4000'
    orangered3 = 'CD3700'
    orangered4 = '8B2500'
    orchid = 'DA70D6'
    orchid1 = 'FF83FA'
    orchid2 = 'EE7AE9'
    orchid3 = 'CD69C9'
    orchid4 = '8B4789'
    palegoldenrod = 'EEE8AA'
    palegreen = '98FB98'
    palegreen1 = '9AFF9A'
    palegreen2 = '90EE90'
    palegreen3 = '7CCD7C'
    palegreen4 = '548B54'
    paleturquoise1 = 'BFF'
    paleturquoise2 = 'AEEEEE'
    paleturquoise3 = '96CDCD'
    paleturquoise4 = '668B8B'
    palevioletred = 'DB7093'
    palevioletred1 = 'FF82AB'
    palevioletred2 = 'EE799F'
    palevioletred3 = 'CD6889'
    palevioletred4 = '8B475D'
    papayawhip = 'FFEFD5'
    peachpuff1 = 'FFDAB9'
    peachpuff2 = 'EECBAD'
    peachpuff3 = 'CDAF95'
    peachpuff4 = '8B7765'
    peacock = '33A1C9'
    pink = 'FFC0CB'
    pink1 = 'FFB5C5'
    pink2 = 'EEA9B8'
    pink3 = 'CD919E'
    pink4 = '8B636C'
    plum = 'DDA0DD'
    plum1 = 'FBF'
    plum2 = 'EEAEEE'
    plum3 = 'CD96CD'
    plum4 = '8B668B'
    powderblue = 'B0E0E6'
    purple = '800080'
    purple1 = '9B30FF'
    purple2 = '912CEE'
    purple3 = '7D26CD'
    purple4 = '551A8B'
    raspberry = '872657'
    rawsienna = 'C76114'
    red1 = 'F00'
    red2 = 'E00'
    red3 = 'CD0000'
    red4 = '8B0000'
    rosybrown = 'BC8F8F'
    rosybrown1 = 'FFC1C1'
    rosybrown2 = 'EEB4B4'
    rosybrown3 = 'CD9B9B'
    rosybrown4 = '8B6969'
    royalblue = '4169E1'
    royalblue1 = '4876FF'
    royalblue2 = '436EEE'
    royalblue3 = '3A5FCD'
    royalblue4 = '27408B'
    salmon = 'FA8072'
    salmon1 = 'FF8C69'
    salmon2 = 'EE8262'
    salmon3 = 'CD7054'
    salmon4 = '8B4C39'
    sandybrown = 'F4A460'
    sapgreen = '308014'
    seagreen1 = '54FF9F'
    seagreen2 = '4EEE94'
    seagreen3 = '43CD80'
    seagreen4 = '2E8B57'
    seashell1 = 'FFF5EE'
    seashell2 = 'EEE5DE'
    seashell3 = 'CDC5BF'
    seashell4 = '8B8682'
    sepia = '5E2612'
    sgibeet = '8E388E'
    sgibrightgray = 'C5C1AA'
    sgichartreuse = '71C671'
    sgidarkgray = '555'
    sgigray12 = '1E1E1E'
    sgigray16 = '282828'
    sgigray32 = '515151'
    sgigray36 = '5B5B5B'
    sgigray52 = '848484'
    sgigray56 = '8E8E8E'
    sgigray72 = 'B7B7B7'
    sgigray76 = 'C1C1C1'
    sgigray92 = 'EAEAEA'
    sgigray96 = 'F4F4F4'
    sgilightblue = '7D9EC0'
    sgilightgray = 'AAA'
    sgiolivedrab = '8E8E38'
    sgisalmon = 'C67171'
    sgislateblue = '7171C6'
    sgiteal = '388E8E'
    sienna = 'A0522D'
    sienna1 = 'FF8247'
    sienna2 = 'EE7942'
    sienna3 = 'CD6839'
    sienna4 = '8B4726'
    silver = 'C0C0C0'
    skyblue = '87CEEB'
    skyblue1 = '87CEFF'
    skyblue2 = '7EC0EE'
    skyblue3 = '6CA6CD'
    skyblue4 = '4A708B'
    slateblue = '6A5ACD'
    slateblue1 = '836FFF'
    slateblue2 = '7A67EE'
    slateblue3 = '6959CD'
    slateblue4 = '473C8B'
    slategray = '708090'
    slategray1 = 'C6E2FF'
    slategray2 = 'B9D3EE'
    slategray3 = '9FB6CD'
    slategray4 = '6C7B8B'
    snow1 = 'FFFAFA'
    snow2 = 'EEE9E9'
    snow3 = 'CDC9C9'
    snow4 = '8B8989'
    springgreen = '00FF7F'
    springgreen1 = '00EE76'
    springgreen2 = '00CD66'
    springgreen3 = '008B45'
    steelblue = '4682B4'
    steelblue1 = '63B8FF'
    steelblue2 = '5CACEE'
    steelblue3 = '4F94CD'
    steelblue4 = '36648B'
    tan = 'D2B48C'
    tan1 = 'FFA54F'
    tan2 = 'EE9A49'
    tan3 = 'CD853F'
    tan4 = '8B5A2B'
    teal = '008080'
    thistle = 'D8BFD8'
    thistle1 = 'FFE1FF'
    thistle2 = 'EED2EE'
    thistle3 = 'CDB5CD'
    thistle4 = '8B7B8B'
    tomato1 = 'FF6347'
    tomato2 = 'EE5C42'
    tomato3 = 'CD4F39'
    tomato4 = '8B3626'
    turquoise = '40E0D0'
    turquoise1 = '00F5FF'
    turquoise2 = '00E5EE'
    turquoise3 = '00C5CD'
    turquoise4 = '00868B'
    turquoiseblue = '00C78C'
    violet = 'EE82EE'
    violetred = 'D02090'
    violetred1 = 'FF3E96'
    violetred2 = 'EE3A8C'
    violetred3 = 'CD3278'
    violetred4 = '8B2252'
    warmgrey = '808069'
    wheat = 'F5DEB3'
    wheat1 = 'FFE7BA'
    wheat2 = 'EED8AE'
    wheat3 = 'CDBA96'
    wheat4 = '8B7E66'
    white = 'FFF'
    whitesmoke = 'F5F5F5'
    yellow1 = 'FF0'
    yellow2 = 'EE0'
    yellow3 = 'CDCD00'
    yellow4 = '8B8B00'

    @staticmethod
    def get(x: str):
        if x.lower() in Literals.__members__:
            return Literals[x.lower()].value
        return x


@dataclass(slots=True)
class Color:
    """
    Represents one color tile in the image, any descriptions it may have - and allows for color conversions

    Attributes:
        name:      Color name

        descLeft:  Left corner description

        descRight: Right corner description

        dark:      Whether the color is dark based on human perception

        alpha:     Transparency value

        alphaD:    Denormalized transparency value

        hex:       Hexadecimal color

        hexa:      hex with transparency

        rgb:       rgb normalized color

        rgba:      rgb with transparency

        rgbD:      rgb denormalized color

        rgbaD:     rgbD with transparency

        hsv:       hsv normalized color

        hsva:      hsv with transparency

        hsvD:      hsv denormalized color

        hsvaD:     hsvD with transparency

        hls:       hls normalized color

        hlsa:      hls with transparency

        hlsD:      hls denormalized color

        hlsaD:     hlsD with transparency

        yiq:       yiq normalized color

        yiqa:      yiq with transparency

        yiqD:      yiq denormalized color

        yiqaD:     yiqD with transparency

        lch:       (ok)lch normalized color

        lcha:      (ok)lch with transparency

        lchD:      (ok)lch denormalized color

        lchaD:     (ok)lchD with transparency
    """
    name:      str | None
    descLeft:  str | None
    descRight: str | None
    dark:      bool
    hex:       str
    hexa:      str
    alpha:     float
    alphaD:    int
    rgb:       f3
    rgba:      f4
    rgbD:      i3
    rgbaD:     i4
    hsv:       f3
    hsva:      f4
    hsvD:      i3
    hsvaD:     i4
    hls:       f3
    hlsa:      f4
    hlsD:      i3
    hlsaD:     i4
    yiq:       f3
    yiqa:      f4
    yiqD:      i3
    yiqaD:     i4
    lch:       f3
    lcha:      f4
    lchD:      i3
    lchaD:     i4

    def __init__(self,
                 color: Literals | str | f3 | f4 | i3 | i4,
                 name: str | None = None,
                 descLeft: str | None = None,
                 descRight: str | None = None,
                 mode: Literal['rgb', 'hsv', 'hls', 'yiq', 'lch'] = 'rgb'
                 ) -> None:
        """
        Create a color from a given value

        Parameters:
            color:     The color value to assign

            name:      The name to display

            descLeft:  Left corner description

            descRight: Right corner description

            mode:      Specifies type of color created
        """
        # css literal parsing
        if isinstance(color, Literals):
            color = color.value
        # hex ignores mode
        if isinstance(color, str):
            # convert css to hex if possible
            color = Literals.get(color)
            # remove the useless hash
            color = color.lstrip('#').upper()
            # convert short hex to full hex
            if len(color) in (3, 4):
                color = ''.join(i * 2 for i in color)
            # extract alpha if present
            if len(color) >= 8:
                self.alpha = int(color[6:8], 16) / 255
            self.hex = color[:6]
            r, g, b = (
                int(self.hex[i * 2:(i + 1) * 2], 16) / 255
                for i in range(3)
            )
            self.rgb = (r, g, b)
        else:
            # extract alpha if present
            if len(color) >= 4:
                self.alpha = color[3]
                color = color[:3]
            if all(isinstance(i, int) for i in color):
                # if alpha was present, normalize it
                if hasattr(self, 'alpha'):
                    self.alpha /= 255
                setattr(self, mode + 'D', color)
                v1, v2, v3 = color
                match mode:
                    case 'rgb' | 'yiq':
                        color = (v1 / 255, v2 / 255, v3 / 255)
                    case 'hsv':
                        color = (v1 / 179, v2 / 255, v3 / 255)
                    case 'hls':
                        color = (v1 / 360, v2 / 100, v3 / 100)
                    case 'lch':
                        color = (v1 / 100, v2 / 100, v3 / 360)
            setattr(self, mode, color)
            # always calculate RGB since it is used for conversions
            match mode:
                case 'hsv' | 'hls' | 'yiq':
                    self.rgb = getattr(colorsys, mode + '_to_rgb')(*color)
                case 'lch':
                    L, C, H = self.lch
                    h = 2 * pi * H
                    a = C * cos(h)
                    b = C * sin(h)
                    # partial values
                    l1 = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
                    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
                    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
                    # some more math magic
                    rgb = (
                        4.0767245293 * l1 - 3.3072168827 * m + 0.2307590544 * s,
                        -1.2681437731 * l1 + 2.6093323231 * m - 0.3411344290 * s,
                        -0.0041119885 * l1 - 0.7034763098 * m + 1.7068625689 * s
                    )
                    # gamma transform
                    rgb = (
                        1.055 * x ** (1 / 2.4) - 0.055
                        if x >= 0.0031308
                        else 12.92 * x
                        for x in rgb
                    )
                    # some colors don't exist in rgb, just clamp them, close enough
                    r, g, b = (
                        max(0, min(x, 1))
                        for x in rgb
                    )
                    self.rgb = (r, g, b)
        if not hasattr(self, 'alpha'):
            self.alpha = 1
        self.name = name
        self.descLeft = descLeft
        self.descRight = descRight

    def __getattribute__(self, item):
        """
        python attribute magic
        this gets called to return a class member
        we capture it to only convert between color types as needed, saves some processing time
        """
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            # lazyload attributes as needed
            match item:
                case 'rgba' | 'hsva' | 'hlsa' | 'yiqa' | 'lcha' | 'rgbaD' | 'hsvaD' | 'hlsaD' | 'yiqaD' | 'lchaD':
                    base = item.removesuffix('D').removesuffix('a')
                    suffix = 'D' if 'D' in item else ''
                    setattr(self, item, (*getattr(self, base + suffix), getattr(self, 'alpha' + suffix)))
                case 'rgbD' | 'hsvD' | 'hlsD' | 'yiqD' | 'lchD':
                    v1, v2, v3 = getattr(self, item.removesuffix('D'))
                    mult = (255, 255, 255)
                    match item:
                        case 'hsvD':
                            mult = (179, 255, 255)
                        case 'hlsD':
                            mult = (360, 100, 100)
                        case 'lchD':
                            mult = (100, 100, 360)
                    setattr(self, item, (int(v1 * mult[0]), int(v2 * mult[1]), int(v3 * mult[2])))
                case 'hsv' | 'hls' | 'yiq':
                    setattr(self, item, getattr(colorsys, 'rgb_to_' + item)(*self.rgb))
                case 'lch':
                    # inverse gamma
                    r, g, b = (
                        ((x + 0.055) / 1.055) ** 2.4
                        if x >= 0.04045
                        else x / 12.92
                        for x in self.rgb
                    )
                    # partial values
                    part = (
                        0.412165612 * r + 0.536275208 * g + 0.0514575653 * b,
                        0.211859107 * r + 0.6807189584 * g + 0.107406579 * b,
                        0.0883097947 * r + 0.2818474174 * g + 0.6302613616 * b
                    )
                    l_, m_, s_ = (
                        x ** (1 / 3)
                        for x in part
                    )
                    a = 1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_
                    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_
                    self.lch = (
                        0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_,
                        (a ** 2 + b ** 2) ** 0.5,
                        degrees(atan2(b, a)) % 360 / 360
                    )
                case 'hex':
                    self.hex = '%02X%02X%02X' % self.rgbD
                case 'hexa':
                    # if opacity = 1, don't write it down
                    self.hexa = self.hex + '%02X' % self.alphaD
                case 'alphaD':
                    self.alphaD = int(self.alpha * 255)
                case 'dark':
                    # lch has a perception-based lightness :)
                    self.dark = self.lch[0] <= 0.483
                case _:
                    # lazyloading unsupported
                    raise LazyloadError(item)
            return object.__getattribute__(self, item)

    def serializeText(self) -> str:
        from base64 import b64encode
        return str(b64encode(bytes(f'{self.name}\0{self.descLeft}\0{self.descRight}', 'utf-8')), 'latin1')

    def deserializeText(self, text: str):
        from base64 import b64decode
        self.name, self.descLeft, self.descRight = str(b64decode(bytes(text, 'latin1')), 'utf-8').split('\0')


# used for Color transformations
#   bar - calculates dark bar color from background color
#   text - calculates text color from background color
tf = Callable[[Color], Color]


@dataclass(kw_only=True, slots=True)
class Settings:
    """
    Image generation settings

    Attributes:
        fileName:          File name to save into (no extension, png)

        fontName:          for svg = Google Font name

                           for png = local file name (no extension, true type)

        fontOpts:          Google Fonts API options (for svg)

        gridHeight:        Height of each individual color tile

        gridWidth:         Width of each individual color tile

        barHeight:         Height of the darkened bar at the bottom of each tile

        nameOffset:        Vertical offset of the color name printed within the tile

        hexOffset:         Vertical offset of the hex value printed below color name

        hexOffsetNameless: Vertical offset of the hex value printed if no name given

        descOffsetX:       Horizontal offset of the corner descriptions

        descOffsetY:       Vertical offset of the corner descriptions

        nameSize:          Text size of the color name

        hexSize:           Text size of the hex value printed under the color name

        hexSizeNameless:   Text size of the hex value printed if no name given

        descSize:          Text size of the corner descriptions

        barFn:             Function to determine bar color from background color

        textFn:            Function to determine text color from background color
    """
    fileName: str = 'result'
    fontName: str = 'Nunito'
    fontOpts: dict | None = None
    gridHeight: int = 168
    gridWidth: int = 224
    barHeight: int = 10
    nameOffset: int = -10
    hexOffset: int = 35
    hexOffsetNameless: int = 0
    descOffsetX: int = 15
    descOffsetY: int = 20
    nameSize: int = 40
    hexSize: int = 26
    hexSizeNameless: int = 34
    descSize: int = 26
    barFn: tf = (
        lambda x:
        Color(
            (
                x.lcha[0] * 0.9,
                x.lcha[1],
                x.lcha[2],
                x.lcha[3]
            ),
            mode='lch'
        )
    )
    textFn: tf = (
        lambda x:
        Color(
            (
                x.lcha[0] * 0.9 + 0.3
                if x.dark
                else x.lcha[0] * 0.75 - 0.15,
                x.lcha[1],
                x.lcha[2],
                x.lcha[3]
            ),
            mode='lch'
        )
    )

    def serialize(self) -> str:
        from dill import dumps
        from base64 import b64encode
        # the "unresolved" warning is wrong
        names = Settings.__slots__
        defaultCls = Settings()
        default = {i: getattr(defaultCls, i) for i in names}
        actual = {i: getattr(self, i) for i in names}
        changed = dict({k: v for k, v in actual.items() if default[k] != v})
        # only serialize non-default values for space-saving
        return str(b64encode(dumps(changed)), 'latin1')

    @staticmethod
    def deserialize(data: str):
        from dill import loads
        from base64 import b64decode
        return Settings(**loads(b64decode(bytes(data, 'latin1'))))


# used to typehint palettes
# usage 1
#   list of
#     Settings (as the first element)
#     Color
u1 = list[Settings | Color]
# usage 2
#   list of
#     None to mark an empty row
#     Settings (as the first element)
#     list of Color
u2 = list[None | Settings | list[Color]]


# used for position and size when placing tiles in an image
# and for the size of the image itself
class Distance(NamedTuple):
    """
    Absolute distance in pixels

    Attributes:
        x: Horizontal offset

        y: Vertical offset
    """
    x: int
    y: int


# used as a container of data when drawing tiles
class Field(NamedTuple):
    """
    A single field in the table, which contains a tile (color) and its geometry

    Attributes:
        pos:  Pixel offset from (0,0) to the top left corner

        size: Pixel offset from the top left corner to the bottom right corner

        col:  Color of this field
    """
    pos: Distance
    size: Distance
    col: Color


@dataclass(slots=True)
class Table:
    """
    A table of colors, which you can iterate over

    Attributes:
        colors:   List of colors, flattened

        settings: The settings available to the user

        height:   Height of the table in fields

        width:    Width of the table in fields

        size:     Size of table in pixels
    """
    colors: list[Color]
    settings: Settings
    height: int
    width: int
    _iter: int

    @property
    def size(self) -> Distance:
        """Size of table in pixels"""
        return Distance(
            self.width * self.settings.gridWidth,
            self.height * self.settings.gridHeight
        )

    def __init__(self,
                 colors: u2 | u1
                 ) -> None:
        """
        Creates a table from a palette

        Parameters:
             colors: The list of colors to use for this table
        """
        # extract settings from palette
        if isinstance(colors[0], Settings):
            self.settings = colors[0]
            colors = colors[1:]
        else:
            self.settings = Settings()
        # get the explicitly given size and flatten list
        if isinstance(colors[0], list):
            self.height = len(colors)
            self.width = max(len(i) for i in colors)
            # equalize row lengths
            for i in colors:
                while len(i) < self.width:
                    i.append(Color('0000'))
            colors = [j for i in colors for j in i]
        # calculate the correct size
        else:
            # try with a square first
            self.height = int(len(colors) ** (1 / 2))
            self.width = self.height
            # extend the square until everything fits
            while self.width * self.height < len(colors):
                self.width += 1
        self.colors = colors
        self._iter = 0

    def __iter__(self) -> Table:
        """
        python iterator magic
        for the iterable magic below
        """
        self._iter = 0
        return self

    def __next__(self) -> Field:
        """
        python iterable magic
        allows to use the Table like a list of Fields
        """
        i = self._iter
        self._iter += 1
        while i < len(self.colors) - 1 and self.colors[i].alpha == 0:
            i += 1
            self._iter += 1
        if i >= len(self.colors) or self.colors[i].alpha == 0:
            self._iter = 0
            raise StopIteration
        return Field(
            Distance(
                i % self.width * self.settings.gridWidth,
                i // self.width * self.settings.gridHeight
            ),
            # the size is decreased by one because the tiles would overlap
            # which you can see if you have an empty tile somewhere
            Distance(
                self.settings.gridWidth - 1,
                self.settings.gridHeight - 1
            ),
            self.colors[i]
        )


class Preview:
    """
    Params:
        palette: The palette of colors to generate an image for

        show:    Whether to display the generated image

        save:    Whether to save the generated palette

        returns: (PIL.Image) the created image
    """
    def __new__(cls,
                palette: u1 | u2,
                show: bool = True,
                save: bool = False
                ) -> Image:

        t = Table(palette)
        s = t.settings
        img = Image.new('RGBA', t.size)
        draw = ImageDraw.Draw(img, 'RGBA')
        if s.fontName == 'Nunito':
            from inspect import currentframe, getabsfile
            font = dirname(getabsfile(currentframe())) + '/nunito.ttf'
        else:
            font = s.fontName + '.ttf'
        meta = PngInfo()
        meta.add_text('colorGen', s.serialize())
        for i, v in enumerate(t):
            l, t = v.pos
            w, h = v.size
            col = v.col
            meta.add_text(f'color{i}', col.serializeText())
            bgCol = col.rgbaD
            barCol = s.barFn(col).rgbaD
            textCol = s.textFn(col).rgbaD
            hx = col.hexa if col.alpha < 1 else col.hex
            draw.rectangle(
                (
                    (l, t),
                    (l + w, t + h - s.barHeight - 1)
                ),
                fill=bgCol
            )
            draw.rectangle(
                (
                    (l, t + h - s.barHeight),
                    (l + w, t + h)
                ),
                fill=barCol
            )
            if col.name is not None:
                draw.text(
                    (l + w / 2, t + h / 2 + s.nameOffset),
                    col.name,
                    font=ImageFont.truetype(font, size=s.nameSize),
                    fill=textCol,
                    anchor='mm'
                )
                draw.text(
                    (l + w / 2, t + h / 2 + s.hexOffset),
                    hx,
                    font=ImageFont.truetype(font, size=s.hexSize),
                    fill=textCol,
                    anchor='mm'
                )
            else:
                draw.text(
                    (l + w / 2, t + h / 2 + s.hexOffsetNameless),
                    hx,
                    font=ImageFont.truetype(font, size=s.hexSizeNameless),
                    fill=textCol,
                    anchor='mm'
                )
            if col.descLeft is not None:
                draw.text(
                    (l + s.descOffsetX, t + s.descOffsetY),
                    col.descLeft,
                    font=ImageFont.truetype(font, size=s.descSize),
                    fill=textCol,
                    anchor='lt'
                )
            if col.descRight is not None:
                draw.text(
                    (l + w - 1 - s.descOffsetX, t + s.descOffsetY),
                    col.descRight,
                    font=ImageFont.truetype(font, size=s.descSize),
                    fill=textCol,
                    anchor='rt'
                )
        if save:
            img.save(s.fileName + '.png', pnginfo=meta)
        if show:
            if not save:
                img.show()
            else:
                # a hacky system-agnostic way to try to open the image
                # unlike what the name suggests, it will try to use native apps as well
                from webbrowser import open
                open(s.fileName + '.png')
        return img


class Reverse:
    """
    Takes an image and returns the palette used to generate it

    Params:
        image: The png image generated with this tool (or compatible)

        changes: The amount of color changes in the x/y-axis to ignore per tile (for the darker bar)

        returns: the palette as a Python list
    """
    def __new__(cls,
                image: Image | str,
                changes: tuple[int, int] = (0, 1)
                ) -> u2:
        if isinstance(image, str):
            image = Image.open(image)
        settings = Settings.deserialize(image.text['colorGen'])
        imageC = image.convert('RGBA')
        imageSize = [imageC.width, imageC.height]
        gridSize = [0, 0]
        chLoc = list(changes)
        # x then y, combined for brevity
        for i in range(0, 2):
            lastCol = imageC.getpixel((0, 0))
            for j in range(0, imageSize[i]):
                c = imageC.getpixel((0, j) if i else (j, 0))
                if not lastCol == c:
                    chLoc[i] -= 1
                    if chLoc[i] < 0:
                        break
                gridSize[i] += 1
                lastCol = c
        ret = [settings]
        index = 0
        for j in range(0, imageSize[1], gridSize[1]):
            row = []
            for i in range(0, imageSize[0], gridSize[0]):
                a = Color('%02X%02X%02X%02X' % imageC.getpixel((i, j)))
                # if alpha is zero, the color does not get drawn
                if not a.alpha == 0:
                    a.deserializeText(image.text[f'color{index}'])
                    index += 1
                row.append(a)
            ret.append(row)
        return ret


class SVGMeta(DrawingElement):
    # for whatever reason custom elements get written twice
    written = False

    def __init__(self, s: Settings):
        super().__init__()
        self.genS = s

    def write_svg_element(self, id_map, is_duplicate, output_file, lcontext, dry_run, force_dup=False):
        if not self.written:
            output_file.write(f'<text use="meta" display="none">{self.genS.serialize()}</text>')
            self.written = True


class PreviewSVG:
    """
    Params:
        palette: The palette of colors to generate an image for

        show:    Whether to display the generated image

        save:    Whether to save the generated palette

        returns: (drawsvg.Drawing) the created image
    """
    def __new__(cls,
                palette: u1 | u2,
                show: bool = True,
                save: bool = False
                ) -> Image:
        t = Table(palette)
        s = t.settings
        draw = Drawing(*t.size, origin=(0, 0), id_prefix='prevgen')
        draw.append(SVGMeta(s))
        fontOpts = s.fontOpts or {'wght': 700}
        if 'wght' in fontOpts:
            draw.append_css(f'text{{font-family:{s.fontName},Calibri,sans-serif;font-weight:{fontOpts["wght"]};}}')
        else:
            draw.append_css(f'text{{font-family:{s.fontName},Calibri,sans-serif;}}')
        # embed google font in svg for correct previews
        try:
            draw.embed_google_font(s.fontName, **fontOpts)
        except HTTPError:
            print(f'\033[31;1mError: \'{s.fontName}\' with opts \'{fontOpts}\' is not available in Google Fonts')
            exit(1)
        for i in t:
            l, t = i.pos
            w, h = i.size
            col = i.col
            bCol = s.barFn(col)
            tCol = s.textFn(col)
            # svg now supports oklch
            bgCol = f'oklch({col.lch[0]} {col.lch[1]} {col.lchD[2]})'
            barCol = f'oklch({bCol.lch[0]} {bCol.lch[1]} {bCol.lchD[2]})'
            textCol = f'oklch({tCol.lch[0]} {tCol.lch[1]} {tCol.lchD[2]})'
            hx = col.hexa if col.alpha < 1 else col.hex
            draw.append(Rectangle(
                l,
                t,
                w + 1,
                h - s.barHeight + 1,
                use='bg',
                fill=bgCol,
                fill_opacity=col.alpha,
                stroke=bgCol
            ))
            draw.append(Rectangle(
                l,
                t + h - s.barHeight + 1,
                w + 1,
                s.barHeight,
                use='bar',
                fill=barCol,
                fill_opacity=col.alpha,
                stroke=barCol
            ))
            if col.name is not None:
                draw.append(Text(
                    col.name,
                    use='name',
                    x=l + w / 2,
                    y=t + h / 2 + s.nameOffset,
                    fill=textCol,
                    fill_opacity=col.alpha,
                    center=True,
                    font_size=s.nameSize,
                    font_family=s.fontName
                ))
                draw.append(Text(
                    hx,
                    use='hex',
                    x=l + w / 2,
                    y=t + h / 2 + s.hexOffset,
                    fill=textCol,
                    fill_opacity=col.alpha,
                    center=True,
                    font_size=s.hexSize,
                    font_family=s.fontName
                ))
            else:
                draw.append(Text(
                    hx,
                    use='hex',
                    x=l + w / 2,
                    y=t + h / 2 + s.hexOffsetNameless,
                    fill=textCol,
                    fill_opacity=col.alpha,
                    center=True,
                    font_size=s.hexSizeNameless,
                    font_family=s.fontName
                ))
            if col.descLeft is not None:
                draw.append(Text(
                    col.descLeft,
                    use='descLeft',
                    x=l + s.descOffsetX,
                    y=t + s.descSize / 2 + s.descOffsetY,
                    center=True,
                    text_anchor='start',
                    fill=textCol,
                    fill_opacity=col.alpha,
                    font_size=s.descSize,
                    font_family=s.fontName
                ))
            if col.descRight is not None:
                draw.append(Text(
                    col.descRight,
                    use='descRight',
                    x=l + w - 1 - s.descOffsetX,
                    y=t + s.descSize / 2 + s.descOffsetY,
                    center=True,
                    text_anchor='end',
                    fill=textCol,
                    fill_opacity=col.alpha,
                    font_size=s.descSize,
                    font_family=s.fontName
                ))
        draw.save_svg(s.fileName + '.svg' if save else 'randomFileNameThatShouldNotExistOnYourSystemYet.svg')
        if show:
            # a hacky system-agnostic way to try to open the image
            # unlike what the name suggests, it will try to use native apps as well
            from webbrowser import open
            open(s.fileName + '.svg' if save else 'randomFileNameThatShouldNotExistOnYourSystemYet.svg')
        # had to save temporarily to display in browser, remove if user did not intend to keep the file
        if not save:
            from time import sleep
            sleep(2)
            remove('randomFileNameThatShouldNotExistOnYourSystemYet.svg')
        return draw


class ReverseSVG:
    """
    This is probably not compatible with many other generators
    As it uses the non-standard keyword "use" to determine element purpose
    """
    def __new__(cls, image: str) -> u2:
        from xml.etree import ElementTree as Et
        tree = Et.parse(image)
        root = tree.getroot()
        ns = root.tag.removesuffix('svg')
        # get the svg element <text use='meta'> which is set by the generator
        settings = Settings.deserialize(list(
            i for i in root.findall(f'./{ns}text') if 'use' in i.attrib and i.attrib['use'] == 'meta')[0].text)
        ret = []
        vals = []
        maxX = -1
        # woohoo XML parsing
        for i in root.findall(f'./{ns}*'):
            # only care about marked values
            if 'use' not in i.attrib.keys():
                continue
            # we don't care about the bars and we already parsed metadata
            if i.attrib['use'] in ('meta', 'bar'):
                continue
            # we need the max width to calculate how many tiles horizontally
            if (v := float(i.attrib['x'])) > maxX:
                maxX = v
            vals.append(i)
        # as long as we have values
        while vals:
            # we get the values until another 'bg'
            curVal = vals.pop(0)
            while vals and vals[0].attrib['use'] != 'bg':
                curVal.append(vals.pop(0))
            # we get the text values we need
            hx = list(x.text for x in curVal if x.attrib['use'] == 'hex')[0] if any(
                x.attrib['use'] == 'hex' for x in curVal) else '0000'
            name = list(x.text for x in curVal if x.attrib['use'] == 'name')[0] if any(
                x.attrib['use'] == 'name' for x in curVal) else None
            descLeft = list(x.text for x in curVal if x.attrib['use'] == 'descLeft')[0] if any(
                x.attrib['use'] == 'descLeft' for x in curVal) else None
            descRight = list(x.text for x in curVal if x.attrib['use'] == 'descRight')[0] if any(
                x.attrib['use'] == 'descRight' for x in curVal) else None
            # and remake the color
            ret.append(Color(hx, name, descLeft, descRight))
        # make the result a 2d list and include settings
        n = int(maxX / settings.gridWidth) + 1
        return [settings] + [ret[i:i + n] for i in range(0, len(ret), n)]


class GUI:
    """
    Shows a graphical editor, I don't really expect anyone to use it
    But if you only have the notepad or something, this at least has syntax highlighting
    """
    def __new__(cls) -> Image:
        import tkinter as tk
        from inspect import currentframe, getabsfile
        from PIL import ImageTk, ImageOps
        import idlelib.colorizer as ic
        import idlelib.percolator as ip

        def onEdit(_):
            editor.unbind('<Key>')
            editor.edited = True

        def preview():
            local = {}
            exec(editor.get('1.0', tk.END), None, local)
            p = local['palette']
            i = Preview(p, show=False)
            j = ImageOps.contain(i, (prev.winfo_width() - 10, prev.winfo_height() - 10))
            img = ImageTk.PhotoImage(j)
            prev.image = img
            prev.config(image=img)
            return i, p

        def save():
            i, p = preview()
            s = p[0]
            if not isinstance(s, Settings):
                s = Settings()
            i.save(s.fileName + '.png')

        def leave():
            _, p = preview()
            if editor.edited:
                with open('gui.py', 'w') as f:
                    f.write(editor.get('1.0', tk.END))
            exit()

        ui = tk.Tk()
        ui.title('Preview Generator GUI')
        ui.rowconfigure(0, weight=1)
        ui.rowconfigure(1, minsize=350)
        ui.columnconfigure(0, weight=1)
        ui.columnconfigure(1, minsize=100)
        ui.config(bg='#282828')
        ui.attributes('-fullscreen', True)
        fEdit = tk.Frame(ui, bg='#282828', border=10)
        fEdit.grid(row=0, column=0, sticky='nsew')
        editor = tk.Text(
            fEdit, bg='#282828', fg='#d4be98', insertbackground='#d4be98', borderwidth=0, font=('Verdana', 13)
        )
        with open(dirname(getabsfile(currentframe())) + '/example.txt', 'r') as f:
            editor.insert(tk.END, f.read())
        editor.pack(fill='both', expand=True)
        editor.edited = False
        editor.bind('<Key>', onEdit)
        col = ic.ColorDelegator()
        for i, j in zip(['STRING', 'COMMENT', 'KEYWORD', 'BUILTIN', 'DEFINITION'],
                        ['#a9b665', '#5a524c', '#ea6962', '#d8a657', '#7daea3']):
            col.tagdefs[i] = {'background': '#282828', 'foreground': j}
        ip.Percolator(editor).insertfilter(col)
        fCmd = tk.Frame(ui, bg='#282828')
        fCmd.grid(row=0, column=1, sticky='nsew')
        tk.Button(fCmd, text='Preview', command=preview, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(fCmd, text='Save', command=save, borderwidth=0, bg='#7daea3').pack(fill='x')
        tk.Button(fCmd, text='Exit', command=leave, borderwidth=0, bg='#7daea3').pack(fill='x')
        fPrev = tk.Frame(ui, bg='#282828', border=10)
        fPrev.grid(row=1, column=0, columnspan=2, sticky='nsew')
        prev = tk.Label(fPrev, bg='#282828')
        prev.pack(fill='both', expand=True)
        ui.wait_visibility(prev)
        preview()
        ui.mainloop()
        return preview()[0]
