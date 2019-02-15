# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado import gen
from tornado.ioloop import IOLoop
import ujson
from auth.auth_tools import get_auth
from auth.auth_tools import check_token


port = 9519


class BaseRequestHandler(tornado.web.RequestHandler):
    """基础的自定义请求处理类"""

    def get_arg(self, name: str, default: str = "") -> str:
        """获取一个单值的arg参数"""
        return self.get_argument(name=name, default=default)

    def get_args(self, name: str, default: str = "") -> str:
        """获取一个list的arg参数"""
        return self.get_arguments(name=name)

    def get_form(self, name: str, default: str = "") -> str:
        """获取一个单值的form参数"""
        return self.get_body_argument(name=name, default=default)

    def get_forms(self, name: str, default: str = "") -> str:
        """获取一个list的form参数"""
        return self.get_body_arguments(name=name)

    def load_json(self) -> dict:
        """
        一次性取出所有的json参数
        :return:
        """
        resp = dict()
        try:
            resp = ujson.loads(self.request.body)
        except Exception as e:
            print(e)
        finally:
            return resp

    def get_arg_by_name(self, name: str, default: str = "") -> str:
        """
        以参数名获取参数,此函数会以此轮询多个存放参数的地方.顺序是
        args(get, params)->form(post, data) -> json(json)
        每次找到后就终止继续查找.
        :param name:
        :param default:
        :return:
        """
        val = self.get_argument(name, default)
        if val == default:
            val = self.get_body_argument(name, default)
            if val == default:
                temp= dict()
                try:
                    temp = ujson.loads(self.request.body)
                except Exception as e:
                    print(e)
                finally:
                    val = temp.get(name, default)
            else:
                pass
        else:
            pass
        return val

    def get_args_by_name(self, name: str) -> list:
        """
        以参数名获取数组形式参数,此函数会以此轮询多个存放参数的地方.
        顺序是: args(get, params)->form(post, data) -> json(json)
        每次找到后就终止继续查找.
        :param name:
        :return:
        """
        val = self.get_arguments(name)
        if len(val) == 0:
            val = self.get_body_arguments(name)
            if len(val) == 0:
                temp = dict()
                try:
                    temp = ujson.loads(self.request.body)
                except Exception as e:
                    print(e)
                finally:
                    val = temp.get(name, list())
            else:
                pass
        else:
            pass
        return val


class HelloHanlder(BaseRequestHandler):
    """
    欢迎页
    """
    @gen.coroutine
    def get(self):
        return self.write("hello tornado!")

    @gen.coroutine
    def post(self):
        return self.get()


class EmployeeLogin(BaseRequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        self.write("Hello, Tornado!")

    @gen.coroutine
    def post(self, *args, **kwargs):
        self.write("hello")


class EmployeeTokenSample(BaseRequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        """
        生成一个authorization, 客户端需要传送三个参数:
        1. user_id
        2. hotel_id
        3. user_name
        :param args:
        :param kwargs:
        :return:
        """
        mes = {"message": "success"}
        user_name = self.get_arg_by_name(name="user_name")
        try:
            user_id = int(self.get_arg_by_name(name="user_id"))
            hotel_id = int(self.get_arg_by_name(name="hotel_id"))
        except Exception as e:
            print(e)
            mes['message'] = "user_id or hotel_id invalid"
        finally:
            if mes['message'] == "success":
                mes = get_auth(user_id=user_id, hotel_id=hotel_id, user_name=user_name)
        self.write(ujson.dumps(mes))

    @gen.coroutine
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class EmployeeCheckToken(BaseRequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        """
        检查authorization的有效性. 客户端可以使用2个参数
        1. authorization  待检验的密文  必须
        2. limit_time: 可以复用多少秒? -1 表示不限制,可以一直复用直到超时
        :param args:
        :param kwargs:
        :return:
        """
        # print(self.request.arguments)
        # print(self.request.body_arguments)
        # print(self.request.body)
        # self.get_argument("age")  # get.param
        # self.get_body_argument("name")  # get.data
        # self.get_query_argument("name")  # get.data
        # json_data = ujson.loads(self.request.body)  # json  参数
        tk = self.get_arg_by_name("authorization", "")
        resp = check_token(authorization=tk)
        self.write(ujson.dumps(resp))

    @gen.coroutine
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


def make_app():
    return tornado.web.Application([
        (r"/", HelloHanlder),
        (r"/common/employee/login", EmployeeLogin),
        (r"/common/employee/create_token", EmployeeTokenSample),
        (r"/common/employee/check_token", EmployeeCheckToken),
    ],
        debug=False
    )


if __name__ == "__main__":
    app = make_app()
    server = HTTPServer(app)
    app.listen(port)
    server.start(1)  # forks one process per cpu
    print("tornado server run on {}....".format(port))
    IOLoop.current().start()
