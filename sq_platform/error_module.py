# -*- coding: utf-8 -*-
from mongo_db import BaseDoc, get_conn
from bson.objectid import ObjectId
import json


"""自定义错误模块"""


class ErrorCode(BaseDoc):
    """错误代码类"""
    _table_name = "error_code_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['code'] = int  # 错误代码,唯一
    type_dict['description'] = str  # 对错误码的注释

    def __init__(self, **kwargs):
        kwargs = {k: (int(v) if k == "code" else v) for k, v in kwargs.items()}
        super(ErrorCode, self).__init__(**kwargs)

    @classmethod
    def query_error_code(cls, error_code: int) -> dict:
        """
        查询错误代码
        :param error_code: 错误代码
        :return:
        成功 {"message": "success", "data":{"description": "description", ”error_code": error_code}}
        失败 {"message": "没有找到预期的对象", ”error_code": 3004, "args":{"error_code": error_code}}
        """
        raw = error_code
        message = {"message": "没有找到预期的对象", "error_code": 3004, "args": {"error_code": raw}}
        try:
            error_code = int(error_code)
        except ValueError as e:
            print(e)
            error_code = 0
        except TypeError as e:
            print(e)
            error_code = 0
        finally:
            if error_code == 0:
                pass
            else:
                error = cls.find_one(code=error_code)
                if error is None:
                    pass
                else:
                    message = {"message": "success", "data": {"error_code": error.get_attr("code"),
                                                              "description": error.get_attr("description")}}
            return message


    @classmethod
    def show(cls, code: (str, int, float))->dict:
        """
        显示某一个或者全部错误代码和注释，注意，如果错误代码很多的话，需要重构此方法
        :param code: 错代码
        :return: 包含字典的数组的字典 {"message":"success","data":[dict_1, dict_2..., dict_n]}
        """
        message = {"message": "success"}
        try:
            code = int(code)
        except ValueError as e:
            print(e)
            message['message'] = "{}无法转换成int类型".format(code)
        except Exception as e:
            print(e)
            message['message'] = "未预知的错误:{}".format(e)
        finally:
            if message['message'] == "success":
                res = cls.find(to_dict=True, code=code)
                data = list() if res is None else res
                message['data'] = data
            else:
                pass
            return message

    @classmethod
    def get_code(cls, code, desc=''):
        """
        获取一个错误代码的实例
        :param code: 错误代码
        :param desc: 错误代码备注
        :return:
        """
        try:
            code = int(code)
        except ValueError as e:
            raise e
        if desc == "":
            old = cls.find_one(code=code)
            if old is None:
                raise ValueError("错误代码{} 还未被定义")
            else:
                return old
        else:
            old = cls.find_one(code=code)
            if old is not None:
                raise ValueError("错误代码{} 已经被定义")
            else:
                obj = cls(code=code, description=desc)
                _id = obj.insert()
                obj._id = _id
                return obj

    def to_json(self):
        """返回对象的json格式"""
        obj = self.to_flat_dict()
        return json.dumps(obj)


class ReturnMessage:
    """返回消息类"""
    def __init__(self):
        self.message = "success"

    def add_error(self, error_code, **kwargs):
        """
        追加一个错误代码
        :param error_code: int 错误代码 3
        3000 参数缺失
        3001 参数类型错误
        4000 没有找到预期对象
        5000 程序处理失败
        :param kwargs: dict 相关参数
        :return:None
        """
        code_obj = ErrorCode.get_code(error_code)
        self.__dict__['error_code'] = code_obj.code
        self.__dict__['args'] = kwargs
        self.message = code_obj.description

    def to_dict(self):
        """转换字典格式"""
        return self.__dict__

    def to_json(self):
        """json化"""
        return json.dumps(self.to_dict())

    @classmethod
    def wrap(cls, message_dict: dict, error_code: int, **kwargs)->dict:
        """
        对消息字典进行包装，返回消息字典
        :param message_dict: 原始消息字典。 dict 这个参数的名称必须是message
        :param error_code:  错误代码  4位 int
        :param kwargs:   相关参数,一般是locals()
        :return: dict
        """
        code_obj = ErrorCode.get_code(error_code)
        message_dict['message'] = code_obj.description
        message_dict['error_code'] = code_obj.code
        args = {k: str(v) for k, v in kwargs.items()}
        message_dict['args'] = args
        return message_dict


def pack_message(message_dict: dict = None, error_code: int = 3000, **kwargs)->dict:
    """
    对消息字典进行包装，返回消息字典,实际上是ReturnMessage.wrap方法的函数化
    :param message_dict: 原始消息字典。 dict ,这个参数的名称必须是message
    :param error_code:  错误代码  4位 int
    :param kwargs:   相关参数,一般是locals()
    :return: dict
    """
    message_dict = {"message": "success"} if message_dict is None else message_dict
    return ReturnMessage.wrap(message_dict, error_code, **kwargs)


class RepeatError(Exception):
    """自定义一个重复类"""
    def __init__(self, *args, **kwargs):
        self.val = "重复的对象，参数：{} {}".format(str(args), str(kwargs))

    def __set__(self):
        return self.val


class ApiQueryError(Exception):
    """自定义一个接口查询错误类"""
    def __init__(self, *args, **kwargs):
        self.val = "查询失败，参数：{} {}".format(str(args), str(kwargs))

    def __set__(self):
        return self.val


class MongoDeleteError(Exception):
    """自定义一个删除类"""
    def __init__(self, *args, **kwargs):
        self.val = "删除失败，参数：{} {}".format(str(args), str(kwargs))

    def __set__(self):
        return self.val


def insert_error_code(**kwargs):
    """插入错误代码"""
    ses = get_conn("error_code_info")
    inserted_id = ses.insert_one(kwargs).inserted_id
    return inserted_id


if __name__ == "__main__":
    """插入一个错误"""
    # args = {"code": 5001,
    #         "description": "文件写入磁盘失败"}
    # print(insert_error_code(**args))
    """根据代码获取一个错误信息（不是实例）"""
    ErrorCode.query_error_code(3000)