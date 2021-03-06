#!/usr/bin/python3

# RUN UNIT TESTS: ./txt2xml.py --self-test DUMMY

import argparse, re, sys
from collections import namedtuple
from itertools import count
from xml.sax.saxutils import quoteattr

from pseudo_markdown_parser import LineGrammar # require pyparsing
from txt_mindmap import parse_graph

PALETTES = {
    'dark-solarized': ( # from http://ethanschoonover.com/solarized
        '#b58900', # yellow
        '#cb4b16', # orange
        '#6c71c4', # violet
        '#dc323f', # red
        '#268bd2', # blue
        '#d33682', # magenta
        '#2aa198', # cyan
        '#859900', # green
        '#939393', # grey
    )
}

Topic = namedtuple('Topic', ('text', 'id', 'link', 'icons', 'attrs', 'see'))

def main(argv):
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    with open(args.input_filepath, encoding='utf8') as txt_file:
        graph = parse_graph(txt_file.read())
    print('<map name="{}" version="tango">'.format(args.name))
    topics = list(recursively_print(graph, args, height=graph.height, counter=count()))
    topics_ids_per_text = {topic.text:topic.id for topic in topics}
    for topic in topics:
        for dest_topic_text in topic.see:
            dest_id = topics_ids_per_text[dest_topic_text]
            print('<relationship srcTopicId="{}" destTopicId="{}" lineType="3" endArrow="false" startArrow="true"/>'.format(topic.id, dest_id))
    print('</map>')

def parse_args(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, fromfile_prefix_chars='@')
    parser.add_argument('--name', default='mindmap')
    parser.add_argument('--default-img-size', default='80,43')
    parser.add_argument('--shrink', action='store_true')
    parser.add_argument('--no-shrinking-edges', action='store_false', dest='shrinking_edges')
    parser.add_argument('--palette', choices=list(PALETTES.keys()) + ['none'], default='dark-solarized')
    parser.add_argument('--font-color', default='white')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('input_filepath')
    return parser.parse_args(argv)

def recursively_print(node, args, height, counter, indent='', branch_id=None, order=None):
    indent += '    '
    attrs = {}
    if order is None:
        attrs['central'] = 'true'
    else:
        attrs['order'] = order
        if branch_id is None:
            branch_id = order
        if args.shrink:
            attrs['shrink'] = 'true'
    topic = topic_from_line(node.content,
                            id=next(counter),
                            edge_colors=None if args.palette == 'none' else PALETTES[args.palette],
                            edge_width=2+2*(height-indent.count('    ')) if args.shrinking_edges else None,
                            branch_id=branch_id,
                            default_attrs=attrs,
                            default_img_size=args.default_img_size,
                            font_color=args.font_color)
    print('{}<topic {} position="0,0" text={} id="{}">'.format(indent, topic.attrs, quoteattr(topic.text), topic.id))
    if topic.link:
        print('{}    <link url="{}" urlType="url"/>'.format(indent, topic.link))
    for icon in topic.icons:
        print('{}    <icon id="{}"/>'.format(indent, icon))
    yield topic
    for order, child in enumerate(node.children):
        yield from recursively_print(child, args, height=height, counter=counter, indent=indent, branch_id=branch_id, order=order)
    print('{}</topic>'.format(indent))

def topic_from_line(text_line, id=0, edge_width=None, edge_colors=None, branch_id=None, default_attrs=None, default_img_size='', font_color=''):
    parsed_line = LineGrammar.parseString(text_line, parseAll=True)
    link = parsed_line.url
    attrs = {}
    if default_attrs:
        attrs.update(default_attrs)
    for kv in parsed_line.attrs.split():
        k, v = kv.split('=')
        attrs[k.strip()] = v.strip()[1:-1]
    if parsed_line.is_img:
        attrs['shape'] = 'image'
        img_size = '{}x{}'.format(int(parsed_line.img_width), int(parsed_line.img_height)) if parsed_line.img_width and parsed_line.img_height else default_img_size
        attrs['image'] = '{}:{}'.format(img_size, link)
        link = None
    set_font_style_attr(attrs, parsed_line, font_color)
    if branch_id is not None:
        if edge_colors:
            attrs['edgeStrokeColor'] = edge_colors[branch_id % len(edge_colors)]
        if edge_width is not None:
            attrs['edgeStrokeWidth'] = edge_width
    attrs = ' '.join('{}="{}"'.format(k, v) for k, v in sorted(attrs.items()))
    icons = tuple(parsed_line.icons)
    if parsed_line.has_checkbox:
        icons = icons + ('tick_tick' if parsed_line.is_checked else 'tick_cross',)
    see = [dest_text.strip() for dest_text in list(parsed_line.see)]
    return Topic(text=(parsed_line.text or [''])[0].strip(), id=id, link=link or None, icons=icons, attrs=attrs, see=see)

def set_font_style_attr(attrs, parsed_line, default_font_color):
    font_size, font_family, font_color, bold, italic  = '', '', '', '', ''
    if 'fontStyle' in attrs:
        font_size, font_family, font_color, bold, italic, _ = attrs['fontStyle'].split(';')
    if not font_color:
        font_color = default_font_color
    is_bold, is_italic, is_striked = bool(parsed_line.is_bold), bool(parsed_line.is_italic), bool(parsed_line.is_striked)
    if is_bold:
        bold = 'bold'
    if is_italic:
        italic = 'italic'
    if font_size or font_family or font_color or bold or italic:
        # cf. https://bitbucket.org/wisemapping/wisemapping-open-source/src/master/mindplot/src/main/javascript/persistence/XMLSerializer_Pela.js?at=develop&fileviewer=file-view-default#XMLSerializer_Pela.js-281
        attrs['fontStyle'] = '{};{};{};{};{};'.format(font_size, font_family, font_color, bold, italic)

def self_test():
    assert topic_from_line('toto') \
            == Topic(text='toto', link=None, icons=(), attrs='', id=0, see=[])
    assert topic_from_line('[Framindmap](https://framindmap.org)') \
            == Topic(text='Framindmap', link='https://framindmap.org', icons=(), attrs='', id=0, see=[])
    assert topic_from_line('![coucou](http://website.com/favicon.ico)') \
            == Topic(text='coucou', link=None, icons=(), attrs='image=":http://website.com/favicon.ico" shape="image"', id=0, see=[])
    assert topic_from_line('!toto') \
            == Topic(text='!toto', link=None, icons=(), attrs='', id=0, see=[])
    assert topic_from_line('Productivity   !icon=chart_bar <!-- fontStyle=";;#104f11;;;" bgColor="#d9b518" -->') \
            == Topic(text='Productivity', link=None, icons=('chart_bar',), attrs='bgColor="#d9b518" fontStyle=";;#104f11;;;"', id=0, see=[])
    assert topic_from_line('**toto**') \
            == Topic(text='toto', link=None, icons=(), attrs='fontStyle=";;;bold;;"', id=0, see=[])
    assert topic_from_line('__toto__') \
            == Topic(text='toto', link=None, icons=(), attrs='fontStyle=";;;;italic;"', id=0, see=[])
    assert topic_from_line('__**toto**__') \
            == Topic(text='toto', link=None, icons=(), attrs='fontStyle=";;;bold;italic;"', id=0, see=[])
    assert topic_from_line('**__toto__**') \
            == Topic(text='toto', link=None, icons=(), attrs='fontStyle=";;;bold;italic;"', id=0, see=[])
    assert topic_from_line('toto !icon=ahoy') \
            == Topic(text='toto', link=None, icons=('ahoy',), attrs='', id=0, see=[])
    assert topic_from_line('!icon=A toto !icon=B') \
            == Topic(text='toto', link=None, icons=('A', 'B'), attrs='', id=0, see=[])
    assert topic_from_line('![toto](http://website.com/favicon.ico 600x0400)') \
            == Topic(text='toto', link=None, icons=(), attrs='image="600x400:http://website.com/favicon.ico" shape="image"', id=0, see=[])
    assert topic_from_line('[x] toto') \
            == Topic(text='toto', link=None, icons=('tick_tick',), attrs='', id=0, see=[])
    assert topic_from_line('toto (see: "a ")') \
            == Topic(text='toto', link=None, icons=(), attrs='', id=0, see=['a'])
    # TODO: require support for https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/text-decoration in mindplot/src/main/javascript/Topic.js line 356 & web2d/src/main/javascript/Text.js line 48
    assert topic_from_line('~~toto~~') \
            == Topic(text='toto', link=None, icons=(), attrs='', id=0, see=[])
    print('All tests passed')


if __name__ == '__main__':
    main(sys.argv[1:])

