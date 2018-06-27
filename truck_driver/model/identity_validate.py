#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import jwt
import datetime
from werkzeug.contrib.cache import SimpleCache
from uuid import uuid4
import mongo_db
from log_module import get_logger


"""身份验证模块,主要是和jwt相关的部分"""


logger = get_logger()
ObjectId = mongo_db.ObjectId
s_cache = SimpleCache()  # 内存型缓存,关闭系统就消失.


class GlobalSignature(mongo_db.BaseDoc):
    """
    全局数字签名,一般用于JWT的secret,
    注意,考虑性能,此集合的大小是固定的.目前只存储100个记录
    """
    _table_name = "global_signature"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['signature'] = str  # 数字签名
    type_dict['algorithm'] = str  # 算法
    type_dict['expire'] = int  # 过期时间.单位秒
    type_dict['time'] = datetime.datetime  # 创建时间.

    def __init__(self, from_unc: bool = False):
        if not from_unc:
            ms = "请不要直接调用本类的初始化方法,请尝试使用cls.get_signature方法"
            raise RuntimeError(ms)
        else:
            args = dict()
            args['_id'] = ObjectId()
            args['signature'] = uuid4().hex
            args['algorithm'] = "HS256"  # 默认算法
            args['expire'] = 7200
            args['time'] = datetime.datetime.now()
            super(GlobalSignature, self).__init__(**args)

    @classmethod
    def __add_signature(cls) -> object:
        """
        增加一个signature,理论上来说,这应该是一个原子操作.
        :return: 实例
        """
        obj = cls(from_unc=True)
        obj.save_plus()
        return obj.get_dict()

    @classmethod
    def __get_signature(cls, return_type: str = "dict") -> (object, dict):
        """
        获取全局加密的数字签名,这是个内部方法,除了类本身外,不应该被其他对象调用.
        :param return_type: 返回的类型.可以选3个值object/dict/can_json,分表代表返回 实例/字典/可json序列化的字典
        :return: 取决于return_type参数.
        """
        """在老的signature过期前5分钟就应该生成一个新的signature,在这5分钟内,新旧signature豆可以使用."""
        now = datetime.datetime.now()
        last = now - datetime.timedelta(seconds=6900)  # 6900是2个小时减去5分钟.
        f = {'time': {"$gte": last}}
        s = {"time": -1}
        one = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
        """表为空或者没有有效的signature,重新生成一个signature"""
        if one is None:
            one = cls.__add_signature()
        if return_type == "object":
            one = cls(**one)
        elif return_type == "can_json":
            one = mongo_db.to_flat_dict(one)
        else:
            pass
        return one

    @classmethod
    def get_signature(cls) -> (object, dict):
        """
        获取全局加密的数字签名,此方法暴露给外界使用.有缓存.
        :return: 取决于return_type参数.
        """
        key = "global_signature"
        signature = s_cache.get(key)
        if signature is None:
            signature = cls.__get_signature(return_type="dict")
            s_cache.set(key, signature, timeout=7200)
        else:
            now = datetime.datetime.now()
            delta_seconds = (now - signature['time']).total_seconds() - signature['expire']
            if delta_seconds <= 300:
                signature = cls.__get_signature(return_type="dict")
                s_cache.set(key, signature, timeout=7200)
            else:
                pass
        return signature

    @classmethod
    def encode(cls, payload: dict, secret: str = None, algorithm: str = "HS256") -> (bytes, None):
        """
        加密.注意返回的类型是bytes.
        :param payload:  需要加密的对象,必须是字典类型,字段都是可json序列化的数字或者字符串
        :param secret:  签名
        :param algorithm:  加密算法
        :return:  bytes
        """
        if isinstance(payload, dict):
            algorithm_list = [
                "HS256", "HS384", "HS512", "ES256", "ES384", "ES512", "RS256",
                "RS384", "RS512", "PS256", "PS384", "PS512"
            ]
            secret = secret if secret is not None else cls.get_signature().get("signature")
            if algorithm not in algorithm_list:
                ms = "不支持的算法:{}".format(algorithm)
                raise ValueError(ms)
            else:
                payload = mongo_db.to_flat_dict(payload)
                res = None
                try:
                    res = jwt.encode(payload=payload, key=secret, algorithm=algorithm)
                except Exception as e:
                    print(e)
                    logger.exception(e)
                finally:
                    return res
        else:
            ms = "待加密对象必须是dict类型"
            raise TypeError(ms)

    @classmethod
    def decode(cls, jwt_str: (str, bytes), secret: str = None, algorithm: str = "HS256") -> (dict, None):
        """
        解密,返回的是字典
        :param jwt_str: 密文
        :param secret:  签名
        :param algorithm: 算法.
        :return: 解密后的dict
        """
        if isinstance(jwt_str, (str, bytes)):
            algorithm_list = [
                "HS256", "HS384", "HS512", "ES256", "ES384", "ES512", "RS256",
                "RS384", "RS512", "PS256", "PS384", "PS512"
            ]
            secret = secret if secret is not None else cls.get_signature().get("signature")
            if algorithm not in algorithm_list:
                ms = "不支持的算法:{}".format(algorithm)
                raise ValueError(ms)
            else:
                res = None
                try:
                    res = jwt.decode(jwt=jwt_str, key=secret, algorithm=algorithm)
                except Exception as e:
                    print(e)
                    logger.exception(e)
                finally:
                    return res
        else:
            ms = "密文必须是字符串或字节类型"
            raise TypeError(ms)


if __name__ == "__main__":
    # s = GlobalSignature.encode({"name": "hello", "time": datetime.datetime.now()})
    s = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiaGVsbG8iLCJ0aW1lIjoiMjAxOC0wNi0yNSAxNzo1MzoyMyJ9.D7-3yV2' \
        '5rKCSCuHTNAmvKsJEXCuLZqVR62PxD3Ejj1M'
    s = GlobalSignature.decode(s)
    print(s)
    pass