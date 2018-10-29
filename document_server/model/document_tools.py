# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import markdown


"""对目录和文件的操作"""


def list_dir(replace_path: str = "") -> dict:
    """
    以列表形式,返回每个项目的文档目录的信息.
    :param replace_path: 用于替换的路径
    :return:
    """
    root_path = os.path.dirname(__project_path)
    l1 = os.listdir(root_path)
    r1 = list()
    for l in l1:
        p_t = os.path.join(root_path, l, "document")
        if os.path.exists(p_t) and os.path.isdir(p_t):
            """有这个目录"""
            r1.append(p_t)
    res = dict()
    for r in r1:
        l2 = os.listdir(r)
        l2 = [x for x in l2 if os.path.isfile(os.path.join(r, x))]
        if "readme.md" in l2:
            """找到有效的目录"""
            readme_path = os.path.join(r, "readme.md")
            project_name = ""
            with open(readme_path, "r", encoding="utf-8") as f:
                for line in f:
                    title = line.replace('#', "")
                    title = title.strip()
                    if title != "":
                        project_name = title
                        break
            if project_name == "":
                """忽略不规范的document文档"""
                pass
            else:
                res[project_name] = {"path": r.replace(replace_path, ""), "children": [{"name": x, "path":
                    os.path.join(r, x).replace(replace_path, "")} for x in l2]}
    return res


def get_project(project_path: str, replace_path: str = "") -> dict:
    """
    根据项目路径,获取项目的文档信息
    :param project_path: 项目绝对路径
    :param replace_path: 因为显示原因,需要替换为空的根目录部分
    :return:
    """
    res = dict()
    if os.path.exists(project_path) and os.path.isdir(project_path):
        l2 = os.listdir(project_path)
        if "readme.md" in l2:
            """找到有效的目录"""
            readme_path = os.path.join(project_path, "readme.md")
            project_name = ""
            with open(readme_path, "r", encoding="utf-8") as f:
                for line in f:
                    title = line.replace('#', "")
                    title = title.strip()
                    if title != "":
                        project_name = title
                        break
            if project_name == "":
                """忽略不规范的document文档"""
                pass
            else:
                res.update({"path": project_path.replace(replace_path, ""), "children": [{"name": x, "path":
                    os.path.join(project_path, x).replace(replace_path, "")} for x in l2], "name": project_name})
        else:
            pass
    else:
        pass
    return res


def get_md(md_path: str) -> str:
    """
    获取文档的内容
    :param md_path: 文档的绝对路径
    :return:
    """
    res = ""
    if os.path.exists(md_path) and os.path.isfile(md_path):
        f = open(md_path, "r", encoding="utf-8")
        res = f.read()
        f.close()
    else:
        pass
    return res


def markdown_to_html(raw: str) -> str:
    """
    转换markdown到html
    :param raw:
    :return:
    """
    exts = [
        'markdown.extensions.extra',
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.tables',
        'markdown.extensions.admonition',
        'markdown.extensions.codehilite',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks'

    ]
    r = markdown.markdown(raw,  output_format='html5', extensions=exts)
    return r


if __name__ == "__main__":
    x = get_md("/home/walle/work/projects/document_server/document/readme.md")
    print(x)
    r = markdown_to_html(x)
    print(r)
    pass