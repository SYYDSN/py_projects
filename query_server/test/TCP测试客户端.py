# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
from tcp_tools.tcp_client import TCPClient


cli = TCPClient()
cli.connect("47.99.105.196", 32000)


def check_code():
    """检查条码信息"""
    cli.send_message("replace_code, 23132102805841430218730720125819577, 1011486229375867227118080")
    cli.listen(delay=2, debug=False)



if __name__ == "__main__":
    check_code()
    pass