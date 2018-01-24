# -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(os.path.split(sys.path[0])[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
import requests
from log_module import get_logger
from mongo_db import cache
from haversine import haversine
import re
import math
from error_module import ApiQueryError
import datetime
from openpyxl import load_workbook
from werkzeug.contrib.cache import RedisCache
from mail_module import send_warning_email


"""高德地图相关模块"""


app_key = "d60786b02c43f787a14dba10fe283680"
# app_key = "9883bdeef04ef5ef45ca1cbb028e0997"  # 企业版的
cache = RedisCache()
logger = get_logger()


def get_position_by_ip(ip: str = None) -> list:
    """
    使用高德地图通过ip地址定位城市经纬度的中心位置。
    :param ip: ip地址。
    :return: 成功返回经纬度组成的数组，失败返回北京市的经纬度坐标
    """
    url = "http://restapi.amap.com/v3/ip"
    params = {"key": app_key, "output": "JSON"}
    if ip is not None:
        params['ip'] = ip
    res = [121.4737000000, 31.2303700000]
    try:
        r = requests.get(url=url, params=params)
        if r.status_code == 200:
            data = r.json()
            if str(data['status']) == "1":
                a_str = data['rectangle']
                xx = [x.split(",") for x in a_str.split(";")]
                data = list()
                flag = True
                for x in xx:
                    if isinstance(x, list):
                        temp_list = list()
                        for y in x:
                            try:
                                temp = float(y)
                                temp_list.append(temp)
                            except ValueError as e:
                                print(e)
                                flag = False
                                break
                        data.append(temp_list)
                    else:
                        flag = False
                        break
                if flag:
                    """可以计算坐标了"""
                    longitude = data[0][0] + (data[1][0] - data[0][0]) / 2  # 经度
                    latitude = data[0][1] + (data[1][1] - data[0][1]) / 2  # 维度
                    res = [longitude, latitude]
            else:
                pass
        else:
            pass
    except Exception as e:
        print(e)
        logger.Error("AMap Error", exc_info=True, stack_info=True)
    finally:
        return res


def get_position_by_address(city: str, address_str: str, real_val: bool = True) -> list:
    """
    通过高德地图的接口，利用地址来定位经纬度。
    :param city: 地址，城市名
    :param address_str: 地址，比如xxx路多少号
    :param real_val: 是否是真实结果
    :return: 经纬度组成的数组和真实性判定
    """
    url = "http://restapi.amap.com/v3/place/text"
    params = {"key": app_key, "keywords": address_str}
    r = requests.get(url, params=params)
    data = []
    if r.status_code == 200:
        res = r.json()
        try:
            data = res['pois'][0]['location'].split(",")
        except IndexError as e:
            print(e)
            logger.error("没有查询到对应的经纬度", exc_info=True, stack_info=True)
            if real_val:
                data, real_val = get_position_by_address(city, "{}政府".format(city), False)
            else:
                data, real_val = [0, 0], False

    else:
        logger.error("get_position_by_address Error: return code {}".format(r.status_code))
    return data, real_val


def query_geo_coordinate(**kwargs):
    """
    查询经纬度的接口，和上面的方法不同，此方法直接暴露给查询接口
    :param arg:city 城市名
    :param kwargs:address 地址字符串
    :return: doc或者none
    """
    city = kwargs['city']
    address = kwargs['address']
    key = "query_geo_coordinate_{}_{}".format(city, address)  # 缓存标识
    if cache.get(key) is None:
        position_data, real = get_position_by_address(city=city, address_str=address)
        cache.delete(key)
        args = {"address": address, "city": city, "real_value": real,
                "longitude": position_data[0], "latitude": position_data[1]}
        return args
    else:
        return None


def coordinate_convert(pos: (list, tuple), sys_type: str = "gps")->list:
    """
    坐标系转换。各大地图厂家的坐标系都经过加密，也就是位置点都经过非线性便宜。如果不进行转换直接使用的话，会
    出现定位漂移的现象。这个方法是转换成高德地图使用的坐标系的。
    :param pos: [经度, 纬度] 位置点的信息，[]或者元组，一般是硬件坐标系。
    :param sys_type: 坐标系类型，默认是gps，由硬件设备采集的坐标信息
    :return: 数组  [经度, 纬度]
    """
    """先统一为经度在前的WGS84标准"""
    if pos[0] > pos[1]:
        pass
    else:
        pos = pos[-1::-1]
    url = "http://restapi.amap.com/v3/assistant/coordinate/convert"
    params = {"key": app_key, "locations": ",".join([str(x) for x in pos]), "coordsys": sys_type}
    r = requests.get(url, params=params)
    if r.status_code == 200 and str(r.json()['status']) == "1":
        return r.json()['locations']
    else:
        raise ApiQueryError("接口查询错误")


def decimal_to_degree(raw: float) -> list:
    """
    把小数表示的经纬度转换为度数表示的经纬度。
    一般来说，小数表示法方便计算，度数表示法方便阅读。
    raw   小数表示的经纬度,浮点或者字符串
    return 度数表示的经纬度的元组，(度, 分, 秒)
    """
    deg, cent, sec = None, None, None
    raw = float(raw)
    deg = math.floor(raw)  # 取度数
    if raw != deg:
        dec = str(raw - deg)
        cent = float(dec[:4]) * 60  # 取分数
        if len(dec) > 4:
            """证明还有秒的部分"""
            sec = round(float("0.{}".format(dec[4:])) * 60, 4) # 取秒数
    res = (deg if deg is not None else 0,
           cent if cent is not None else 0,
           sec if sec is not None else 0)
    return res


def degree_to_decimal(raw: str) -> float:
    """
    把度分秒表示的经纬度转换为小数表示的经纬度。
    一般来说，小数表示法方便计算，度数表示法方便阅读。
    raw   度数表示的经纬度
    return 小数表示的经纬度,浮点或者字符串
    """
    """获取度"""
    sep_01 = re.search('\D+', raw)
    if sep_01 is None:
        raise KeyError("转换失败，没有找到合法的字符串:{}".format(raw))
    else:
        deg, raw_02 = raw.split(sep_01.group(), 1)
        sep_02 = re.search('\D+', raw_02)
        if sep_02 is None:
            raise KeyError("转换失败，没有找到合法的字符串:{}".format(raw))
        else:
            cent, raw_03 = raw_02.split(sep_02.group(), 1)
            sep_03 = re.search('\D+', raw_03)
            if sep_03 is None:
                raise KeyError("转换失败，没有找到合法的字符串:{}".format(raw))
            else:
                sec = raw_03.split(sep_03.group(), 1)[0]
    num = (float(sec) / 60 + float(cent)) / 60 + float(deg)
    return num


def position_distance(pos_01: (list, tuple), pos_02: (list, tuple), miles: bool = False) -> float:
    """
    利用haversine（半正矢）算法计算两个点之间的距离，haversine计算的时候是纬度在前经度在后的纬度,经度）。
    :param pos_01: [经度,纬度]数组或者元组表示的坐标
    :param pos_02: [经度,纬度]数组或者元组表示的坐标，
    :param miles: 是否以英里计算距离？默认值是False，以公里计算距离。
    :return: 两点之间的距离，以千米或者英里为单位。
    """
    """先统一为经度在前的WGS84标准"""
    if pos_01[0] > pos_01[1]:
        pass
    else:
        pos_01 = pos_01[-1::-1]
    if pos_02[0] > pos_02[1]:
        pass
    else:
        pos_02 = pos_02[-1::-1]
    """这个算法求距离是经度在后的"""
    pos_01 = pos_01[-1::-1]
    pos_02 = pos_02[-1::-1]
    res = haversine(pos_01, pos_02, miles=miles)
    return res


def get_info_by_position(pos: (list, tuple)) -> dict:
    """
    利用经纬度查询adcode等信息
    :param pos: 经纬度 ,经度在前,纬度在后.
    :return: 各种信息的字典
    {
     'address': '江苏省苏州市昆山市花桥镇光明路建滔广场',
     'city_code': '0512',
     'city': '苏州市',
     'province': '江苏省',
     'country': '中国',
     'district': '昆山市',
     'township': '花桥镇',
     'ad_code': '320583'
     }
    """
    remote_url = "http://restapi.amap.com/v3/geocode/regeo"
    args = {"location": ",".join([str(x) for x in pos]), "key": app_key}
    r = requests.get(remote_url, params=args)
    if r.status_code == 200:
        res = r.json()
        status = res['status']
        info = res['info']
        if info.lower() == "ok" and status == "1":
            re_geo_dict = res['regeocode']
            address = re_geo_dict['formatted_address']  # 地址
            address_component = re_geo_dict['addressComponent']
            province = address_component.get("province")  # 省份/直辖市
            ad_code = address_component.get("adcode")  # adcode码
            city = address_component.get("city")  # 城市/地级市
            city_code = address_component.get("citycode")  # 城市码/电话区号
            country = address_component.get("country")  # 国家
            district = address_component.get("district")  # 区/县级市
            township = address_component.get("township")  # 镇
            res_dict = {
                "address": address, 'province': province,
                'ad_code': ad_code, "city": city,
                "city_code": city_code, "country": country,
                "district": district, "township": township
                        }
            res_dict = {k: v for k, v in res_dict.items() if v is not None and len(v) != 0}
            return res_dict

        else:
            ms = "利用经纬度查询adcode信息返回错误的信息,info:{},status:{}".format(info, status)
            logger.exception(ms)
            print(ms)
    else:
        ms = "get_adcode_by_position Error, args:{}.,status_code:{}".format(pos, r.status_code)
        logger.exception(ms)
        print(ms)
        send_warning_email("根据经纬度查询adcode失败", ms)


def get_weather_by_ad_code(code: (int, float, str), forecast: bool = False) -> dict:
    """
    根据城市的ad_code查询天气
    :param code: 城市的adcode/ad_code,
    :param forecast: 是预报还是当时的实况天气?默认是实况天气
    :return: 返回天气的字典.注意实时天气和天气预报的返回格式的不同.
    查询实时天气:
    {
    'city': '萧山区',
    'report_time': '2017-11-07 18:00:00',
    'win_direction': '东南', 'weather': '多云',
    'humidity': '79',
    'temperature': '18',
    'province': '浙江'
    }
    查询天气预报:
    {
    'report_time': '2017-11-07 18:00:00',
    'province': '浙江',
    'city': '萧山区',
    'weathers': [
                {
                'day_temperature': '20',
                'night_weather': '阴',
                'night_temperature': '13',
                'day_wind_direction': '北',
                'day_wind_power': '≤3',
                'night_wind_direction': '北',
                'date': '2017-11-07',
                'day_weather': '小雨',
                'week': '2',
                'night_wind_power': '≤3'
                },
                {
                'day_temperature': '21',
                'night_weather': '晴',
                'night_temperature': '12',
                'day_wind_direction': '东北',
                'day_wind_power': '≤3',
                'night_wind_direction': '东北',
                'date': '2017-11-08',
                'day_weather': '多云',
                'week': '3',
                'night_wind_power': '≤3'
                },
                ....]}
    """
    remote_url = "http://restapi.amap.com/v3/weather/weatherInfo"
    if code is None:
        ms = "ad_code参数不能为空"
        logger.exception(ms)
        raise ValueError(ms)
    elif isinstance(code, (int, float)):
        code = str(code if isinstance(code, int) else int(code))
    else:
        pass
    extensions = "all" if forecast else "base"
    args = {"city": code, "key": app_key, "extensions": extensions}
    r = requests.get(remote_url, params=args)  # 查询必须用get方法.
    if r.status_code == 200:
        res = r.json()
        status = res['status']
        info = res['info']
        if info.lower() == "ok" and status == "1":
            result = dict()
            if extensions == "base":
                """查询实时天气"""
                if len(res['lives']) == 0:  # 没有查询到天气
                    pass
                else:
                    info = res['lives'][0]  # 信息字典
                    city = info.get("city")  # 城市
                    humidity = info.get("humidity")  # 湿度
                    province = info.get("province")  # 省份
                    temperature = info.get("temperature")  # 温度
                    weather = info.get("weather")  # 天气描述
                    win_direction = info.get("winddirection")  # 风向
                    win_power = info.get("winpower")  # 风力  实时预报风力偏差过大
                    report_time = info.get("reporttime")  # 发布时间
                    result = {
                        "humidity": humidity, 'province': province,
                        'temperature': temperature, "city": city,
                        "weather": weather, "win_direction": win_direction,
                        "report_time": report_time, "win_power": win_power
                    }
                    result = {k: v for k, v in result.items() if v is not None and len(v) != 0}
            else:
                """查询天气预报"""
                info_dict = res['forecasts'][0]
                casts = info_dict['casts']
                if len(casts) == 0:  # 没有查询到天气预报
                    pass
                else:
                    province = info_dict.get("province")  # 省份
                    city = info_dict.get("city")  # 城市
                    report_time = info_dict.get("reporttime")  # 发布时间
                    result = {"city": city, "province": province, "report_time": report_time}
                    weathers = list()
                    for cast in casts:
                        date = cast.get("date")  # 预报日期
                        day_wind_power = cast.get("daypower")  # 白天风力
                        day_temperature = cast.get("daytemp")  # 白天温度
                        day_weather = cast.get("dayweather")  # 白天天气
                        day_wind_direction = cast.get("daywind")  # 白天风向
                        night_wind_power = cast.get("nightpower")  # 夜晚风力
                        night_temperature = cast.get("nighttemp")  # 夜晚温度
                        night_weather = cast.get("nightweather")  # 夜晚天气
                        night_wind_direction = cast.get("nightwind")  # 夜晚风向
                        week = cast.get("week")  # 星期几
                        weather = {
                            "date": date, "day_wind_power": day_wind_power,
                            'day_temperature': day_temperature, "day_weather": day_weather,
                            'day_wind_direction': day_wind_direction, "night_wind_power": night_wind_power,
                            "night_temperature": night_temperature, "night_weather": night_weather,
                            "night_wind_direction": night_wind_direction, "week": week
                        }
                        weather = {k: v for k, v in weather.items() if v is not None and len(v) != 0}
                        weathers.append(weather)
                    weathers.sort(key=lambda obj: datetime.datetime.strptime(obj['date'], "%Y-%m-%d"))
                    result['weathers'] = weathers
            return result

        else:
            ms = "根据城市的ad_code查询天气返回错误的信息,info:{},status:{}".format(info, status)
            logger.exception(ms)
            print(ms)
    else:
        ms = "get_weather_by_ad_code Error, args:{}.,status_code:{}".format(code, r.status_code)
        logger.exception(ms)
        print(ms)
        send_warning_email("根据城市的ad_code查询天气", ms)


def get_district_info(keywords: str) -> dict:
    """
    查询城市行政区域信息,现阶段只返回城市中心位置.
    :param keywords: 城市名称或者adcode
    :return: 信息字典
    """
    url = "http://restapi.amap.com/v3/config/district"
    args = {"key": app_key, "keywords": keywords}
    r = requests.get(url, params=args)
    res = r.json()
    """城市中心r.json()['districts'][0]['center']"""
    center = r.json()['districts'][0]['center']
    center = dict(zip(["lng", "lat"], center.split(",")))
    return center


class AMapAdCode:
    """用于查询高德地图adcode和城市名称的映射关系的类
        暂时停用.
    """
    def __init__(self):
        key = "amap_adcode"
        ad_codes = cache.get(key)
        if ad_codes is None:
            pass

    @staticmethod
    def read_xlsx():
        """读取adcode文件"""
        adcode_dir = os.path.join(os.sys.path[0], "resources", "amap_adcode")
        file_name = os.listdir(adcode_dir)[0]
        file_path = os.path.join(adcode_dir, file_name)
        wb = load_workbook(file_path)
        print(wb)


    @staticmethod
    def check_update():
        """
        检查adcode的版本更新,如果有更新,那就发送一封邮件提醒更新.
        管理员需要把从http://lbs.amap.com/api/webservice/download/ 把文件下载下来,
        然后把文件以 "高德地图API城市编码表_2017-08-10.xlsx"方式命名后,存在在resources/amap_adcode目录下.
        :return:
        """
        page_url = "http://lbs.amap.com/api/webservice/download/"
        try:
            r = requests.get(page_url)
            r.encoding = "utf-8"
            html = r.text
            content = html.split("城市编码表", 1)[-1]
            pattern = re.compile(r'更新于2\d{3}年[01]?\d月[0-3]?\d日')
            res = pattern.search(content)
            temp = res.group()
            temp1, temp2 = temp.split("年", 1)
            pattern2 = re.compile(r'2\d{3}')
            year = pattern2.search(temp1).group()
            month, temp3 = temp2.split("月", 1)
            day = temp3.split("日", 1)[0]
            date_str = "{}-{}-{}".format(year, month, day)
            remote_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            adcode_dir = os.path.join(os.sys.path[0], "resources", "amap_adcode")
            file_name = os.listdir(adcode_dir)[0]
            last_date_str = file_name.split("高德地图API城市编码表_", 1)[-1].split(".xlsx")[0]
            last_date = datetime.datetime.strptime(last_date_str, "%Y-%m-%d")
            if last_date == remote_date:
                pass
            else:
                title = "高德地图adcode文件更新"
                content = "高德地图的最新版adcode于{}更新,请前往 {} 下载".format(date_str, page_url)
                interval = 60 * 60 * 24
                send_warning_email(title, content, interval)
        except Exception as e:
            print(e)
            logger.exception(e)
            title = "高德地图更新页面打开失败"
            content = "url:{} 打开失败,错误:{}".format(page_url, e)
            interval = 60 * 60 * 24
            send_warning_email(title, content, interval)


def scale_mileage(begin: (list, tuple), end: (list, tuple)) -> float:
    """
    根据两个坐标点计算他们之间的路程数字,单位公里,注意,不是距离,路程可能会因为时间变迁,道路改变而返回不同的结果.
    :param begin: 起点坐标,经度在前,纬度在后.
    :param end: 终点坐标,经度在前,纬度在后.
    :return: 里程数字,单位公里.
    华新镇到萧山机场的距离计算的是167公里,和网上的基本一致
    """
    begin = [str(x) for x in begin]
    end = [str(x) for x in end]
    begin = ",".join(begin)
    end = ",".join(end)
    url = "http://restapi.amap.com/v3/distance"
    params = {
        "key": app_key,
        "origins": begin,
        "destination": end,
    }
    r = requests.get(url, params=params)
    res = r.json()
    results = res['results']  # 因为可能会有多个路线,所以查询路程可能会返回多个结果
    print(results)
    return round(float(results[0]['distance']) / 1000, 3)


if __name__ == "__main__":
    print(scale_mileage([120.44536946614583, 30.240664333767363],[121.29519368489584, 31.213871527777776]))
    pass

