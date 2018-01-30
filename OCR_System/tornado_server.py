# -*-coding:utf8-*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado import autoreload
from tornado import gen
from tornado.websocket import WebSocketHandler
from tornado.websocket import WebSocketClosedError
import tornado.web
from uuid import uuid4
from main_server import port as f_port
from tornado_tools import *
import os
import json
from tornado.options import define, options



port = f_port + 10  # 定义端口号


define("port", default=port, help="run on the given port", type=int)


def send_all(data, except_list=[]):
    """向所有的ws客户端发送消息，except_list是排除在外的客户端id列表，
    不往列表中的客户端发送消息"""
    ws_dict = get_online_dict()
    [v.send(data) for k, v in ws_dict.items() if k not in except_list]


class MyWebSocket(WebSocketHandler):
    """websocket的handler"""

    def check_origin(self, origin):
        """跨域"""
        return True

    def get_ws_id(self):
        """获取客户端的id"""
        ws_id = self.request.headers.get("Sec-Websocket-Key")
        return ws_id

    def send(self, message):
        """发送消息，message需要被json编码后发送"""
        ws_id = self.get_ws_id()
        try:
            self.write_message(json.dumps(message))
        except WebSocketClosedError as e:
            print(e)
            remove_online_id(ws_id)
        finally:
            pass

    def open(self):
        """客户端建立连接时"""
        ws_id = self.get_ws_id()
        add_online_id(ws_id, self)
        ws_list = get_online_list()
        data = {"channel": "first", "my_id": ws_id, "id_list": ws_list}
        self.send(data)

    def on_close(self):
        """客户端断开连接时"""
        ws_id = self.get_ws_id()
        remove_online_id(ws_id)

    def on_message(self, message):
        """通讯时"""
        args = json.loads(message)
        channel = args['channel']
        if channel == "get_text":
            """获取abbyy识别的结果"""

        elif channel == "join_work":
            """后台输入打开页面后加入工作"""

            self.send(args)

        elif channel == "broadcast":
            """向全体客户端广播消息，一般用作测试或者特殊用途"""
            send_all({"channel": "broadcast", "message": "hello"})
        else:
            pass


"""定义路由"""
handlers = [    (r'/ws_handler', MyWebSocket)]

"""定义配置"""
cookie_secret = "83a9a1dad18548fbb88525a97d6da090"
setting = {"debug": False, "autoreload": False, "cookie_secret": cookie_secret, "template_path": "templates",
           'complied_template_cache': True, "static_hash_cache": False,
           "static_path": os.path.join(os.path.dirname(__file__), "static")}


must_single = True  # 是否必须单进程


if __name__ == "__main__":
    """当开启setting中的debug和autoreload时，无法开启tornado的多进程模式，这两者有冲突
        注意，当前程序未考虑多进程模式，必须运行在单进程模式下。
    """
    if not setting.get("debug") and not setting.get("autoreload") and not must_single:
        tornado.options.parse_command_line()
        app = tornado.web.Application(handlers=handlers, **setting)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.bind(options.port)
        http_server.start(0)
        print("running on port {}".format(options.port))
        tornado.ioloop.IOLoop.current().start()
    else:
        tornado.options.parse_command_line()
        app = tornado.web.Application(handlers=handlers, **setting)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port=options.port, address="0.0.0.0")
        print("tornado 在{}端口以单进程模式运行".format(options.port))
        tornado.ioloop.IOLoop.current().start()
