# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)


users = []


class Server1:

    def add_user(self, user_name: str):
        if user_name in users:
            return "{} exists!".format(user_name)
        else:
            users.append(user_name)
            return "ok"


class Server2:
    def find_user(self, user_name):
        if user_name in users:
            return user_name
        else:
            return "not found!"

    def all_user(self):
        return ",".join(users) if len(users) > 0 else ""


if __name__ == "__main__":
    pass