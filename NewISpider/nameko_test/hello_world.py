# -*- coding: utf-8 -*-
from nameko.rpc import rpc
import datetime


class GreetingService:
    name = "greeting_server"

    @rpc
    def hello(self, name: str) -> str:
        now = datetime.datetime.now()
        return "Hello, {}! {}".format(name, now)


if __name__ == "__main__":
    pass