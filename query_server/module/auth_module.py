import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
from pymongo import WriteConcern


ObjectId = orm_module.ObjectId
GrantAuthorizationInfo = orm_module.GrantAuthorizationInfo


"""身份验证模块"""


class A(orm_module.BaseFile):
    _table_name = "test_a"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name_a'] = str
    type_dict['phone_a'] = str
    type_dict['time'] = datetime.datetime

    GrantAuthorizationInfo.register(_table_name, type_dict, True)


class B(orm_module.BaseFile):
    _table_name = "test_b"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name_b'] = str
    type_dict['phone_b'] = str
    type_dict['time'] = datetime.datetime

    GrantAuthorizationInfo.register(_table_name, type_dict, True)


class User(orm_module.BaseDoc):
    """用户类"""
    _table_name = "test_user"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['password'] = str

    @classmethod
    @orm_module.OperateLog.log
    def hello(cls, name: str, age: int = 12):
        s = "hello world! my name is {}, I am {} years old.".format(name, age)
        return s

    @orm_module.OperateLog.log
    def hello2(self, name: str, age: int = 12):
        s = "{}! my name is {}, I am {} years old.".format(str(self), name, age)
        return s


@orm_module.OperateLog.log
def test():
    ls = GrantAuthorizationInfo.class_and_attribute(True)
    print(ls)


if __name__ == "__main__":
    # GrantAuthorizationInfo.register(table_name='a', columns=[], force=True)
    # test()
    # x = User.hello("jack", age="12")
    # print(x)
    u = User()
    print(u.hello2("jack", age="12"))
    pass




