# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import socket
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

    def listen(self):
        """

        :return:
        """
        client = self.client
        self.stop = False
        while not self.stop:
            data = client.recv(1024).decode(encoding="utf-8")
            print(data)
            time.sleep(0.01)
            client.sendall("CheckTraceCodeCanUse, I coming!".encode(encoding="utf-8"))

    def close(self):
        self.client.close()
        del self


if __name__ == "__main__":
    cli = TCPClient()
    cli.connect('127.0.0.1', 7000)
    cli.listen()
    pass
