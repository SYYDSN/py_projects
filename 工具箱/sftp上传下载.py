# -*- coding:utf-8 -*-


"""Sftp工具，上传或者下载文件"""


HOST = "safego.org"
PORT = 22
USER = "lijie.xu"
PASSWORD = "-=[]_+{}"


def get_sftp(host: str = "safego.org", port: int = 22, user_name: str = "lijie.xu", password="-=[]_+{}"):
    """
    创建一个sftp连接
    :param host: 
    :param port:
    :param user_name:
    :param password:
    :return:
    """
