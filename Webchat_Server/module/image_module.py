#  -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from log_module import get_logger
import mongo_db
from send_moudle import *
from mail_module import send_mail
from pymongo import ReturnDocument
from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


logger = get_logger()
ObjectId = mongo_db.ObjectId
activate_path = os.path.join(__project_path, 'static', 'images', 'praise', 'activate_template.jpg')
deposit_path = os.path.join(__project_path, 'static', 'images', 'praise', 'deposit_template.jpg')


"""
图像操作模块
此模块应该放置在Message_server下面,在接收交易平台的入金成功信息的时候操作此模块
在此存在的目的仅仅是验证技术
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


def create_image(the_type: int = 0, dept: str = '', group: str = '', sales: str = '', customer: str = '',
                 money: (int, float) = 0) -> Image:
    """
    生成一个图像文件
    :param the_type: 类型,0为激活,1为加金
    :param dept: 部门 最长三个汉字
    :param group: 组 最长三个汉字
    :param sales: 销售 最长三个汉字
    :param customer: 客户 最长三个汉字
    :param money: 美金
    :return:
    """
    f_path = activate_path if the_type == 0 else deposit_path
    im = Image.open(f_path)
    width, height = im.size
    draw = ImageDraw.Draw(im)
    font_path = os.path.join(__project_path, 'resource', 'fonts', 'YaHei.ttf')
    title = "恭喜{} ({})".format(dept, group)
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
    l3l_position = (210, 930)
    money = "{}美元".format(add_comma(money))
    m_position = ((width - len(money) * size2) / 2 + 110, 930)
    draw.text(title_position, title, font=my_font1, fill="#f8e34d")
    draw.text(line2_position, line2, font=my_font2, fill="black")
    draw.text(l3l_position, line3, font=my_font2, fill="black")
    draw.text(m_position, money, font=my_font2, fill="red")
    return im


class PraiseImage(mongo_db.BaseFile):
    """战报图片"""
    _table_name = "praise_image"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['the_type'] = int  # 类型 0激活,1加金
    type_dict['dept'] = str  # 部门
    type_dict['group'] = str  # 组
    type_dict['sales'] = str  # 销售
    type_dict['customer'] = str  # 客户
    type_dict['money'] = float  #
    type_dict['time'] = datetime.datetime  # 事件事件
    type_dict['file_name'] = str
    type_dict['file_type'] = str  # 文件类型
    type_dict['description'] = str
    type_dict['uploadDate'] = datetime.datetime
    type_dict['length'] = int
    type_dict['chunkSize'] = int
    type_dict['md5'] = str
    type_dict['data'] = bytes

    @classmethod
    def get_image(cls, the_type: int = 0, dept: str = '', group: str = '', sales: str = '', customer: str = '',
                  money: (int, float) = 0) -> ObjectId:
        """
        根据条件获取图片,如果图片不存在就创建它.
        :param the_type: 类型,0为激活,1为加金
        :param dept: 部门 最长三个汉字
        :param group: 组 最长三个汉字
        :param sales: 销售 最长三个汉字
        :param customer: 客户 最长三个汉字
        :param money: 美金
        :return:  ObjectId
        """
        f = {
            "the_type": the_type,
            "dept": dept,
            "group": group,
            "sales": sales,
            "customer": customer,
            "money": money
        }
        one = cls.find_one_cls(filter_dict=f)
        if one is None:
            """没有查到,需要创建一个"""
            img = create_image(**f)
            data = BytesIO()
            file_type = 'png'
            img.save(fp=data, format=file_type)  # 图片格式必须对应,其中jpg文件的格式是jpeg
            f['file_type'] = file_type
            f['time'] = datetime.datetime.now()
            data = data.getvalue()
            _id = cls.save_cls(file_obj=data, **f)
        else:
            _id = one['_id']
        return _id


if __name__ == "__main__":
    image_id = PraiseImage.get_image(the_type=1, dept="一部", group="雄鹰队", sales="张三", customer="李四", money=1200)
    pass