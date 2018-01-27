from api.data.item_module import GPS, GeoJSON
from mongo_db import get_conn
from amap_module import app_key
import requests
from log_module import get_logger
from tools_module import expand_list


logger = get_logger()


def repair_gps():
    """修整gps数据"""
    obj_list = GPS.find()
    ses = get_conn(GPS.get_table_name())
    for obj in obj_list:
        geo = obj.__dict__.get("geo")
        if geo is not None:
            oid = obj.get_id()
            geo = obj.geo
            loc = GeoJSON("Point", geo)
            obj.__dict__.pop("geo")
            obj.__dict__['loc'] = loc
            doc = obj.to_flat_dict()
            doc.pop("_id")
            ses.find_one_and_replace(filter={"_id": oid}, replacement=doc)


def create_demo_path(begin_pos: (list, tuple) = None, end_pos: (list, tuple) = None, simple: bool = True) -> list:
    """
    创建用于测试的数据
    :param begin_pos: 开始地点的坐标，[经度, 纬度]
    :param end_pos: 结束地点的坐标，[经度, 纬度]
    :param simple: 是否减少节点数优化性能？
    :return: 路径的数组
    """
    url = "http://restapi.amap.com/v3/direction/driving"  # 驾车路径规划
    origin = ",".join([str(x) for x in begin_pos])
    destination = ",".join([str(x) for x in end_pos])
    """
    下方策略 0~9的策略，仅会返回一条路径规划结果。 
    下方10~20的策略，会返回多条路径规划结果。（高德地图APP策略也包含在内）
       
    下方策略仅返回一条路径规划结果
    
    0，不考虑当时路况，返回耗时最短的路线，但是此路线不一定距离最短   
    1，不走收费路段，且耗时最少的路线   
    2，距离最短的路线，但是不会考虑路况  
    3，不走快速路，例如京通快速路  
    4，躲避拥堵的路线，但是可能会存在绕路的情况，耗时可能较长  
    5，多策略（同时使用速度优先、费用优先、距离优先三个策略计算路径）。   
    其中必须说明，就算使用三个策略算路，会根据路况不固定的返回一~三条路径规划信息。   
    6，不走高速，但是不排除走其余收费路段 
    7，不走高速且避免所有收费路段  
    8，躲避收费和拥堵，可能存在走高速的情况，并且考虑路况不走拥堵路线，但有可能存在绕路和时间较长   
    9，不走高速且躲避收费和拥堵
        
    下方策略返回多条路径规划结果
       
    10，返回结果会躲避拥堵，路程较短，尽量缩短时间  
    11，返回结果时间最短，距离最短 （由于有更优秀的算法，建议不使用此值）   
    12，返回的结果考虑路况，尽量躲避拥堵而规划路径，与高德地图的“躲避拥堵”策略一致    
    13，返回的结果不走高速，与高德地图“不走高速”策略一致    
    14，返回的结果尽可能规划收费较低甚至免费的路径，与高德地图“避免收费”策略一致   
    15，返回的结果考虑路况，尽量躲避拥堵而规划路径，并且不走高速，与高德地图的“躲避拥堵&不走高速”策略一致   
    16，返回的结果尽量不走高速，并且尽量规划收费较低甚至免费的路径结果，与高德地图的“避免收费&不走高速”策略一致    
    17，返回路径规划结果会尽量的躲避拥堵，并且规划收费较低甚至免费的路径结果，与高德地图的“躲避拥堵&避免收费”策略一致    
    18，返回的结果尽量躲避拥堵，规划收费较低甚至免费的路径结果，并且尽量不走高速路，与高德地图的“避免拥堵&避免收费&不走高速”策略一致   
    19，返回的结果会优先选择高速路，与高德地图的“高速优先”策略一致   
    20，返回的结果会优先考虑高速路，并且会考虑路况躲避拥堵，与高德地图的“躲避拥堵&高速优先”策略一致
    """
    strategy = 5
    params = {"key": app_key, "output": "JSON", "origin": origin, "destination": destination, "strategy": strategy}
    r = None
    message = {"message": "success"}
    try:
        r = requests.get(url, params=params)
    except Exception as e:
        logger.error("Amp Error:", exc_info=True, stack_info=True)
        raise e
    finally:
        if r is None:
            message['message'] = "连接失败，网络不可用"
        else:
            if r.status_code == 200:
                data = r.json()
                raw = [[y.split(",") for y in x['polyline'].split(";") if y.strip() != ''] for x in
                       data['route']['paths'][0]['steps']]
                data = list()
                for x in raw:
                    data.extend(x)
                if simple:
                    l = len(data)
                    per = 2  # 精简为原来的几分之一？
                    data = [x for i, x in enumerate(data) if i == 0 or i == l - 1 or i % per == 0]
                message['data'] = data
            else:
                message['message'] = "status_code {}".format(r.status_code)
        return message


if __name__ == "__main__":
    begin = [121.316674, 31.287422]
    end = [121.675421, 31.175273]
    print(create_demo_path(begin, end, True))