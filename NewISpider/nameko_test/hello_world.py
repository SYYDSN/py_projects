# -*- coding: utf-8 -*-
from nameko.rpc import rpc
import datetime


class GreetingService:
    name = "greeting_server"

    @rpc
    def hello(self, name: str) -> str:
        now = datetime.datetime.now()
        return "Hello, {}! {}".format(name, now)


class GreetingServiceB:
    name = "greeting_server2"

    @rpc
    def hello(self, name: str) -> str:
        now = datetime.datetime.now()
        return "Hello world, {}! {}".format(name, now)


if __name__ == "__main__":
    """
    运行方法:
    命令行: nameko run --config default.yaml  hello_world
    """
    pass