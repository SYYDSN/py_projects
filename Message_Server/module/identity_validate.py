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
from mail_module import send_mail
from jwt.exceptions import InvalidSignatureError


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
        f = dict()
        now = datetime.datetime.now()
        f['time'] = {"$gte": now - datetime.timedelta(seconds=6900)}
        s = {"time": -1}
        one = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
        """表为空或者没有有效的signature,重新生成一个signature"""
        if one is None:
            one = cls.__add_signature()
        else:
            pass
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
        key_now = "global_signature_now"
        obj = s_cache.get(key_now)
        if obj is None:
            obj = cls.__get_signature(return_type="dict")
            s_cache.set(key_now, obj, timeout=7200)
        else:
            """检查是不是要过期？"""
            now = datetime.datetime.now()
            create_time = obj['time']
            delta = (now - create_time).total_seconds()
            if delta > 7200:
                """过期了"""
                obj = cls.__get_signature(return_type="dict")
                s_cache.set(key_now, obj, timeout=7200)
            elif 6900 <= delta <= 7200:
                """还有五分钟过期，生成一个新的凭证，老的存入备用"""
                key_prev = "global_signature_prev"
                s_cache.set(key_prev, obj, timeout=delta)
                obj = cls.__get_signature(return_type="dict")
                s_cache.set(key_now, obj, timeout=7200)
            else:
                pass
        return obj

    @classmethod
    def get_signature_prev(cls) -> (None, dict):
        """
        获取上一次的，但仍未过期的。全局加密的数字签名,此方法暴只给用来解密的函数使用.有缓存.
        :return: dict/None
        """
        key_prev = "global_signature_prev"
        obj = s_cache.get(key_prev)
        return obj

    @classmethod
    def get_history_signature(cls, prev: int = 1) -> (dict, None):
        """
        从数据库查询已经失效的旧的签名,此方法暂时没有使用.处于备用状态.
        :param prev: 上溯第几个签名?默认是上溯一个,也就是刚刚失效的那个签名.
        :return: 签名对象的字典
        """
        f = dict()
        s = {"time": -1}
        skip = prev
        r = cls.find_plus(filter_dict=f, sort_dict=s, skip=skip, limit=1, to_dict=True)
        if len(r) == 0:
            return None
        else:
            return r[0]

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
            print({"signature": secret})
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
    def decode(cls, jwt_str: (str, bytes), secret: str = None, algorithm: str = "HS256",
               to_str: bool = True) -> (dict, None):
        """
        解密,返回的是字典
        :param jwt_str: 密文
        :param secret:  签名
        :param algorithm: 算法.
        :param to_str: 是否将结果转成str格式?默认是bytes格式.
        :return: 解密后的dict
        """
        if isinstance(jwt_str, (str, bytes)):
            algorithm_list = [
                "HS256", "HS384", "HS512", "ES256", "ES384", "ES512", "RS256",
                "RS384", "RS512", "PS256", "PS384", "PS512"
            ]
            secret = secret if secret is not None else cls.get_signature().get("signature")
            print({"signature": secret})
            if algorithm not in algorithm_list:
                ms = "不支持的算法:{}".format(algorithm)
                raise ValueError(ms)
            else:
                res = None
                try:
                    res = jwt.decode(jwt=jwt_str, key=secret, algorithm=algorithm)
                except InvalidSignatureError as e:
                    logger.exception(e)
                    print(e)
                    try:
                        old_secret = cls.get_signature_prev()
                        if old_secret is None:
                            ms = "signature验证失败"
                            print(ms)
                            title = "{}解密信息出现错误,签名过期并且没找到旧的签名.".format(datetime.datetime.now())
                            content = "错误原因：{},参数：jwt:{}, key: {}, algorithm: {}".format(e, jwt_str, secret, algorithm)
                            ms = "{}，{}".format(title, content)
                            send_mail(title=title, content=content)
                            logger.exception(ms)
                            raise ValueError(ms)
                        else:
                            res = jwt.decode(jwt=jwt_str, key=old_secret, algorithm=algorithm)
                    except Exception as e:
                        print(e)
                        title = "{}解密信息出现错误,新旧签名皆无效".format(datetime.datetime.now())
                        content = "错误原因：{},参数：jwt:{}, key: {}, algorithm: {}".format(e, jwt_str, secret, algorithm)
                        ms = "{}，{}".format(title, content)
                        send_mail(title=title, content=content)
                        logger.exception(ms)
                        raise e
                except Exception as e:
                    title = "{}解密信息出现未预料错误".format(datetime.datetime.now())
                    content = "错误原因：{},参数：jwt:{}, key: {}, algorithm: {}".format(e, jwt_str, secret, algorithm)
                    ms = "{}，{}".format(title, content)
                    send_mail(title=title, content=content)
                    print(ms)
                    logger.exception(ms)
                    raise e
                finally:
                    if isinstance(res, bytes) and to_str:
                        res = res.decode(encoding="utf-8")
                    return res
        else:
            ms = "密文必须是字符串或字节类型"
            raise TypeError(ms)


if __name__ == "__main__":
    """编码"""
    # s = GlobalSignature.encode({"user_name": "jack", "user_password": "e10adc3949ba59abbe56e057f20f883e"})
    # print(s)
    """解码"""
    s = 'eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoie1widXNlcl9uYW1lXCI6XCLlvKDnkZ5cIixcIk1UNF9hY2NvdW50XCI6ODMwMDM1MCxcImRlcG' \
        '9zaXRfb3JkZXJcIjpcIjAwMDAwMDAwMDAwMDAwMDAxOTMyXCIsXCJkZXBvc2l0X21vbmV5XCI6MTAwLjAsXCJ0aXRsZVwiOlwi5YWl6YeR5o' \
        'iQ5YqfXCIsXCJ1c2VyX3BhcmVudF9uYW1lXCI6XCIwMDQwMDBcIixcInN0YXR1c1wiOlwi5bey5pSv5LuYXCIsXCJvcGVyYXRlX3RpbWVcI' \
        'jpcIjIwMTgtMDgtMjMgMTY6MzU6NTVcIn0iLCJpc3MiOiJhdXRoMCIsImV4cCI6MTUzNTAyMDU1NX0.3smM2Xf5HlaCUVX9SsvdptURRsi' \
        'zdiRGShAp-GfhpS4'
    print(s)
    key = "4c5232f5d1784a94a2d486cf55d30aca"
    key_old = "d94f22d89abd40ff82b2c736d8df9a88"
    s = GlobalSignature.decode(jwt_str=s, secret=key_old, algorithm="HS256")
    print(s)
    pass