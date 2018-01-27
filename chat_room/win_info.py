# -*- coding:utf-8 -*-
# 生成虚拟的客户盈利信息，返回数组形式的字典[{'Sex': '女士', 'Tname': '张老师', 'Cname': '海口', 'Uname': '包', 'Money': '59900'}，...]
__author__ = 'Administrator'
import time, random, db_module


# 返回数据库连接
def get_conn():
    flag = True
    while flag:
        try:
            conn = my_sql.get_conn()
            flag = False
        except:
            flag = True
            time.sleep(3)
    return conn


# 查询数据库中大户室老师的名字，返回名字组成的数组
def get_teacher_list():
    result = []
    ses = db_module.sql_session()
    sql = "select t_nickname from teacherinfo where t_nickname!='范老师' and t_nickname!='华澜之家'"
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    if len(raw) == 0:
        result =['大山老师']
    else:
        result = [x[0] for x in raw]
    ses.close()
    return result


# 随机选择姓氏
def get_family_name():
    family_names = '''赵钱孙李周吴郑王冯陈卫蒋沈韩杨朱秦许何林吕徐江张张孔严华程黄李周吴郑李王窦章蔡田胡霍万卢丁邓洪包仇刘白'''
    return random.choice(family_names)


# 随机性别
def get_sex():
    rand_sex = random.random()
    if rand_sex < 0.5:
        return '先生'
    elif rand_sex < 0.8:
        return '女士'
    else:
        return '小姐'


# 随机选择地区
def get_area():
    area = ['上海', '北京', '深圳', '广州', '苏州', '杭州', '天津', '宁波', '南京', '温州', '大连', '青岛', '厦门', '无锡', '济南', '珠海', '常州', '重庆',
            '成都', '西安', '武汉', '长春', '长沙', '沈阳', '烟台', '南通', '哈尔滨', '合肥', '南昌', '秦皇岛', '郑州', '福州', '呼和浩特', '石家庄', '乌鲁木齐',
            '南宁', '贵阳', '扬州', '桂林', '昆明', '海口', '太原', '洛阳', '兰州', '连云港', '湛江', '齐齐哈尔', '开封', '汕头']
    return random.choice(area)


# 随机生成盈利额
def get_money():
    money = int(random.normalvariate(450, 200))
    if money < 50:
        money = random.randint(200, 600)
    elif money > 1000:
        money = random.randint(200, 600)
    return money * 100


# 随机选择老师
T_list = []  # 全局变量，存储老师的名字


def get_teacher():
    global T_list
    if len(T_list) == 0:
        T_list = get_teacher_list()
    else:
        pass
    return random.choice(T_list)


# 生成虚拟盈利信息
def create_info(count=8):
    lis = []
    global result
    for i in range(0, count):
        lis.append({"Cname": get_area(), "Uname": get_family_name(), "Tname": get_teacher(), "Money": str(get_money()),
                    "Sex": get_sex()})
    # print(lis)
    result = {"message": "success", "data": lis}
    return result
