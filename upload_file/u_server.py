# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import send_file
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask_session import Session
from flask import redirect
import json
import datetime
import os


key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
SESSION_TYPE = "redis"
Session(app)
port = 7002
root_dir = os.path.dirname(os.path.realpath(__file__))
resource_dir = os.path.join(root_dir, 'resource')


@app.route("/favicon.ico")
def favicon_func():
    return send_file("static/image/favicon.ico")


@app.route("/")
def upload_demo():
    """上传页面"""
    id = request.args.get("id")
    if str(id) == "123":
        return render_template("upload_demo.html", page_title="批量上传")
    else:
        return abort(404)


@app.route("/file/<action>", methods=['post', 'get'])
def file_func(action):
    """
    此函数仅允许上传/查看图片.
    当前使用auth参数作为验证 auth = '647a5253c1de4812baf1c64406e91396'
    :param action: 动作, save/get(保存/获取)
    :return:
    """
    mes = {"message": "success"}
    if action == "save":
        """保存文件"""
        if os.path.exists(resource_dir):
            pass
        else:
            os.makedirs(resource_dir)

        for key_name, file_storage in request.files.items():
            if file_storage is not None:
                file_name = file_storage.filename
                file_storage.save(os.path.join(resource_dir, file_name))
                file_storage.close()
    elif action == "view":
        """获取文件/图片"""
        pass
    return json.dumps(mes)


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    pass


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
