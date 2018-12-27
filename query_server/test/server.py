# -*- coding: utf-8 -*-
from flask import Flask
from flask import request


"""嵌入式用来测试上传文件的服务器"""


port = 8000
app = Flask(__name__)


@app.route("/")
def welcome():
    """首页"""
    return "hello world"


@app.route("/upload", methods=['post', 'get'])
def upload_func():
    """
    上传文件
    request有5个地方存放数据:
    1. request.args       url提交的参数  键值对形式的数据.值是字符串/数值
    2. request.form      表单提交的参数  键值对形式的数据,值是字符串/数值
    3. request.data     xml的参数  字节格式
    4. request.json     json提交的参数  键值对形式的数据.值是字符串/数值
    15. request.files      上传的文件和图片  键值对形式的数据,值是二进制数据
    """
    args = request.args               # url参数
    args = {k: v for k, v in args.items()}
    form = request.form               # 表单参数
    form = {k: v for k, v in form.items()}
    json_data = request.json          # json参数,可能是None
    files = request.files             # 上传的文件
    files = {k: v.filename for k, v in files.items()}
    xml = request.data                # xml数据
    print("本次请求接受到的数据如下:")
    print("url参数: {}".format(args))
    print("表单参数: {}".format(form))
    print("son参数: {}".format(json_data))
    print("文件: {}".format(files))
    print("xml: {}".format(xml))
    print("-------------------")
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)

"""
使用说明:
python版本: python 3.6 理论上 3.4以上都行
你还需要安装flask ,安装方法  pip install flask
运行方法
1. 进入到项目的目录
python server.py
或者
python3 server.py
即可
如果你的linux是python版本是2.7系列的.请不要贸然升级.
你需要安装一个虚拟环境来运行本服务器----virtualenv, 
然后在这个下面安装一个3x系列的python,
在这个虚拟环境下执行.具体的操作请百度.
"""