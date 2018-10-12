# -*- coding: utf-8 -*-
from orm_module import *


class A:
    def __init__(self):
        self.name = "jack"


    def __call__(self, *args, **kwargs):
        print()


if __name__ == "__main__":
    conn = get_conn("test", db_client=cli, w="majority", j=True)
    # conn = get_conn("test", w="majority", j=True)
    print(conn)
    pass