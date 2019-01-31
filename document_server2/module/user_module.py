#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from module.sql_module import *


class User(BaseModel):
    """
    用户表
    管理员账户密码: root/NISpider@123
    """
    id = PrimaryKeyField(int)
    user_name = CharField(max_length=256, unique=True)
    password = CharField(max_length=512)
    nick_name = CharField(max_length=256, null=True)
    role = CharField(max_length=128, default="user")
    root_path = CharField(max_length=3000)
    create_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "user_info"

    @classmethod
    @db.connection_context()
    def reg(cls, user_name: str, password: str, **kwargs) -> dict:
        """
        注册用户
        :param user_name:
        :param password:
        :param kwargs:
        :return:
        """
        mes = {"message":  "success"}
        user_id = None
        try:
            kwargs['user_name'] = user_name
            kwargs['password'] = password
            if 'root_path' not in kwargs:
                kwargs['root_path'] = user_name
            user = cls.create(**kwargs)
            user_id = user.save()
        except Exception as e:
            ms = "Error: {}".format(e)
            print(ms)
        finally:
            if user_id is None:
                mes['message'] = "insert fail"
            else:
                pass
            return mes

    @classmethod
    @db.connection_context()
    def login(cls, user_name: str, password: str) -> dict:
        """
        注册用户
        :param user_name:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        user = None
        try:
            user = cls.select().where((cls.user_name == user_name) & (cls.password == password)).get()
        except Exception as e:
            ms = "Error: {}".format(e)
            print(ms)
        finally:
            if user is None:
                mes['message'] = "用户名或密码错误"
            else:
                """
                如果是查询多个,那就是[x.get_dict() for x in p]
                """
                data = user.get_dict()
                mes['data'] = to_flat_dict(data)
            return mes

    @classmethod
    @db.connection_context()
    def edit(cls, doc: dict) -> dict:
        """
        更新信息
        :param doc:
        :return:
        """
        mes = {"message": "success"}
        user_id = doc.pop("id", None)
        if user_id is None or user_id == "":
            mes['message'] = "用户id不能为空"
        else:
            try:
                user_id = user_id if isinstance(user_id, int) else int(user_id)
            except Exception as e:
                print(e)
            finally:
                if isinstance(user_id, int):
                    sql_str = cls.update(**doc).where(cls.id == user_id)
                    row_number = sql_str.execute()
                    if isinstance(row_number, int):
                        pass
                    else:
                        mes['message'] = "修改失败"
                else:
                    mes['message'] = "无效的用户id"
                return mes

    @classmethod
    @db.connection_context()
    def change_pw(cls, user_id: int, old_pw: str, pw1: str, pw2: str) -> dict:
        """
        修改密码
        :param user_id:
        :param old_pw:
        :param pw1:
        :param pw2:
        :return:
        """
        mes = {"message": "success"}
        user = cls.select().where(cls.id == user_id).get()
        if old_pw != user.password:
            mes['message'] = "旧密码不正确"
        else:
            if pw1 != pw2:
                mes['message'] = "两次输入的新密码不一致"
            else:
                user.password = pw1
                user.save()
        return mes

    @classmethod
    @db.connection_context()
    def change_nick(cls, user_id: int, nick_name: str) -> dict:
        mes = {"message": "success"}
        user = cls.select().where(cls.id == user_id).get()
        user.nick_name = nick_name
        user.save()
        return mes

    @classmethod
    @db.connection_context()
    def remove(cls, user_id: int) -> dict:
        """
        删除用户
        :param user_id:
        :return:
        """
        mes = {"message": "success"}
        try:
            user_id = user_id if isinstance(user_id, int) else int(user_id)
        except Exception as e:
            print(e)
        finally:
            if isinstance(user_id, int):
                sql_str = cls.delete().where(cls.id == user_id)
                row_number = sql_str.execute()
                if isinstance(row_number, int):
                    pass
                else:
                    mes['message'] = "删除失败"
            else:
                mes['message'] = "无效的用户id"
            return mes


models = [User]
db.create_tables(models=models)

if __name__ == "__main__":
    # doc = {
    #     "user_name": "root",
    #     "password": '78b5585f9a45c2c60fd66d5e2aa08f88',
    #     "role": "root",
    #     "nick_name": "系统管理员"
    # }
    doc = {
        "user_name": "user_01",
        "password": '78b5585f9a45c2c60fd66d5e2aa08f88',
        "role": "user",
        "nick_name": "张三"
    }
    r = User.reg(**doc)
    print(r)
    # User.login(user_name="root", password="as")
    # sql = 'select * from user_info'
    # r = db.execute_sql(sql=sql)
    # print([x for x in r])
    pass