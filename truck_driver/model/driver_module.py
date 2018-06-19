#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import datetime


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


"""司机相关的模型"""


class Region(mongo_db.BaseDoc):
    """
    行政区域代码  http://cnis.7east.com/
    """
    _table_name = "region_info"
    type_dict = dict()
    type_dict['_id'] = str  # 行政区域数字码
    type_dict['name'] = str  # 名称
    type_dict['superior'] = str  # 上级行政区域数字码

    def __init__(self, **kwargs):
        if "superior" in kwargs:
            superior = kwargs.pop('superior')
            if isinstance(superior, str) and len(superior) == 6:
                kwargs['superior'] = superior
            else:
                pass
        super(Region, self).__init__(**kwargs)


class Route(mongo_db.BaseDoc):
    """
    (熟悉)线路类,注意,这个和保驾犬的TrafficRoute类不同.
    本例只是为了标记司机熟悉的城市线路.只要城市节点相同,不分顺序和来往,都是一条线路.
    """
    _table_name = "route_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['region_list'] = list  # Region._id组成的list
    type_dict['create_date'] = datetime.datetime  # 创建时间

    def __init__(self, **kwargs):
        if 'city_code_list' not in kwargs or 'city_name_list' not in kwargs:
            ms = "city_name_list和city_code_list都是必要参数"
            raise ValueError(ms)
        if len(kwargs['city_code_list']) == 0 or len(kwargs['city_name_list']) == 0:
            ms = "city_name_list和city_code_list长度不能为0"
            raise ValueError(ms)
        if len(kwargs['city_code_list']) != len(kwargs['city_name_list']):
            ms = "city_name_list和city_code_list长度不想等"
            raise ValueError(ms)
        if 'create_date' not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(TrafficRoute, self).__init__(**kwargs)


class VehicleLicense(mongo_db.BaseDoc):
    """
    行车证信息
    """
    _table_name = "vehicle_license_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict["license_image"] = bytes  # 车辆照片
    type_dict["plate_number"] = str  # 车辆号牌, 英文字母必须大写,允许空,不做唯一判定
    type_dict["vehicle_type"] = str  # 车辆类型  比如 重型箱式货车
    type_dict["owner_name"] = str  # 车主姓名/不一定是驾驶员
    type_dict["address"] = str  # 地址
    type_dict["use_character"] = str  # 使用性质
    type_dict["vehicle_model"] = str  # 车辆型号  比如 一汽解放J6
    type_dict["vin_id"] = str  # 车辆识别码/车架号的后六位 如果大于6未，查询违章的时候就用后6位查询
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
        super(VehicleLicense, self).__init__(**kwargs)


class Driver(mongo_db.BaseDoc):
    """司机"""
    _table_name = "driver_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str  # 用户名,唯一判定,默认和手机相同
    type_dict['gender'] = str   # 以驾驶证信息为准.
    type_dict['birth_place'] = str   # 籍贯/出生地
    type_dict['living_place'] = str   # 居住地
    type_dict['address'] = str  # 家庭地址
    type_dict['phone'] = str  # 手机号码
    type_dict['email'] = str  # 邮箱
    type_dict['birth_date'] = datetime.datetime  # 出生日期,以身份证号码为准
    type_dict['id_num'] = str  # 身份证号码
    type_dict['age'] = int  # 年龄 以身份证号码为准
    type_dict['driving_experience'] = int  # 驾龄 单位 年 用驾驶证信息中的首次领证日期计算
    type_dict['industry_experience'] = int  # 从业年限 单位 年 用道路运输从业资格证信息中的首次领证日期计算
    """
    学历分以下几种:
    1. 初等教育(小学及以下)
    2. 中等教育(中学,含初中,高中,职高,中专,技校)
    3. 高等教育(大专)
    4. 高等教育(本科及以上)
    """
    type_dict['education'] = int  # 学历,学历代码见注释
    type_dict['status'] = int  # 任职/经营 状态. -1 个体经营/0 离职/ 1 在职
    """驾驶证信息 Driving License,简称dl"""
    type_dict['dl_image'] = bytes  # 驾驶证信息,驾驶证照片,这里直接存储的是图片,注意大小不可太大.
    type_dict['dl_license_class'] = str  # 驾驶证信息.驾驶证类型,准驾车型
    type_dict['dl_first_date'] = datetime.datetime  # 驾驶证信息 首次领证日期
    type_dict['dl_valid_begin'] = datetime.datetime  # 驾驶证信息 驾照有效期的开始时间
    type_dict['dl_valid_duration'] = int  # 驾驶证信息 驾照有效持续期,单位年
    """道路运输从业资格证部分,Road transport qualification certificate 简称rtqc"""
    type_dict['rtqc_image'] = bytes  # 道路运输从业资格证信息,照片
    type_dict['rtqc_license_class'] = str  # 道路运输从业资格证信息.驾驶证类型,准驾车型
    type_dict['rtqc_first_date'] = datetime.datetime  # 道路运输从业资格证信息 首次领证日期,用于推定从业年限
    type_dict['rtqc_valid_begin'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的开始时间
    type_dict['rtqc_valid_end'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的结束时间
    """求职意愿"""
    type_dict['want_job'] = bool  # 是否有求职意向?有求职意向的才会推荐工作,可以认为这是个开关.
    type_dict['expected_regions'] = list()    # 期望工作地区,list是区域代码的list
    """
     期望待遇,2个int元素组成的数组.第一个元素表示待遇下限,第二个元素表示待遇上限.
     如果只有一个元素,则代表下限.
     如果没有元素,代表待遇面议.
     超过2个的元素会被抛弃.
     元素必须是int类型
    """
    type_dict['expected_salary'] = list()    # 期望待遇


