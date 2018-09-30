# uwsgi部署flask的方式和其他的部署方式不同.

## 安装 

pip3/pip install uwsgi


uwsgi有独立部署和作为web容器的后端部署两种方式.这两种方式最主要的差别是前者可以直接访问,而后者需要部署在类似nginx这样的服务器的后面.
这2种部署方式最主要的差别在于参数

1. 独立部署 使用 --http host:port 方式绑定主机和端口
2. 后端部署 使用 --http-socket  host:port 方式绑定主机和端口

* 当你使用 --http参数把uwsgi部署在web服务器后面时, 会导致uwsgi不停的反复重新加载对站,直至服务器宕机.
* 当你使用  --http-socket或者--socket参数独立部署uwsgi的时候,你在访问服务器的时uwsgi会报错
```shell
invalid request block size: 21573 (max 4096)...skip
```

一般的部署flask的方式如下:

下面直接给一个supervisor的配置文件(假设你的项目目录是 /home/web/aaa, 入口文件是main.py)
先是独立部署

```
[program: uwsgi-7001-alone]

command = uwsgi --http 127.0.0.1:7001 --wsgi-file main.py --callable app --process 4 --threads 2 --buffer-size 8192;

directory = /home/web/aaa       ; 运行的脚本的目录

autostart = true                                      ;  随supervisor自动启动

autorestart = unexpected                              ; 出错重启

startsecs = 3                         ; 启动后3秒不报错就认为程序启动成功

startretries = 3                      ; 程序失败的重试次数web


```

后端部署,这种方式前面必须放一个支持wsgi的web服务器
```
[program: uwsgi-7001-back]

command = uwsgi --http-socket 127.0.0.1:7001 --wsgi-file main.py --callable app --process 4 --threads 2 --buffer-size 8192;

directory = /home/web/aaa       ; 运行的脚本的目录

autostart = true                                      ;  随supervisor自动启动

autorestart = unexpected                              ; 出错重启

startsecs = 3                         ; 启动后3秒不报错就认为程序启动成功

startretries = 3                      ; 程序失败的重试次数web


```

参数说明

* **--http或者--http-socket**: 绑定主机和端口,比如127.0.0.1:7001
* **--wsgi-file**: 配置文件,对于flask来说,就是入口的那个py文件
* **--callable**: 就是入口文件中run的那个app
* **--process**: 启动几个进程? 官方建议为计算机核心数目*2
* **--threads**: 每个进程开几个线程?
* **--stats**: 运行状态转发到那个地址和端口? 一般配合--stats-http命令使用.可以使用 nc ip port  的命令查看,注意,这个是snmp协议的(不能在网页上直接查看).
* **--stats-http**: 配合--stats参数,把信息以http的方式输出到--stats参数指定的端口(你可以在网页上直接查看这个地址)
* **--buffer-size**: 缓冲区尺寸,最大65535,uwsgi的默认缓冲区很小.如果您在日志中开始收到“invalid request block size”，则可能意味着您需要更大的缓冲区。
* **--post-buffering**  post文件在磁盘上的缓冲区大小,一般这个文件都缓存在内存中,所以这个选项并不常用.


使用配置文件可以得到更好的效果具体的配置相对复杂.官方文档在[这里](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html)


uwsgi的官方文档[https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html)