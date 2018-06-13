# -*- coding:utf-8 -*-
import logging
import datetime
import os
import hashlib
import logging.handlers

"""日志模块"""


"""
sys._getframe().f_code.co_name 当前运行函数的名称
sys._getframe().f_locals 是当前运行函数的本地变量，也包含了很多__开头的内部变量。
一般直接使用str(sys._getframe().f_locals)就能略过这些__开头的变量转换为字符串
建议的记录方式：
logger.error("function={},args={}".format(sys._getframe().f_code.co_name, str(sys._getframe().f_locals)))
logger.info("function={},args={}".format(sys._getframe().f_code.co_name, str(sys._getframe().f_locals)))

如果是在except分支中，可以直接使用
logger.exception("error:")
记录
"""


dir_path = os.path.split(__file__)[0]


def get_logger(name="server"):
    """按天切分的日志记录工具"""
    path_str = os.path.join(dir_path, "logs")
    if not os.path.exists(path_str):
        os.makedirs(path_str)
    else:
        pass
    file_path_info = os.path.join(path_str, "{}_{}_info.log".format(name, datetime.datetime.now().strftime("%Y%m%d")))
    file_path_error = os.path.join(path_str, "{}_{}_error.log".format(name, datetime.datetime.now().strftime("%Y%m%d")))
    file_path_debug = os.path.join(path_str, "{}_{}_debug.log".format(name, datetime.datetime.now().strftime("%Y%m%d")))

    # when表示时间的间隔，interval表示是否循环，backupCount表示备份文件的数目
    # 记录一般性日志
    fh = logging.handlers.TimedRotatingFileHandler(
        filename=file_path_info, when="D", interval=1, backupCount=10, encoding="utf-8")
    fh.setLevel(logging.INFO)
    # 记录错误日志
    fh2 = logging.handlers.TimedRotatingFileHandler(
        filename=file_path_error, when="D", interval=1, backupCount=10, encoding="utf-8")
    fh2.setLevel(logging.ERROR)
    # 记录debug信息
    fh3 = logging.handlers.TimedRotatingFileHandler(
        filename=file_path_debug, when="D", interval=1, backupCount=10, encoding="utf-8")
    fh3.setLevel(logging.DEBUG)

    # 输出错误日志到控制台
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    fh2.setFormatter(formatter)
    fh3.setFormatter(formatter)
    console.setFormatter(formatter)
    # 日志部分
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        handlers=[fh, fh2, fh3, console]
                        )
    my_logger = logging.getLogger(name)
    return my_logger


def recode(mes: str)->None:
    """
    记录工具，替代logger，用于记录那些非异常的自定义记录
    仅在调试时使用，平时开启会有大量的数据浪费。
    :param mes: 需要被记录的内容
    :return:
    """
    if 0:
        pass
    else:
        recode_path_str = os.path.join(dir_path, "logs", "recode")
        recode_file_path = "{}.log".format(datetime.datetime.now().strftime("%Y-%m-%d-%H"))
        if not os.path.exists(recode_path_str):
            os.makedirs(recode_path_str)
        recode_file_path = os.path.join(recode_path_str, recode_file_path)
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        recoder = open(recode_file_path, "a", encoding="utf-8")
        recoder.write("pid: {} ,{} Recode: {} \n".format(os.getpid(), t, mes))
        recoder.flush()
        recoder.close()


if __name__ == "__main__":
    pass
