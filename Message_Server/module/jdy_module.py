#  -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from log_module import get_logger
import mongo_db
from send_moudle import *
from pymongo import ReturnDocument
import requests
from module.image_module import Praise
from module.image_module import MaterialPushHistory
from send_moudle import send_signal
import datetime


ObjectId = mongo_db.ObjectId
app_key = 'gavQrjmjxekfyK4qeZAI0usSZmZq0oww'
headers = {'Authorization': 'Bearer {}'.format(app_key)}


"""简道云相关的模块"""


class RefreshInfo(mongo_db.BaseDoc):
    """
    记录刷新时间
    """
    _table_name = "refresh_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['table_name'] = str
    type_dict['time'] = datetime.datetime  # 刷新时间

    @classmethod
    def get_prev(cls, table_name: str) -> (datetime.datetime, None):
        """
        获取上一次的刷新信息
        :param table_name: 表名
        :return:
        """
        f = {"table_name": table_name}
        r = cls.find_one_plus(filter_dict=f, instance=False)
        if r is None:
            pass
        else:
            return r['time']

    @classmethod
    def update_time(cls,  table_name: str) -> None:
        """
        更新刷新时间
        :param table_name:
        :return:
        """
        f = {"table_name": table_name}
        u = {"$set": {"time": datetime.datetime.now()}}
        cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)


def listen_jdy(**kwargs) -> dict:
    """
    监听简道云通过.api推送过来的消息
    :param kwargs:
    :return:
    """
    req_type = kwargs.pop("req_type", None)
    mes = {"message": "success"}
    if req_type == 'deposit':
        """入金宣传表"""
        process_praise(**kwargs)
    elif req_type == "material":
        """上传图片素材"""
        MaterialPushHistory.push(**kwargs)
    else:
        ms = "错误的req_type:{}".format(req_type)
        print(ms)
        logger.exception(msg=ms)
        mes['message'] = ms
    return mes


def process_praise(**kwargs) -> None:
    """
    处理简道云发送过来的战报海报消息
    :param kwargs:
    :return:
    """
    args = dict()
    args['order'] = kwargs['_id']
    args['the_type'] = kwargs['the_type']
    args['customer'] = kwargs['customer']
    args['sales'] = kwargs['sales']
    args['manager'] = kwargs['manager']
    args['director'] = kwargs['director']
    args['event_time'] = mongo_db.get_datetime_from_str(kwargs['time'])
    money = kwargs['money']
    desc = kwargs.get('desc', '')
    try:
        money = int(money)
    except Exception as e:
        ms = "转换入金宣传表中的金额时出错,money={}, error:{}".format(money, e)
        logger.exception(msg=ms)
        print(ms)
    finally:
        args['money'] = money
        """创建并保存入金宣传信息"""
        r = Praise.create(**args)
        if isinstance(r, ObjectId):
            """发送钉订消息"""
            data = dict()
            data['msgtype'] = 'markdown'
            markdown_doc = dict()
            markdown_doc['title'] = "入金喜报"
            i = str(r)
            if desc == '':
                text = "![screenshot](http://47.106.68.161:8000/normal/praise_image/view?fid={})".format(r)
            else:
                text = "![screenshot](http://47.106.68.161:8000/normal/praise_image/view?fid={}) \n  ##### {} [胜利][胜利][胜利]，继续加油！[加油][加油][加油]".format(r, desc)
            print("text = {}".format(text))
            markdown_doc['text'] = text
            data['markdown'] = markdown_doc
            token_name = '入金宣传'
            send_signal(send_data=data, token_name=token_name)
        else:
            """发送钉订失败"""
            title = "使用钉钉机器人发送入金宣传失败{}".format(datetime.datetime.now())
            content = "args: {}".format(args)
            send_mail(title=title, content=content)
            ms = "{}, {}".format(title, content)
            logger.exception(msg=ms)


def process_material(**kwargs) -> None:
    """
    处理简道云发送过来的每日素材
    :param kwargs:
    :return:
    """
    args = dict()
    files = kwargs.get("file", [])
    if len(files) < 1:
        file_url = ''
        file_name = ''
    else:
        file = files[0]
        file_url = file.get("url", "")
        file_name = file.get("name", "")
    images = kwargs.get("image", [])
    if len(images) < 1:
        image_url = ''
        image_name = ''
    else:
        image = images[0]
        image_url = image.get("url", "")
        image_name = image.get("name", "")
    args["file"] = {"url": file_url, "name": file_name}
    args["image"] = {"url": image_url, "name": image_name}
    args['date_time'] = mongo_db.get_datetime_from_str(kwargs.get("date_time"))
    groups = kwargs.get("group", list())
    args['groups'] = groups
    desc = kwargs.get("desc", '')
    args['desc'] = desc
    print("---------------")
    print(args)
    print("groups {}".format(groups))

    """发送钉订消息"""
    data = dict()
    data['msgtype'] = 'markdown'
    markdown_doc = dict()
    markdown_doc['title'] = "每日素材"
    text = "![{}]({}) \n  [{}]({})  \n  ##### {}".format(image_name, image_url, file_name, file_url, desc)
    print("text = {}".format(text))
    markdown_doc['text'] = text
    data['markdown'] = markdown_doc
    transform = {
        "素材群": "素材群",
        "高管沟通群": "高管沟通群",
        "电销部门业务群": "战报"
    }
    sent = dict()
    for x in groups:
        if x in transform:
            token_name = transform[x]
            r = send_signal(send_data=data, token_name=token_name)
            print("sent {}".format(x))
            sent[x] = r
        else:
            pass

    args['send_result'] = sent
    now = datetime.datetime.now()
    args['push_time'] = now
    """创建并保存每日素材发送结果"""
    r = MaterialPushHistory.insert_one(**args)
    if r is None:
        title = "保存每日素材发送结果失败{}".format(now)
        send_mail(title=title)
    else:
        pass


if __name__ == "__main__":
    pass



