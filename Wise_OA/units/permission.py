#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.views import MethodView
from flask import Flask
from flask.blueprints import Blueprint
from units.peewee_sql import *


"""
权限管理模块
"""


class Rule(BaseModel):
    """
    (权限组的)规则
    """
    id = PrimaryKeyField()
    view_name = CharField()   # 视图名称. 和ViewUrlRule.view_name,是同一个值
    """
    规则字典. 源于ViewUrlRule.rules,然后做了设置.
    rules = {
                    "view": 1,
                    "update": 1,
                    "insert": 0,
                    "delete": 1
                }
    """
    rules = JSONField()

    class Meta:
        table_name = "rule_info"


class Role(BaseModel):
    """
    权限组
    """
    id = PrimaryKeyField()
    role_name = CharField()
    create_user = IntegerField()  # 创建者id, 应该是用户id.
    create_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "role_info"


class ViewUrlRule(BaseModel):
    """
    保存.App所有的路由规则. 任何一个视图函数允许的三种访问方法(view/edit/delete)的权限的取值范围都在这里保存
    """
    id = PrimaryKeyField()
    view_name = CharField(unique=True, index=True)  # 视图函数名称. 就是视图函数的类名,一个视图函数只有一个view_name
    methods = JSONField()  # 函数支持的方法, ['post', 'get']
    url_path = CharField(max_length=1000)  # 路由url, 仅仅保存,不做匹配
    """
    rules 是个字典.大致的样子如下
    rules = {
                    "view": 
                        {
                            0: "禁止访问",  # key是权限规则的值,取自MyView._access_rules的key
                            1: "允许访问"   # value是规则的备注.取自MyView._access_rules的value
                        },
                    "update": 
                        {
                            0: "禁止访问",
                            1: "允许访问"
                        },
                    "insert": 
                        {
                            0: "禁止访问",
                            1: "允许访问"
                        },
                    "delete": 
                        {
                            0: "禁止访问",
                            1: "允许访问"
                        }
                }
    """
    rules = JSONField()

    class Meta:
        table_name = "view_url_rule"


try:
    db.drop_tables(models=ViewUrlRule)   # 每次重启都要删除这个表
except ProgrammingError as e:
    print(e)
except Exception as e:
    raise e
finally:
    pass


class MyView(MethodView):
    """
    自定义视图.可以定制用户的访问权限
    字典_access_rules用来定义权限的之对应的级别.如果想有更多的访问级别限制,请扩展_access_rules字典.比如:
    _access_rules[0] = "禁止访问"
    _access_rules[1] = "允许访问全部"
    _access_rules[2] = "允许访问本部门"
    _access_rules[3] = "允许访问本组"

    最简单的逻辑就是:
    1. 涉及where条件过滤的,比如类似查看本部门所有人员信息这样的接口的访问.只有允许和禁止两种权限.
    ....

    子类建议进行以下这些属性的设置.
    必须设置的属性:
        1. _name 友好名称, 用于设置权限时识别对应的视图. 建议名称唯一
        2. _url_path 路由地址,  ,视图的url,同一蓝图下必须唯一.
        3. _root_role, 最高管理员的id, 只需要在MyView类下面设置一次即可.
    非必须设置的属性:
        1. 如果需要扩展属性的值, 请定义 _access_rules {0: 禁止访问, 1: 允许访问, 2: 自定义访问, ...}

    """
    _access_rules = dict()                  # 定义访问级别
    _can_setting = False                    # 是否能设备本视图的权限?(某些视图无需设置权限,比如登录和注销之类的视图)
    _access_rules[0] = "禁止访问"
    _access_rules[1] = "允许访问"

    _url_prefix = ""                                     # 蓝图的前缀,不需要设置.注册的时候会自动修正这个值
    _root_role = None                                    # 设置root权限组的id,此角色有全部的访问权限
    _endpoint = None                                     # 定义endpoint名 子类必须定义,否则自动使用类名称替代
    _url_path = None                                     # 定义url访问规则(不包括前缀). 子类必须定义,否则需要在注册时候手动添加,那样会缺失功能

    _name = ""                                           # 视图的说明.用于识别视图, 在编辑角色权限的时候很重要.
    _allowed_view = _access_rules                        # 允许的查看权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
    _allowed_edit = _access_rules                        # 允许的编辑权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
    _allowed_insert = _access_rules                      # 允许的添加权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
    _allowed_delete = _access_rules                      # 允许的删除权限的值 ,必须是_access_rules的子集.用于定义可用的权限的值.
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

    def rule_value(self, user: dict, rule_type: str = "view", role_field: str = "role_id",
                   role_table: str = "role_info", rule_table: str = "rule_info") -> int:
        """
        获取用户对本视图的访问权限的值, 一般是0/1,代表是禁止/允许访问.
        这是获取权限值的方法!!!
        :param user:  用户信息字典.
        :param rule_type:  规则类型  view/update/insert/delete
        :param role_field:    用户信息字典中,记录角色id的字段的名称.
        :param role_table:  记录角色信息的表名,本表的id就是用户信息中role_id对应的外键
        :param rule_table:  记录路由和权限值字典对应规则的表名,本表是role_table的子表
        :return:
        """
        resp = 0
        if isinstance(user, dict) and role_field in user:
            val = user[role_field]
            role_id = None
            try:
                role_id = val if isinstance(val, int) else int(val)
            except (TypeError, ValueError) as e:
                print(e)
            except Exception as e:
                raise e
            finally:
                if role_id is None:
                    pass
                else:
                    cls = self.__class__
                    if cls.is_root(user=user, role_field=role_field):
                        """最高管理员拥有全部权限"""
                        resp = 1
                    else:
                        view_name = cls.__name__  # 视图名
                        rule = Rule.select(Rule).where(view_name == view_name).get()

        else:
            pass
        return resp

    @classmethod
    def can_setting(cls) -> bool:
        """
        检查一个视图类是否需要设置权限?
        :return:
        """
        return cls._can_setting

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
        url_path = cls._url_path if url_path is None or url_path == "" else url_path
        return url_path if cls.get_url_prefix() == "" else "{}{}".format(cls.get_url_prefix(), url_path)

    @classmethod
    def register(cls, app: (Flask, Blueprint), url_path: str = None) -> None:
        """
        注册视图函数. 视图函数的规则定义忽略请求的方法而重视url
        :param app:   app或者blueprint
        :param url_path:  想对于app根路径/或者蓝图根路径(/blueprint)的视图函数的url,也可以在定义类的时候设置 cls.url_path,
                      不过在本函数中的rule参数会覆盖 cls.url_path,
        :return:
        """
        methods = cls.methods         # 视图支持的方法
        if methods is None:
            ms = "{}视图没有定义任何的方法".format(cls.__name__)
            raise AttributeError(ms)
        else:
            methods = [x.lower() for x in methods]
            url_path = url_path.strip() if url_path else cls._url_path
            if url_path is None or url_path == "":
                ms = "url_path 没有定义"
                raise ValueError(ms)
            else:
                endpoint = cls._endpoint if cls._endpoint else cls.__name__
                """向flask的app注册路由"""
                app.add_url_rule(rule=url_path, view_func=cls.as_view(name=endpoint), methods=methods)
                if cls.can_setting():
                    """处理允许访问的值"""
                    desc = cls.__dict__['__doc__']  # 类的注释
                    rules = {
                        "view": cls._allowed_view,
                        "edit": cls._allowed_edit,
                        "insert": cls._allowed_insert,
                        "delete": cls._allowed_delete
                    }
                    doc = {
                        "view_name": cls._name,        # 用于标识的简短的名称
                        "methods": methods,
                        "endpoint": endpoint,   # 如果不在子类中重新定义endpoint的话,endpoint和name是同一个值
                        "url_path": url_path,
                        "desc": desc,
                        "rules": rules,
                        "time": datetime.datetime.now()
                    }
                    r = None
                    if r is None:
                        ms = "注册视图失败: {}".format(doc)
                        raise ValueError(ms)
                    else:
                        pass
                else:
                    pass


models = [
    ViewUrlRule, Rule, Role
]
db.create_tables(models=models)


if __name__ == "__main__":
    pass
