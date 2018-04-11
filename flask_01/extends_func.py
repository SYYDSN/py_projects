# -*-coding:utf-8-*-
from uuid import uuid4


def add_uuid(part_str: str) -> str:
    """
    把一段字符串后面加上一段uuid,这么无聊的程序当然是用来演示啦.
    :param part_str: 字符串
    :return:part_str + uuid
    """
    if part_str is None:
        ms = "part_str参数不能为空"
        raise TypeError(ms)
    else:
        if not isinstance(part_str, str):
            part_str = str(part_str)
        else:
            pass
        return part_str + uuid4().hex


if __name__ == "__main__":
    add_uuid("a")
    pass

