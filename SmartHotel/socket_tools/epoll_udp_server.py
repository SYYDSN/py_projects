# -*- coding: utf-8 -*-
import socket
import select
import json



"""
利用非阻塞和epoll来实现一个服务器. udp工作模式
本模块是生产环境是用的.
"""


class WebServer:
    """
    定义一个web服务器
    """

    def __init__(self):
        # 1.创建UDP 服务器
        self.udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 复用端口
        self.udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 2.绑定端口
        self.host = "0.0.0.0"
        self.port = 32001
        self.udp_server.bind((self.host, self.port))

    def run(self, debug: bool = False):
        print("udp server run on {}:{}".format(self.host, self.port))
        """运行一个服务器"""
        # 1.把服务器设置为非阻塞模式
        self.udp_server.setblocking(False)
        # 2.创建一个epoll对象并为服务器注册一个可接受连接的事件
        epoll = select.epoll()
        epoll.register(self.udp_server.fileno(), select.EPOLLIN)
        client_dict = dict()  # 让fd与client建立关联
        # 3.服务器接受客户端的请求
        while True:
            # 4.监听epoll中哪个fd发生了什么事件
            epoll_list = epoll.poll()
            for fd, event in epoll_list:
                if fd == self.udp_server.fileno():
                    # 有客户端来连接被动套接字服务器
                    peer_msg, peer_tuple = self.udp_server.recvfrom(1024)
                    peer_address = peer_tuple[0]
                    peer_port = peer_tuple[1]

                    print("客户端已连接--{}".format(addr))
                    # 把客户端注册到epoll中
                    epoll.register(client.fileno(), select.EPOLLIN)
                    # 把客户端和客户端对应的fd添加到client字典中去
                    client_dict[client.fileno()] = client
                    """发送欢迎数据"""
                    client.send("{} connected, welcome!".format(addr).encode("utf-8"))
                    """记录日志"""
                    c_ip, c_port = client.getsockname()
                    ms = "用户已连接: ip={},port={}".format(c_ip, c_port)
                    kw = {
                        "file": __file__,
                        "func": self.__class__.__name__,
                        "log_type": "连接",
                        "content": ms,
                        "ip": c_ip
                    }
                    for k, v in kw.items():
                        print(k, v)
                else:
                    # 有客户端发送数据过来,但是该如何去获得这个客户端呢？
                    peer_msg, peer_tuple = self.udp_server.recvfrom(1024)
                    peer_address = peer_tuple[0]
                    peer_port = peer_tuple[1]

                    client = client_dict[fd]
                    c_ip, c_port = ('', '')
                    data = ''
                    try:
                        c_ip, c_port = client.getpeername()
                        data = client_dict[fd].recv(1024).decode('utf-8')
                    except ConnectionResetError as e:
                        print(e)
                    except ConnectionAbortedError as e:
                        print(e)
                    except ConnectionRefusedError as e:
                        print(e)
                    except Exception as e:
                        print(e)
                    finally:
                        if data and data != "":
                            """处理接收到的数据"""
                            # 说明客户端发送数据过来了
                            if debug:
                                kw = {
                                    "file": __file__,
                                    "func": self.__class__.__name__,
                                    "log_type": "接收数据",
                                    "content": data,
                                    "ip": c_ip
                                }
                                for k, v in kw.items():
                                    print(k, v)
                            print(data)
                            error = None
                            resp = json.dumps({"message": "success"})
                            try:
                                client.send(resp.encode(encoding="utf-8"))
                            except ConnectionResetError as e:
                                print(e)
                                error = str(e)
                            finally:
                                if debug and error is None:
                                    """调试模式"""
                                    kw = {
                                        "file": __file__,
                                        "func": self.__class__.__name__,
                                        "log_type": "返回数据",
                                        "content": resp,
                                        "ip": c_ip
                                    }
                                    for k, v in kw.items():
                                        print(k, v)
                                elif error is not None:
                                    ms = "向客户端发送消息时出错,消息:{}, 错误原因:{}".format(resp, error)
                                    kw = {
                                        "file": __file__,
                                        "func": self.__class__.__name__,
                                        "log_type": "返回数据",
                                        "content": ms,
                                        "ip": c_ip
                                    }
                                    for k, v in kw.items():
                                        print(k, v)
                        else:
                            # 说明客户端已经关闭了
                            # print('{}:{}已断开！\n'.format(c_ip, c_port))
                            c_ip, c_port = client.getsockname()
                            print('{}:{}已断开！\n'.format(c_ip, c_port))
                            client_dict[fd].close()
                            client_dict.pop(fd)
                            """需要把该客户端注册的事件取消掉"""
                            epoll.unregister(fd)
                            """记录日志"""
                            ms = "用户已断开: ip={},port={}".format(c_ip, c_port)
                            kw = {
                                "file": __file__,
                                "func": self.__class__.__name__,
                                "log_type": "断开",
                                "content": ms,
                                "ip": c_ip
                            }
                            for k, v in kw.items():
                                print(k, v)

            # 遍历client字典中每个客户端对应的fd
            # for fd, sock in client_dict.items():
            #     print('fd:{}--->addr:{}'.format(fd, sock))
            #     print('-' * 50)
            #     cli = sock
            #     cli.sendall("hello".encode(encoding="utf-8"))
        # 关闭服务器
        self.udp_server.close()


def main(debug: bool = False):
    # 1.初始化一个TCP服务器
    server = WebServer()
    # 2.运行一个服务器
    """多进程有问题"""
    # cpu_num = cpu_count()
    # print(cpu_num)
    # for i in range(int(cpu_num/2)):
    #     os.fork()
    # server.run()
    server.run(debug=debug)


if __name__ == '__main__':
    main()
    pass