# -*- coding: utf-8 -*-
import hashlib


"""用户登录模块"""


class User:
    @staticmethod
    def login(user_name, user_password) -> bool:
        if user_name == "teacher_admin" and user_password == hashlib.md5("2018@0429".encode()).hexdigest():
            return True
        else:
            return False