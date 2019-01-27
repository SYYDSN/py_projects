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


"""生成和检查jwt"""


cache = RedisCache()
logger = get_logger()
default_algorithm = "HS256"
default_secret = uuid4().hex


def encode(user_id: (int, str)) -> dict:
    """
    加密.注意返回的类型是bytes.
    :param user_id:  用户id.
    :return:  {'message': 'success', 'authorization': 'eyJ0eXAil...'}
    """
    res = {'message': 'success'}
    payload = {
        "user_id": user_id,
        "expire": (datetime.datetime.now() + datetime.timedelta(hours=2)).timestamp()
    }
    jwt_str = None
    try:
        jwt_str = jwt.encode(payload=payload, key=default_secret, algorithm=default_algorithm)
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


def decode(authorization: (str, bytes)) -> dict:
    """
    解密
    :param authorization: 请求头密文
    :return: {'message': 'success', 'user_id': 12}
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
                expire = payload.get("expire")
                user_id = payload.get("user_id")
                try:
                    expire = float(expire) if not isinstance(expire, float) else expire
                except Exception as e:
                    logger.exception(e)
                finally:
                    if isinstance(expire, float):
                        if (datetime.datetime.now().timestamp() - expire) > 0:
                            res['message'] = "expire timeout"  # 生存期超时
                        else:
                            if user_id is None:
                                res['message'] = "user_id invalid"  # 用户id无效
                            else:
                                res = encode(user_id=user_id)
                                res['user_id'] = user_id
                    else:
                        res['message'] = "expire invalid"  # 生存期无效
    return res


if __name__ == "__main__":
    # r = encode(12)
    # print(r)
    # r2 = decode(r['authorization'])
    r2 = decode('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMiwiZXhwaXJlIjoxNTQ4NjExODk5Ljk2MDYxOX0.GJe_YtjpZCtBEtVqAzpZ-4i0ETiPgxEOyvW9PgsunLY')
    print(r2)
    pass
