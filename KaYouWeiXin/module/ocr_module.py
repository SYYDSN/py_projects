# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db2
import datetime
from log_module import get_logger
from aip import AipOcr


ObjectId = mongo_db2.ObjectId
logger = get_logger()


"""
图像识别模块,用于识别:
1. 身份证
2. 驾驶证
3. 行车证

"""

app_id = '11782934'                              # 百度AppID
api_key = 'SMQ57H9K6P2TBR2X6tfQlYRH'             # 百度API Key
secret_key = 'ALhDsnARbu58NsWRXFWFgwRbRivYaBYv'  # 百度Secret Key


def get_client() -> AipOcr:
    """
    获取百度ocr客户端
    :return:
    """
    cli = AipOcr(appId=app_id, apiKey=api_key, secretKey=secret_key)
    return cli


def driving_license(img: bytes = None) -> dict:
    """
    识别驾驶证识别图像内容,这是个独立的方法. 用于验证代码
    :param img: 图像的二进制文件
    :return:
    """
    client = get_client()
    data = client.drivingLicense(image=img, options={'detect_direction': 'true'})
    return data


def id_card(img: bytes = None, ab: str = "face") -> dict:
    """
    识别身份证,这是个独立的方法. 用于验证代码
    :param img: 图像的二进制文件
    :param ab: 正面还是背面?  注意,这里的正面指的是有照片的一面,不是严格意义上的身份证正面
    :return:
    """
    client = get_client()
    if ab.lower() in ['face', 'front', 'a']:
        id_card_side = 'front'
    else:
        id_card_side = 'back'
    data = client.idcard(image=img, id_card_side=id_card_side, options={'detect_direction': 'true'})
    return data


class OcrResult(mongo_db2.BaseDoc):
    """
    ocr的识别结果,保存他们是为了方便复用.避免多次重复识别同一张图片.
    注意数据是存在招聘站点的数据库的
    """
    _table_name = "ocr_result"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # _id也是图片的原始id,注意,不同的图片理论上有id相同的可能.
    type_dict['img_table'] = str   # 原始图片保存的表名
    type_dict['result'] = dict  # 识别的结果
    type_dict['raw'] = dict  # 识别的原始结果
    type_dict['success'] = bool  # 识别的结果是否成功? 如果不成功然会的数据就没有意义,记录本身是为了表明这个图片是无效的.
    type_dict['time'] = datetime.datetime

    @classmethod
    def id_card(cls, img_id: ObjectId, ab: str = "face") -> dict:
        """
        识别身份证
        :param img_id: 身份证图片的d_id
        :param ab: 正面还是背面?  注意,这里的正面指的是有照片的一面,不是严格意义上的身份证正面
        :return:
        """
        data = None
        img_id = img_id if isinstance(img_id, ObjectId) else ObjectId(img_id)
        f = {"_id": img_id}
        one = cls.find_one_plus(filter_dict=f, instance=False)
        if one is None:
            """以前没识别过"""
            if ab.lower() in ['face', 'front', 'a']:
                id_card_side = 'front'
            else:
                id_card_side = 'back'
            client = get_client()
            table_name = "id_image"
            img = mongo_db2.BaseFile.get_one_data(filter_dict=f, collection=table_name)
            if img is None:
                ms = "身份证图片:{} 不存在".format(img_id)
                logger.exception(msg=ms)
                raise ValueError(ms)
            else:
                resp = client.idcard(image=img, id_card_side=id_card_side, options={'detect_direction': 'true'})
                data = dict()
                data['_id'] = img_id
                data['img_table'] = table_name
                data['raw'] = resp
                words_result = resp.get("words_result")
                if words_result is None:
                    """识别失败"""
                    data['success'] = False
                else:
                    data['success'] = True
                    result = dict()
                    if id_card_side is "front":
                        """正面"""
                        try:
                            name = words_result['姓名']['words']
                            result['name'] = name
                        except Exception as e:
                            ms = "识别身份证姓名出错,id={}, case:{}".format(img_id, e)
                            logger.exception(msg=ms)
                        try:
                            sex = words_result['性别']['words']
                            result['sex'] = sex
                        except Exception as e:
                            ms = "识别身份证性别出错,id={}, case:{}".format(img_id, e)
                            logger.exception(msg=ms)
                        try:
                            id_num = words_result['公民身份号码']['words']
                            result['id_num'] = id_num
                        except Exception as e:
                            ms = "识别身份证号码出错,id={}, case:{}".format(img_id, e)
                            logger.exception(msg=ms)
                        try:
                            born = words_result['出生']['words']
                            born = born.strip()
                            y = born[0: 4]
                            m = born[4: 6]
                            d = born[6: 8]
                            birth_date = mongo_db2.get_datetime_from_str("{}-{}-{}".format(y, m, d))
                            result['birth_date'] = birth_date
                        except Exception as e:
                            ms = "识别身份证号码出错,id={}, case:{}".format(img_id, e)
                            logger.exception(msg=ms)
                    else:
                        """背面"""
                        try:
                            end = words_result['失效日期']['words']
                            end = end.strip()
                            y = end[0: 4]
                            m = end[4: 6]
                            d = end[6: 8]
                            id_card_end = mongo_db2.get_datetime_from_str("{}-{}-{}".format(y, m, d))
                            result['id_card_end'] = id_card_end
                        except Exception as e:
                            ms = "识别身份证失效日期出错,id={}, case:{}".format(img_id, e)
                            logger.exception(msg=ms)
                    data['result'] = result
                data['time'] = datetime.datetime.now()
                o = cls.insert_one(**data)
                if isinstance(o, ObjectId):
                    pass
                else:
                    ms = "保存身份证识别结果出错: {}".format(data)
                    logger.exception(msg=ms)
        else:
            """以前识别过"""
            data = one
        return data


class IdCardOcrRequest(mongo_db2.BaseDoc):
    """
    简历中的身份证OCR识别请求.
    celery每次检查这个表,对需要进行OCR识别的简历中的图片进行识别.
    识别的结果发送到对应的用户.
    业务逻辑如下:

    1. 用户在保存身份证正反面图片时,进行如下检查:
        正反面图片的id存在,而且简历的real_name也存在
        if resume.id_image_face is not None and resume.id_image_back is not None and resume.get('real_name', '') != '':
            在OcrRequest中添加一条请求识别信息.注意,是find_and_update,不是insert,防止因为多次上传导致的重复请求.
    2. celery定时检查OcrRequest中resp_time = 2000-01-01 00:00:00.000的记录,调用cls.process进行处理.
    """
    _table_name = "id_card_ocr_request"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 和DriverResume._id相同
    type_dict['a'] = ObjectId  # 身份证正面的id, 有照片的那一面
    type_dict['b'] = ObjectId  # 身份证背面的id
    type_dict['real_name'] = str  # 真是姓名
    type_dict['req_time'] = datetime.datetime  # 请求时间
    """
    """
    type_dict['resp_time'] = datetime.datetime  # 响应/处理时间

    @classmethod
    def process(cls) -> None:
        """
        处理简历相关的OCR识别请求
        :return:
        """
        f = {"resp_time": {"$exists": False}}
        l = cls.find_plus(filter_dict=f, to_dict=True)
        for x in l:
            resume_id = x['_id']
            a_id = x['a']
            b_id = x['b']
            real_name = x['real_name']
            process = x['process']
            if hasattr(OcrResult, process):
                now = datetime.datetime.now()
                handler = getattr(OcrResult, process)
                r1 = handler(img_id=a_id, ab="a")
                r2 = handler(img_id=b_id, ab="b")
                f = {"_id": resume_id}
                u = {"$set": {"resp_time": now}}
                cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                result1 = r1.get("result")  # 正面识别结果
                result2 = r2.get("result")  # 背面识别结果
                if isinstance(result1, dict) and isinstance(result2, dict):
                    result1.update(result2)
                    id_card_end = result1.get("id_card_end")
                    real_name2 = result1.get("real_name")
                    id_num = result1.get("id_num")
                    if real_name == real_name2 and len(id_num) == 18:
                        """名字一致,身份证号码合法.通过"""
                        t1 = mongo_db2.get_conn("driver_resume")
                        f = {"_id": resume_id}
                        uu = {
                            "locked_id_card": 1,
                            "id_card_end": id_card_end,
                            "id_num": id_num
                        }
                        u = {"$set": uu}
                        r = t1.find_one_and_update(filter=f, upsert=False, update=u)
                        if r is None:
                            ms = "写入身份证审核成功的信息失败:doc={}, u={}".format(r, u)
                            logger.exception(msg=ms)
                            print(ms)
                        else:
                            """
                            身份证审核成功,可以在这里向用户发送模板消息.
                            """
                            pass
                    else:
                        """
                        身份证审核失败,可以在这里向用户发送模板消息.
                        """
                        pass
                else:
                    """
                    身份证审核失败,可以在这里向用户发送模板消息.
                    """
                    pass
            else:
                """未知的操作"""
                ms = "未知的操作process u={}".format(process)
                logger.exception(msg=ms)
                print(ms)
                pass



if __name__ == "__main__":
    pass