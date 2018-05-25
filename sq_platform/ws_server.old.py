# -*-coding:utf-8-*-
import tornado.httpserver, time
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
import os.path
import sys
import re
from flask_server import port
import tornado.autoreload
import threading, json
import datetime
import log_module
from tornado.options import define, options
import tornado.websocket
import random
import mongo_db
import hashlib
import requests
import urllib.request
import urllib.parse
import platform
from tools_module import get_platform_cors_session_dict
from tools_module import save_platform_cors_session
from tools_module import save_platform_cors_session
from api.data.item_module import Track
from manage.company_module import Employee


logger = log_module.get_logger("ws_server")
cache = mongo_db.cache


class BlackIpDict:
    """黑名单类"""
    cache_key = "ws_handler_black_ip_dict"
    black_ip_map = cache.get(cache_key)
    if black_ip_map is None:
        black_ip_map = dict()

    @classmethod
    def clear(cls) -> None:
        """清除缓存中的数据"""
        key = cls.cache_key
        cache.delete(key)

    @classmethod
    def save_data(cls, map_data) -> None:
        """保存数据到cache
        ：param map_data: 新的map数据
        """
        cls.black_ip_map = map_data

    @classmethod
    def get_data(cls) -> dict:
        """返回一个handler_map对象
        return: dict
        """
        return cls.black_ip_map

    @classmethod
    def check_ip(cls, ip)->bool:
        """检查一个ip是否合法？
        :param ip“IP地址
        ”return 合法返回True（不在黑名单中）
        """
        data = cls.get_data()
        if ip in data.keys():
            return False
        else:
            return True

    @classmethod
    def remove_ip(cls, ip)->None:
        """
        从黑名单列表中清除一个ip的信息
        :param ip: ip地址
        :return: None
        """
        data = cls.get_data()
        if ip in data.keys():
            data.pop(ip)
            cls.save_data(data)
        else:
            pass

    @classmethod
    def add_ip(cls, ip, ip_obj)->None:
        """
        向黑名单列表中添加一个ip的信息
        :param ip: ip地址
        :param ip_obj: ip地址信息
        :return: None
        """
        data = cls.get_data()
        data[ip] = ip_obj
        cls.save_data(data)


class WSIdMap:
    """
    操作ws的handler,ws_id,user_id的类，记录的是三者之间的对应关系

    cache_key_ws_handler用于记录ws_id与user_id&handler的对应关系。
    cache_key_user_ws 用于记录user_id和ws_id的对应关系

    cache_key_ws_handler字典格式如下：
    {
     ws_id:                                     # web_socket客户端id的str格式。
            {
            handler:WebSocketHandler.instance,  # 一个WebSocketHandler的实例。
            user_id:user_id_str                 # 用户的ObjectId的str
            },
     ...
    }
    cache_key_user_ws字典的格式如下：
    {
     user_id: ws_id,  # 用户的ObjectId的str: web_socket客户端id的str格式
     ...
    }
    """
    cache_key_ws_handler = "ws_handler_and_ws_client_id"
    cache_key_user_ws = "user_id_and_ws_client_id"
    handler_map = cache.get(cache_key_ws_handler)
    id_map = cache.get(cache_key_user_ws)
    if handler_map is None:
        handler_map = dict()
    if id_map is None:
        id_map = dict()

    @classmethod
    def save_data(cls, map_data: dict, id_map: dict)->None:
        """保存数据到cache
        ：param map_data: 新的handler map数据
        ：param id_map: 新的id map数据
        """
        cls.handler_map = map_data
        cls.id_map = id_map

    @classmethod
    def get_data(cls)->tuple:
        """返回一个tuple对象,包含handler_map和id_map
        return: tuple
        """
        return cls.handler_map, cls.id_map

    @classmethod
    def clear(cls)->None:
        """清除缓存中的数据，启动系统时使用，用于避免历史数据的干扰"""
        key = cls.cache_key_ws_handler
        cache.delete(key)
        key = cls.cache_key_user_ws
        cache.delete(key)

    @classmethod
    def client_on_line(cls, ws_id: str, user_id: str, client_obj: tornado.websocket.WebSocketHandler)->None:
        """
        web-socket客户端上线/连接成功。这个方法应该在WebSocketHandler对象open的时候被调用。
        :param ws_id: 客户端id
        :param user_id: 登录用户的id
        :param client_obj:  客户端对象
        :return:None
        """
        handler_maps, id_map = cls.get_data()
        handler_maps[ws_id] = {"handler": client_obj, "user_id": user_id}
        id_map[user_id] = ws_id
        cls.save_data(handler_maps, id_map)

    @classmethod
    def client_off_line(cls, ws_id)->None:
        """
        web-sockegt客户端下线/断开链接。这个方法应该在WebSocketHandler对象发生on_close事件，
        执行WebSocketHandler对象的close方法，或者WebSocketHandler对象在执行write_message
        方法（也可能在其他场景下）抛出WebSocketClosedError错误的时候被调用。
        :param ws_id:客户端id
        :return:None
        """
        handler_maps, id_map = cls.get_data()
        try:
            temp = handler_maps.pop(ws_id)
            """
            成功的话：
            temp = {
                    handler:WebSocketHandler.instance,  # 一个WebSocketHandler的实例。
                    user_id:user_id_str                 # 用户的ObjectId的str
                    }
            """
            user_id = temp['user_Id']
            id_map.pop(user_id)
        except KeyError as e:
            print(e)
        except AttributeError as e1:
            print(e1)
            logger.exception("{} Error".format(sys._getframe().f_code.co_name), exc_inf=True, stack_info=True)
        finally:
            cls.save_data(handler_maps, id_map)

    @classmethod
    def handler_is_none(cls, handler: tornado.websocket.WebSocketHandler)->None:
        """
        在发送消息失败的时候，把handler从id和handler的映射集合中移除。
        :param handler: tornado.websocket.WebSocketHandler的实例，一般是self
        :return:
        """
        try:
            ws_id = handler.ws_id
            cls.client_off_line(ws_id)
        except AttributeError as e:
            print(e)
            pass


def check_session(handler: tornado.websocket.WebSocketHandler)->str:
    """
    检查某个ws客户端是否已经登录？
    这个是从redis中取登录用户id的方法
    :param handler: 一个tornado.websocket.WebSocketHandler的实例
    :return: 用户id的字符串格式
    """
    res = None
    if isinstance(handler, tornado.websocket.WebSocketHandler):
        ses_str = None
        try:
            ses_str = handler.cookies['session'].value
        except KeyError as e:
            print(e)
        except Exception as e1:
            logger.exception("Error")
            raise e1
        finally:
            if ses_str is None:
                pass  # 没有登录或者跨域用户登录
            else:
                """是本域用户,开始从flask-session的会话中取值"""
                key = "session:{}".format(ses_str)
                val = cache.get(key)
                if val is None:
                    pass
                else:
                    val = val.decode("windows-1252")
                    temp_set = val.split("user_id")
                    temp_str = temp_set[-1]
                    pattern = re.compile(r'\w{24}')  # 匹配ObjectId的字符串
                    user_id = re.search(pattern, temp_str)
                    if user_id is None:
                        pass
                    else:
                        res = user_id.group()
            """如果这时候res还是None的话,开始针对跨域用户检测"""
            if res is None:
                """没有从session中取得用户id,那可能是跨域用户,就取sid"""
                cors = handler.get_argument("cors", None)
                sid = handler.get_argument("sid", None)
                if cors == "cors" and isinstance(sid, str) and len(sid) == 32:
                    user_dict = get_platform_cors_session_dict(sid)
                    if isinstance(user_dict, dict):
                        res = user_dict['user_id']
                else:
                    pass
    return res


def get_real_ip(req)->str:
    """
    获取当前请求的真实ip。参数只有一个：
    1.req  当前的请求。一般都是传入当前上下文的request
    return ip地址(字符串格式)
    注意，如果前端的反向代理服务器是nginx的话，需要在配置文件中加上几句。
    在location / 配置下面的proxy_pass   http://127.0.0.1:5666; 后面加上
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    然后才可以用headers["X-Forwarded-For"]取真实ip
    虽然只加proxy_set_header X-Real-IP $remote_addr;这一句的话。
    也可以用request.headers["X-Real-IP"]获取。
    但为了和IIS的兼容性。还是需要再加一句
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    参数
    :parm req: flask 是request对象，
    tornado是 tornado.web.RequestHandler.request或者tornado.websocket.WebSocketHandler.reuest
    """
    try:
        ip = req.headers["X-Forwarded-For"].split(":")[0]
    except KeyError as e:
        ip = req.remote_ip  # 注意：tornado是 request.remote_ip   flask是 req.remote_addr
    if ip.find(",") != -1:
        """处理微信登录时转发的双ip"""
        ip = ip.split(",")[0]
    return ip


# 文字直播室公共消息的群发
def send_all(message):  #
    global WS_DICT
    for ws_id in WS_DICT:
        handler = WS_DICT[ws_id]
        handler.send_message(json.dumps(message))


# 老师的界面，ws通讯方法,群发
def send_all_dialogs(message):  #
    global ANSWER_WS_DICT
    for ws_id in ANSWER_WS_DICT:
        handler = ANSWER_WS_DICT[ws_id]
        handler.send_message(json.dumps(message))


# 限制FIRST_INFO的长度，防止客户在打开时候一次接收消息过多。
def check_info_length():
    global FIRST_INFO
    if len(FIRST_INFO) > 30:
        FIRST_INFO = FIRST_INFO[len(FIRST_INFO) - 15:]
    else:
        pass


class Hello(tornado.web.RequestHandler):
    """测试类"""
    @tornado.gen.coroutine
    def get(self):
        ip = get_real_ip(self.request)
        self.write("hello world, ip={}".format(ip))

    @tornado.gen.coroutine
    def post(self):
        self.send_error(405)


async def keep_cors_session_beat(sid: str) -> bool:
    """
    维持跨域用户的会话的心跳,心跳最大间隔期在tools_module模块中的cors_session_timeout设置
    :param sid: 会话id
    :return:
    """
    key = "session_key_{}".format(sid)
    user_dict = cache.get(key)
    res = False
    if isinstance(user_dict, dict):
        res = await save_platform_cors_session(**user_dict)

    return res


class ListenCORSSessionBeat(tornado.web.RequestHandler):
    """监听跨域用户的会话心跳"""
    @tornado.gen.coroutine
    def get(self):
        message = {"message": "success"}
        sid = self.get_argument('sid', None)
        if sid:
            res = yield keep_cors_session_beat(sid)
            if res:
                pass
            else:
                message['message'] = "error"
        else:
            message['message'] = 'validate sid'
        self.write(json.dumps(message))

    def set_default_headers(self):
        """跨域"""
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Cache-Control', 'public, max-age=7200')
        self.set_header('Content-type', 'text/script')  # 指定了返回类型


class InfoHandler(tornado.websocket.WebSocketHandler):  # ws服务器必须继承于tornado.websocket.WebSocketHandler。
    """实时推送消息的服务"""
    def check_origin(self, origin):  # 重写同源检查的方法，在每次请求到达时最先执行
        ip = get_real_ip(self.request)
        if BlackIpDict.check_ip(ip):
            """黑名单检查通过"""
            return True
        else:
            return False

    def write_message(self, message: (str, dict), binary: bool = False):
        """
        覆盖了同名的方法。发送消息给ws客户端，用于生产环境，已进行了异常处理。
        :param message: 发送的消息，如果是dict的话，会被自动json
        :param binary: False发送的是utf-8编码的字符串，否则发送的是字节对象。
        :return: 一个对象，用于后继处理
        注意，发送消息的格式是和客户端约定的。
        发给消息一定是字典格式，并且遵照一定的格式。
         {
         mes_type: string    消息类型 字符串格式，用于区别不同的操作。
         data_dict: dict     消息内容，字典格式，自行约定
         }
         比如，发给客户端的欢迎信息
         {"mes_type":"welcome", "data_dict":{},"message":"你好，用户"}
        """
        if self.ws_connection is None:
            print("client {} is lost connect".format(self.ws_id))
            WSIdMap.handler_is_none(self)
        else:
            if isinstance(message, dict):
                message = tornado.escape.json_encode(message)
            return self.ws_connection.write_message(message, binary=binary)

    @staticmethod
    def package_message(mes_type: str, data_dict: (dict, list) = None, message: str = "success")->dict:
        """
        包装消息字典的工具。把消息快速打包成符合发送格式要求的方法。
        :param mes_type: 消息类型。
        :param data_dict: 消息参数的字典/数组
        :param message: 消息状态，表示成功或者失败，也可以自定义一段话。
        :return:包装好的而消息字典
        """
        data_dict = dict() if data_dict is None else data_dict
        data = {"mes_type": mes_type, "data_dict": data_dict, "message": message}
        return data

    def open(self):  # 此方法在每次连接到达时执行。会给客户发送open的状态。
        ws_id = self.request.headers["Sec-Websocket-Key"]  # web-socket客户端id
        self.ws_id = ws_id
        user_id_str = None
        sid = self.get_argument("sid", None)  # 取跨域用户id
        user_dict = get_platform_cors_session_dict(sid)
        if isinstance(user_dict, dict):
            user_id_str = user_dict['user_id']
        if user_id_str is None:
            user_id_str = check_session(self)  # 从会话获取一般用户用户id
        if user_id_str is None:
            self.close(406, "没有登录")
        else:
            WSIdMap.client_on_line(ws_id, user_id_str, self)  # 填充客户端id映射集合
            """检查身份的方法暂时省略"""
            mes = "welcome! your id is {}".format(ws_id)
            mes_type = "welcome"
            message = self.package_message(mes_type, None, mes)
            self.write_message(message)  # 发送欢迎信息

    def on_close(self):  # 此方法必须写，用于防止用户直接关闭浏览器导致的异常。
        ws_id = self.request.headers["Sec-Websocket-Key"]  # 从当前被关闭的连接中取出安全id
        WSIdMap.client_off_line(ws_id)  # 从线程池弹出此线程

    def on_message(self, message: str):
        """
        接收到客户端发来的消息时
        :param message: 消息内容。json化的字典
        :return:
        注意，客户端发来的消息是有固定格式的。
        {
         mes_type: string    消息类型 字符串格式，用于区别不同的操作。
         data_dict: dict     消息内容，字典格式，自行约定
         }
        """
        try:
            message = json.loads(message)
        except json.decoder.JSONDecodeError as e:
            print(e)
            message = message
        except Exception as e1:
            print(e1)
            logger.exception("Error")
            message = None
            raise e1
        finally:
            print("on message ", end='')
            print(message)
            """开始处理消息"""
            if isinstance(message, dict):
                """只处理合法的类型的请求"""
                mes_type = message['mes_type']  # 请求类型
                arg_dict = message.get('data_dict')  # 参数字典，不一定存在
                """检查身份，不一定成功"""
                user_id = check_session(self)
                if user_id is None:
                    """用户身份检测失败"""
                    pass
                else:
                    """开始分类处理消息"""
                    if mes_type == "all_last_position":
                        """
                        获取所有自己能看到的最后一次更新数据的位置点信息，
                        一般是在客户端刚刚连接上的时候发送的请求
                        """
                        if arg_dict is not None:
                            """调试模式，可以查看所有用户"""
                            is_debug = arg_dict.get("is_debug")
                            if is_debug:
                                user_id = "debug"
                            else:
                                pass
                        else:
                            pass
                        message = all_last_position(user_id)
                    else:
                        mes = "未知的请求类型:{}".format(mes_type)
                        mesage = self.package_message(mes_type, message=mes)
                    if message is not None:
                        self.write_message(message)
            else:
                pass

    def on_connection_close(self):
        ws_id = self.request.headers["Sec-Websocket-Key"]  # 从当前被关闭的连接中取出安全id
        WSIdMap.client_off_line(ws_id)


class ListenRequestHandler(tornado.web.RequestHandler):
    """
    接受flask传来的数据，这是接受flask数据的主要方式.未完成
    flask发送来的消息的格式：
         {
         mes_type: string    消息类型 字符串格式，用于区别不同的操作。
         data_dict: dict     消息内容，字典格式，自行约定
         }
    """
    def post(self):
        mes_type = self.get_argument("mes_type", default=None)
        if mes_type is None:
            self.write_error(406, exc_info="类型参数不能为空")
        else:
            if mes_type == "last_position":
                data_dict = self.get_argument('data_dict', dict())
                user_id = data_dict['position']


# 查看ip黑名单
class ViewBlackIpHandler(tornado.web.RequestHandler):
    def get(self):
        global BLACK_IP
        self.write(json.dumps(BLACK_IP))


# 统计在线人数/ip
class OnlineCount(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        global ID_IP
        self.write({"count": len(ID_IP)})

    @tornado.gen.coroutine
    def post(self):
        global ID_IP
        self.write({"ID_IP": ID_IP})


"""定义消息函数集合，专门处理和client的通讯消息，注意，这个系列的函数名必须调用时的mes_type保持一致"""


def all_last_position(user_id: str)->dict:
    """

    获取最后的位置点，为show_points函数提供数据。web-socket使用
    :param user_id: 用户的id，24位字符串，代表请求者的身份，注意这是一次性请求。
    :return:标准消息字典
    """
    res = list()
    mes_type = sys._getframe().f_code.co_name
    user_id = user_id  # user_id = "debug" 是调试用，查看所有的人的位置
    subordinate_id_list = Employee.subordinates_id(user_id)  # 获取下属/能查看的用户列表。
    if subordinate_id_list is None:
        """user_id错误"""
        mes = "user_id错误"
        res = InfoHandler.package_message(mes_type, message=mes)
    else:
        if len(subordinate_id_list) == 0:
            """没有下属，只能查看自己的位置了"""
            subordinate_id_list = [mongo_db.get_obj_id(user_id)]
        key = "all_last_position_{}".format(user_id)
        user_position_dict = cache.get(key)
        if user_position_dict is None:
            user_position_dict = Track.get_last_position(subordinate_id_list)  # 获取最后的点信息
            if sys.platform == "linux":
                timeout = 60 * 20
            else:
                timeout = 60 * 60 * 12
            cache.set(key, user_position_dict, timeout=timeout)
        else:
            pass
        user_position_list = list(user_position_dict.values())
        res = InfoHandler.package_message(mes_type, user_position_list)
    return res


"""消息函数集合定义结束"""


# 定义一个app对象。
app = tornado.web.Application(handlers=[
    (r'/ws', InfoHandler),  # ws连接
    (r'/listen_request', ListenRequestHandler),  # 接受flask发送过来的数据。
    (r'/listen_beat', ListenCORSSessionBeat),  # 接受跨域用户发过来的会话心跳信息。
    (r'/hello', Hello),  # 测试页面
    (r'/black_ip', ViewBlackIpHandler),  # 查看黑名单
    (r'/online', OnlineCount),  # 在线实时统计人数
    (r'/info', InfoHandler)  # 实时消息

], template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret="bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=", debug=False)  # app的配置


if __name__ == "__main__":  # 标准写法。
    # 启动日志,调试时注销日志，以方便调试
    logger.info("begin....")
    # 启动服务
    http_server = tornado.httpserver.HTTPServer(app)  # 一个http_server的实例对象。
    port = port + 1
    if sys.platform == "win32":
        http_server.listen(port)
        print("windows系统,消息推送服务运行{0}端口".format(port))
        tornado.ioloop.IOLoop.instance().start()
    else:

        http_server.bind(port)
        http_server.start(1)  # 注意，多进程下可能会存在进程间通讯问题
        print("linux系统,消息推送服务运行{0}端口".format(port))
        tornado.ioloop.IOLoop.current().start()