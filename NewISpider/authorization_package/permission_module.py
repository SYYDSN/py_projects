#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from orm_unit.sql_module import *
import datetime
from toolbox.log_module import get_logger


"""
权限模块
包括:
1. (业务接口)规则表 rule  一个具体的业务接口对应一个规则, 只有允许和拒绝两种选择
2. 权限(规则)组表 rule_group   逻辑上关联或者业务上相近,可以归为一组的rule组成权限组.
3. 角色表  Role  一个角色包含多个rule_group的副本.这个副本组合起来决定这个role的权限
"""


logger = get_logger()


class RuleRegisterException(BaseException):
    """
    自定义的插入异常
    """

# 系统定义部分


class RuleTemplate(BaseModel):
    """
    (业务接口的)权限规则模板,
    权限规则和api视图路由是1:1的关系
    """
    id = PrimaryKeyField(help_text="权限规则的id,权限规则和api视图路由是1:1的关系")
    api_url = CharField(max_length=191, unique=True, help_text="接口的url地址,不包含host,port和参数的全路径接口path,唯一")
    rule_name = CharField(max_length=128, unique=True, help_text=" 接口/规则的名字.唯一")
    desc = CharField(max_length=1000, default='', help_text='描述.本接口是干什么的?')
    status = IntegerField(default=1, help_text="是否可用,默认是可用.0的话就不能被选择加入权限组了.")
    reg_time = DateTimeField(default=datetime.datetime.now, help_text="注册时间")

    class Meta:
        table_name = "rule_template"

    @classmethod
    @db.connection_context()
    def register_rule(cls, api_url: str, api_name: str, desc: str = ""):
        """
        注册业务权限接口路由.此接口应该有视图类/函数自动调用进行注册
        :param api_url: 接口地址,唯一.
        :param api_name: 接口名字,唯一
        :param desc:
        :return: 注册失败会抛出异常
        """
        obj = cls(api_url=api_url, api_name=api_name, desc=desc)
        try:
            obj.save()
        except IntegrityError as e:
            print(e)
            s = e.args[1]
            if "Duplicate entry" in s and "api_url" in s:
                raise RuleRegisterException("重复的api_url: {}".format(api_url))
            elif "Duplicate entry" in s and "api_name" in s:
                raise RuleRegisterException("重复的api_name: {}".format(api_name))
            else:
                raise RuleRegisterException("错误原因: {}".format(e))
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            pass

    @classmethod
    @db.connection_context()
    def get_all(cls) -> dict:
        """
        获取所有可用来编辑权限的接口视图路由
        :return:
        """
        mes = {"message": "success"}
        res = cls.select(cls)
        res= [x.get_dict(flat=True) for x in res]
        mes['data'] = res
        return mes


class AppModule(BaseModel):
    """
    app模块信息
    """
    id = AutoField(primary_key=True)
    app_name = CharField(max_length=128, unique=True)
    desc = CharField()
    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统管理员id")

    class Meta:
        table_name = "app_module"

    @classmethod
    @db.connection_context()
    def add_app(cls, user_id: int, app_name: str, desc: str = '') -> dict:
        """
        添加模块
        :param user_id:
        :param app_name:
        :param desc:
        :return:
        """
        mes = {"message": "success"}
        doc = dict(creator=user_id, last_user=user_id, app_name=app_name, desc=desc)
        try:
            sql = cls.insert(**doc)
            app_id = sql.execute()
        except IntegrityError as e:
            logger.exception(e)
            print(e)
            s = e.args[1]
            if "Duplicate entry" in s and "app_name" in s:
                mes['message'] = "重复的app模块名称"
            else:
                mes['message'] = "内部错误"
        except Exception as e:
            logger.exception(e)
            print(e)
            mes['message'] = "保存失败"
        finally:
            return mes

    @classmethod
    @db.connection_context()
    def update_app(cls, user_id: int, app_id: int, app_name: str, status: int, desc: str = '') -> dict:
        """
        修改模块
        :param user_id:
        :param app_id:
        :param app_name:
        :param status:
        :param desc:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=app_id)
        except DoesNotExist as e:
            logger.exception(e)
            print(e)
            mes['message'] = "对象不存在"
        finally:
            if obj is None:
                pass
            else:
                obj.last_user = user_id
                obj.last_time = datetime.datetime.now()
                obj.app_name = app_name
                obj.status = status
                if desc is not None:
                    obj.desc = desc
            return mes

    @classmethod
    @db.connection_context()
    def delete_app(cls, app_id: int) -> dict:
        """
        删除app模块
        :param app_id:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=app_id)
        except DoesNotExist as e:
            logger.exception(e)
            print(e)
            mes['message'] = "对象不存在"
        finally:
            if obj is None:
                pass
            else:
                obj.delete_instance()
            return mes


class UsableApp(BaseModel):
    """
    集团可用的app
    """
    id = AutoField(primary_key=True)
    app_id = IntegerField(help_text="app的id")
    hotel_group_id = IntegerField(help_text="集团id,单店的酒店,需要创建一个虚拟的集团")
    usable = IntegerField(default=0, help_text="模块是否可用?1表示可用")
    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统管理员id")

    class Meta:
        table_name = "usable_app"
        indexes = [
            (("app_id", "hotel_group_id"), True),
        ]

    @classmethod
    def init_status(cls, user_id: int, hotel_group_id, apps: list) -> dict:
        """
        初始化/批量添加可用的app信息
        :param user_id:
        :param hotel_group_id:
        :param apps: [{"app_id": app_id, "usable": usable},...]
        :return:
        """
        mes = {"message": "success"}
        now = datetime.datetime.now()
        d2 = {
            "hotel_group_id": hotel_group_id,
            "creator": user_id,
            "last_user": user_id,
            "create_time": now,
            "last_time": now,

        }
        apps = [update_dict(app, d2) for app in apps]
        with db.atomic() as transaction:
            try:
                cls.insert_many(rows=apps)
            except Exception as e:
                logger.exception(e)
                print(e)
                mes['message'] = "保存失败"
                transaction.rollback()
            finally:
                pass
        return mes

    @classmethod
    @db.connection_context()
    def add_record(cls, user_id: int, app_id: int, hotel_group_id: int, usable: int = 0) -> dict:
        """
        添加一条app是否可用的记录
        :param user_id:
        :param app_id:
        :param hotel_group_id:
        :param usable:
        :return:
        """
        mes = {"message": "success"}
        now = datetime.datetime.now()
        doc = {
            "creator": user_id, "app_id": app_id, "hotel_group_id": hotel_group_id,
            "last_user": user_id, "create_time": now, "last_time": now,
            "usable": usable
        }
        try:
            obj = cls(**doc)
            obj.save()
        except Exception as e:
            logger.exception(e)
            print(e)
            s = e.args[1]
            if "Duplicate entry" in s:
                mes['message'] = "重复的设置"
            else:
                mes['message'] = "保存失败"
        finally:
            return mes

    @classmethod
    @db.connection_context()
    def change_status(cls, user_id: int, record_id: int, usable: int = 0) -> dict:
        """
        修改一条app是否可用的记录,也就是常说的停用启用.
        :param user_id:
        :param record_id:
        :param usable:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=record_id)
        except DoesNotExist as e:
            print(e)
        finally:
            if obj is None:
                mes['message'] = "对象不存在"
            else:
                now = datetime.datetime.now()
                obj.last_user = user_id
                obj.last_time = now
                obj.usable = usable
                obj.save()
            return mes

    @classmethod
    @db.connection_context()
    def delete_record(cls, record_id: int) -> dict:
        """
        删除一条app是否可用的记录
        :param record_id:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=record_id)
        except DoesNotExist as e:
            print(e)
        finally:
            if obj is None:
                mes['message'] = "对象不存在"
            else:
                obj.delete_instance()
            return mes


class RuleGroupTemplate(BaseModel):
    """
    权限规则组模板.系统管理员操作
    权限组模板和权限模板(RuleTemplate)是n:n的关系
    系统只有一套权限组.理论上: 只有系统管理员能够才能创建一个规则组.
    在创建角色的时候.都从本表选择权限组进行权限设置的.即使是对单个权限的设置.
    也是必须归属于权限组的权限才可以进行权限值设置.无权限组归属的权限无法被选择和设置权限的值
    """

    group_name = CharField(max_length=128, help_text="权限组名称")
    desc = CharField(max_length=1000, default='权限组说明')
    app_id = ForeignKeyField(column_name="app_id", model=AppModule, field=AppModule.id, backref="rule_group")
    is_public = IntegerField(default=1, help_text='本权限组是否面向用户开放?')
    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统管理员id")

    class Meta:
        table_name = "rule_group_template"

    @classmethod
    def create_group_template(cls, user_id: int, app_id: int, group_name: str, desc: str = "", rules: list = list()) -> dict:
        """
        创建权限组.
        此命令只应该由系统管理员在创建初始的权限组的时候执行.
        :param user_id:
        :param app_id:
        :param group_name: 比如我们可以把 创建用户, 编辑用户和删除用户信息都放到一个 用户管理组
        :param desc: 对这个组的说明,比如: "对酒店内部工作人员的用户信息的管理"
        :param rules: 权限规则的id的list对象.
                      [
                        {"rule_id": rule_id, "permission_value": permission_value},
                        {"rule_id": rule_id, "permission_value": permission_value},
                        ...
                      ]
        :return:
        """
        mes = {"message": "success"}
        now = datetime.datetime.now()
        kw = dict(
            creator=user_id, group_name=group_name, desc=desc, is_public=1,
            create_time=now, last_user=user_id, last_time=now, app_id=app_id
        )
        group_id = 0
        with db.atomic() as transaction:
            try:

                insert = cls.insert(**kw)
                group_id = insert.execute()
                print(group_id)
            except IntegrityError as e:
                logger.exception(e)
                mes = {"message": "重复的权限组名称"}
            except Exception as e:
                logger.exception(e)
                mes['message'] = "数据保存失败"
            finally:
                if mes['message'] == "success":
                    """开始保存RuleAndGroupRelation的实例"""
                    if len(rules) > 0:
                        rules = [update_dict(x, {'group_id': group_id}) for x in rules]
                        rules = check_composite_keys(raw_doc=rules,
                                                     keys=RuleAndGroupTemplateRelation._meta.indexes[0][0])
                        ids = list()
                        try:
                            insert2 = RuleAndGroupTemplateRelation.insert_many(rows=rules)
                            ids = insert2.execute()
                            print(ids)
                        except Exception as e:
                            logger.exception(e)
                            s = e.args[1]
                            if "foreign key constraint fails" in s:
                                mes['message'] = "至少一条权限规则的id错误,请联系管理员"
                            else:
                                mes['message'] = "保存权限组定义失败"
                        finally:
                            if ids == 0:
                                transaction.rollback()
                            else:
                                pass
                    else:
                        pass
                else:
                    pass
        return mes

    @classmethod
    @db.connection_context()
    def update_group_template(cls, user_id: int, app_id: int, group_id: int, group_name: str, desc: str = "") -> dict:
        """
        修改权限组模板, 只能修改名称和备注
        :param user_id:
        :param app_id:
        :param group_id:
        :param group_name:
        :param desc:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=group_id)
        except DoesNotExist as e:
            logger.exception(e)
            print(e)
        finally:
            if obj is None:
                mes['success'] = "对象不存在"
            else:
                obj.group_name = group_name
                obj.app_id = app_id
                if desc is not None:
                    obj.desc = desc
                obj.last_user = user_id
                obj.last_time = datetime.datetime.now()
                try:
                    obj.save()
                except Exception as e:
                    logger.exception(e)
                    print(e)
                    mes['message'] = "保存数据库失败"
                finally:
                    pass
            return mes

    @classmethod
    @db.connection_context()
    def delete_group_template(cls, group_id: int) -> dict:
        """
        删除权限组模板
        :param group_id:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=group_id)
        except DoesNotExist as e:
            logger.exception(e)
            print(e)
        finally:
            if obj is None:
                mes['success'] = "删除的对象不存在"
            else:
                count = RuleAndGroupTemplateRelation.select().count()
                if count == 0:
                    obj.delete()
                else:
                    mes['message'] = "请先清空权限组模板下的权限规则"
            return mes


class RuleAndGroupTemplateRelation(BaseModel):
    """
    记录权限组模板和权限模板(RuleTemplate)之间关系的表.
    系统/酒店管理员在创建角色的时候,实际上都是从这个表拷贝的信息
    """
    id = AutoField(primary_key=True, verbose_name="记录权限组模板和权限模板(RuleTemplate)之间关系的表")
    group_id = ForeignKeyField(model=RuleGroupTemplate, column_name="group_id", field="id", backref="relation", help_text="权限规则组模板RuleGroupTemplate.id")
    rule_id = ForeignKeyField(model=RuleTemplate, column_name="rule_id", field="id", backref="relation", help_text="权限规则RuleTemplate.id")
    api_url = CharField(help_text="冗余字段,从RuleTemplate.api_url")
    rule_name = CharField(help_text="冗余字段,从RuleTemplate.rule_name拷贝")
    permission_value = IntegerField(default=0, help_text="权限值")
    order_value = IntegerField(default=0, help_text="(权限组内)排序的值")
    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统管理员id")
    status = IntegerField(default=1, help_text="是否生效,默认是生效.0的话即使加入的权限里面也不再生效")

    class Meta:
        table_name = "rule_and_group_template_relation"
        indexes = (
            # 联合索引,第二个布尔值参数表示是否唯一,注意,如果只有一个多列索引的话,末尾一定要加逗号
            (('group_id', 'rule_id'), True),
        )

    @classmethod
    def add_relations(cls, user_id: int, rules: list, group_id: int) -> dict:
        """
        向权限组模板增加一/多条规则, 这是系统管理员在调整权限组模板时所做的操作.
        :param user_id:
        :param rules: {"rule_id": rule_id, "rule_name": rule_name, "api_url": api_url, "value": permission_value}
        :param group_id:
        :return:
        """
        mes = {"message": "success"}
        relations = list()
        for rule in rules:
            rule['user_id'] = user_id
            rule['group_id'] = group_id
            relations.append(rule)
        with db.atomic() as transaction:
            try:
                cls.insert_many(rows=relations)
            except Exception as e:
                logger.exception(e)
                print(e)
                mes['message'] = "保存数据失败"
                transaction.rollback()
            finally:
                pass
        return mes

    @classmethod
    @db.connection_context()
    def update_relation(cls, user_id: int, relation_id: int, value: int, status: int) -> dict:
        """
        系统管理员调整权限组模板中的权限规则的默认值
        :param user_id:
        :param relation_id: 权限组模板中的权限规则的id
        :param value:
        :param status:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=relation_id)
        except DoesNotExist as e:
            print(e)
        finally:
            if obj is None:
                mes['message'] = "对象不存在"
            else:
                obj.permission_value = value
                obj.status = status
                obj.last_user = user_id
                obj.last_time = datetime.datetime.now()
                obj.save()
            return mes

    @classmethod
    @db.connection_context()
    def delete_relation(cls, relation_id: int) -> dict:
        """
        系统管理员把权限规则从权限组模板中移除
        :param relation_id:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls.get_by_id(pk=relation_id)
        except DoesNotExist as e:
            print(e)
        finally:
            if obj is None:
                mes['message'] = "对象不存在"
            else:
                obj.delete_instance()
            return mes


# 以下是用户级别部分,可以自定义


class UserRole(BaseModel):
    """
    用户角色
    """
    id = AutoField(primary_key=True, help_text="角色对象的id")
    role_name = CharField(max_length=128, help_text='角色名,和hotel_group_id, hotel_id 构成多重索引')
    hotel_group_id = IntegerField(default=0, help_text="酒店集团id, 指向HotelGroup.id, 0表示是本记录是系统管理员创建的角色")
    hotel_id = IntegerField(default=0, help_text="酒店id, 指向Hotel.id, 0表示是本记录是系统管理员创建的角色")
    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管/酒店理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统/酒店管理员id")

    class Meta:
        table_name = "user_role"
        indexes = {
            # 集团id,酒店id,和角色名称构成联合唯一索引. 可以用cls._meta.indexes[0][0]方法获取
            (("hotel_group_id", "hotel_id", "role_name"), True),
        }


class UserRoleApp(BaseModel):
    """
    用户角色能访问的app的规则
    """
    id = AutoField(primary_key=True)
    role_id = ForeignKeyField(model=UserRole, column_name="role_id", field="id", help_text="角色id", backref="rule_id")
    app_id = ForeignKeyField(model=UsableApp, column_name="app_id", field="id", help_text="可用的app_id", backref="app_id")

    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管/酒店理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统/酒店管理员id")

    class Meta:
        table_name = "user_role_app"


class UserRoleRule(BaseModel):
    """
    用户角色的权限规则,
    这个表里的信息是从RuleTemplate中复制过来的
    """
    id = AutoField(primary_key=True)
    role_id = ForeignKeyField(model=UserRole, column_name="role_id", field="id", help_text="角色id", backref="rule_id")
    raw_rule = ForeignKeyField(model=RuleAndGroupTemplateRelation, field="id", column_name="raw_rule_id",
                               backref="user_rule", help_text="原始权限id, 指向RuleAndGroupTemplateRelation.id")
    permission_value = IntegerField(default=0, help_text="权限值")
    create_time = DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    last_time = DateTimeField(default=datetime.datetime.now, help_text="最后一次修改时间")
    creator = IntegerField(help_text='创建人.指向系统管/酒店理员id')
    last_user = IntegerField(help_text="最后修改人.指向系统/酒店管理员id")

    class Meta:
        table_name = "user_role_rule"





models = [
    RuleTemplate,
    RuleGroupTemplate,
    RuleAndGroupTemplateRelation,
    AppModule,
    UsableApp,
    UserRole,
    UserRoleApp,
    UserRoleRule,
]
db.create_tables(models=models)


if __name__ == "__main__":
    """添加规则"""
    # args = {
    #     "api_url": "/system/user/add",
    #     "api_name": "管理员添加用户"
    # }
    # RuleTemplate.register_rule(**args)
    # """创建权限组"""
    # args = {
    #     "user_id": 12,
    #     "group_name": "用户管理",
    #     "desc": "管理用户的模块",
    #     "rules": [
    #         {"rule_id": 3, "permission_value": 0},
    #         {"rule_id": 2, "permission_value": 1},
    #         {"rule_id": 1, "permission_value": 1},
    #     ]
    # }
    # result = RuleGroupTemplate.create_group_template(**args)
    # print(result)
    """添加app"""
    # AppModule.add_app(user_id=12, app_name="财务管理", desc="heheh")
    """添加可用的app"""
    # print(UsableApp.add_record(user_id=12, app_id=1, hotel_group_id=2))
    """更新权限组模板"""
    # RuleGroupTemplate.update_group_template(user_id=12, group_id=3, group_name="用户管理", desc="管理本酒店员工账户")
    """添加角色"""
    print(UserRole.add_record(id=9, role_name="系统管理员", creator=12, hotel_group_id=1, hotel_id=3))
    pass