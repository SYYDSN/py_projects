# uwsgi部署flask的方式和其他的部署方式不同.

## 安装 

sudo apt install uwsgi

python的插件也是要安装的

sudo apt install uwsgi-plugin-python3

最好是 sudo apt-get install uwsgi-plugins-all 一步到位

你可以用 --version查看版本我当前的版本是2.015

uwsgi有独立部署和作为web容器的后端部署两种方式.这两种方式最主要的差别是前者可以直接访问,而后者需要部署在类似nginx这样的服务器的后面.
这2种部署方式最主要的差别在于参数

1. 独立部署 使用 --http-socket host:port 方式绑定主机和端口
2. 后端部署 使用 --socket  host:port 方式绑定主机和端口

* 当你使用 --http参数把uwsgi部署在web服务器后面时, 会导致uwsgi不停的反复重新加载对站,直至服务器宕机.
* 当你使用 --http-socket或者--socket参数独立部署uwsgi的时候,你在访问服务器的时uwsgi会报错
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

* **--py-autoreload**: 1或者0, 自动重载,开发时使用这个参数
* **----http-socket或者--socket**: 绑定主机和端口,比如127.0.0.1:7001
* **--wsgi-file**: 配置文件,对于flask来说,就是入口的那个py文件
* **--callable**: 就是入口文件中run的那个app
* **--process**: 启动几个进程? 官方建议为计算机核心数目*2
* **--threads**: 每个进程开几个线程?
* **--stats**: 运行状态转发到那个地址和端口? 一般配合--stats-http命令使用.可以使用 nc ip port  的命令查看,注意,这个是snmp协议的(不能在网页上直接查看).
* **--stats-http**: 配合--stats参数,把信息以http的方式输出到--stats参数指定的端口(你可以在网页上直接查看这个地址)
* **--buffer-size**: 缓冲区尺寸,最大65535,uwsgi的默认缓冲区很小.如果您在日志中开始收到“invalid request block size”，则可能意味着您需要更大的缓冲区。
* **--post-buffering**  post文件在磁盘上的缓冲区大小,单位字节.超过此限制的文件会被缓存在磁盘上,这个选项是防止上传大文件耗尽内存的.
* **--post-buffering-bufsize**: 为post的缓存设置内部的缓冲区大小。（这个分配的内存是用来读取socket流的字节块）.单位字节,一般用不到这个选项.
* **--limit-post**  限制post请求体的大小,比如最大65535就是最大64m.
* **--procname-prefix**  为进程名增加指定的前缀,这个建议配置,方便你crash的时候kill僵尸进程,注意,前缀和名字是连起来的,你需要自己增加一个空格什么的.
* **--procname-prefix-spaced**  同上, 为进程名增加指定的前缀,前缀和名字之间有个空格的.
* **--procname-append**  为进程名增加指定的后缀,前缀和名字之间是连起来的.
* **--procname-master**  指定主进程的名字.
* **--emperor**  皇帝模式,可以使用各种配置来源包括数据库的表进行热部署.这个在大型应用的时候特别有用.不过配置也很复杂,值得花时间研究.[文档在此](https://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/Emperor.html)
* **--ini**: 设置ini文件的配置路径
* **--yaml**: 设置yaml文件的配置路径
* **--json**: 设置json文件的配置路径
* **--limit-as**: 设置每个进程的虚拟内存使用上限,单位是M,超过会报错.
* **--reload-on-as**: 设置每个进程的虚拟内存使用上限,单位是M,超过会重启进程,重启时,当前进程不受影响.用来防止内存泄露很有效,配合--reload-on-rss使用.
* **--reload-on-rss**: 设置每个进程的物理内存使用上限,单位是M,超过会重启进程,重启时,当前进程不受影响.用来防止内存泄露很有效,配合--reload-on-as使用.
* **--evil-reload-on-as**: 设置主进程的虚拟内存使用上限,单位是M,超过会重启进程,用来防止内存泄露很有效,配合--evil-reload-on-rss使用.
* **--evil-reload-on-rss**: 设置主进程的物理内存使用上限,单位是M,超过会重启进程,用来防止内存泄露很有效,配合--evil-reload-on-as使用.
* **--touch-reload**: 配置文件改变时,自动重启. 值是配置文件的路径
* **--no-default-app**: 开启此选项时,如果你app配置错误,则会抛出一个错误.
* **--callable**: 设置默认的callable的名字,值是入口程序中的app的名字.一般在部署flask时使用.
* **--cluster**: 集群配置选项. 不过中文版文档中说这个没实现
* **--asyncio**: 异步配置选项. 值int,需要配合--greenlet参数.--asyncio 10,启用10个uWSGI异步核，让你能够用一个单一的进程就可以管理多达10个并发请求。要求py3.4+.相关文档看[这里](https://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/asyncio.html)
* **--greenlet**: 启用greenlet作为挂起引擎,wsgi目前只支持greenlet,这是在使用异步模式的一个必须选项.比如配合--asyncio,这个参数无需设置值
* **--logto**: 将日志打印到指定的文件,值是一个路径.
* **--logdate**: 在日志的每一行都打印时间信息,参数也可以写成值是一个路径.值是一个strftime()格式的参数,也可以写成--log-date
* **--static-map**: 静态文件映射,如果是后端部署,一般都使用nginx做这个映射了,配置的例子 --static-map /images=/var/www/img
* **--static-index**: 静态文件的索引,比如 --static-index index.html --static-index index.htm 这样可以配置多个文件名
* **--tornado**: 使用tornado引擎.值是一个int, 需要配合--greenlet参数.--tornado 100 表示启用10个uWSGI异步核.当然,这需要你的程序也是地狱般的回调式写法.文档在[这里](https://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/Tornado.html)
* **--gevent**: 同上使用gevent引擎,不需要配合--greenlet参数
* **--virtualenv**: 虚拟环境配置,值是一个路径


使用配置文件可以得到更好的效果具体的配置相对复杂.官方文档在[这里](https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html)


uwsgi的英文官方文档[https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html)
uwsgi的中文官方文档[https://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/](https://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/)