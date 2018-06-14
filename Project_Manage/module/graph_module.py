# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from graphviz import Digraph
import datetime
from uuid import uuid4
from module.user_module import User
import mongo_db


"""
绘制图标的模块
使用此模块之前,需要安装graphviz, sudo apt-get install graphviz
然后再安装对应的python库.  pip3 install graphviz
py库文档的地址: https://graphviz.readthedocs.io/en/stable/manual.html
Graphviz的例子 http://www.tonyballantyne.com/graphs.html
Graphviz的参考文档:http://www.graphviz.org/doc/info/
1. 绘制有向图(流程图)
"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class Node(dict):
    def __init__(self, **kwargs):
        """Node对象不需要id，name就可以做唯一性判定"""
        super(Node, self).__init__()
        if 'desc' not in kwargs:
            kwargs['desc'] = ''
        if "shape" not in kwargs:
            kwargs['shape'] = "ellipse"
        if "name" not in kwargs:
            kwargs['name'] = uuid4().hex
        if "label" not in kwargs:
            ms = "label参数必须"
            raise ValueError(ms)
        for k, v in kwargs.items():
            self[k] = v


class Edge(dict):
    def __init__(self, **kwargs):
        super(Edge, self).__init__()
        if "_id" not in kwargs:
            kwargs['_id'] = uuid4().hex
        if 'desc' not in kwargs:
            kwargs['desc'] = ''
        if "tail_name" not in kwargs:
            ms = "tail_name参数必须"
            raise ValueError(ms)
        if "head_name" not in kwargs:
            ms = "head_name参数必须"
            raise ValueError(ms)
        if "label" not in kwargs:
            ms = "label参数必须"
            raise ValueError(ms)
        for k, v in kwargs.items():
            self[k] = v


class MyDigraph(mongo_db.BaseDoc):
    """
    有向图/流程图
    """
    _table_name = "digraph_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str        # 图的名称,理论上唯一
    type_dict['owner'] = DBRef       # 创建(所有)者
    type_dict['editors'] = list        # 可以编辑本图的人,指向用户的dbref的list
    """
    一个数组,用于存放构建Digraph的参数,这些参数可以是int和str等没有名字的参数,也可以是以dict方式保存的带名字的参数,举例
    dot = [
        {"comment": "this is a example",
        "format": "png"
    ]
    代表着,dot = Digraph(comment="this is a example", format="png")
    """
    type_dict['dot'] = list
    """
     一个数组,用于存放node信息.node 是字典格式的数据,一个node的字典的示范如下:
     node = {
                "shape": "rarrow", # 形状 默认为ellipse(椭圆) box/circle/diamond(方形/原型/菱形)
                "name": "我是加工数据的模块",  # svg格式中,鼠标悬停在节点上面时显示的文字,必须
                "label": "数据模块",  # 节点中间的文字,必须
                "color": "red",      # 节点的边框的颜色默认为black
                "fontcolor": "green",  # 字体颜色,默认为black
                "id": "dom_id",        # svg内部的元素的id.可以当作DOM的id来处理.默认为类型+索引
                "URL": url,    # 链接,注意这个参数区分大小写,而且是在当前页面打开.
                "fontname": "Microsoft YaHei",  # 字体名称 
                "fontnames": "SimSun Microsoft YaHei",  # 多个字体名称 
                "fontsize": 14,              # 字体大小,默认14px
                "desc": "我是备注"  # 注意,这个不是构造参数,是用来描述节点的.
            }
    """
    type_dict['nodes'] = list
    """
         一个数组,用于存放edge信息.edge 是字典格式的数据,一个edge的字典的示范如下:
         edge = {
                    "arrowhead": "ediamond", # 箭头形状形状 ,默认normal
                    "arrowsize": 2, # 箭头的尺寸 ,默认1
                    "tail_name": "node1_name",  # 弧尾连接的节点的name, 必须
                    "head_name": "node2_name",  # 弧头连接的节点的name, 必须
                    "label": "生成数据",  # 弧中间的文字 
                    "color": "red",      # 弧的颜色默认为black
                    "fontcolor": "green",  # 字体颜色,默认为black
                    "id": "dom_id",        # svg内部的元素的id.可以当作DOM的id来处理.默认为类型+索引
                    "URL": url,    # 链接,注意这个参数区分大小写,而且是在当前页面打开.
                    "fontname": "Microsoft YaHei",  # 字体名称 
                    "fontsize": 14,              # 字体大小,默认14px
                    "desc": "我是备注"  # 注意,这个不是构造参数,是用来描述节点的.
                }
        """
    type_dict['edges'] = list
    type_dict['desc'] = str  # 整个有向图的说明
    type_dict['image'] = bytes  # 图片文件
    type_dict['time'] = datetime.datetime
    """
    format可选多种格式: svg/png/pdf一个例子如下:
    dot = Digraph(comment="this is a example", format="svg", encoding="utf-8")
    dot.node("A", "步骤1", text="我是说明", id="No1", fontname="SimSun Microsoft YaHei")
    dot.node("B", "步骤2", shape="star", color="red")
    dot.node("C", "步骤3")
    dot.node("D", "步骤4")
    dot.edges(["AB", "AC"])
    dot.edge("C", "D", "判断", constraint='true')
    dot.edge("D", "A", "递归", constraint='true')
    print(dot.source)
    dot.render('test-output/round-table')
    """
    # dot = Digraph(comment="this is a example", format="svg", encoding="utf-8")
    # dot.node("A", "步骤1", text="我是说明", id="No1", fontname="SimSun Microsoft YaHei")
    # dot.node("B", "步骤2", shape="star", color="red")
    # dot.node("C", "步骤3")
    # dot.node("D", "步骤4")
    # dot.edges(["AB", "AC"])
    # dot.edge("C", "D", "判断", constraint='true')
    # dot.edge("D", "A", "递归", constraint='true')
    # print(dot.source)
    # svg = dot.pipe(format="svg")
    # print(svg)

    def __init__(self, **kwargs):
        if "editors" not in kwargs:
            kwargs['editors'] = list()
        else:
            editors = kwargs['editors']
            new_editors = list()
            for editor in editors:
                if isinstance(editor, DBRef):
                    new_editors.append(editor)
                elif isinstance(editor, ObjectId):
                    editor = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=editor)
                    new_editors.append(editor)
                elif isinstance(editor, str) and len(editor) == 24:
                    oid = ObjectId(editor)
                    editor = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=oid)
                    new_editors.append(editor)
                else:
                    pass
            kwargs['editors'] = new_editors
        if "owner" not in kwargs:
            ms = "owner必须"
            raise ValueError(ms)
        else:
            owner = kwargs['owner']
            if isinstance(owner, DBRef):
                pass
            elif isinstance(owner, ObjectId):
                kwargs['owner'] = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=owner)
            elif isinstance(owner, str) and len(owner) == 24:
                oid = ObjectId(owner)
                kwargs['owner'] = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=oid)
            else:
                ms = "owner错误,{}".format(owner)
                raise ValueError(ms)
        if "name" not in kwargs:
            ms = "name必须"
            raise ValueError(ms)
        if "nodes" not in kwargs:
            kwargs['nodes'] = list()
        if "edges" not in kwargs:
            kwargs['edges'] = list()
        if "desc" not in kwargs:
            kwargs['desc'] = ''
        if "image" not in kwargs:
            kwargs['image'] = b''
        if "time" not in kwargs:
            kwargs['time'] = datetime.datetime.now()

        super(MyDigraph, self).__init__(**kwargs)

    def draw(self) -> bytes:
        """
        绘制并以bytes方式返回svg格式的图片。
        :return:
        """
        # dot = Digraph(comment="this is a example", format="svg", encoding="utf-8")
        # dot.node("A", "步骤1", text="我是说明", id="No1", fontname="SimSun Microsoft YaHei")
        # dot.node("B", "步骤2", shape="star", color="red")
        # dot.node("C", "步骤3")
        # dot.node("D", "步骤4")
        # dot.edges(["AB", "AC"])
        # dot.edge("C", "D", "判断", constraint='true')
        # dot.edge("D", "A", "递归", constraint='true')
        # print(dot.source)
        # svg = dot.pipe(format="svg")
        # print(svg)
        dot = Digraph(comment=self.get_attr("name"), format="svg", encoding="utf-8")
        for node in self.get_attr("nodes"):
            dot.node(name=node['name'], label=node['label'], shape=node['shape'],
                     id=node['name'], fontname="SimSun Microsoft YaHei")
        for edge in self.get_attr("edges"):
            dot.edge(tail_name=edge['tail_name'], label=node['label'], head_name=node['head_name'],
                     id=node['_id'], fontname="SimSun Microsoft YaHei")
        svg = dot.pipe(format="svg")
        self.set_attr("image", svg)
        return svg



if __name__ == "__main__":
    pass