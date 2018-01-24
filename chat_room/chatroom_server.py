# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import tornado.httpserver, time, chat_room_manage, ext_tools
import tornado.ioloop
from tornado import autoreload
import tornado.options
import tornado.web
import tornado.httpclient
import os.path
import tornado.autoreload
import threading, json
from datetime import datetime
from tornado.options import define, options
import tornado.websocket, tornado.gen
from uuid import uuid4
import random
import online_news
import hashlib
import requests
import urllib.request
import urllib.parse
import platform
import user_module

define("port", default=9015, help="server run on the given port", type=int)  # 设置默认配置

print("营销直播室运行在9015端口....")

thread_dict = {}  # 实时行情客户线程池
data_dict = {}  # 行情数据字典

# ws服务器内容
################################


##############################################################
# 聊天室大厅的服务类

ws_dict = {}  # 全局变量，用于存放ws服务端对象
ws2_dict = {}  # 全局变量，用于存放老师的连接对象
questions = {}  # 全局变量，用于存放待审核的发言
ip_list = []  # 全局变量，用于存放被管制的IP地址
dialogs = []  # 全局变量，用于存放聊天的历史记录，有固定长度，用于客户登录的时候读取历史聊天记录，此数据在第一次启动程序的时候需要从数据库读取历史聊天记录
temp_dialogs = []  # 全局变量，用于定时把聊天记录写入数据库
delete_dialogs = []  # 全局变量，存放被删除的发言的uuid
access_ip_dict = {}  # 全局变量，存放access_ip对象，代表着访问主页的ip信息以ip为key，访问时间组成的数组为值

black_ip_file = open(file="logs" + os.sep + "{0} black_ip.log".format(datetime.now().strftime("%Y%m%d")), mode="a",
                     encoding="utf-8")


#################################################################
# 来访ip信息对象，主要用来统计短时期来访ip的频次，防止恶意的压力攻击。
def access_ip(ip):
    step = 1  # 检测的时间间隔，在此时间段内超过一定连接数就拉黑
    count = 100  # 预警值上限
    global access_ip_dict, ip_list
    access_date = datetime.now()
    if ip in access_ip_dict.keys():
        access_ip_dict[ip].append(access_date)
    else:
        access_ip_dict[ip] = [access_date]
    the_ip_list = access_ip_dict[ip]
    the_ip_list = [x for x in the_ip_list if (access_date - x).total_seconds() <= step]
    if len(the_ip_list) >= count:
        ip_list.append(ip)
        access_ip_dict.pop(ip)
        global black_ip_file
        astr = "{0} : {1}".format(str(access_date), ip)
        print(astr, file=black_ip_file)
        black_ip_file.flush()
    else:
        access_ip_dict[ip] = the_ip_list


# 根据黑名单容器，决定当前ip是否有资格访问
def validate_ip(ip):
    global ip_list
    if ip in ip_list:
        return False  # 在黑名单中的ip将被拒绝访问。
    else:
        return True  # 返回true表示可以访问


# 聊天室的ws对象
class CharRoomHandler(tornado.websocket.WebSocketHandler):  # ws服务器必须继承于tornado.websocket.WebSocketHandler。
    # print("CharRoomHandler")
    def check_origin(self, origin):  # 重写同源检查的方法，在每次请求到达时最先执行
        if len(ws_dict) > 400:
            print("已超过连接数")
            return False
        else:
            return True
        ###########################
        global ip_list
        if validate_ip(get_real_ip(self.request)):  # 检查是否在黑名单
            return True
        else:
            return False

    def open(self):  # 此方法在每次连接到达时执行。会给客户发送open的状态。
        ws_id = self.request.headers["Sec-Websocket-Key"]
        # print("new char room user")
        global ws_dict

        ws_dict[ws_id] = self
        # print("ws_dict is ",end=" ")
        # print(ws_dict)
        self.write_message({"ws_id": ws_id})  # 从请求头中取出安全id发送到客户端，让客户端作为身份凭证。
        global dialogs
        if len(dialogs) > 0:
            self.send_message({"data": dialogs})
        else:
            pass

    def on_close(self):  # 此方法必须写，用于防止用户直接关闭浏览器导致的异常。
        ws_id = self.request.headers["Sec-Websocket-Key"]  # 从当前被关闭的连接中取出安全id
        if ws_id in ws_dict.keys():
            ws_dict.pop(ws_id)  # 从线程池弹出此线程
        else:
            pass

    def on_message(self, message):
        # print("on message ",end='')
        # print(message)
        global ip_list
        # print(ip_list)
        # print(get_real_ip(self.request))
        if not validate_ip(get_real_ip(self.request)):
            self.close()
        else:
            message = json.loads(message)
            # print("on_message is ",end=" ")
            # print(message)
            if message.get("type") == "start_char":  # 如果是旧聊天室，提醒客户更新
                message = {"come_from": "dialog", "user_level": 6, "name": "系统管理员",
                           "time": datetime.now().strftime("%H:%M:%S"), "message": "聊天室已升级，请刷新页面后重试",
                           "ip": get_real_ip(self.request), "page_url": message["page_url"]}
                self.send_message({"data": [message]})
            elif message.get("dialog_type") == "start_char":
                pass
            elif message["dialog_type"] == "online":  # 注册用户上线信息，用于防止用户多处登录
                user_id = message["user_id"]
                send_all({"dialog_type": "online", "user_id": user_id}, [self])
            elif message["dialog_type"] == "delete_message":  # 删除已审核发言
                user_id = message["message_id"]
                send_all({"dialog_type": "delete_message", "message_id": user_id})
            elif message["dialog_type"] == "teacher":  # 老师发言
                # {"guest_id":"443","user_id":"3","user_name":"张三","dialog_message":"th","dialog_type":"teacher","page_url":"http://127.0.0.1:9015/","user_level":1}
                # {"user_level","name","time","message"}
                message = {"come_from": "dialog", "user_level": message["user_level"], "name": message["user_name"],
                           "time": datetime.now().strftime("%H:%M:%S"), "message": message["dialog_message"],
                           "message_id": uuid4().hex,
                           "ip": get_real_ip(self.request), "page_url": message["page_url"]}
                # print(message)
                send_all(message)
            else:  # 客户发言或者其他情况
                if validate_ip(get_real_ip(self.request)):
                    user_message = message["dialog_message"]
                    if not ext_tools.check_message(user_message):  # 如果没有找到违禁的词汇
                        message = {"come_from": "dialog", "user_level": message["user_level"],
                                   "name": message["user_name"], "time": datetime.now().strftime("%H:%M:%S"),
                                   "message": user_message, "ip": get_real_ip(self.request),
                                   "page_url": message["page_url"]}
                        global questions
                        message_id = uuid4().hex
                        questions[message_id] = message  # 把需要审核的发言放入全局容器
                        send_question_all("add_message", message_id, message)
                    else:
                        print("发现敏感词句:" + user_message)  # 发现违禁的词汇后就抛弃这条发言
                else:
                    pass

    def on_connection_close(self):
        ws_id = self.request.headers["Sec-Websocket-Key"]  # 从当前被关闭的连接中取出安全id
        if ws_id in ws_dict.keys():
            ws_dict.pop(ws_id)  # 从线程池弹出此线程
        else:
            pass

    def send_message(self, message):
        if validate_ip(get_real_ip(self.request)):
            self.write_message(message)
        else:
            pass


# 筛选发言的方法，把上线信息等辅助消息除去，只留下聊天室对话并加入全局容器。
def filter_message(message):
    global dialogs
    global temp_dialogs
    # print("filter_message ",end="= ")
    # print(message)
    if message.get("dialog_type") is None:  # 说明这是对话
        if len(dialogs) > 40:
            dialogs.pop(0)
        else:
            pass
        dialogs.append(message)
        temp_dialogs.append(message)
    else:
        pass


# 一个定时把留言写入数据库的类
class save_dialog_handler(threading.Thread):
    def __init__(self):
        self.thread_stop = False
        threading.Thread.__init__(self)

    def run(self):
        while not self.thread_stop:
            global temp_dialogs
            global delete_dialogs
            print("save_dialog_handler", end=" = ")
            print(temp_dialogs.copy(), end=" time = ")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            if len(temp_dialogs) == 0:
                pass
            else:
                save_dialog = [x for x in temp_dialogs if x not in delete_dialogs]
                print("存储发言到数据库")
                # print(save_dialog)
                url = "http://127.0.0.1:" + str(options.port - 1) + "/talks/save"
                resp = requests.post(url, {"messages": json.dumps(save_dialog)})
                print(resp.text)
                # db_tools.talks(the_type="save", messages=save_dialog)
                temp_dialogs = []
            if len(delete_dialogs) > 0:
                print("删除已存储发言")
                url = "http://127.0.0.1:" + str(options.port - 1) + "/talks/delete"
                resp = requests.post(url, {"messages": json.dumps(delete_dialogs)})
                print(resp.text)
                delete_dialogs = []
            else:
                pass
            time.sleep(15)

    def stop(self):
        self.thread_stop = True


saver = save_dialog_handler()
saver.setDaemon(True)
saver.start()
# 检测saver线程是否存活的方法 ,此方法在老师发言和客户发言被审核之前调用。
thread_error_file = open(file="logs" + os.sep + "{0} thread_serror.log".format(datetime.now().strftime("%Y%m%d")),
                         mode="a", encoding="utf-8")  # 全局变量，存放线程状态出错信息


def saver_is_alive():
    global saver
    if saver.is_alive():
        print("{0} saver is alive".format(str(datetime.now())))
        pass
    else:
        global thread_error_file
        astr = "{0} 定时写入数据库的线程失败，正在重新创建线程".format(str(datetime.now()))
        print(astr, file=thread_error_file)
        thread_error_file.flush()
        saver = save_dialog_handler()
        saver.setDaemon(True)
        saver.start()


# 启动程序时，加载数据库中发言历史记录的方法。
def load_talks():
    global dialogs
    url = "http://127.0.0.1:" + str(options.port - 1) + "/talks/load"
    resp = requests.post(url, {})
    print(resp.text)
    dialogs = json.loads(resp.text).get("data")


loader = threading.Thread(target=load_talks, daemon=1)
loader.start()


# 向所有用户发消息的方法
def send_all(message, exclude=[]):  # exclude是排除的对象的数组，在send_all的时候，不向此数组中的对象发送消息。
    saver_is_alive()  # 检测saver线程是否存活。
    global ws_dict
    # print("send_all",end=" = ")
    # print(message)
    if len(exclude) == 0:  # exclud不等于空的情况一般是上线信息等辅助信息
        filter_message(message)
    else:
        pass

    for x in ws_dict.keys():
        if ws_dict[x] in exclude:
            pass
        else:
            try:
                ws_dict[x].send_message({"data": [message]})
            except:
                ws_dict.pop(x)
                print("send_all function except!")


class question_handler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):  # 重写同源检查的方法，在每次请求到达时最先执行
        return validate_ip(get_real_ip(self.request))

    def open(self):  # 此方法在每次连接到达时执行。会给客户发送open的状态。
        ws2_id = self.request.headers["Sec-Websocket-Key"]
        # print("new char room user")
        global ws2_dict
        ws2_dict[ws2_id] = self
        # print("ws2_dict is ",end=" ")
        # print(ws2_dict)
        self.write_message({"ws_id": ws2_id})  # 从请求头中取出安全id发送到客户端，让客户端作为身份凭证。

    def on_close(self):  # 此方法必须写，用于防止用户直接关闭浏览器导致的异常。
        ws2_id = self.request.headers["Sec-Websocket-Key"]  # 从当前被关闭的连接中取出安全id
        if ws2_id in ws2_dict.keys():
            ws2_dict.pop(ws2_id)  # 从线程池弹出此线程
        else:
            pass

    def on_message(self, message):
        message = json.loads(message)
        # print("question_handler on message is ",end="")
        # print(message)
        the_type = message["the_type"]
        if the_type == "all_message":  # 启动管理页面时获取所有需要审核的发言
            global questions
            q = questions.copy()
            # print(q)
            message_list = []
            for x in q.keys():
                temp = {"message_id": x}
                temp.update(q[x])
                message_list.append(temp)
            message_list.reverse()
            self.send_message({"the_type": the_type, "message_list": message_list})
        else:
            message_id = message["message_id"]
            message = message["message"]
            send_question_all(the_type, message_id, message)

            if the_type == "allow_message":
                send_all(message)
            else:
                pass

    def on_connection_close(self):
        global ws2_dict
        ws2_id = self.request.headers["Sec-Websocket-Key"]  # 从当前被关闭的连接中取出安全id
        if ws2_id in ws2_dict.keys():
            ws2_dict.pop(ws2_id)  # 从线程池弹出此线程
        else:
            pass

    def send_message(self, message):
        if validate_ip(get_real_ip(self.request)):
            self.write_message(message)
        else:
            pass


# 发送待审核问题和操作这些发言的方法
def send_question_all(the_type, message_id, message=''):
    if the_type == "allow_message":
        global ws_dict
        global questions
        temp = {"message_id": message_id}
        # print(questions)
        try:
            temp.update(questions.pop(message_id))
            # 发送这条发言给客户
            send_all(temp)
        except KeyError as e:
            print("过时的审核信息,消息的 uuid 是", end=" ：")
            print(e)
        # 通知所有审核者此条留言已审核。
        for x in ws2_dict.keys():
            try:
                ws2_dict[x].send_message({"the_type": the_type, "message_id": message_id})
            except:
                ws2_dict.pop(x)
    elif the_type == "allow_ip":
        ip = message
        global ip_list
        if ip in ip_list:
            ip_list.remove(ip)
        else:
            pass
        for x in ws2_dict.keys():  # 通知所有管理员页面，此ip已被解除封禁
            ws2_dict[x].send_message({"the_type": the_type, "message_id": 0, "message": ip})
    elif the_type == "stop_ip":
        ip = message
        global ip_list
        if ip not in ip_list:
            ip_list.append(ip)
        else:
            pass
        for x in ws2_dict.keys():  # 通知所有管理员页面，此ip已被禁止
            ws2_dict[x].send_message({"the_type": the_type, "message_id": 0, "message": ip})
    elif the_type == "add_message":
        global ws2_dict
        for x in ws2_dict.keys():
            ws2_dict[x].send_message({"the_type": the_type, "message_id": message_id, "message": message})
    elif the_type == "delete_message":  # 删除发言
        global ws2_dict
        global questions
        global dialogs
        try:
            questions.pop(message_id)
            print("待审核发言 {0} 已删除".format(str(message_id)))
        except KeyError as e:
            print(e)
            try:
                print(dialogs[-1])
                for x in dialogs:  # 删除dialogs里已审核发言
                    if x["message_id"] == message_id:
                        dialogs.remove(x)
                        print("已审核发言 {0} 已删除".format(str(message_id)))
                        break
                    else:
                        pass
                global delete_dialogs
                delete_dialogs.append(message_id)  # 加入被删除发言的全局变量
            except KeyError as e:
                print(e)
                print("删除发言出现异常，uuid不存在")
        for x in ws2_dict.keys():
            ws2_dict[x].send_message({"the_type": the_type, "message_id": message_id, "message": message})
    else:
        print("未知的操作")


# ws服务器内容完毕。
# 定义一个方法，用于接收后台老师发来的消息。
class dialog_listen(tornado.web.RequestHandler):
    # 重写此方法是为了跨域请求
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    @tornado.gen.coroutine
    def post(self):
        # {"guest_id":guest_id,"user_id":user_id,"user_name":user_name,"teacher_id":teacher_id,"dialog_message":current_message,"dialog_type":"private","page_url":page_url}
        # 0。客户匿名id，1.注册用户id 2.员工id ，3消息内容 4.消息类型。5.消息日期。6.聊天室地址
        guest_id = self.get_argument("guest_id", 0)
        # print("cookie ")
        # print(not self.get_secure_cookie("user_id"))
        user_id = self.get_secure_cookie("user_id").decode() if self.get_secure_cookie("user_id") else 0
        # print(user_id)
        teacher_id = self.get_argument("teacher_id", 0)
        user_level = self.get_argument("user_level", 0)
        user_name = self.get_argument("user_name", '')
        dialog_message = self.get_argument("dialog_message", '')
        dialog_type = "teacher" if self.get_argument("dialog_type",
                                                     '') == "teacher"  else "wait"  # 只要发出来的消息不是老师发出的，全部要审核。
        page_url = self.get_argument("page_url", '')
        ip = get_real_ip(self.request)
        # {"user_level":message["user_level"],"name":message["user_name"],"time":datetime.now().strftime("%H:%M:%S"),"message":message["dialog_message"],"ip":get_real_ip(self.request),"page_url":message["page_url"]}
        message = {"user_level": user_level, "name": user_name, "time": datetime.now().strftime("%H:%M:%S"),
                   "message": dialog_message, "ip": ip, "page_url": page_url, "come_from": "dialog",
                   "dialog_type": dialog_type}

        if dialog_type == "teacher":
            send_all(message)
        else:
            global questions
            message_id = uuid4().hex
            questions[message_id] = message
            send_question_all("all_message", message_id, message)
        self.write({"message": "success"})
        # self.write(chart_room_manage.dialog(guest_id,user_id,user_level,user_name,teacher_id,dialog_message,dialog_type,page_url,ip))


# 登录后台账户管理l登录页面的，管理老师和巡官的账户
class admin_login_page(tornado.web.RequestHandler):
    def check_ip(self):
        ip = get_real_ip(self.request)
        return ip

    def get(self):
        self.render("admin_login_page.html")

    def post(self):
        self.get()


# 聊天室后台用户的管理员面 admin_user  有管理巡管和老师账号的功能
class manage_teacher_page(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        referer = '' if self.request.headers.get('referer') is None  else self.request.headers.get(
            "referer")  # 必须是从登录页面跳转过来的
        # print(referer)
        if referer is None or referer.split("/")[-1].find("admin_login_page") == -1:
            self.redirect("/admin_login_page")
        else:
            username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                                 bytes) else self.get_secure_cookie(
                "username")
            password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                                 bytes) else self.get_secure_cookie(
                "password")
            url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
            req_data = urllib.parse.urlencode({"username": username, "password": password})
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            message = {"message": "服务器忙，请稍后再试"}
            if resp.code == 200:
                message = json.loads(resp.body.decode())

            if message["message"] == "success" and message["teacher_name"] == "admin_user":
                print("is admin_user")
                self.set_secure_cookie("teacher_name", username, expires_days=0)
                self.render("manage_teacher.html", current_user=username)
            else:
                self.redirect("/admin_login_page")


# 聊天室后台发言和机器人管理页面 robots 管理发言和机器人
class dialog_and_robot(tornado.web.RequestHandler):
    def get(self):
        referer = '' if self.request.headers.get('referer') is None  else self.request.headers.get(
            "referer")  # 必须是从登录页面跳转过来的
        # print(referer)
        if referer is None or referer.split("/")[-1].find("admin_login_page") == -1:
            self.redirect("/admin_login_page")
        else:
            username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                                 bytes) else self.get_secure_cookie(
                "username")
            password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                                 bytes) else self.get_secure_cookie(
                "password")
            message = chat_room_manage.check_login(username, password)
            # print(message)
            if message["message"] == "success" and username == 'robots':
                self.render("dialog_robots_page.html", teacher_id=message["teacher_id"], teacher_name=username)
            else:
                self.redirect("/admin_login_page")


# 聊天室用户管理页面  一般管理员，只能管理聊天室用户账户 manager  聊天室用户管理账户
class manage_user_page(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        referer = '' if self.request.headers.get('referer') is None  else self.request.headers.get(
            "referer")  # 必须是从登录页面跳转过来的
        # print(referer)
        if referer is None or referer.split("/")[-1].find("admin_login_page") == -1:
            self.redirect("/admin_login_page")
        else:
            username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                                 bytes) else self.get_secure_cookie(
                "username")
            password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                                 bytes) else self.get_secure_cookie(
                "password")
            url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
            req_data = urllib.parse.urlencode({"username": username, "password": password})
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            message = {"message": "服务器忙，请稍后再试"}
            if resp.code == 200:
                message = json.loads(resp.body.decode())
            if message["message"] == "success" and username == "manager":
                self.render("manage_user.html", teacher_name=username, current_user=username,
                            user_level_list=json.dumps(chat_room_manage.edit_chatroom_user("view_level", {})))
            else:
                self.redirect("/admin_login_page")


# 聊天室后台发言管理页面  一般管理员，只具备发言管理功能
class admin_page(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        referer = '' if self.request.headers.get('referer') is None  else self.request.headers.get(
            "referer")  # 必须是从登录页面跳转过来的
        # print(referer)
        if referer is None or referer.split("/")[-1].find("admin_login_page") == -1:
            self.redirect("/admin_login_page")
        else:
            username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                                 bytes) else self.get_secure_cookie(
                "username")
            password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                                 bytes) else self.get_secure_cookie(
                "password")

            url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
            req_data = urllib.parse.urlencode({"username": username, "password": password})
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            message = {"message": "服务器忙，请稍后再试"}
            if resp.code == 200:
                message = json.loads(resp.body.decode())

            if message["message"] == "success" and username != "manager" and username != "admin_user" and username != "robots":
                print("admin_page ok")
                self.render("dialog_page.html", teacher_name=username, teacher_id=message["teacher_id"],
                            level_and_prefix=json.dumps(chat_room_manage.level_and_prefix()),
                            current_ip=get_real_ip(self.request))
            else:
                print("admin_page error")
                self.redirect("/admin_login_page")


# 处理登录视频聊天室管理页面的登录请求
class check_login(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        name = self.get_argument("username", '')
        password = self.get_argument("password", '')

        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        step = self.get_argument("step", 0)
        req_data = urllib.parse.urlencode({"username": name, "password": password, "step": step})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        if message["message"] == "success":  # 如果登录成功。
            self.set_secure_cookie("username", name, expires_days=None)  # expires_days=None是设置立即过期，否则默认的过期时间是30填
            self.set_secure_cookie("password", password, expires_days=None)  # expires_days=None是设置立即过期，否则默认的过期时间是30填
        else:
            self.clear_all_cookies()
        self.write(message)


# 获取聊天室在线人数的方法。
class count_online(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        global ws_dict
        global ws2_dict
        user_count = len(ws_dict)
        admin_count = len(ws2_dict)
        # print("count is "+str(length))
        self.write(str(user_count - admin_count))


# 获取l老师管理员列表。
class get_teacher_user(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                             bytes) else self.get_secure_cookie(
            "username")
        password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                             bytes) else self.get_secure_cookie(
            "password")
        url = "http://127.0.0.1:{0}/query_teacher_admin".format(options.port - 1)
        step = self.get_argument("step", 0)
        req_data = urllib.parse.urlencode({"username": username, "password": password, "step": step})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        print(message)
        self.write(message)


# 操作老师管理员的各种请求。
class edit_teacher_user(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self, input):
        username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                             bytes) else self.get_secure_cookie(
            "username")
        password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                             bytes) else self.get_secure_cookie(
            "password")
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        step = self.get_argument("step", 0)
        req_data = urllib.parse.urlencode({"username": username, "password": password, "step": step})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        if message["message"] == "success":
            objname = self.get_argument("objname", '')
            password = self.get_argument("password", '')

            url = "http://127.0.0.1:{0}/edit_teacher_user".format(options.port - 1)
            step = self.get_argument("step", 0)
            req_data = urllib.parse.urlencode({"objname": objname, "password": password, "input": input})
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            message = {"message": "服务器忙，请稍后再试"}
            if resp.code == 200:
                message = json.loads(resp.body.decode())

            self.write(message)


# 操作聊天室账户的各种请求。
class edit_chatroom_user(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self, input):
        username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                             bytes) else self.get_secure_cookie(
            "username")
        password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                             bytes) else self.get_secure_cookie(
            "password")
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        step = self.get_argument("step", 0)
        req_data = urllib.parse.urlencode({"username": username, "password": password, "input": input})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())
        if message["message"] == "success":
            args = self.get_argument("data", {})
            args = args if isinstance(args, dict) else json.loads(args)
            # print(args)
            # print(type(args))
            url = "http://127.0.0.1:{0}/edit_chatroom_user".format(options.port - 1)
            req_data = urllib.parse.urlencode({"input": input, "args": args})
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            message = {"message": "服务器忙，请稍后再试"}
            if resp.code == 200:
                message = json.loads(resp.body.decode())
            self.write(message)


# 获取ip黑名单
class get_black_ip(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                             bytes) else self.get_secure_cookie(
            "username")
        password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                             bytes) else self.get_secure_cookie(
            "password")
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        step = self.get_argument("step", 0)
        req_data = urllib.parse.urlencode({"username": username, "password": password, "input": input})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())
        if message["message"] == "success":
            global ip_list
            ips = ip_list.copy()
            self.write({"message": "success", "data": ips})
        else:
            self.write({"message": "权限不足"})


class ShowUser(tornado.web.RequestHandler):
    """显示注册用户"""
    @tornado.gen.coroutine
    def get(self):
        username = self.get_secure_cookie("username").decode() if isinstance(self.get_secure_cookie("username"),
                                                                             bytes) else self.get_secure_cookie(
            "username")
        password = self.get_secure_cookie("password").decode() if isinstance(self.get_secure_cookie("password"),
                                                                             bytes) else self.get_secure_cookie(
            "password")
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        req_data = urllib.parse.urlencode({"username": username, "password": password, "input": input})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            message = json.loads(resp.body.decode())
            if message["message"] == "success":
                all_user_list = user_module.all_user()
                self.render("show_user.html", all_user_list=all_user_list)
            else:
                self.redirect("/admin_login_page")
        else:
            self.write_error(505)


# 对营销直播室老师风采的各种操作。
class teachers(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self, the_type=''):
        message = {"message": "success"}
        url = "http://127.0.0.1:{0}/teachers".format(options.port - 1)
        if the_type != "":
            t_name, t_nickname, t_description, t_password, t_title, t_can_use, t_id = self.get_argument("t_name",
                                                                                                        ""), self.get_argument(
                "t_nickname", ""), self.get_argument("t_description", ""), self.get_argument("t_password",
                                                                                             ""), self.get_argument(
                "t_title", ""), self.get_argument("t_can_use", 1), self.get_argument("t_id", 0)
            adata = {"the_type": the_type, "t_name": t_name, "t_nickname": t_nickname, "t_description": t_description,
                     "t_password": t_password, "t_title": t_title, "t_can_use": t_can_use, "t_id": t_id}
            req_data = urllib.parse.urlencode({"data": adata})
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            message = {"message": "服务器忙，请稍后再试"}
            if resp.code == 200:
                message = json.loads(resp.body.decode())
        else:
            message = {"message": "未知的操作"}
        self.write(message)


# 读取/保存课程表
class edit_class(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self, the_type):
        class_data = json.loads(self.get_argument("class_data")) if self.get_argument("class_data", '') != '' else ''
        url = "http://127.0.0.1:{0}/edit_class".format(options.port - 1)
        adata = {"the_type": the_type, "class_data": class_data}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())
        message = chat_room_manage.edit_class(the_type=the_type, class_data=class_data)
        self.write(message)


# 课程表和老师风采的后台管理页面
class tab_news_table(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        message = {"message": "error"}
        username = '' if self.get_secure_cookie("username") is None else self.get_secure_cookie("username").decode()
        password = '' if self.get_secure_cookie("password") is None else self.get_secure_cookie("password").decode()
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        adata = {"username": username, "password": password}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        print(resp)
        if resp.code == 200:
            message = json.loads(resp.body.decode())
            print(message)
        print(message)
        # message = chart_room_manage.check_login(username, password)
        if message["message"] == "success":
            url2 = "http://127.0.0.1:{0}/teachers".format(options.port - 1)
            adata2 = {"the_type": "all"}
            req_data2 = urllib.parse.urlencode({"data": adata2})
            req2 = tornado.httpclient.HTTPRequest(url=url2, method="POST", body=req_data2)
            client2 = tornado.httpclient.AsyncHTTPClient()
            resp2 = yield tornado.gen.Task(client2.fetch, req2)
            if resp2.code == 200:
                teachers = json.loads(resp2.body.decode())
                print("teacher is ", end=": ")
                print(teachers)
                teacher_list = [x["t_nickname"] + " " + x["t_name"] for x in
                                teachers["data"]]
                self.render("tab_news_table.html", teacher_list=json.dumps(teacher_list))
            else:
                self.write("服务器忙")
        else:
            self.write("没有足够的权限")


# 老师登录聊天室私聊后台页面的请求
# class login_dialog_page(tornado.web.RequestHandler):
#
#     def post(self):
#         teacher_id = self.get_argument("teacher_id", "0")
#         teacher_password = self.get_argument("teacher_password", '')
#         ws_id = self.get_argument("ws_id", 0)
#         if teacher_id == 0 or teacher_password == "" or ws_id == 0:
#             self.write({"message": "参数不足"})
#         else:
#             if chart_room_manage.login_dialog_page(teacher_id, teacher_password, ws_id)["message"] == "success":
#                 self.set_secure_cookie("teacher_id", teacher_id)
#                 self.set_secure_cookie("teacher_password", teacher_password)
#                 self.write({"message": "success"})
#             else:
#                 self.write(chart_room_manage.login_dialog_page(teacher_id, teacher_password, ws_id))
#     def get(self):


# 客户登录聊天室页面的请求
class chartroom_user_login(tornado.web.RequestHandler):
    # 重写此方法是为了跨域请求
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    @tornado.gen.coroutine
    def post(self):
        user_name = self.get_argument("user_name", '')
        user_password = self.get_argument("user_password", '')
        user_phone = self.get_argument("user_phone", '')
        nick_name = self.get_argument("nick_name", "")
        message = {"message": "error"}
        ip = get_real_ip(self.request)  # 获取ip
        url = "http://127.0.0.1:{0}/chartroom_user_login".format(options.port - 1)
        adata = {"user_name": user_name, "user_password": user_password, "ip": ip}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            message = json.loads(resp.body.decode())
        message = chat_room_manage.chartroom_user_login(user_name, user_password, ip)
        if message["message"] == "success":
            self.set_secure_cookie("user_id", message["user_id"], expires_days=None)  # 用户id
            self.set_secure_cookie("user_name", message["user_name"], expires_days=None)  # 用户名/账户
            self.set_secure_cookie("nick_name", message["real_name"], expires_days=None)  # 用户昵称
            self.set_secure_cookie("user_password", user_password, expires_days=None)  # 用户密码
            self.set_secure_cookie("user_level", message["level"], expires_days=None)  # 用户级别
        else:
            self.clear_all_cookies()
        self.write(message)


# 聊天室客户修改个人资料
class edit_user_info(tornado.web.RequestHandler):
    # 重写此方法是为了跨域请求
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    @tornado.gen.coroutine
    def post(self):
        try:
            user_id = self.get_secure_cookie("user_id").decode()
        except:
            user_id = '' if self.get_argument("user_id", 0) == 0 else self.get_argument("user_id")
        # print("user id is "+user_id)
        real_name = self.get_argument("u_AccountName", '')
        nick_name = self.get_argument("nick_name", "")
        new_password = self.get_argument("new_password", '')
        message = {"message": "error"}
        url = "http://127.0.0.1:{0}/edit_user_info".format(options.port - 1)
        adata = {"real_name": real_name, "new_password": new_password, "user_id": user_id, "nick_name": nick_name}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            message = json.loads(resp.body.decode())
        self.write(message)


# 聊天室客户修改绑定的手机号码
class change_user_phone(tornado.web.RequestHandler):
    # 重写此方法是为了跨域请求
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    @tornado.gen.coroutine
    def post(self):
        try:
            user_id = self.get_secure_cookie("user_id").decode()
        except:
            user_id = '' if self.get_argument("user_id", 0) == 0 else self.get_argument("user_id")
        # print("user id is "+user_id)
        phone = self.get_argument("phone", '')
        message = {"message": "error"}
        url = "http://127.0.0.1:{0}/change_user_phone".format(options.port - 1)
        adata = {"phone": phone, "user_id": user_id}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            message = json.loads(resp.body.decode())
        self.write(message)


# 聊天室后台对话页面
class dialog_page(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        teacher_id = self.get_secure_cookie("username") if self.get_secure_cookie("username") else 0
        # print("teacher_id is "+str(teacher_id))
        if teacher_id == 0:
            self.redirect("错误的请求")
        else:
            message = "error"
            url = "http://127.0.0.1:{0}/edit_teacher_user".format(options.port - 1)
            adata = {"input": "find_name", "objname": teacher_id}
            req_data = urllib.parse.urlencode(adata)
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            if resp.code == 200:
                message = json.loads(resp.body.decode())
            t_name = message
            # 获取用户级别和图标路径的字典
            level_and_prefix = []
            url2 = "http://127.0.0.1:{0}/level_and_prefix".format(options.port - 1)
            req2 = tornado.httpclient.HTTPRequest(url=url2, method="POST")
            client2 = tornado.httpclient.AsyncHTTPClient()
            resp2 = yield tornado.gen.Task(client2.fetch, req2)
            if resp2.code == 200:
                level_and_prefix = json.loads(resp2.body.decode())
            if t_name == 0:
                self.render("dialog_page.html", teacher_id=teacher_id, teacher_name=None,
                            level_and_prefix=json.dumps(level_and_prefix),
                            current_ip=get_real_ip(self.request))
            else:
                self.render("dialog_page.html", teacher_id=teacher_id, teacher_name=t_name,
                            level_and_prefix=json.dumps(level_and_prefix),
                            current_ip=get_real_ip(self.request))


# 聊天室后台放行/禁止客户发言的请求
class change_question_status(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        message_id = self.get_argument("message_id")
        the_type = self.get_argument("the_type")
        send_question_all(the_type, message_id)
        self.write({"message": "success"})


# 聊天室首页之前的登录页面
class chatroom_login_page(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.render("chatroom_login_page.html")


# 聊天室首页，于windows下面工作
class chat_index_nt(tornado.web.RequestHandler):
    def get(self):
        ip = get_real_ip(self.request)  # 获取ip
        print(validate_ip(get_real_ip(self.request)))
        access_ip(ip)

        if not validate_ip(ip):
            self.write("当前页面无法访问")
        else:
            username = self.get_secure_cookie("user_name").decode() if isinstance(self.get_secure_cookie("user_name"),
                                                                                  bytes) else self.get_secure_cookie(
                "user_name")
            password = self.get_secure_cookie("user_password").decode() if isinstance(
                self.get_secure_cookie("user_password"), bytes) else self.get_secure_cookie("user_password")
            referer = '' if self.request.headers.get('referer') is None  else self.request.headers.get(
                "referer")  # 获取前导页面url
            message = chat_room_manage.chartroom_user_login(username, password, ip)
            print("index login")
            # print(message)
            nick_name = '游客 ' if message.get("real_name") is None or message.get("real_name") == "" else message.get(
                "real_name")
            user_id = 0 if message.get("user_id") is None else message.get("user_id")
            u_phone = 0 if message.get("u_phone") is None else message.get("u_phone")
            user_level = 0 if message.get("level") is None else message.get("level")
            guest_id = 0 if self.get_secure_cookie("guest_id") is None  else self.get_secure_cookie(
                "guest_id").decode()  # 获取匿名id
            print("index's guest_id is {0}".format(guest_id))
            print(self.get_secure_cookie("guest_id"))
            if int(guest_id) == 0:
                now = datetime.now().strftime("%Y%m%d%H%M%S%f")  # g格式化输出到毫秒
                random_number = random.randint(0, 999)  # 生成随机数，跟日期一起作为新id的唯一判断。
                guest_id = int(now[2:-3] + str(random_number))
                self.set_secure_cookie("guest_id", str(guest_id))
            else:
                pass
            print("发首页")
            self.render("live_center.html", nick_name=nick_name, user_id=user_id, user_name=username,
                        user_level=user_level, u_phone=u_phone, guest_id=guest_id,
                        level_and_prefix=json.dumps(chat_room_manage.level_and_prefix()))
            print("首页发送成功 windows")


# 于非windows下面工作
class chat_index(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        print(validate_ip(get_real_ip(self.request)))
        access_ip(get_real_ip(self.request))
        if not validate_ip(get_real_ip(self.request)):
            self.write("当前页面无法访问")
        else:
            username = self.get_secure_cookie("user_name").decode() if isinstance(self.get_secure_cookie("user_name"),
                                                                                  bytes) else self.get_secure_cookie(
                "user_name")
            password = self.get_secure_cookie("user_password").decode() if isinstance(
                self.get_secure_cookie("user_password"), bytes) else self.get_secure_cookie("user_password")
            ip = get_real_ip(self.request)  # 获取ip
            referer = '' if self.request.headers.get('referer') is None  else self.request.headers.get(
                "referer")  # 获取前导页面url
            guest_id = 0 if self.get_secure_cookie("guest_id") is None  else self.get_secure_cookie(
                "guest_id").decode()  # 获取匿名id
            print("index's guest_id is {0}".format(guest_id))
            print(self.get_secure_cookie("guest_id"))
            if int(guest_id) == 0:
                now = datetime.now().strftime("%Y%m%d%H%M%S%f")  # g格式化输出到毫秒
                random_number = random.randint(0, 999)  # 生成随机数，跟日期一起作为新id的唯一判断。
                guest_id = int(now[2:-3] + str(random_number))
                self.set_secure_cookie("guest_id", str(guest_id))
            else:
                pass
            message = {"message": "error"}
            url = "http://127.0.0.1:{0}/chartroom_user_login".format(options.port - 1)
            adata = {"user_name": username, "user_password": password, "ip": ip}
            req_data = urllib.parse.urlencode(adata)
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            if resp.code == 200:
                message = json.loads(resp.body.decode())

            print("index login")
            # print(message)
            nick_name = '游客 ' if message.get("real_name") is None or message.get("real_name") == "" else message.get(
                "real_name")
            user_id = 0 if message.get("user_id") is None else message.get("user_id")
            u_phone = 0 if message.get("u_phone") is None else message.get("u_phone")
            user_level = 0 if message.get("level") is None else message.get("level")
            # 获取用户级别和图标路径的字典
            level_and_prefix = []
            url2 = "http://127.0.0.1:{0}/level_and_prefix".format(options.port - 1)
            req2 = tornado.httpclient.HTTPRequest(url=url2, method="POST")
            client2 = tornado.httpclient.AsyncHTTPClient()
            resp2 = yield tornado.gen.Task(client2.fetch, req2)
            if resp2.code == 200:
                level_and_prefix = json.loads(resp2.body.decode())
            self.render("live_center.html", nick_name=nick_name, user_id=user_id, user_name=username,
                        user_level=user_level, u_phone=u_phone, guest_id=guest_id,
                        level_and_prefix=json.dumps(level_and_prefix))
            print("首页发送完毕 linux")


# 点击下载聊天室快捷方式
class download_url(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        filename = "www.18lion.com:9015.url"
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + filename)
        self.write("[InternetShortcut]\rURL=http://www.18lion.com:9015")
        self.flush()


# 查询客户分级的请求
class query_user_level(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        # 0 级别id  1 级别顺序 2 级别名字
        level = []
        url = "http://127.0.0.1:{0}/edit_chatroom_user".format(options.port - 1)
        adata = {"input": "view_level", "args": {}}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            level = json.loads(resp.body.decode())

        self.write(level)


# 对聊天室机器人的各种操作请求
# class operate_robot(tornado.web.RequestHandler):
#     def post(self, input):
#         if input == "index":
#             pass  # 返回操作页面
#         elif input == "init":
#             return robot.init_robots()
#         else:
#             args = self.request.arguments
#             result = robot.robot_handler(input, args)
#             print("操作机器人的返回信息：")
#             print(result)
#             self.write(result)
#
#     def get(self, input):
#         self.post(input)


# 获取公共发言库的发言
# class query_dialog(tornado.web.RequestHandler):
#     def get(self):
#         job_id = self.get_argument("job_id", "")
#         page_number = self.get_argument("page_number", 0)
#         self.write(robot.backup_dialog(job_id, page_number))
#
#     def post(self):
#         self.get()


# 机器人设置页面
# class robots(tornado.web.RequestHandler):
#     def get(self):
#         teacher_id = self.get_secure_cookie("username") if self.get_secure_cookie("username") else 0
#         print("robots teacher_id is " + str(teacher_id))
#         if teacher_id == 0:
#             self.redirect("/91dashicnlogin?from=robots")
#         else:
#             t_name = chart_room_manage.edit_teacher_user("find_name", teacher_id.decode())["message"]
#             if t_name == 0:
#                 self.render("robots.html", teacher_id=teacher_id, teacher_name=None)
#             else:
#                 self.render("robots.html", teacher_id=teacher_id, teacher_name=t_name)


# class get_robot_dialog_list(tornado.web.RequestHandler):
#     def post(self):
#         robot_id = self.get_argument("robot_id")
#         self.write(robot.get_robot_dialog_list(robot_id))


# 插入机器人发言库的方法
# class update_robot_dialog(tornado.web.RequestHandler):
#     def post(self):
#         robot_id = self.get_argument("robot_id")
#         owner_id = self.get_argument("owner_id")
#         str_list = json.loads(self.get_argument("str_list"))
#         delete_list = json.loads(self.get_argument("delete_list", "[]"))
#         # print(len(str_list))
#         self.write(robot.update_robot_dialog(robot_id, owner_id, str_list, delete_list))


# 操作机器人化名的类
# class robot_alias(tornado.web.RequestHandler):
#     def post(self, input):
#         alias_list = json.loads(self.get_argument("alias_list", "[]"))
#         delete_list = json.loads(self.get_argument("delete_list", "[]"))
#         self.write(robot.robot_alias(input, alias_list, delete_list))


# 一个获取真实ip的方法
def get_real_ip(request):
    ip = ""
    try:
        ip = request.headers["X-Forwarded-For"].split(":")[0]
    except KeyError as e:
        ip = request.remote_ip
    return ip


# request这个参数就是self.request
# 提供匿名id和记录匿名用户的操作
class guest_message(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        ip = get_real_ip(self.request)  # 获取ip
        id = self.get_argument("id", 0)
        event_type = self.get_argument("event_type", "未知")
        referer = self.get_argument("referer", "")
        page_url = self.get_argument("page_url", "")
        message = []
        url = "http://127.0.0.1:{0}/guest_message".format(options.port - 1)
        adata = {"id": id, "event_type": event_type, "referer": referer, "page_url": page_url, "ip": ip}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        self.write(json.dumps(message))


# 发送新闻数据的信息,接收post请求，不是用于ws方式的。
class get_caijing_data(tornado.web.RequestHandler):
    # 重写此方法是为了跨域请求
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Cache-Control', 'public, max-age=7200')
        self.set_header('Content-type', 'application/json')  # 指定了返回类型为json

    @tornado.gen.coroutine
    def post(self, input):
        if input == "news":
            message = {"data": []}
            # 注意，开启跨域后返回的数据不再需要JSON.parse()方法
            md5_str = self.get_argument("md5_str", "")
            anews = online_news.get_jin10_news()
            md5_2 = hashlib.md5(json.dumps(anews).encode())
            if md5_str == '' or md5_str.lower() != md5_2:
                message = {"data": anews}
            else:
                pass
            self.write(json.dumps(message))
        elif input == "calendar":
            pass
        else:
            self.write("nothing...")


# 查询虚拟客户跟单 收益
class get_win_info(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        message = []
        url = "http://127.0.0.1:{0}/create_info".format(options.port - 1)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=urllib.parse.urlencode({}))
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        # print(resp.code)
        # print(resp)
        if resp.code == 200:
            message = json.loads(resp.body.decode())
            # print("message is ",end="")
            # print(message)
        self.write(message)


# 用户注册
class user_reg(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        ip = get_real_ip(self.request)  # 获取ip
        guest_id = self.get_cookie("guest_id")
        # print("guest_id is "+str(guest_id))
        page_url = self.get_argument("page_url", "")
        nick_name = self.get_argument("nick_name", "")
        user_phone = self.get_argument("user_phone", "")
        user_password = self.get_argument("user_password", "")
        user_name = self.get_argument("user_name", "")
        message = {"message": "error"}
        url = "http://127.0.0.1:{0}/user_reg".format(options.port - 1)
        adata = {"user_name": user_name, "user_password": user_password, "user_phone": user_phone,
                 "nick_name": nick_name, "ip": ip}
        req_data = urllib.parse.urlencode(adata)
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        self.write(message)


# 用户在聊天室注册用户时，当用户名失焦的时候，检测用户名是否重复的方法
class check_user_repeat(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        user_name = self.get_argument("user_name", '')
        if user_name == '':
            self.write({"message": "用户名不能为空"})
        else:
            message = {"message": "error"}
            url = "http://127.0.0.1:{0}/check_user_repeat".format(options.port - 1)
            adata = {"user_name": user_name}
            req_data = urllib.parse.urlencode(adata)
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            if resp.code == 200:
                message = json.loads(resp.body.decode())
            self.write(message)


# 20160513 添加，查询security，判断是否已经登录，如果登录写出用户级别,根据用户级别判断是否返回每日策略
class show_method_or_not(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        username = self.get_secure_cookie("user_name").decode() if isinstance(self.get_secure_cookie("user_name"),
                                                                              bytes) else self.get_secure_cookie(
            "user_name")
        password = self.get_secure_cookie("user_password").decode() if isinstance(
            self.get_secure_cookie("user_password"), bytes) else self.get_secure_cookie("user_password")
        user_level = self.get_secure_cookie("user_level").decode() if isinstance(self.get_secure_cookie("user_level"),
                                                                                 bytes) else self.get_secure_cookie(
            "user_level")
        # self.write(json.dumps([username,password,user_level]))
        # user_name_front_page_html=self.get_argument('username','not_transport') #从前端页面传送过来的用户名称
        message = {"message": "error"}
        print("show_method_or_not")
        print(username)
        print(password)
        if username is None or password is None:
            # print([username,password])
            message['message'] = '请先登录'
            self.clear_all_cookies()  # 清除掉所有的cookie
            self.write(message)
        else:
            message = {"message": "error"}
            url = "http://127.0.0.1:{0}/chartroom_user_login".format(options.port - 1)
            adata = {"user_name": username, "user_password": password, "ip": get_real_ip(self.request)}
            req_data = urllib.parse.urlencode(adata)
            req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
            client = tornado.httpclient.AsyncHTTPClient()
            resp = yield tornado.gen.Task(client.fetch, req)
            if resp.code == 200:
                re1 = json.loads(resp.body.decode())

            if re1["message"] == "success":
                if int(re1["level"]) > 4:
                    message["message"] = "需要铜牌以上用户才能查看，请联系客户提升等级"
                else:
                    url2 = "http://127.0.0.1:{0}/tips".format(options.port - 1)
                    req_data2 = urllib.parse.urlencode({"the_type": "top5", "args_dict": {}})
                    req2 = tornado.httpclient.HTTPRequest(url=url2, method="POST", body=req_data2)
                    client2 = tornado.httpclient.AsyncHTTPClient()
                    resp2 = yield tornado.gen.Task(client2.fetch, req2)
                    res = {"message": "服务器忙，请稍后再试"}
                    if resp2.code == 200:
                        res = json.loads(resp2.body.decode())
                        message = {"message": "success", "data": json.dumps(res["data"])}
            else:
                message["message"] = "用户名或密码错误"
            self.write(message)


# 每日策略的各种操作
class tips(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self, the_type):
        username = '' if self.get_secure_cookie("username") is None else self.get_secure_cookie("username").decode()
        password = '' if self.get_secure_cookie("password") is None else self.get_secure_cookie("password").decode()
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        req_data = urllib.parse.urlencode({"username": username, "password": password})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        if message["message"] == "success":
            e_id = self.get_argument("e_id", "")
            e_title = self.get_argument("e_title", "")
            e_content = self.get_argument("e_content", "")
            e_author = self.get_argument("e_author", "")
            adata = {"e_id": e_id, "e_title": e_title, "e_content": e_content, "e_author": e_author}
            url2 = "http://127.0.0.1:{0}/tips".format(options.port - 1)
            req_data2 = urllib.parse.urlencode({"the_type": the_type, "args_dict": adata})
            req2 = tornado.httpclient.HTTPRequest(url=url2, method="POST", body=req_data2)
            client2 = tornado.httpclient.AsyncHTTPClient()
            resp2 = yield tornado.gen.Task(client2.fetch, req2)
            message = {"message": "服务器忙，请稍后再试"}
            if resp2.code == 200:
                message = json.loads(resp2.body.decode())
                # message = chart_room_manage.tips(the_type=the_type, args_dict=adata)
        else:
            message = {"message": "权限不足"}

        self.write(message)


# 今日策略管理页面
class tips_page(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        username = '' if self.get_secure_cookie("username") is None else self.get_secure_cookie("username").decode()
        password = '' if self.get_secure_cookie("password") is None else self.get_secure_cookie("password").decode()
        url = "http://127.0.0.1:{0}/check_admin_login".format(options.port - 1)
        req_data = urllib.parse.urlencode({"username": username, "password": password})
        req = tornado.httpclient.HTTPRequest(url=url, method="POST", body=req_data)
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(client.fetch, req)
        message = {"message": "服务器忙，请稍后再试"}
        if resp.code == 200:
            message = json.loads(resp.body.decode())

        if message["message"] == "success":
            self.render("tips.html", current_user=username)
        else:
            self.write("没有足够的权限")


# 接收jin10首页发送过来的数据传给后端处理。
class jin10_index(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        # print(self.request.arguments)
        info_list = json.loads(self.get_argument("info_list"))
        try:
            online_news.listen_jin10_index(info_list)
            self.write({"message": "success"})
        except:
            self.write({"message": "error"})


# 上传图片
class upload_img(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def post(self):
        # 文件的暂存路径
        upload_path = "static\\update_image"
        # 判断目录是否存在？不存在就创建目录
        if os.path.exists(upload_path):  # 如果这个目录存在
            pass
        else:
            os.makedirs(upload_path)  # 否则创建这个目录 注意不要用成mkdir方法，那个方法会报错。
        print(upload_path)
        # 提取表单中‘name’为‘file’的文件元数据
        print(self.request.files)
        file_metas = self.request.files['myfile']
        filename = ''
        for meta in file_metas:
            filename = meta['filename']  # 不可使用文件的本名，因为那样会导致文件名重复，只取文件的后缀名即可，
            filename = datetime.now().strftime("%Y%m%d%H%M%S%f") + str(random.randint(10, 99)) + "." + \
                       filename.split(".")[-1]  # 格式化到毫秒再加一个任意数
            filepath = upload_path + "\\" + filename
            # 有些文件需要已二进制的形式存储，实际中可以更改
            with open(filepath, 'wb') as up:
                up.write(meta['body'])

        name = "巡管" if self.get_secure_cookie("current_alias") is None else self.get_secure_cookie(
            "current_alias").decode()
        page_url = "" if self.get_secure_cookie("page_url") is None else self.get_secure_cookie("page_url").decode()
        src = "../static/update_image/" + filename
        # img="<img src='"+src+"'/>"
        img = "<a class='example-image-link' href='" + src + "' data-lightbox='example-1'><img class='example-image' src='" + src + "'/></a>"  # 配合Lightbox插件的写法的
        message = {"come_from": "dialog", "time": datetime.now().strftime("%H:%M:%S"), "name": name, "message": img,
                   "page_url": page_url, "user_level": 6, "ip": get_real_ip(self.request), "message_id": uuid4().hex}
        send_all(message)
        self.write("static/update_image/" + filename)


###########################################################################################################
# 定义一个app对象。
app = tornado.web.Application(handlers=[
    (r'/admin_login_page', admin_login_page),  # ；管理后台账户的登录页
    (r'/manage_teacher_page', manage_teacher_page),  # ；聊天室后台用户管理也  admin_user用
    (r'/dialog_and_robot', dialog_and_robot),  # ；聊天室后台用户管理也 robots用
    (r'/manage_user_page', manage_user_page),  # ；聊天室后台用户管理也 manager用
    (r'/admin_page', admin_page),  # ；聊天室后台用户管理也 一般巡管用
    (r"/dialog_listen", dialog_listen),  # 接收私聊客户发来的数据。
    (r'/check_login', check_login),  # 检测老师登录的用户名和密码
    (r'/count_online', count_online),  # 获取聊天室在线人数的方法。
    (r'/get_teacher_user', get_teacher_user),  # 获取后台老师用户列表
    (r'/show_user', ShowUser), # 显示注册用户
    (r'/edit_teacher_user/(\w+)', edit_teacher_user),  # 编辑后台管理员用户信息
    (r'/teachers/(\w+)', teachers),  # 编辑老师风采的各种操作
    (r'/class/(\w+)', edit_class),  # 读取/保存课程表
    (r'/class_table', tab_news_table),  # 课程表和老师风采后台管理也页面
    (r'/edit_chatroom_user/(\w+)', edit_chatroom_user),  # 编辑聊天室用户信息
    # (r'/teacher_login', login_dialog_page),  # 聊天室老师登录
    (r'/user_login', chartroom_user_login),  # 聊天室客户登录
    (r'/user_reg', user_reg),  # 聊天室客户注册
    (r'/check_user_repeat', check_user_repeat),  # 用户在聊天室注册用户时，当用户名失焦的时候，检测用户名是否重复的方法
    (r'/query_user_level', query_user_level),  # 查询聊天室用户的分级资料
    (r'/edit_user_info', edit_user_info),  # 聊天室客户修改个人资料
    (r'/change_user_phone', change_user_phone),  # 聊天室客户修改绑定手机
    (r'/dialog_page', dialog_page),  # 聊天室后台私聊页面
    (r'/change_question_status', change_question_status),  # 聊天室后台放行/禁止客户发言的请求
    (r'/', chat_index_nt if platform.system() == "Windows" else chat_index),  # 聊天室是首页
    (r'/download_url', download_url),  # 点击下载聊天室快捷方式
    (r'/upload_image', upload_img),  # 上传图片
    (r"/live_login.php", chatroom_login_page),  # 聊天室登录前页面
    (r'/char', CharRoomHandler),  # ；ws
    (r'/questions', question_handler),  # 管理发言和ip的ws对象
    # (r'/operate_robot/(\w+)', operate_robot),  # 对机器人的操作请求，比如创建，管理运行等
    # (r'/query_dialog', query_dialog),  # 查询聊天发言库
    # (r'/robots', robots),  # 机器人的设置管理页面
    # (r'/get_robot_dialog_list', get_robot_dialog_list),  # 查询机器人的全部聊天库
    # (r'/update_robot_dialog', update_robot_dialog),  # 更新单个机器人的发言库
    # (r'/robot_alias/(\w+)', robot_alias),  # 对机器人别名的各种操作
    (r'/guest_message', guest_message),  # 提供匿名id 的服务和记录工作
    (r'/get_caijing_data/(\w+)', get_caijing_data),  # 返回金10的日历和新闻
    (r'/get_win_info', get_win_info),  # 查询虚拟客户跟单收益
    (r'/tips_page', tips_page),  # 每日策略操作页面
    (r'/tips/(\w+)', tips),  # 对每日策略的操作请求
    (r'/get_black_ip', get_black_ip),  # 获取被封禁的ip地址列表
    (r'/show_method_or_not', show_method_or_not),  # 每日策略的5条策略信息返回 或者出错信息
    (r"/jin10_index", jin10_index)  # 接收金10前段发送来的数据传给后端

], template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    cookie_secret="bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=", debug=True)  # app的配置

if __name__ == "__main__":  # 标准写法。
    # 启动日志,调试时注销日志，以方便调试
    logger = ext_tools.get_logger_everyday(__name__)
    logger.info("begin....")

    # 启动服务
    http_server = tornado.httpserver.HTTPServer(app)  # 一个http_server的实例对象。
    http_server.listen(9015)  # 设置监听端口。
    tornado.ioloop.IOLoop.instance().start()  # 运行此服务器。
