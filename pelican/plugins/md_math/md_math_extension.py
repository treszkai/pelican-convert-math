import re
import xml.etree.ElementTree as etree

import markdown
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor
from markdown.util import AtomicString


class MathInlineProcessor(InlineProcessor):
    RE_INLINE = r'(?:\\\((.*?)\\\)|\$([^ \t\r\n\$]+?)\$)'

    def handleMatch(self, m, data):
        el = etree.Element('script', attrib={'type': 'math/tex'})
        el.text = AtomicString(m.group(1) or m.group(2))
        return el, m.start(0), m.end(0)


class MathBlockProcessor(BlockProcessor):
    RE_DISPLAY_BLOCK = r'(?:\\\[|\$\$)(.*)(?:\\\]|\$\$)'
    ELEM_TEXT_BEGIN = '% <![CDATA[\n'
    ELEM_TEXT_END = ' %]]>'

    def test(self, parent, block):
        return re.fullmatch(self.RE_DISPLAY_BLOCK, block, re.DOTALL)

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = re.fullmatch(self.RE_DISPLAY_BLOCK, block, re.DOTALL)

        e = etree.SubElement(parent, 'script')
        e.set('type', 'math/tex; mode=display')
        e.text = AtomicString(
            self.ELEM_TEXT_BEGIN + m.group(1).strip('\n') + self.ELEM_TEXT_END
        )

        return True


class MathExtension(markdown.Extension):
    def extendMarkdown(self, md):
        # priority higher than that of "escape" (180), which deals with backslash escapes,
        # but lower than "backtick" (190), which replaces `e=f()` or ``e=f("`")``.
        # (see markdown/inlinepatterns.py:build_inlinepatterns)
        md.inlinePatterns.register(
            MathInlineProcessor(MathInlineProcessor.RE_INLINE, md), 'math', 185
        )

        # best to have it higher than "indent" (90), which deals with indented list items
        # (see markdown/blockprocessors/blockprocessors.py:build_block_parser)
        md.parser.blockprocessors.register(MathBlockProcessor(md.parser), 'math', 95)


def makeExtension(**kwargs):
    return MathExtension(**kwargs)
