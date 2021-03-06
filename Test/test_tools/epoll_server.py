# -*- coding: utf-8 -*-
import socket
from multiprocessing import cpu_count
import select
import os

"""
利用非阻塞和epoll来实现一个服务器
"""


class WebServer:
    """定义一个web服务器"""

    def __init__(self):
        # 1.创建TCP 服务器
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 复用端口
        self.tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 2.绑定端口
        self.host = "0.0.0.0"
        self.port = 7000
        self.tcp_server.bind((self.host, self.port))
        # 3.设为被动套接字
        self.tcp_server.listen(128)

    def run(self):
        print("server run on {}{}".format(self.host, self.port))
        """运行一个服务器"""
        # 1.把服务器设置为非阻塞模式
        self.tcp_server.setblocking(False)
        # 2.创建一个epoll对象并为服务器注册一个可接受连接的事件
        epoll = select.epoll()
        epoll.register(self.tcp_server.fileno(), select.EPOLLIN)
        client_dict = dict()  # 让fd与client建立关联
        # 3.服务器接受客户端的请求
        while True:
            # 4.监听epoll中哪个fd发生了什么事件
            epoll_list = epoll.poll()
            for fd, event in epoll_list:
                if fd == self.tcp_server.fileno():
                    # 有客户端来连接被动套接字服务器
                    client, addr = self.tcp_server.accept()
                    print("客户端已连接--{}".format(addr))
                    # 把客户端注册到epoll中
                    epoll.register(client.fileno(), select.EPOLLIN)
                    # 把客户端和客户端对应的fd添加到client字典中去
                    client_dict[client.fileno()] = client
                else:
                    # 有客户端发送数据过来,但是该如何去获得这个客户端呢？
                    data = ''
                    try:
                        data = client_dict[fd].recv(1024).decode('utf-8')
                    except ConnectionResetError as e:
                        print(e)
                    except ConnectionAbortedError as e:
                        print(e)
                    except ConnectionRefusedError as e:
                        print(e)
                    finally:
                        if data and data != "":
                            # 说明客户端发送数据过来了
                            print(data)
                            client = client_dict[fd]
                            c_ip, c_port = client.getpeername()
                            client.send('{}:{}我已经收到你的数据了！\n'.format(c_ip, c_port).encode('utf-8'))
                        else:
                            # 说明客户端已经关闭了
                            client_dict[fd].close()

                            client_dict.popitem()
                            # 需要把该客户端注册的事件取消掉
                            epoll.unregister(fd)

            # 遍历client字典中每个客户端对应的fd
            # for fd, sock in client_dict.items():
            #     print('fd:{}--->addr:{}'.format(fd, sock))
            #     print('-' * 50)
            #     cli = sock
            #     cli.sendall("hello".encode(encoding="utf-8"))
        # 关闭服务器
        self.tcp_server.close()


def main():
    # 1.初始化一个TCP服务器
    server = WebServer()
    # 2.运行一个服务器
    print(cpu_count())
    [os.fork() for x in range(cpu_count() - 1)]
    server.run()


if __name__ == '__main__':
    main()
    pass