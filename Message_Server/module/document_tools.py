# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import markdown


"""对目录和文件的操作"""


def get_md() -> str:
    """
    获取文档的内容
    :param md_path: 文档的绝对路径
    :return:
    """
    md_path = os.path.join(__project_path, "document", "api.md")
    res = ""
    if os.path.exists(md_path) and os.path.isfile(md_path):
        f = open(md_path, "r", encoding="utf-8")
        res = f.read()
        f.close()
    else:
        pass
    return res


def markdown_to_html() -> str:
    """
    转换markdown到html
    :param raw:
    :return:
    """
    raw = get_md()
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
            'markdown.extensions.toc']
    r = markdown.markdown(raw,  output_format='html5', extensions=exts)
    return r


if __name__ == "__main__":
    pass