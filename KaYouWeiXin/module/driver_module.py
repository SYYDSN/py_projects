#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db2
import requests
import datetime
import re
from log_module import get_logger
from pymongo.results import InsertOneResult
from pymongo.results import UpdateResult
from pymongo.results import DeleteResult


ObjectId = mongo_db2.ObjectId
logger = get_logger()


"""
司机简历相关的模型
这个模块有两个项目有:
1. 司机招聘网站
2. 卡佑微信服务号
"""


class Region(mongo_db2.BaseDoc):
    """
    行政区域代码  http://cnis.7east.com/
    """
    _table_name = "region_info"
    type_dict = dict()
    type_dict['_id'] = int
    type_dict['name'] = str  # 名称
    type_dict['code'] = int  # 六位数字,实际上用途不明.
    type_dict['region_path'] = str  # 字符串,表明层级关系,不重要
    type_dict['parent_id'] = int  # 上级行政区域_id 如果是顶层的,这个值是0

    @classmethod
    def get_province(cls, can_json: bool = False) -> list:
        """
        获取全国的省和直辖市
        : param can_json:
        :return:
        """
        f = {"parent_id": 0}
        res = cls.find_plus(filter_dict=f, to_dict=True ,can_json=can_json)
        return res

    @classmethod
    def get_city(cls, province_code: int = None, province_name: str = None, can_json: bool = False) -> list:
        """
        根据省的code/名称获取其下一级的行政单位(市)
        :param province_code: 省code
        :param province_name: 省全名(比如湖南省)
        :param can_json:
        :return:
        """
        if isinstance(province_code, str) and province_code.isdigit():
            province_code = int(province_code)
        else:
            pass
        if not isinstance(province_code, int):
            if isinstance(province_name, str):
                f = {"name": province_name}
                res = cls.find_one_plus(filter_dict=f, instance=False, can_json=False)
                if res is None:
                    ms = "province_name值不合法"
                    raise ValueError(ms)
                else:
                    province_code = res['code']
            else:
                ms = "province_code和province_name参数名不合法"
                raise ValueError(ms)
        else:
            """开始查找城市列表"""
            if province_code in [1, 864, 22, 2476]:
                province_code += 1
            f = {"parent_id": province_code}
            res = cls.find_plus(filter_dict=f, to_dict=True, can_json=can_json)
            return res

    @classmethod
    def build_region_1(cls):
        """
        从网络初始化第一级行政区
        :return:
        """
        url = "http://cnis.7east.com/widget.do?type=service&ajax=yes&action=cnislist"
        resp = requests.get(url=url)
        status = resp.status_code
        if status == 200:
            data = resp.json()
            for x in data['rows']:
                args = {
                    "_id": int(x['region_id']),
                    "name": x['local_name'],
                    "code": x['code'],
                    "region_path": x['region_path'],
                    "parent_id": x['_parentId']
                }
                no1 = cls(**args)
                no1.save_plus(upsert=True)

        else:
            ms = "服务器返回了错误的响应码:{}".format(status)
            raise ValueError(ms)

    @classmethod
    def build_region_2(cls):
        """
        从网络初始化第二级行政区
        :return:
        """
        url = "http://cnis.7east.com/widget.do?type=service&action=cnischildlist&a=2&ajax=yes&pid={}"
        a = cls.find_plus(filter_dict=dict(), projection=['_id', 'name'], to_dict=True)
        for x in a:
            the_url = url.format(x['_id'])
            data = {"_id": x['_id']}
            resp = requests.post(url=the_url, data=data)
            status = resp.status_code
            if status == 200:
                data = resp.json()
                rows = data['rows']
                if len(rows) == 1:
                    """市辖区"""
                    _id = rows[0]['region_id']
                    the_url = url.format(_id)
                    data = {"_id": _id}
                    resp = requests.post(url=the_url, data=data)
                    status = resp.status_code
                    if status != 200:
                        ms = "服务器返回了错误的响应码:{}".format(status)
                        raise ValueError(ms)
                    else:
                        data = resp.json()
                        rows = data['rows']
                        if len(rows) == 1:
                            print(data)
                        else:
                            for y in rows:
                                args = {
                                    "_id": int(y['region_id']),
                                    "name": y['local_name'],
                                    "code": y['code'],
                                    "region_path": y['region_path'],
                                    "parent_id": y['_parentId']
                                }
                                no = cls(**args)
                                no.save_plus(upsert=True)
                else:
                    for y in rows:
                        args = {
                            "_id": int(y['region_id']),
                            "name": y['local_name'],
                            "code": y['code'],
                            "region_path": y['region_path'],
                            "parent_id": y['_parentId']
                        }
                        no = cls(**args)
                        no.save_plus(upsert=True)
            else:
                ms = "服务器返回了错误的响应码:{}".format(status)
                raise ValueError(ms)

    @classmethod
    def get_data(cls) -> list:
        """
        返回第一级行政辖区
        :return:
        """
        f = {"parent_id": 0}
        p = ["_id", "name"]
        r = cls.find_plus(filter_dict=f, projection=p, to_dict=True, can_json=True)
        return r


class Route(mongo_db2.BaseDoc):
    """
    (熟悉)线路类,注意,这个和保驾犬的TrafficRoute类不同.
    本例只是为了标记司机熟悉的城市线路.只要城市节点相同,不分顺序和来往,都是一条线路.
    和简历是多对一的关系.
    """
    _table_name = "route_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['cities'] = list  # 城市名称(str)组成的list
    type_dict['create_date'] = datetime.datetime  # 创建时间

    def __init__(self, **kwargs):
        if "region_list" not in kwargs:
            kwargs['region_list'] = list()
        if 'create_date' not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(Route, self).__init__(**kwargs)


class Honor(mongo_db2.BaseDoc):
    """
    荣誉证书信息,和简历是多对一的关系.
    """
    _table_name = "honor_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['time'] = datetime.datetime  # 获奖时间
    type_dict['title'] = str    # 荣誉称号
    type_dict['info'] = str    # 荣誉信息
    type_dict['image_id'] = ObjectId  # 荣誉图片
    type_dict['image_url'] = str  # 荣誉图片的地址,这个字段是计算出来的,不保存实际的值.
    type_dict['create_date'] = datetime.datetime  # 创建时间


class Vehicle(mongo_db2.BaseDoc):
    """
    车辆信息,某些司机可能自己有车辆.
    与保驾犬不同,司机招聘网站的车辆信息和司机(简历)是多对一的关系
    """
    _table_name = "vehicle_license_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict["image_id"] = ObjectId  # 车辆照片
    type_dict["image_url"] = str  # 车辆照片的url,这个字段是计算出来的,不保存实际的值.
    type_dict["plate_number"] = str  # 车辆号牌, 英文字母必须大写,允许空,不做唯一判定
    """
    相关标准参考GB1589
    直接扫描行车证可得到,另外修正时提供下拉选项, 也可以手动填写.
    小型轿车、小型客车、中型客车、大型客车、平板式货车、栏板式货车、厢式货车、仓栅式货车、罐式车、自卸车、其他（手动填写）
    """
    type_dict["vehicle_type"] = str  # 车辆类型
    """
    载重量,只有货车有这个选项.
    1.8/6/14三档 6代表1.8<t<6,以此类推,None代表没有此项数据,-1代表大于14
    """
    type_dict['vehicle_load'] = float  # 车辆载重量,单位吨.
    """
    车长,只有货车有这个选项.
    6/9.6/17.5 三档 None代表没有此项数据,-1代表大于17.5
    """
    type_dict['vehicle_length'] = float  # 车辆载重量,单位米.
    type_dict["owner_name"] = str  # 车主姓名/不一定是驾驶员
    type_dict["address"] = str  # 地址
    type_dict["vehicle_model"] = str  # 车辆型号  比如 一汽解放J6
    type_dict["vin_id"] = str  # 车辆识别码/车架号的后六位 如果大于6，查询违章的时候就用后6位查询
    type_dict["engine_id"] = str  # 发动机号
    type_dict["register_date"] = datetime.datetime  # 注册日期
    type_dict["issued_date"] = datetime.datetime  # 发证日期
    type_dict["create_date"] = datetime.datetime  # 创建日期

    def __init__(self, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        if "plate_number" in kwargs:
            """plate_number为空是在仅仅上传了行车证照片，还没有输入车牌信息的情况。一个用户只允许一条这样的记录"""
            kwargs['plate_number'] = kwargs['plate_number'].upper()
        super(Vehicle, self).__init__(**kwargs)


class WorkHistory(mongo_db2.BaseDoc):
    """
    工作经历,用于在简历中表示一段工作历史,
    和简历是多对一的关系
    """
    _table_name = "work_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime
    type_dict['enterprise_name'] = str  # 企业名称
    type_dict['enterprise_class'] = str  # 企业性质
    type_dict['industry'] = str  # 所属行业
    """
    企业规模
    50/100/500/1000  50表示小于等于50人规模 -1表示大于1000人规模
    """
    type_dict['enterprise_scale'] = int  # 企业规模
    type_dict['dept_name'] = str  # 部门名称
    """
    预置几个岗位名称,留给客户自己填写的机会.
    驾驶员/车队经理/其他
    """
    type_dict['post_name'] = str  # 岗位名称.
    type_dict['team_size'] = int  # 团队/下属人数
    """
    相关标准参考GB1589
    车型提供下拉选项,也可以手动填写.
    小型轿车、小型客车、中型客车、大型客车、平板式货车、栏板式货车、厢式货车、仓栅式货车、罐式车、自卸车、其他（手动填写）
    """
    type_dict['vehicle_type'] = str  # 车型
    """
    载重量,只有货车有这个选项.
    1.8/6/14三档 6代表1.8<t<6,以此类推,None代表没有此项数据,-1代表大于14
    """
    type_dict['vehicle_load'] = float  # 车辆载重量,单位吨.
    """
    车长,只有货车有这个选项.
    6/9.6/17.5 三档 None代表没有此项数据,-1代表大于17.5
    """
    type_dict['vehicle_length'] = float  # 车辆载重量,单位米.
    type_dict['description'] = str  # 工作描述.带换行符和空格的字符串格式.
    type_dict['achievement'] = str  # 工作业绩.带换行符和空格的字符串格式.
    type_dict["create_date"] = datetime.datetime  # 创建日期


class Education(mongo_db2.BaseDoc):
    """
    教育经历,用于在简历中表示一段教育历史,
    和简历是多对一的关系
    """
    _table_name = "education"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['level'] = str  # 用户选择,  小学/初中/高中/高等教育/培训机构/其他
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime
    type_dict['school_name'] = str  # 学校名称
    type_dict['major'] = str  # 主修专业


class HeadImage(mongo_db2.BaseFile):
    """
    用户头像
    """
    _table_name = "head_image"


class IdImage(mongo_db2.BaseFile):
    """
    身份证图片
    """
    _table_name = "id_image"


class HonorImage(mongo_db2.BaseFile):
    """
    荣誉证书照片
    """
    _table_name = "honor_image"


class VehicleImage(mongo_db2.BaseFile):
    """
    行车证(机动车)照片
    """
    _table_name = "vehicle_image"


class DrivingLicenseImage(mongo_db2.BaseFile):
    """
    驾驶证(驾照)图片
    """
    _table_name = "driving_license_image"


class RTQCImage(mongo_db2.BaseFile):
    """
    公路运输从业资格证图片
    """
    _table_name = "rtqc_image"


class DriverResume(mongo_db2.BaseDoc):
    """司机简历"""
    _table_name = "driver_resume"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['app_id'] = ObjectId     # app用户的id,
    type_dict['wx_id'] = ObjectId     # 微信用户的id,
    type_dict['user_name'] = str  # 用户名,唯一判定,默认和手机相同,可以登录司机招聘网(功能未实现)
    type_dict['real_name'] = str  # 真实姓名 ,可以从驾驶证取
    type_dict['head_image'] = ObjectId  # 头像
    type_dict['gender'] = str   # 以驾驶证信息为准. 男/女
    type_dict['married'] = int  # 婚否? 0/1/-1 未婚/已婚/离异  None 空白
    type_dict['birth_place'] = str   # 籍贯/出生地
    type_dict['living_place'] = str   # 居住地,
    type_dict['address'] = str  # 家庭地址
    type_dict['phone'] = str  # 手机号码
    type_dict['email'] = str  # 邮箱
    type_dict['birth_date'] = datetime.datetime  # 出生日期,以身份证号码为准
    type_dict['id_num'] = str  # 身份证号码
    type_dict['id_image_face'] = ObjectId  # 身份证正面图片
    type_dict['id_image_face_url'] = str  # 身份证正面图片
    type_dict['id_image_back'] = ObjectId  # 身份证背面图片
    type_dict['id_image_back_url'] = str  # 身份证背面图片
    type_dict['age'] = int  # 年龄 以身份证号码为准
    """以下3个字段因为是动态的,需要在每次查询doc的时候进行计算,以保证准确性"""
    type_dict['driving_experience'] = int  # 驾龄 单位 年 用驾驶证信息中的首次领证日期计算
    type_dict['industry_experience'] = int  # 从业年限 单位 年 用道路运输从业资格证信息中的首次领证日期计算
    type_dict['work_experience'] = int  # 工作年限 单位 年 依赖first_work_date属性

    """
    学历分以下几种:
    1. 初等教育(小学及以下)
    2. 中等教育(中学,含初中,高中,职高,中专,技校)
    3. 高等教育(大专)
    4. 高等教育(本科及以上)
    """
    type_dict['education'] = int  # (最高)学历,学历代码见注释
    """教育经历部分,是Education的ObjectId的list对象"""
    type_dict['education_history'] = list
    type_dict['status'] = int  # 任职/经营 状态. -1 个体经营/0 离职/ 1 在职
    """驾驶证信息 Driving License,简称dl"""
    type_dict['dl_image'] = ObjectId  # 驾驶证图片,.
    type_dict['dl_image_url'] = str  # 驾驶证图片的地址,.
    type_dict['dl_license_class'] = str  # 驾驶证信息.驾驶证类型,准驾车型 英文字母一律大写
    type_dict['dl_first_date'] = datetime.datetime  # 驾驶证信息 首次领证日期
    type_dict['dl_valid_begin'] = datetime.datetime  # 驾驶证信息 驾照有效期的开始时间
    type_dict['dl_valid_duration'] = int  # 驾驶证信息 驾照有效持续期,单位年
    """道路运输从业资格证部分,Road transport qualification certificate 简称rtqc"""
    type_dict['rtqc_image'] = ObjectId  # 道路运输从业资格证信息,照片
    type_dict['rtqc_image_url'] = str  # 道路运输从业资格证信息照片的地址
    type_dict['rtqc_license_class'] = str  # 道路运输从业资格证信息.货物运输驾驶员/危险货物运输驾驶员
    type_dict['rtqc_first_date'] = datetime.datetime  # 道路运输从业资格证信息 首次领证日期,用于推定从业年限
    type_dict['rtqc_valid_begin'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的开始时间
    type_dict['rtqc_valid_end'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的结束时间
    """某些司机自己有车辆"""
    type_dict['vehicle'] = list  # 车辆信息, Vehicle.的ObjectId对象
    """求职意愿"""
    type_dict['want_job'] = bool  # 是否有求职意向?有求职意向的才会推荐工作,可以认为这是个开关.
    type_dict['remote'] = bool  # 是否原因在外地工作?
    type_dict['target_city'] = str  # 期望工作城市,这是一个临时性的字段,地区编码库完善后,此阻断将由 expected_regions替代.
    """留下,暂时不用,只有愿意不愿意取外地工作这个选项"""
    type_dict['expected_regions'] = list    # 期望工作地区,list是区域代码的list,
    """
     期望待遇,2个int元素组成的数组.第一个元素表示待遇下限,第二个元素表示待遇上限.  
     如果只有一个元素,则代表下限.
     如果没有元素,代表待遇面议.
     超过2个的元素会被抛弃.
     元素必须是int类型
    """
    type_dict['expected_salary'] = list   # 期望待遇
    """熟悉线路"""
    type_dict['routes'] = list  # 熟悉线路,城市名称组成的数组的的list
    """工作履历部分,是WorkHistory.的ObjectId的list对象"""
    type_dict['work_history'] = list
    type_dict['last_company'] = str  # 最后工作的公司,仅仅为列表页而添加,需要更新工作经历时同步
    type_dict['first_work_date'] = datetime.datetime  # 最早的工作时间,由最早的工作经历确定.可以用来计算工龄.需要更新工作经历时同步
    """
    最后的工作截至时间. 需要配合status字段使用:
    1. 如果这个值不存在.status==1,那就是在职没添加过工作简历. 
    1. 如果这个值不存在.status!=1,那就是离职没添加过工作简历. 
    由于目前的ORM的datetime字段不能赋值为None,所以在清除所有的工作经历时需要删掉此字段
    """
    type_dict['end_work_date'] = datetime.datetime
    type_dict['self_evaluation'] = str  # 自我评价
    """获奖/荣誉证书 Honor._id的list对象"""
    type_dict['honor'] = list
    type_dict['update_date'] = datetime.datetime  # 简历的刷新时间
    type_dict['create_date'] = datetime.datetime  # 简历的创建时间

    def __init__(self, **kwargs):
        user_name = kwargs.pop("user_name", "")
        if user_name == "":
            kwargs['user_name'] = kwargs.get("phone")
        dl_license_class = kwargs.pop("dl_license_class", None)
        if isinstance(dl_license_class, str):
            kwargs['dl_license_class'] = dl_license_class.upper()
        now = datetime.datetime.now()
        if "create_date" not in kwargs:
            kwargs['create_date'] = now
        if "update_date" not in kwargs:
            kwargs['update_date'] = now
        if "gender" not in kwargs:
            kwargs['gender'] = "男"
        phone = kwargs.get("phone")
        if isinstance(phone, str) and len(phone) == 11 and phone.isdigit() and phone.startswith("1"):
            pass
        else:
            ms = "错误的手机号码:{}".format(phone)
            raise ValueError(ms)
        email = kwargs.pop('email', '')
        if re.match(r"\S+@\S{1,10}\.\S{1,8}", email):
            kwargs['email'] = email
        else:
            pass
        age = kwargs.pop('age', "")
        if isinstance(age, int):
            pass
        elif isinstance(age, str) and age.isdigit():
            age = int(age)
        else:
            pass
        if isinstance(age, int) and 16 <= age <= 60:
            kwargs['age'] = age
        else:
            pass

        birth_date = kwargs.pop("birth_date", None)
        if isinstance(birth_date, datetime.datetime):
            kwargs['birth_date'] = birth_date
        elif isinstance(birth_date, str):
            birth_date = mongo_db2.get_datetime_from_str(birth_date)
            if isinstance(birth_date, datetime.datetime):
                kwargs['birth_date'] = birth_date
            else:
                pass
        else:
            pass
        id_num = kwargs.pop("id_num", "")
        if re.match(r"\d{17}\S", id_num):
            """身份证号码正确"""
            y, m, d = id_num[6: 10], id_num[10: 12], id_num[12: 14]
            age = now.year - int(y)
            bd = mongo_db2.get_datetime_from_str("{}-{}-{}".format(y, m, d))
            kwargs['id_num'] = id_num
            kwargs['birth_date'] = bd
            kwargs['age'] = age
        else:
            pass
        dl_first_date = kwargs.pop("dl_first_date", None)  # 驾照首次申领日期
        if isinstance(dl_first_date, str):
            dl_first_date = mongo_db2.get_datetime_from_str(dl_first_date)
        else:
            pass
        if isinstance(dl_first_date, datetime.datetime):
            kwargs['dl_first_date'] = dl_first_date
            driving_experience = now.year - dl_first_date.year
            kwargs['driving_experience'] = driving_experience
        else:
            pass
        rtqc_first_date = kwargs.pop("rtqc_first_date", None)  # 运输许可证首次申领日期
        if isinstance(rtqc_first_date, str):
            rtqc_first_date = mongo_db2.get_datetime_from_str(rtqc_first_date)
        else:
            pass
        if isinstance(rtqc_first_date, datetime.datetime):
            kwargs['rtqc_first_date'] = rtqc_first_date
            industry_experience = now.year - rtqc_first_date.year
            kwargs['industry_experience'] = industry_experience
        else:
            pass
        super(DriverResume, self).__init__(**kwargs)

    @classmethod
    def extend_info(cls, raw: dict) -> dict:
        """
        重新计算扩展的信息,此函数需要在查询的时候被调用以计算
        1. 工龄
        2. 驾龄
        3. 从业年限
        ,最常见的情况是在分页查询时.重新计算经验
        type_dict['driving_experience'] = int  # 驾龄 单位 年 用驾驶证信息中的首次领证日期计算
        type_dict['industry_experience'] = int  # 从业年限 单位 年 用道路运输从业资格证信息中的首次领证日期计算
        type_dict['work_experience'] = int  # 工作年限 单位 年 工作履历记录中最早的开始计算,需要更新工作经历时同步
        :param raw: 实例的doc类型,确保时间类型的原有格式
        :return:
        """
        """计算驾龄"""
        now = datetime.datetime.now()
        dl_first_date = raw.pop("dl_first_date", None)  # 驾照首次申领日期
        if isinstance(dl_first_date, str) or isinstance(dl_first_date, datetime.datetime):
            dl_first_date = dl_first_date if isinstance(dl_first_date,
                                                        datetime.datetime) else mongo_db2.get_datetime_from_str(
                dl_first_date)
            if isinstance(dl_first_date, datetime.datetime):
                driving_experience = now.year - dl_first_date.year
                raw['driving_experience'] = driving_experience
            else:
                pass
        else:
            pass
        """计算从业年限"""
        rtqc_first_date = raw.pop("rtqc_first_date", None)  # 运输许可证首次申领日期
        if isinstance(rtqc_first_date, str) or isinstance(rtqc_first_date, datetime.datetime):
            rtqc_first_date = rtqc_first_date if isinstance(rtqc_first_date, datetime.datetime) else \
                mongo_db2.get_datetime_from_str(rtqc_first_date)
            if isinstance(rtqc_first_date, datetime.datetime):
                industry_experience = now.year - rtqc_first_date.year
                raw['industry_experience'] = industry_experience
            else:
                pass
        else:
            pass
        """计算工龄"""
        first_work_date = raw.pop("first_work_date", None)  # 首次工作时间
        if first_work_date is None:
            """查工作履历"""
            f = {"driver_id": raw['_id']}
            s = {"begin": 1}
            projection = ['begin']
            r = WorkHistory.find_one_plus(filter_dict=f, sort_dict=s, projection=projection, instance=False)
            if r is None:
                pass
            else:
                begin = r['begin']
                f = {"_id": raw['_id']}
                u = {"$set": {"first_work_date": begin}}
                cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)  # 更新首次工作日期
                first_work_date = begin
        else:
            pass
        if isinstance(first_work_date, str) or isinstance(first_work_date, datetime.datetime):
            first_work_date = first_work_date if isinstance(first_work_date, datetime.datetime) else \
                mongo_db2.get_datetime_from_str(first_work_date)
            if isinstance(first_work_date, datetime.datetime):
                work_experience = now.year - first_work_date.year
                raw['work_experience'] = work_experience
            else:
                pass
        else:
            pass
        """计算年龄"""
        birth = raw['birth_date']
        if isinstance(birth, datetime.datetime):
            age = now.year - birth.year
            raw['age'] = age
        """转期望待遇的数组为字符串,以方便前端展示"""
        expected_salary = raw.get("expected_salary")
        if isinstance(expected_salary, list):
            expected_salary = expected_salary[0:2]
            if len(expected_salary) == 1:
                expected_salary = "{}k".format(round(expected_salary[0] / 1000, 1))
            else:
                expected_salary = "{}k至{}k".format(round(expected_salary[0] / 1000, 1),
                                                   round(expected_salary[1] / 1000, 1))
        else:
            expected_salary = "面议"
        raw['expected_salary'] = expected_salary

        return raw

    @classmethod
    def query_by_page(cls, filter_dict: dict, sort_dict: dict = None, projection: list = None, page_size: int = 10,
                      ruler: int = 5, page_index: int = 1, to_dict: bool = True, can_json: bool = False,
                      func: object = None, target: str = "dict"):
        """
        分页查询,覆盖了父类的对象
        :param filter_dict:  查询条件字典
        :param sort_dict:  排序条件字典
        :param projection:  投影数组,决定输出哪些字段?
        :param page_size: 每页大小(多少条记录?)
        :param ruler: 翻页器最多显示几个页码？
        :param page_index: 页码(当前页码)
        :param to_dict: 返回的元素是否转成字典(默认就是字典.否则是类的实例)
        :param can_json: 是否调用to_flat_dict函数转换成可以json的字典?
        :param func: 额外的处理函数.这种函数用于在返回数据前对每条数据进行额外的处理.会把doc或者实例当作唯一的对象传入.
        :param target: 和func参数配合使用,指明func是对实例本身操作还是对doc进行操作(instance/dict)
        :return: 字典对象.
        查询结果示范:
        {
            "total_record": record_count,
            "total_page": page_count,
            "data": res,
            "current_page": page_index,
            "pages": pages
        }
        """
        func = cls.extend_info
        target = "dict"
        return super().query_by_page(filter_dict=filter_dict, sort_dict=sort_dict, projection=projection,
                                     page_size=page_size, ruler=ruler, page_index=page_index, to_dict=to_dict,
                                     can_json=can_json, func=func, target=target)

    @classmethod
    def add_work_history(cls, resume_id: (str, ObjectId), history_args: dict) -> ObjectId:
        """
        添加工作经历,在添加工作经历的后,进行一下字段的更新:
        1. work_history 工作经历列表
        2. last_company 最后工作过的公司
        3. first_work_date 最早的工作开始时间
        4. end_work_date 最后的工作截至时间

        :param resume_id:
        :param history_args:  WorkHistory的init字典
        :return: ObjectId, WorkHistory._id
        """
        res = None
        work = WorkHistory(**history_args).get_dict()
        resume = cls.find_by_id(o_id=resume_id, to_dict=True)
        if isinstance(work, dict) and isinstance(resume, dict):
            """开始事务操作"""
            resume_id = resume['_id']
            driver_id = work.get("driver_id", "")
            if isinstance(driver_id, str) and len(driver_id) == 24:
                driver_id = ObjectId(driver_id)
            elif isinstance(driver_id, ObjectId):
                pass
            else:
                driver_id = resume_id
            work['driver_id'] = driver_id
            client = mongo_db2.get_client()
            handler1 = client[mongo_db2.db_name][WorkHistory.get_table_name()]
            handler2 = client[mongo_db2.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    r = None
                    try:
                        r = handler1.insert_one(document=work, session=ses)
                    except Exception as e:
                        ms = "插入工作经历失败:{}".format(str(e))
                        logger.exception(msg=ms)
                        ses.abort_transaction()
                    work_id = r.inserted_id if isinstance(r, InsertOneResult) else r
                    if isinstance(work_id, ObjectId):
                        """
                        确认是否更新last_company,first_work_date,end_work_date三个字段
                        """
                        u = {"$set": {}}
                        last_company = resume.get("last_company", "")
                        first_work_date = resume.get("first_work_date", None)
                        end_work_date = resume.get("end_work_date", None)
                        f = {"driver_id": resume_id}
                        s = [("begin", -1)]
                        ws = handler1.find(filter=f, sort=s)
                        ws = [x for x in ws]
                        ws.append(work)
                        u['$set'] = {"work_history": [x['_id'] for x in ws]}
                        if len(ws) == 0:
                            unset = {"last_company": "", "first_work_date": "", "end_work_date": ""}
                            u['$unset'] = unset
                        else:
                            end_work_date2 = ws[0].get('end')
                            if end_work_date2 != end_work_date:
                                set_d = u['$set']
                                set_d['end_work_date'] = end_work_date2
                                u['$set'] = set_d
                            last_company2 = ws[0].get('enterprise_name')
                            if last_company2 != last_company:
                                set_d = u['$set']
                                set_d['last_company'] = last_company2
                                u['$set'] = set_d
                            first_work_date2 = ws[-1].get('begin')
                            if first_work_date2 != first_work_date:
                                set_d = u['$set']
                                set_d['first_work_date'] = first_work_date2
                                u['$set'] = set_d
                        """更新简历"""
                        f = {"_id": resume_id}
                        handler2.update_one(filter=f, update=u, upsert=False, session=ses)
                        res = work_id
                    else:
                        ms = "事务错误: resume_id: {}, history_args: {}".format(resume_id, history_args)
                        logger.exception(msg=ms)
                        raise ValueError(ms)
        else:
            ms = "参数错误: resume_id: {}, history_args: {}".format(resume_id, history_args)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return res

    @classmethod
    def update_work_history(cls, resume_id: (str, ObjectId), work_id: (str, ObjectId), update_args: dict) -> ObjectId:
        """
        修改工作经历,在修改工作经历的后,进行一下字段的更新:
        1. work_history 工作经历列表
        2. last_company 最后工作过的公司
        3. first_work_date 最早的工作开始时间
        4. end_work_date 最后的工作截至时间

        :param resume_id:
        :param work_id:  工作经历的id
        :param update_args:  update字典
        :return: ObjectId, WorkHistory._id
        """
        res = None
        work = WorkHistory.find_by_id(o_id=work_id, to_dict=True)
        resume = cls.find_by_id(o_id=resume_id, to_dict=True)
        if isinstance(work, dict) and isinstance(resume, dict):
            """开始事务操作"""
            work_id = work['_id']
            resume_id = resume['_id']
            update_args['driver_id'] = resume_id
            client = mongo_db2.get_client()
            handler1 = client[mongo_db2.db_name][WorkHistory.get_table_name()]
            handler2 = client[mongo_db2.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    f = {"driver_id": resume_id}
                    s = [("begin", -1)]
                    ws = handler1.find(filter=f, sort=s)
                    ws = [x for x in ws]
                    if work_id not in [x['_id'] for x in ws]:
                        ms = "非本简历的工作经历! id:{}".format(work_id)
                        logger.exception(msg=ms)
                        raise ValueError(ms)
                    else:
                        r = None
                        try:
                            f = {"_id": work_id}
                            u = {"$set": update_args}
                            r = handler1.update_one(filter=f, update=u, session=ses)
                        except Exception as e:
                            ms = "修改工作经历失败:{}".format(str(e))
                            logger.exception(msg=ms)
                            ses.abort_transaction()
                        match_count = r.matched_count if isinstance(r, UpdateResult) else r
                        if match_count == 1:
                            """
                            确认是否更新last_company,first_work_date,end_work_date三个字段
                            """
                            u = {"$set": {}}
                            last_company = resume.get("last_company", "")
                            first_work_date = resume.get("first_work_date", None)
                            end_work_date = resume.get("end_work_date", None)

                            # ws.append(work)  # 更新工作建立不需要这个操作
                            u['$set'] = {"work_history": [x['_id'] for x in ws]}
                            if len(ws) == 0:
                                unset = {"last_company": "", "first_work_date": "", "end_work_date": ""}
                                u['$unset'] = unset
                            else:
                                end_work_date2 = ws[0].get('end')
                                if end_work_date2 != end_work_date:
                                    set_d = u['$set']
                                    set_d['end_work_date'] = end_work_date2
                                    u['$set'] = set_d
                                last_company2 = ws[0].get('enterprise_name')
                                if last_company2 != last_company:
                                    set_d = u['$set']
                                    set_d['last_company'] = last_company2
                                    u['$set'] = set_d
                                first_work_date2 = ws[-1].get('begin')
                                if first_work_date2 != first_work_date:
                                    set_d = u['$set']
                                    set_d['first_work_date'] = first_work_date2
                                    u['$set'] = set_d
                            """更新简历"""
                            f = {"_id": resume_id}
                            handler2.update_one(filter=f, update=u, upsert=False, session=ses)
                            res = work_id
                        else:
                            ms = "事务错误: resume_id: {}, history_args: {}".format(resume_id, update_args)
                            logger.exception(msg=ms)
                            raise ValueError(ms)
        else:
            ms = "参数错误: resume_id: {}, history_args: {}".format(resume_id, update_args)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return res

    @classmethod
    def delete_work_history(cls, resume_id: (str, ObjectId), work_id: (str, ObjectId)) -> ObjectId:
        """
        删除工作经历,在删除工作经历的后,进行一下字段的更新:
        1. work_history 工作经历列表
        2. last_company 最后工作过的公司
        3. first_work_date 最早的工作开始时间
        4. end_work_date 最后的工作截至时间

        :param resume_id:
        :param work_id:  工作经历的id
        :return: ObjectId, WorkHistory._id
        """
        res = None
        work = WorkHistory.find_by_id(o_id=work_id, to_dict=True)
        resume = cls.find_by_id(o_id=resume_id, to_dict=True)
        if isinstance(work, dict) and isinstance(resume, dict):
            """开始事务操作"""
            work_id = work['_id']
            resume_id = resume['_id']
            client = mongo_db2.get_client()
            handler1 = client[mongo_db2.db_name][WorkHistory.get_table_name()]
            handler2 = client[mongo_db2.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    f = {"driver_id": resume_id}
                    s = [("begin", -1)]
                    ws = handler1.find(filter=f, sort=s)
                    ws = [x for x in ws]
                    if work_id not in [x['_id'] for x in ws]:
                        ms = "非本简历的工作经历! id:{}".format(work_id)
                        logger.exception(msg=ms)
                        raise ValueError(ms)
                    else:
                        r = None
                        try:
                            f = {"_id": work_id}
                            r = handler1.delete_one(filter=f, session=ses)
                        except Exception as e:
                            ms = "插入工作经历失败:{}".format(str(e))
                            logger.exception(msg=ms)
                            ses.abort_transaction()
                        deleted_count = r.deleted_count if isinstance(r, DeleteResult) else r
                        if deleted_count == 1:
                            ws = [x for x in ws if x['_id'] != work_id]
                            """
                            确认是否更新last_company,first_work_date,end_work_date三个字段
                            """
                            u = {"$set": {}}
                            last_company = resume.get("last_company", "")
                            first_work_date = resume.get("first_work_date", None)
                            end_work_date = resume.get("end_work_date", None)
                            u['$set'] = {"work_history": [x['_id'] for x in ws]}
                            if len(ws) == 0:
                                unset = {"last_company": "", "first_work_date": "", "end_work_date": ""}
                                u['$unset'] = unset
                            else:
                                end_work_date2 = ws[0].get('end')
                                if end_work_date2 != end_work_date:
                                    set_d = u['$set']
                                    set_d['end_work_date'] = end_work_date2
                                    u['$set'] = set_d
                                last_company2 = ws[0].get('enterprise_name')
                                if last_company2 != last_company:
                                    set_d = u['$set']
                                    set_d['last_company'] = last_company2
                                    u['$set'] = set_d
                                first_work_date2 = ws[-1].get('begin')
                                if first_work_date2 != first_work_date:
                                    set_d = u['$set']
                                    set_d['first_work_date'] = first_work_date2
                                    u['$set'] = set_d
                            """更新简历"""
                            f = {"_id": resume_id}
                            handler2.update_one(filter=f, update=u, upsert=False, session=ses)
                            res = work_id
                        else:
                            ms = "事务错误: resume_id: {}, work_id: {}".format(resume_id, work_id)
                            logger.exception(msg=ms)
                            raise ValueError(ms)
        else:
            ms = "参数错误: resume_id: {}, work_id: {}".format(resume_id, work_id)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return res

    @classmethod
    def add_education(cls, resume_id: (str, ObjectId), init_args: dict) -> ObjectId:
        """
        添加教育经历
        :param resume_id:
        :param init_args:  Education的init字典
        :return: ObjectId, Education._id
        """
        res = None
        education = Education(**init_args).get_dict()
        resume = cls.find_by_id(o_id=resume_id, to_dict=True)
        if isinstance(education, dict) and isinstance(resume, dict):
            """开始事务操作"""
            resume_id = resume['_id']
            driver_id = education.get("driver_id", "")
            if isinstance(driver_id, str) and len(driver_id) == 24:
                driver_id = ObjectId(driver_id)
            elif isinstance(driver_id, ObjectId):
                pass
            else:
                driver_id = resume_id
            education['driver_id'] = driver_id
            client = mongo_db2.get_client()
            handler1 = client[mongo_db2.db_name][Education.get_table_name()]
            handler2 = client[mongo_db2.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    r = None
                    try:
                        r = handler1.insert_one(document=education, session=ses)
                    except Exception as e:
                        ms = "插入教育经历失败:{}".format(str(e))
                        logger.exception(msg=ms)
                        ses.abort_transaction()
                    e_id = r.inserted_id if isinstance(r, InsertOneResult) else r
                    if isinstance(e_id, ObjectId):
                        """
                        更新education_history字段
                        """
                        u = dict()
                        f = {"driver_id": resume_id}
                        ws = handler1.find(filter=f)
                        ws = [x for x in ws]
                        ws.append(education)
                        u['$set'] = {"education_history": [x['_id'] for x in ws]}
                        """更新简历"""
                        f = {"_id": resume_id}
                        handler2.update_one(filter=f, update=u, upsert=False, session=ses)
                        res = work_id
                    else:
                        ms = "事务错误: resume_id: {}, init_args: {}".format(resume_id, init_args)
                        logger.exception(msg=ms)
                        raise ValueError(ms)
        else:
            ms = "参数错误: resume_id: {}, init_args: {}".format(resume_id, init_args)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return res

    @classmethod
    def update_education(cls, resume_id: (str, ObjectId), e_id: (str, ObjectId), update_args: dict) -> ObjectId:
        """
        修改教育经历

        :param resume_id:
        :param e_id:  教育经历的id
        :param update_args:  update字典
        :return: ObjectId, Education._id
        """
        res = None
        education = Education.find_by_id(o_id=e_id, to_dict=True)
        resume = cls.find_by_id(o_id=resume_id, to_dict=True)
        if isinstance(education, dict) and isinstance(resume, dict):
            """开始事务操作"""
            e_id = education['_id']
            resume_id = resume['_id']
            update_args['driver_id'] = resume_id
            client = mongo_db2.get_client()
            handler1 = client[mongo_db2.db_name][Education.get_table_name()]
            handler2 = client[mongo_db2.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    f = {"driver_id": resume_id}
                    ws = handler1.find(filter=f)
                    ws = [x for x in ws]
                    if e_id not in [x['_id'] for x in ws]:
                        ms = "非本简历的教育经历! id:{}".format(e_id)
                        logger.exception(msg=ms)
                        raise ValueError(ms)
                    else:
                        r = None
                        try:
                            f = {"_id": e_id}
                            u = {"$set": update_args}
                            r = handler1.update_one(filter=f, update=u, session=ses)
                        except Exception as e:
                            ms = "修改教育经历失败:{}".format(str(e))
                            logger.exception(msg=ms)
                            ses.abort_transaction()
                        match_count = r.matched_count if isinstance(r, UpdateResult) else r
                        if match_count == 1:
                            res = e_id
                        else:
                            ms = "事务错误: resume_id: {}, e_id: {}, update_args: {}".format(resume_id, e_id, update_args)
                            logger.exception(msg=ms)
                            raise ValueError(ms)
        else:
            ms = "参数错误: resume_id: {}, e_id:{}, update_args: {}".format(resume_id, e_id, update_args)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return res

    @classmethod
    def delete_education(cls, resume_id: (str, ObjectId), e_id: (str, ObjectId)) -> ObjectId:
        """
        删除教育经历

        :param resume_id:
        :param e_id:  教育经历的id
        :return: ObjectId, Education._id
        """
        res = None
        education = Education.find_by_id(o_id=e_id, to_dict=True)
        resume = cls.find_by_id(o_id=resume_id, to_dict=True)
        if isinstance(education, dict) and isinstance(resume, dict):
            """开始事务操作"""
            e_id = education['_id']
            resume_id = resume['_id']
            client = mongo_db2.get_client()
            handler1 = client[mongo_db2.db_name][Education.get_table_name()]
            handler2 = client[mongo_db2.db_name][cls.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    f = {"driver_id": resume_id}
                    ws = handler1.find(filter=f)
                    ws = [x for x in ws]
                    if e_id not in [x['_id'] for x in ws]:
                        ms = "非本简历的教育经历! id:{}".format(e_id)
                        logger.exception(msg=ms)
                        raise ValueError(ms)
                    else:
                        r = None
                        try:
                            f = {"_id": e_id}
                            r = handler1.delete_one(filter=f, session=ses)
                        except Exception as e:
                            ms = "删除教育经历失败:{}".format(str(e))
                            logger.exception(msg=ms)
                            ses.abort_transaction()
                        deleted_count = r.deleted_count if isinstance(r, DeleteResult) else r
                        if deleted_count == 1:
                            ws = [x['_id'] for x in ws if x['_id'] != e_id]
                            """
                            更新education_history字段
                            """
                            u = dict()
                            u['$set'] = {"education_history": ws}
                            """更新简历"""
                            f = {"_id": resume_id}
                            handler2.update_one(filter=f, update=u, upsert=False, session=ses)
                            res = e_id
                        else:
                            ms = "事务错误: resume_id: {},e_id: {}".format(resume_id,e_id)
                            logger.exception(msg=ms)
                            raise ValueError(ms)
        else:
            ms = "参数错误: resume_id: {}, e_id: {}".format(resume_id, e_id)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return res


if __name__ == "__main__":
    """查询省和直辖市"""
    # print(Region.get_province())
    # a = Region.get_city(province_code=864)
    # print(a)
    """添加简历"""
    args = {"_id": ObjectId("5b5969df99e87f46d93c1c13")}
    work_id = ObjectId("5b597b6099e87f5219329c45")
    args = {
        "begin": "2016-1-1",
        "end": "2017-1-1",
        "enterprise_name": "BBB公司"
    }
    DriverResume.delete_work_history(resume_id="5b3da7d84660d33df4a40a81", work_id=work_id)
    pass




