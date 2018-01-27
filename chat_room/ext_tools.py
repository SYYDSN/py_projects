# -*- encoding: utf-8 -*-
__author__ = 'Administrator'

import datetime, random, json, re
import logging
import os.path, os
import logging.handlers
import datetime
import logging
import db_module


# 提供附加功能的模块

# 接受匿名用户发来的信息，并作出回应。服务于匿名用户跟踪系统，此方法用于获取匿名信息和对匿名信息进行登记
# 接受匿名用户发来的信息，并作出回应。服务于匿名用户跟踪系统，此方法用于获取匿名信息和对匿名信息进行登记
def guest_message(id, event_type, referer, page_url, ip):
    ses = db_module.sql_session()
    result_select = ""
    print("page_url is " + page_url + " referer is " + referer)
    # 取完参数，运行程序
    print("id is ", str(id), " referer is ", referer, " page_url is ", page_url, " event_type is ", event_type)
    the_id = id
    if int(the_id) == 0:
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")  # g格式化输出到毫秒
        random_number = random.randint(0, 999)  # 生成随机数，跟日期一起作为新id的唯一判断。
        the_id = int(now[2:-3] + str(random_number))
        print("the id is " + str(the_id))

    if event_type == "open_page":
        # 插入一条open_page类型的记录
        sql_action = "insert into guest_action_recode(Guest_id,Referer,Page_url,Event_type,Event_Date,Ip) values({0},'{1}','{2}','{3}',now(),'{4}')".format(
            the_id, referer, page_url, 'open_page', ip)  # 插入一条open_page的事件记录。
        print("sql_action:" + sql_action)
        ses.execute(sql_action)
        ses.commit()
        print("result_select is " + str(result_select))
        print("josn result_select is " + str(json.dumps(result_select)))
        ses.close()
        return json.dumps(the_id)  # 返回id
    else:
        sql_action = "insert into guest_action_recode(Guest_id,Referer,Page_url,Event_type,Event_Date) values({0},'{1}','{2}','{3}',now())".format(
            the_id, referer, page_url, event_type)  # 插入一条open_page的事件记录。
        print("event_type不等于open_page时的 sql_action:" + sql_action)
        ses.execute(sql_action)
        ses.commit()
        ses.close()
        return json.dumps('recode insert success')


# 聊天室用户发言的过滤器，用于屏蔽带手机号码或者敏感字的发言。
def check_message(message):
    # pattern="^1\d{9}\d$"  #匹配以1开头的11位纯数字  "^1\d{9}\d$"
    pattern = "1\d{10}"  # 发言中有以1开头的连续的11位数字
    if re.search(pattern, message):
        return True
    elif message.lower().find("qq") != -1:
        return True
    else:
        return False


# 特殊事件记录器,记录例如审核之类的关键操作
def logger(the_type, data={}):
    ses = db_module.sql_session()
    sql = "insert into Logger(event_type,event_context,event_href,event_ip,guest_id,user_agent,event_date) values('{0}','{1}','{2}','{3}',{4},'{5}',now())".format(
        data["event_type"], data["event_context"], data["event_href"], data["event_ip"], data["guest_id"],
        data["user_agent"])
    ses.execute(sql)
    ses.commit()
    ses.close()


# 日志记录工具
def get_logger(name):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    else:
        pass
    fh = logging.FileHandler("logs" + os.sep + name + ".log", "a", "utf-8")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    # 日志部分
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        # datefmt='%a, %d %b %Y %H:%M:%S',
                        # filename='myapp.log',
                        handlers=[fh]
                        )
    my_logger = logging.getLogger(name)
    return my_logger


# 日志记录工具，按天切分,error独立文件
def get_logger_everyday(name):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    else:
        pass
    # when表示时间的间隔，interval表示是否循环，backupCount表示备份文件的数目
    # 记录一般性日志
    fh = logging.handlers.TimedRotatingFileHandler(
        filename="logs" + os.sep + name + "_" + datetime.datetime.now().strftime("%Y%m%d") + ".log",
        when="D", interval=1, backupCount=10, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    # 记录错误日志
    fh2 = logging.handlers.TimedRotatingFileHandler(
        filename="logs" + os.sep + name + "_error_" + datetime.datetime.now().strftime("%Y%m%d") + ".log",
        when="D", interval=1, backupCount=10, encoding="utf-8")
    fh2.setLevel(logging.ERROR)

    # 输出错误日志到控制台
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    fh2.setFormatter(formatter)
    console.setFormatter(formatter)
    # 日志部分
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        handlers=[fh, fh2, console]
                        )
    my_logger = logging.getLogger(name)
    return my_logger
