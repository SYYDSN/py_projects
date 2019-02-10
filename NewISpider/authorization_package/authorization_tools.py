#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import jwt
from werkzeug.contrib.cache import RedisCache
from toolbox.log_module import get_logger
import datetime
from uuid import uuid4


"""
生成和检查jwt
目前分四个版本
1. v1.0 使用uuid + redis 缓存. 每次更换token. 通讯内容不加密
2. v2.0 单独使用jwt, 2小时换一次secret, 需要额外的获取secret和algorithm的接口, 客户端需要加密. 通讯内容加密.暂时不实现

"""


cache = RedisCache()
logger = get_logger()
default_algorithm = "HS256"
default_secret = uuid4().hex
# default_secret = "dffgdgfdfg456456t4ygdgtrey656r5y656y54yyyr5544565"  # 测试用


def encode_1(**kwargs) -> dict:
    """
    加密v 1版本. 对用户信息的键值对对象保存在redis里,返回uuid给客户端做token
    行为:
    1. 检测传入的参数类型是否合法? 是否包含了user_id字段?
    2. 保存kwargs到redis(2个小时有效,)返回应对的redis的key作为uuid
    3. 返回结果.类似{'message': 'success', 'authorization': uuid}
    uuid 只可使用一次
    前端可以使用"uuid"放入请求头中做身份验证. headers = {"authorization": "uuid"}
    :param kwargs:  用户信息的键值对对象. 至少需要user_id,
    :return:  {'message': 'success', 'authorization': uuid}
    """
    res = {'message': 'success'}
    if isinstance(kwargs, dict) and "user_id" not in kwargs:
        res['message'] = "user_id invalid"
    else:
        kwargs['expire'] = (datetime.datetime.now() + datetime.timedelta(hours=2))
        key = uuid4().hex
        cache.set(key=key, value=kwargs, timeout=7200)
        res['authorization'] = key
    return res


def decode_1(authorization: str) -> dict:
    """
    解密v 1版本.
    行为:
    1. 检查密文(redis的key)是否被使用过?(是否有这个key?)
    2. 取出redis中的用户信息字典.
    3. 检查用户信息字典中的过期时间是否超时?, 超时返回失败信息,否则进入下一步
    4. 调用encode_1重新 返回 {'message': 'success', 'authorization': 新的uuid}
    :param authorization: 请求头密文
    :return: {'message': 'success', 'authorization': 新的uuid}
    """
    res = {"message": "success"}
    user_info = cache.get(key=authorization)
    if user_info is None:
        res['message'] = "authorization invalid"  # 密文无效
    else:
        cache.delete(key=authorization)
        expire = user_info.pop("expire", None)
        now = datetime.datetime.now()
        if expire is None or (isinstance(expire, datetime.datetime) and now > expire):
            """过期"""
            res['message'] = "expire timeout"  # 生存期超时或者时间戳无效
        else:
            res = encode_1(**user_info)
    return res


def encode_2(**kwargs) -> dict:
    """
    加密v 2版本. 对用户信息的键值对对象进行加密
    行为:
    1. 检测传入的参数类型是否合法? 是否包含了user_id字段?
    2. 加入时间戳(2个小时有效,时间戳可以换算成截止日期)并加密整个键值对
    3. 返回结果.类似{'message': 'success', 'authorization': 可用的密文}
    前端可以使用"可用的密文"放入请求头中做身份验证. headers = {"authorization": "可用的密文"}
    "可用的密文"只可使用一次
    :param kwargs:  用户信息的键值对对象. 至少需要user_id,
    :return:  {'message': 'success', 'authorization': 可用的密文}
    """
    res = {'message': 'success'}
    if isinstance(kwargs, dict) and "user_id" not in kwargs:
        res['message'] = "user_id invalid"
    else:
        kwargs['expire'] = (datetime.datetime.now() + datetime.timedelta(hours=2)).timestamp()
        jwt_str = None
        try:
            jwt_str = jwt.encode(payload=kwargs, key=default_secret, algorithm=default_algorithm)
        except Exception as e:
            res['message'] = "encode fail"  # 加密失败
            print(e)
            logger.exception(e)
        finally:
            if isinstance(jwt_str, bytes):
                jwt_str = jwt_str.decode(encoding="utf-8")
                res['authorization'] = jwt_str
            key = "authorization_{}".format(jwt_str)
            cache.set(key=key, value=1, timeout=7200)
    return res


def decode_2(authorization: (str, bytes)) -> dict:
    """
    解密v 2版本.
    行为:
    1. 检查密文是否被使用过?
    2. 解密.解密失败会报错返回,成功则进入下一步.
    3. 将出时间戳之外的键值对用encode_21加密
    4. 返回 {'message': 'success', 'authorization': 新的密文}
    :param authorization: 请求头密文
    :return: {'message': 'success', 'authorization': 新的密文}
    """
    res = {"message": "success"}
    key = "authorization_{}".format(authorization)
    if cache.get(key=key) != 1:
        res['message'] = "authorization invalid"  # 密文无效
    else:
        cache.delete(key=key)
        payload = None
        try:
            payload = jwt.decode(jwt=authorization, key=default_secret, algorithm=default_algorithm)
        except Exception as e:
            title = "{}解密信息出现未预料错误".format(datetime.datetime.now())
            content = "错误原因：{},参数：jwt:{}, key: {}, algorithm: {}".format(e, authorization, default_secret, default_algorithm)
            ms = "{}，{}".format(title, content)
            print(ms)
            logger.exception(ms)
            raise e
        finally:

            if payload is None:
                res['message'] = "decode fail"  # 解码失败
            else:
                expire = payload.pop("expire", None)
                user_id = payload.get("user_id")
                try:
                    expire = float(expire) if not isinstance(expire, float) else expire
                except Exception as e:
                    logger.exception(e)
                finally:
                    if isinstance(expire, float):
                        if expire is None or (datetime.datetime.now().timestamp() - expire) > 0:
                            res['message'] = "expire timeout"  # 生存期超时
                        else:
                            if user_id is None:
                                res['message'] = "user_id invalid"  # 用户id无效
                            else:
                                res = encode_2(**payload)
                    else:
                        res['message'] = "expire invalid"  # 生存期无效
    return res


if __name__ == "__main__":
    """v1.0版本测试"""
    # r1 = encode_1(user_id=12, role_id=1)
    # print(r1)
    # r2 = decode_1(r1['authorization'])
    # print(r2)
    # print(decode_1(r1['authorization']))
    """v2.0版本测试"""
    # r = encode_2(user_id=12)
    # print(r)
    # r2 = decode_2(r['authorization'])
    # print(r2)
    pass
