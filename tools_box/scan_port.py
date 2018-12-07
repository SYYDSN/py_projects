# -*- coding: utf-8 -*-
import telnetlib


"""扫描服务器端口号"""


def scan_server(host: str, ports: (list, tuple)) -> list:
    """
    探测服务器的端口号是否开放
    :param host: 主机ip地址
    :param ports: 端口的数组或者元组
    :return:  端口状态的数组
    """
    result = list()
    for port in ports:
        current_status = False
        try:
            t = telnetlib.Telnet(host=host, port=port, timeout=15)
            current_status = True
            t.close()
        except Exception as e:
            mes = "连接失败,错误原因:{}".format(e)
            print(e)
        finally:
            mes = "服务器:{} 端口:{} 探测{}!".format(host, port, "成功" if current_status else "失败")
            result.append(mes)
    return result

    
if __name__ == "__main__":
    host = "git.safego.org"
    ports = list(range(7171, 7176))
    ports.extend(list(range(8181, 8186)))
    res = scan_server(host=host, ports=ports)
    for mes in res:
        print(mes)