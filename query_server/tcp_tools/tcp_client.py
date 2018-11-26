# -*- coding: utf-8 -*-
import socket
from uuid import uuid4
from threading import Thread
import time


class TCPClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stop = True

    def connect(self, host: str, port: int) -> socket.socket:
        """
        连接
        :param host:
        :param port:
        :return:
        """
        client = self.client
        client.connect((host, port))
        return client

    def send_message(self, mes: str) -> None:
        """

        :param mes:
        :return:
        """
        s = mes.encode(encoding='utf-8')
        client = self.client
        client.sendall(s)

    def listen(self, delay: float = 2):
        """

        :return:
        """
        client = self.client
        self.stop = False
        while not self.stop:
            data = client.recv(1024).decode(encoding="utf-8")
            print(data)
            time.sleep(delay)
            s = "CheckTraceCodeCanUse, {}".format(uuid4().hex)
            client.sendall(s.encode(encoding="utf-8"))

    def close(self):
        self.client.close()
        del self

    @classmethod
    def batch_listen(cls, num: int = 3, delay: float = 2) -> None:
        """
        批量监听
        :param num:
        :param delay:
        :return:
        """
        for i in range(num):
            cli = TCPClient()
            cli.connect('127.0.0.1', 7012)
            lis = cli.listen
            t = Thread(target=lis, args=(delay,))
            print(i)
            t.start()


if __name__ == "__main__":
    cli = TCPClient()
    cli.connect('127.0.0.1', 32000)
    cli.listen()
    # import os
    # os.fork()
    # os.fork()
    # os.fork()
    # os.fork()
    # TCPClient.batch_listen(1, 0.001)
    pass
