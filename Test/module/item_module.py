# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
print(__root_path)
import types
import asyncio
import time


async def func_a(n):
    print("a")
    return n


async def func_b(n):
    print("b")
    yield n


async def func_c(n):
    print("c")
    yield n




async def func_1():
    resp = await func_a(12)
    print(resp)


if __name__ == "__main__":

    r = func_1()
    try:
        r.send(None)
    except Exception as e:
        print(e.value)
    pass