# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from graphviz import Digraph
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


class MyDigraph(mongo_db.BaseDoc):
    """
    有向图/流程图
    """
    _table_name = "digraph_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str        # 图的名称,理论上唯一
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
                "shape": "rarrow", # 形状 默认为ellipse(椭圆)
                "name": "我是加工数据的模块",  # svg格式中,鼠标悬停在节点上面时显示的文字,必须
                "label": "数据模块",  # 节点中间的文字,必须
                "color": "red",      # 节点的边框的颜色默认为black
                "fontcolor": "green",  # 字体颜色,默认为black
                "id": "dom_id",        # svg内部的元素的id.可以当作DOM的id来处理.默认为类型+索引
                "URL": url,    # 链接,注意这个参数区分大小写,而且是在当前页面打开.
                "fontname": "Microsoft YaHei",  # 字体名称 
                "fontnames": "SimSun Microsoft YaHei",  # 多个字体名称 
                "fontsize": 14,              # 字体大小,默认14px
            }
    """
    type_dict['nodes'] = list
    type_dict['_id'] = ObjectId
    type_dict['_id'] = ObjectId


"""format可选多种格式: svg/png/pdf"""
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
