#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.views import MethodView
from flask import Flask
from flask.blueprints import Blueprint
from collections import OrderedDict
from units.peewee_sql import *


"""
权限管理模块
"""


class ViewUrlRule(BaseModel):
    """
        保存.App所有的路由规则. 任何一个视图函数允许的三种访问方法(view/edit/delete)的权限的取值范围都在这里保存
    """
    id = PrimaryKeyField()
    view_name = CharField()  # 视图函数名称. 就是视图函数的类名,一个视图函数只有一个view_name
    methods = JSONField()  # 函数支持的方法,
    url_path = CharField(max_length=1000)  # 路由url
    """
    rule_dict 是个字典.大致的样子如下
    rule_dict = {
                    "view": {
                            1: 
                        }
                }
    """
    rule_dict = JSONField()
    rule_value = IntegerField()  # 权限规则的值,取自MyView._access_rules的key
    rule_desc = CharField(max_length=1000)   # 规则的备注.取自MyView._access_rules的value

    class Meta:
        table_name = "view_url_rule"


db.drop_tables(models=ViewUrlRule)   # 每次重启都要删除这个表


class MyView(MethodView):
    """
    自定义视图.可以定制用户的访问权限
    字典_access_rules用来定义权限的之对应的级别.如果想有更多的访问级别限制,请扩展_access_rules字典.比如:
    _access_rules[0] = "禁止访问"
    _access_rules[1] = "允许访问全部"
    _access_rules[2] = "允许访问本部门"
    _access_rules[3] = "允许访问本组"
    ....

    """
    _access_rules = OrderedDict()           # 定义访问级别
    _access_rules[0] = "禁止访问"
    _access_rules[1] = "允许访问"

    _url_prefix = ""                                     # 蓝图的前缀,一般不需要设置.注册的时候会自动修正这个值
    _root_role = None                                    # 设置root权限组的id,此角色有全部的访问权限
    _endpoint = None                                     # 定义endpoint名 子类必须定义,否则自动使用类名称替代
    _rule = None                                         # 定义url访问规则. 子类必须定义,否则需要在注册时候手动添加,那样会缺失功能
    _name = ""                                           # 视图的说明.用于识别视图, 在编辑角色权限的时候很重要.
    _allowed_view = list(_access_rules.keys()).sort()    # 允许的查看权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
    _allowed_edit = _allowed_view                        # 允许的编辑权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
    _allowed_delete = _allowed_edit                      # 允许的删除权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
    """
    建议的权限定义方式: 
    _allowed_view = [0, 1, 2, 3] 
    _allowed_edit = [0, 1, 2, 3] 
    _allowed_delete = [0, 1, 2, 3] 
    最简情况下,你可以只定义_allowed_view:
    _allowed_view = [0, 1, 2, 3] 
    如果不允许设置某一类操作,请做如下设置
    _allowed_edit = [] 
    千万不要 _allowed_edit = None 或者不设置.那样默认的等于和_allowed_view一样的设置

    子类继承的时候,建议重写以下函数以实现精确的权限控制:
    1. cls._get_filter  
    用于详细定义和权限值对应的过滤器.这个函数只有uer_id(用户id),access_value(权限值) operate(访问类型),返回过滤器字典
    """

    def is_root(self, user: dict, role_field: str = "role_id") -> bool:
        """
        检查用户是否是管理员身份
        :param user:
        :param role_field: 角色id在用户信息中对应的字段
        :return:
        """
        cls = self.__class__
        root_role_id = cls._root_role
        if root_role_id is None:
            ms = "管理员权限组ID未设置"
            raise ValueError(ms)
        elif user.get(role_field) == root_role_id:
            return True
        else:
            return False

    @classmethod
    def get_rules(cls, operate: str = "view") -> list:
        """
        获取某种类型的操作设定的权限值的集合
        :param operate: 权限的类型 分为 view/edit/delete  查看/编辑/删除
        :return:
        """
        res = list()
        if operate == "view":
            res = cls._allowed_view
        elif operate == "edit":
            res = cls._allowed_view if cls._allowed_edit is None else cls._allowed_edit
        elif operate == "delete":
            res = cls.get_rules("edit") if cls._allowed_delete is None else cls._allowed_delete
        else:
            pass
        return res

    @classmethod
    def __set_url_prefix(cls, url_prefix: str) -> None:
        """
        设置路由规则的前缀,在注册视图的时候自动调用
        :param url_prefix:
        :return:
        """
        cls._url_prefix = url_prefix

    @classmethod
    def get_url_prefix(cls) -> str:
        """
        获取路由规则的前缀
        :return:
        """
        return cls._url_prefix

    @classmethod
    def get_full_path(cls, url_path: str = None) -> str:
        """
        获取url_path的完全路径
        :param url_path:
        :return:
        """
        url_path = cls._rule if url_path is None or url_path == "" else url_path
        return url_path if cls.get_url_prefix() == "" else "{}{}".format(cls.get_url_prefix(), url_path)

    @classmethod
    def register(cls, app: (Flask, Blueprint), rule: str = None) -> None:
        """
        注册视图函数. 视图函数的规则定义忽略请求的方法而重视url
        :param app:   app或者blueprint
        :param rule:  想对于app根路径/或者蓝图根路径(/blueprint)的视图函数的url,也可以在定义类的时候设置 cls._rule,
                      不过在本函数中的rule参数会覆盖 cls._rule,
        :return:
        """
        methods = cls.methods
        if methods is None:
            ms = "{}视图没有定义任何的方法".format(cls.__name__)
            raise AttributeError(ms)
        else:
            methods = [x.lower() for x in methods]
            rule = rule.strip() if rule else cls._rule
            if rule is None or rule == "":
                ms = "rule 没有定义"
                raise ValueError(ms)
            else:
                endpoint = cls._endpoint if cls._endpoint else cls.__name__
                app.add_url_rule(rule=rule, view_func=cls.as_view(name=endpoint), methods=methods)
                """处理允许访问的值"""
                view_rules = list()
                for val in cls.get_rules("view"):
                    if val in cls._access_rules:
                        temp = {"value": val, "desc": cls._access_rules[val]}
                        view_rules.append(temp)
                view_rules.sort(key=lambda obj: obj['value'], reverse=False)
                edit_rules = list()
                for val in cls.get_rules("edit"):
                    if val in cls._access_rules:
                        temp = {"value": val, "desc": cls._access_rules[val]}
                        edit_rules.append(temp)
                edit_rules.sort(key=lambda obj: obj['value'], reverse=False)
                delete_rules = list()
                for val in cls.get_rules("delete"):
                    if val in cls._access_rules:
                        temp = {"value": val, "desc": cls._access_rules[val]}
                        delete_rules.append(temp)
                delete_rules.sort(key=lambda obj: obj['value'], reverse=False)
                desc = cls.__dict__['__doc__']
                rules = {
                    "view": view_rules,
                    "edit": edit_rules,
                    "delete": delete_rules
                }
                doc = {
                    "name": cls._name,
                    "methods": methods,
                    "endpoint": endpoint,
                    "url_path": url_path,
                    "desc": desc,
                    "rules": rules,
                    "time": datetime.datetime.now()
                }
                w = get_write_concern()
                r = FlaskUrlRule.insert_one(doc=doc, write_concern=w)
                if r is None:
                    ms = "注册视图失败: {}".format(doc)
                    raise ValueError(ms)
                else:
                    pass


class Rule(BaseModel):
    """
    (权限组的)规则
    """

    class Meta:
        table_name = "rule_info"


class Role(BaseModel):
    """
    权限组
    """

    class Meta:
        table_name = "role_info"


models = [
    ViewRule, Rule, Role
]
db.create_tables(models=models)


if __name__ == "__main__":
    pass
