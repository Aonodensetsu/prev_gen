from __future__ import annotations

from xml.etree import ElementTree

from .color import Color
from .settings import Settings
from .table import u2


class ReverseSVG:
    def __new__(cls, tree: ElementTree | str) -> u2:
        """
        This is probably not compatible ith many other generators
        As it uses the non-standard keyword "use" to determine element purpose
        :param tree: The xml.etree.ElementTree or filename to load
        """
        if isinstance(tree, str):
            tree = ElementTree.parse(tree)
        root = tree.getroot()
        ns = root.tag.removesuffix('svg')
        # get the svg element <text use='meta'> which is set by the generator
        settings = Settings.deserialize(list(
            i for i in root.findall(f'./{ns}text') if 'use' in i.attrib and i.attrib['use'] == 'meta')[0].text)
        ret = []
        vals = []
        maxX = -1
        # woo-hoo XML parsing
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
