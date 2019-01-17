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


"""
权限管理模块
"""


class MyView(MethodView):
    """
    自定义视图.可以定制用户的访问权限
    字典_access_rules用来定义权限的之对应的级别
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
    def __set_url_prefix(cls, url_prefix: str) -> None:
        """
        设置路由规则的前缀,在注册视图的时候自动调用
        :param url_prefix:
        :return:
        """
        cls._url_prefix = url_prefix

    @classmethod
    def register(cls, app: (Flask, Blueprint), rule: str = None) -> None:
        """
        注册视图函数.
        :param app:
        :param rule:
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
                rule = rule if rule.startswith("/") else "/{}".format(rule)
                if isinstance(app, Blueprint):
                    url_prefix = app.url_prefix
                else:
                    url_prefix = ""
                cls.__set_url_prefix(url_prefix=url_prefix)
                app.add_url_rule(rule=rule, view_func=cls.as_view(name=endpoint), methods=methods)
                url_path = "{}{}".format(url_prefix, rule)
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




if __name__ == "__main__":
    pass
