#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import requests
import datetime
import re


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


"""司机相关的模型"""


class Region(mongo_db.BaseDoc):
    """
    行政区域代码  http://cnis.7east.com/
    """
    _table_name = "region_info"
    type_dict = dict()
    type_dict['_id'] = int
    type_dict['name'] = str  # 名称
    type_dict['code'] = int  # 六位数字
    type_dict['region_path'] = str  # 六位数字,左右都有逗号
    type_dict['parent_id'] = int  # 上级行政区域_id 如果是顶层的,这个值是0

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


class Route(mongo_db.BaseDoc):
    """
    (熟悉)线路类,注意,这个和保驾犬的TrafficRoute类不同.
    本例只是为了标记司机熟悉的城市线路.只要城市节点相同,不分顺序和来往,都是一条线路.
    和简历是多对一的关系.
    """
    _table_name = "route_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['driver_id'] = DBRef  # 关键的(司机)简历的DBRef对象
    type_dict['cities'] = list  # 城市名称(str)组成的list
    type_dict['create_date'] = datetime.datetime  # 创建时间

    def __init__(self, **kwargs):
        if "region_list" not in kwargs:
            kwargs['region_list'] = list()
        if 'create_date' not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(Route, self).__init__(**kwargs)


class Honor(mongo_db.BaseDoc):
    """
    荣誉证书信息,和简历是多对一的关系.
    """
    _table_name = "honor_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = DBRef  # 关键的(司机)简历的DBRef对象
    type_dict['time'] = datetime.datetime  # 获奖时间
    type_dict['info'] = str    # 荣誉信息
    type_dict['image'] = bytes  # 荣誉图片
    type_dict['create_date'] = datetime.datetime  # 创建时间


class Vehicle(mongo_db.BaseDoc):
    """
    车辆信息,某些司机可能自己有车辆.
    与保驾犬不同,司机招聘网站的车辆信息和司机(简历)是多对一的关系
    """
    _table_name = "vehicle_license_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = DBRef  # 关键的(司机)简历的DBRef对象
    type_dict["image"] = bytes  # 车辆照片
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


class WorkHistory(mongo_db.BaseDoc):
    """
    工作经历,用于在简历中表示一段工作历史,
    和简历是多对一的关系
    """
    _table_name = "work_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = DBRef  # 关键的(司机)简历的DBRef对象
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime
    type_dict['enterprise_name'] = str  # 企业名称
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


class DriverResume(mongo_db.BaseDoc):
    """司机简历"""
    _table_name = "driver_resume"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str  # 用户名,唯一判定,默认和手机相同
    type_dict['real_name'] = str  # 真实姓名 ,可以从驾驶证取
    type_dict['gender'] = str   # 以驾驶证信息为准. 男/女
    type_dict['birth_place'] = str   # 籍贯/出生地
    type_dict['living_place'] = str   # 居住地,
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
    type_dict['rtqc_license_class'] = str  # 道路运输从业资格证信息.货物运输驾驶员/危险货物运输驾驶员
    type_dict['rtqc_first_date'] = datetime.datetime  # 道路运输从业资格证信息 首次领证日期,用于推定从业年限
    type_dict['rtqc_valid_begin'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的开始时间
    type_dict['rtqc_valid_end'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的结束时间
    """某些司机自己有车辆"""
    type_dict['vehicle'] = list  # 车辆信息, Vehicle.的DBRef对象
    """求职意愿"""
    type_dict['want_job'] = bool  # 是否有求职意向?有求职意向的才会推荐工作,可以认为这是个开关.
    type_dict['remote'] = bool  # 是否原因在外地工作?
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
    type_dict['routes'] = list  # 熟悉线路,Route的DBRef的list
    """工作履历部分,是WorkHistory.的DBRef的list对象"""
    type_dict['work_history'] = list
    type_dict['last_company'] = str  # 最后工作的公司,仅仅为列表页而添加
    type_dict['self_evaluation'] = str  # 自我评价
    """获奖/荣誉证书 Honor._id的list对象"""
    type_dict['honor'] = list
    type_dict['update_date'] = datetime.datetime  # 简历的刷新时间
    type_dict['create_date'] = datetime.datetime  # 简历的创建时间

    def __init__(self, **kwargs):
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
            birth_date = mongo_db.get_datetime_from_str(birth_date)
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
            bd = mongo_db.get_datetime_from_str("{}-{}-{}".format(y, m, d))
            kwargs['id_num'] = id_num
            kwargs['birth_date'] = bd
            kwargs['age'] = age
        else:
            pass
        dl_first_date = kwargs.pop("dl_first_date", None)  # 驾照首次申领日期
        if isinstance(dl_first_date, str):
            dl_first_date = mongo_db.get_datetime_from_str(dl_first_date)
            if isinstance(dl_first_date, datetime.datetime):
                kwargs['dl_first_date'] = dl_first_date
                driving_experience = now.year - dl_first_date.year
                kwargs['driving_experience'] = driving_experience
            else:
                pass
        else:
            pass
        rtqc_first_date = kwargs.pop("rtqc_first_date", None)  # 运输许可证首次申领日期
        if isinstance(rtqc_first_date, str):
            rtqc_first_date = mongo_db.get_datetime_from_str(rtqc_first_date)
            if isinstance(rtqc_first_date, datetime.datetime):
                kwargs['rtqc_first_date'] = rtqc_first_date
                industry_experience = now.year - rtqc_first_date.year
                kwargs['industry_experience'] = industry_experience
            else:
                pass
        else:
            pass
        super(DriverResume, self).__init__(**kwargs)

    @classmethod
    def add_work_history(cls, history_args):


if __name__ == "__main__":
    Region.get_dict()
    pass




