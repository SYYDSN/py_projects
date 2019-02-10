# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import zerorpc
from global_logging.logging_module import GlobalJournal

"""zero-rpc的服务器"""


class Cooler(
    GlobalJournal,

):
    """
    服务器,只需要继承具体的服务类即可.注意这些服务类中不可有同名的实例方法
    """


if __name__ == "__main__":
    port = 4242
    s = zerorpc.Server(Cooler())
    s.bind("tcp://0.0.0.0:{}".format(port))
    print("zero-rpc running on {} ...".format(port))
    s.run()
