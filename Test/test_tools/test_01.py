# -*- coding: utf-8 -*-
from orm_module import *


if __name__ == "__main__":
    t = Field("name", str, "hello")
    conn = get_conn("test", w="majority", j=True)
    print(conn)
    pass