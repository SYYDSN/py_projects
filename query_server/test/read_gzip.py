# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import gzip
import zipfile


"""测试读取gzip文件"""


def read():
    f_path = os.path.join(__root_path, "task_sync", "5c248602b8a0d3100471666d.zip")
    # file = zipfile.ZipFile(file=f_path, mode="r", compression=zipfile.ZIP_DEFLATED)
    file = gzip.open(filename=f_path)

    content = file.read()
    file.close()
    print(content)



if __name__== "__main__":
    read()
    pass