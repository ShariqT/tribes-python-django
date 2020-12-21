from tribes_django import settings
import os, re

def read_jekyll_config():
    fp = open(os.path.join(settings.BASE_DIR, "tribes_front_matter", "src_web", "_config.yml"))
    content = fp.read()
    fp.close()
    return content

def save_jekyll_config(txt):

    fp = open(os.path.join(settings.BASE_DIR, "tribes_front_matter", "src_web", "_config.yml"), "w")
    fp.write(txt)
    fp.close()
    return True


COLOR_DICT = {
    '31': [(255, 0, 0), (128, 0, 0)],
    '32': [(0, 255, 0), (0, 128, 0)],
    '33': [(255, 255, 0), (128, 128, 0)],
    '34': [(0, 0, 255), (0, 0, 128)],
    '35': [(255, 0, 255), (128, 0, 128)],
    '36': [(0, 255, 255), (0, 128, 128)],
    '0': [(0, 255, 255), (0, 128, 128)]
}

COLOR_REGEX = re.compile(r'\[(?P<arg_1>\d+)(;(?P<arg_2>\d+)(;(?P<arg_3>\d+))?)?m')

BOLD_TEMPLATE = '<span style="color: rgb{}; font-weight: bolder">'
LIGHT_TEMPLATE = '<span style="color: rgb{}">'


def ansi_to_html(text):
    text = text.replace('[m', '</span>')

    def single_sub(match):
        argsdict = match.groupdict()
        if argsdict['arg_3'] is None:
            if argsdict['arg_2'] is None:
                color, bold = argsdict['arg_1'], 0
            else:
                color, bold = argsdict['arg_1'], int(argsdict['arg_2'])
        else:
            color, bold = argsdict['arg_2'], int(argsdict['arg_3'])

        if bold:
            return BOLD_TEMPLATE.format(COLOR_DICT[color][1])
        return LIGHT_TEMPLATE.format(COLOR_DICT[color][0])

    return COLOR_REGEX.sub(single_sub, text)