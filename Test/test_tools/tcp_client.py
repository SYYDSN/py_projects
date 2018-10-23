# -*- coding: utf-8 -*-
import socket


class TCPClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

    def close(self):
        self.client.close()
        del self


if __name__ == "__main__":
    cli = TCPClient()
    cli.connect('127.0.0.1', 7000)
    pass
