#  -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from send_moudle import *
from werkzeug.contrib.cache import SimpleCache
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


logger = get_logger()
s_cache = SimpleCache()
ObjectId = mongo_db.ObjectId
activate_path = os.path.join(__project_path, 'static', 'images', 'praise', 'activate_template.jpg')
deposit_path = os.path.join(__project_path, 'static', 'images', 'praise', 'deposit_template.jpg')


"""
图像操作模块
"""


def add_comma(num: (int, float)) -> str:
    """
    把数字转为str,并加上千分位标记.
    :param num:
    :return:
    """
    num = str(num)
    flag = True if "." in num else False
    num_int, num_decimal = num.split(".", 1) if flag else [num, '']
    num_int = [x for x in num_int]
    num_int.reverse()
    res = list()
    for index, item in enumerate(num_int):
        if index % 3 == 0 and index != 0:
            res.append(",")
        else:
            pass
        res.append(item)

    res.reverse()
    num_int = "".join(res)
    if flag:
        data = num_int + "." + num_decimal.strip("")
    else:
        data = num_int + num_decimal.strip("")
    return data


def create_image_01(the_type: int = 0, director: str = '', manager: str = '', sales: str = '', customer: str = '',
                    money: (int, float) = 0) -> Image:
    """
    2018-10-23废止 第一批模板
    生成一个图像文件
    :param the_type: 类型,0为激活,1为加金
    :param director: 总监 最长三个汉字
    :param manager: 经历 最长三个汉字
    :param sales: 销售 最长三个汉字
    :param customer: 客户 最长三个汉字
    :param money: 美金
    :return:
    """
    cache_key = 'activate_img' if the_type == 0 else 'deposit_img'
    im = s_cache.get(key=cache_key)
    if im is None:
        f_path = activate_path if the_type == 0 else deposit_path
        im = Image.open(f_path)
        s_cache.set(key=cache_key, value=im, timeout=None)
    else:
        pass
    width, height = im.size
    draw = ImageDraw.Draw(im)
    font_path = os.path.join(__project_path, 'resource', 'fonts', 'YaHei.ttf')
    title = "恭喜{} ({})".format(director, manager)
    if len(title) < 10:
        size1 = 55
        title_position = (180, 552)
    elif len(title) == 10:
        size1 = 50
        title_position = (180, 555)
    else:
        size1 = 45
        title_position = (170, 560)
    size2 = 45
    my_font1 = ImageFont.truetype(font_path, size=size1)
    my_font2 = ImageFont.truetype(font_path, size=size2)

    line2 = "{}客户 : {}".format(sales, customer)
    line2_position = ((width - len(line2) * size2) / 2 + 50, 850)
    line3_activate = "激活:"
    line3_deposit = "加金:"
    line3 = line3_activate if the_type == 0 else line3_deposit
    # l3l_position = (210, 930)
    money = "{}美元".format(add_comma(money))
    w2 = (width - (((len(line3 + money) - 4) / 2) + 4) * size2) / 2
    l3l_position = (w2, 930)
    # m_position = ((width - len(money) * size2) / 2 + 150, 930)
    w3 = w2 + 2.5 * size2
    m_position = (w3, 930)
    draw.text(title_position, title, font=my_font1, fill="#f8e34d")
    draw.text(line2_position, line2, font=my_font2, fill="black")
    draw.text(l3l_position, line3, font=my_font2, fill="black")
    draw.text(m_position, money, font=my_font2, fill="red")
    return im


def create_image(the_type: int = 0, director: str = '', manager: str = '', sales: str = '', customer: str = '',
                 money: (int, float) = 0) -> Image:
    """
    生成一个图像文件
    :param the_type: 类型,0为激活,1为加金
    :param director: 总监 最长三个汉字
    :param manager: 经历 最长三个汉字
    :param sales: 销售 最长三个汉字
    :param customer: 客户 最长三个汉字
    :param money: 美金
    :return:
    """
    cache_key = 'activate_img' if the_type == 0 else 'deposit_img'
    im = s_cache.get(key=cache_key)
    if im is None:
        f_path = activate_path if the_type == 0 else deposit_path
        im = Image.open(f_path)
        s_cache.set(key=cache_key, value=im, timeout=None)
    else:
        pass
    width, height = im.size
    draw = ImageDraw.Draw(im)
    font_path = os.path.join(__project_path, 'resource', 'fonts', 'YaHei.ttf')
    title = "恭喜{} ({})".format(director, manager)
    if len(title) < 10:
        size1 = 55
        title_position = (180, 552)
    elif len(title) == 10:
        size1 = 50
        title_position = (180, 555)
    else:
        size1 = 45
        title_position = (170, 560)
    size2 = 45
    my_font1 = ImageFont.truetype(font_path, size=size1)
    my_font2 = ImageFont.truetype(font_path, size=size2)

    line2 = "{}客户 : {}".format(sales, customer)
    line2_position = ((width - len(line2) * size2) / 2 + 50, 850)
    line3_activate = "激活:"
    line3_deposit = "加金:"
    line3 = line3_activate if the_type == 0 else line3_deposit
    # l3l_position = (210, 930)
    money = "{}美元".format(add_comma(money))
    w2 = (width - (((len(line3 + money) - 4) / 2) + 4) * size2) / 2
    l3l_position = (w2, 930)
    # m_position = ((width - len(money) * size2) / 2 + 150, 930)
    w3 = w2 + 2.5 * size2
    m_position = (w3, 930)
    draw.text(title_position, title, font=my_font1, fill="#f8e34d")
    draw.text(line2_position, line2, font=my_font2, fill="black")
    draw.text(l3l_position, line3, font=my_font2, fill="black")
    draw.text(m_position, money, font=my_font2, fill="red")
    return im


class Praise(mongo_db.BaseDoc):
    """战报信息"""
    _table_name = "praise_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['the_type'] = int  # 类型 0激活,1加金
    type_dict['order'] = str  # 平台事件序列号,也就是_id,唯一
    type_dict['director'] = str  # 总监
    type_dict['manager'] = str  # 经理
    type_dict['sales'] = str  # 销售
    type_dict['customer'] = str  # 客户
    type_dict['money'] = int  #
    type_dict['time'] = datetime.datetime  # 事件事件
    type_dict['desc'] = str

    @classmethod
    def create(cls, order: str, the_type: int = 0, director: str = '', manager: str = '', sales: str = '',
               customer: str = '', money: (int, float) = 0, event_time: datetime.datetime = None,
               desc: str = '') -> ObjectId:
        """
        根据条件获取加金,如果信息不存在就创建它.
        :param order: 平台事件序列号
        :param the_type: 类型,0为激活,1为加金
        :param director: 总监 最长三个汉字
        :param manager: 经理 最长三个汉字
        :param sales: 销售 最长三个汉字
        :param customer: 客户 最长三个汉字
        :param money: 美金
        :param event_time:
        :param desc:
        :return:  ObjectId
        """
        args = {
            "the_type": the_type,
            "director": director,
            "manager": manager,
            "sales": sales,
            "customer": customer,
            "money": money,
            "time": event_time,
            "desc": desc
        }
        f = {"order": order}
        one = cls.find_one_plus(filter_dict=f)
        if one is None:
            """没有查到记录,需要创建一个"""
            args.update(f)
            _id = cls.insert_one(**args)
        else:
            _id = one['_id']
        return _id

    @classmethod
    def get_image(cls, _id: (str, ObjectId)) -> Image:
        if not isinstance(_id, (str, ObjectId)):
            ms = "错误的参数,_id={}".format(_id)
            raise ValueError(ms)
        else:
            _id = _id if isinstance(_id, ObjectId) else ObjectId(_id)
            key = "praise_img_{}".format(str(_id))
            img = s_cache.get(key)
            if img is None:
                one = cls.find_by_id(o_id=_id, to_dict=True)
                if one is None:
                    ms = "错误的_id, {}".format(_id)
                    raise ValueError(ms)
                else:
                    args = {
                        "the_type": one['the_type'],
                        "order": one['order'],
                        "director": one['director'],
                        "manager": one['manager'],
                        "sales": one['sales'],
                        "customer": one['customer'],
                        "money": one['money']
                    }
                    args.pop("order", None)
                    img = create_image(**args)
                    if img is not None:
                        s_cache.set(key=key, value=img, timeout=86400)
                    else:
                        pass
            else:
                pass
            return img


class MaterialPushHistory(mongo_db.BaseDoc):
    """
    每日素材的推送历史
    """
    _table_name = "material_push_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['image'] = dict
    type_dict['file'] = dict
    type_dict['groups'] = list
    type_dict['send_result'] = dict
    type_dict['date_time'] = datetime.datetime
    type_dict['push_time'] = datetime.datetime


if __name__ == "__main__":
    # image_id = Praise.create(order="12",the_type=1, director="李总监", manager="张经理", sales="张三", customer="李四", money=1200)
    # print(image_id)
    # i_id = "5bad2affdbea624788968109"
    # img = Praise.get_image(i_id)
    # img.show()
    im = create_image(the_type=0, director="李总监", manager="张经理", sales="张三", customer="李四", money=1200)
    im.show()

    pass