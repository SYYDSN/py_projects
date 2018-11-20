# -*- coding: utf-8 -*-
import socket
import select
from module.code_module import CodeInfo


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
                    """延时发送数据"""
                    client.send("hello world".encode("utf-8"))
                else:
                    # 有客户端发送数据过来,但是该如何去获得这个客户端呢？
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
                            # 说明客户端发送数据过来了
                            print(data)
                            c_str = "{}:{}".format(c_ip, c_port)
                            client.send('{}我已经收到你的数据了！\n'.format(c_str).encode('utf-8'))
                            if data.startswith("CheckTraceCodeCanUse"):
                                """
                                条码合格判定
                                请求检测数据是否合格: CheckTraceCodeCanUse, 10401911001201805011536541033317
                                系统检测条码合格返回数据格式: 10401911001201805011536541033317,1    
                                系统检测条码重复返回数据格式: 10401911001201805011536541033317,2 
                                系统检测条码非当前生产数据格式: 10401911001201805011536541033317,3 
                                系统检测条码格式错误: 10401911001201805011536541033317,4 
                                条码加请求检测结果后的返回值，返回值为以上定义的 1-4数据。
                                """
                                code = data.split(",")[-1].strip("")
                                r = CodeInfo.query_code(code=code)
                                print(r)
                                pass
                            elif data.startswith("UploadTraceCodeToDb"):
                                """
                                UploadTraceCodeToDb
                                请求检测数据是否合格: UploadTraceCodeToDb, 10401911001201805011536541033317, 
                                10401911001201805011536541033318, 10401911001201805011536541033319, 
                                10401911001201805011536541033311, 10401911001201805011536541033312,
                                ……
                                系统检测条码合格返回数据格式: UploadTraceCodeToDb ,10401911001201805011536541033317,1
                                系统数据返回格式解释: 用请求的接口名，加第一个请求的条码内容，加结果。
                                1. 代表本次请求接口处理成功，0则代表本次接口处理数据失败。
                                """
                                pass
                            else:
                                client.send('{}你发送的数据我未能理解: data={}！\n'.format(c_str, data).encode('utf-8'))
                        else:
                            # 说明客户端已经关闭了
                            print('{}:{}已断开！\n'.format(c_ip, c_port))
                            client_dict[fd].close()
                            client_dict.pop(fd)
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
    """多进程有问题"""
    # cpu_num = cpu_count()
    # print(cpu_num)
    # for i in range(int(cpu_num/2)):
    #     os.fork()
    server.run()


if __name__ == '__main__':
    main()
    pass