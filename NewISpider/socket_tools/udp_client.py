# -*- coding: utf-8 -*-
import socket
from uuid import uuid4
from threading import Thread
import json
import time


class UDPClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stop = True

    def send_message(self, mes: str, host: str, port: int) -> None:
        """

        :param mes:
        :param host:
        :param port:
        :return:
        """
        s = mes.encode(encoding='utf-8')
        client = self.client
        client.sendto(s, (host, port))

    def listen(self, delay: float = 2, debug: bool = False):
        """

        :return:
        """
        client = self.client
        self.stop = False
        count = 1
        while not self.stop:
            data = client.recv(1024).decode(encoding="utf-8")
            print(data)
            try:
                d = json.loads(data)
                for k, v in d.items():
                    print(k, v)
            except Exception as e:
                print(e)
                pass
            if not debug and count >= 2:
                count += 1
                self.stop = True
            else:
                count += 1
            time.sleep(delay)
            s = "uuid, {}".format(uuid4().hex)
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
            cli = UDPClient()
            cli.bind('127.0.0.1', 7012)
            lis = cli.listen
            t = Thread(target=lis, args=(delay,))
            print(i)
            t.start()


if __name__ == "__main__":
    cli = UDPClient()
    cli.send_message(mes="hello", host="127.0.0.1", port=32001)
    # import os
    # os.fork()
    # os.fork()
    # os.fork()
    # os.fork()
    # UDPClient.batch_listen(1, 0.001)
    pass
