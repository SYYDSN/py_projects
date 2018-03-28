#  -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
from flask import render_template_string
from flask import send_file
from flask import request
from werkzeug.contrib.cache import RedisCache
from flask_session import Session
from log_module import get_logger
import sms_module
import json
from tools_module import *
import os


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8000


def get_signature(nonce, payload, secret, timestamp):
    """生成简道云的签名验证"""
    content = ':'.join([nonce, payload, secret, timestamp]).encode('utf-8')
    m = hashlib.sha1()
    m.update(content)
    return m.hexdigest()


def validate_signature(req, secret, signature) -> bool:
    """验证简道云发来的消息的签名是否正确？"""
    payload = req.data.decode('utf-8')
    nonce = req.args['nonce']
    timestamp = req.args['timestamp']
    if signature != get_signature(nonce, payload, secret, timestamp):
        return False
    else:
        return True


@app.route('/', methods=['post', 'get'])
def hello_world():
    return 'Hello World!'


@app.route("/listen_<key>", methods=['post'])
def listen_func(key):
    """监听简道云发送过来的消息"""
    mes = {"message":"success"}
    headers = request.headers
    event_id = headers.get("X-JDY-DeliverId")
    signature = headers.get("X-JDY-Signature")
    data = request.json
    print(event_id)
    print(signature)
    print(data)
    if key == "test":
        """测试消息"""
        secret_str = "ckFqpdtIr45aXwPkSITuW2iY"  # 不同的消息定义的secret不同，用来验证消息的合法性
        print(validate_signature(request, secret_str, signature))
    else:
        mes['message'] = '错误的path'
    return json.dumps(mes)



@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    headers = "headers: {}".format(request.headers)
    args = "args: {}".format(request.args)
    form = "form: {}".format(request.form)
    json = "json: {}".format(request.json)
    logger.info(headers)
    logger.info(args)
    logger.info(form)
    logger.info(json)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
