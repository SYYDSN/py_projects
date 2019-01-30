from flask import Flask
from flask import request
import json
from zerorpc_test.my_service import *


app = Flask(__name__)


"""restful接口服务器"""


def check_auth(auth):
    """
    检查token的装饰器.
    这里只是示范,实际工作中代码要复杂一些
    :param auth:  authorization
    :return:
    """
    """
    检查的结果 :
    0表示没有authorization
    -1表示权限不足
    1表示检查通过
    """
    validated = 0

    if auth is None:
        pass
    else:
            """
            调用authorization检查的微服务根据检查结果确认validated的值.
            """
            pass
    return validated


@app.route("/some_api")
def index_func():
    """
    视图函数
    :return:
    """
    user_name = request.args.get("user_name")
    a = Server1()
    if user_name is not None:
        r = a.add_user(user_name=user_name)
    b = Server2()
    return b.all_user()


@app.before_request
def permission_check():
    """
    在每次请求前进行检查.
    :return:
    """
    auth = request.headers.get("authorization")
    validated = check_auth(auth=auth)
    validated = 1  # 测试的时候人为赋值
    """
    0表示没有authorization
    -1表示权限不足
    1表示检查通过
    """
    if validated == 0:
        return json.dumps({"message": "401"})
    elif validated == -1:
        return json.dumps({"message": "rejected"})
    else:
        """放行"""
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)
    pass