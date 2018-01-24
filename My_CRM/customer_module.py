# -*- coding:utf-8 -*-
import db_module
from plan_module import next_company_sn
from celery_module import bak_customer
import os
import xlwt
import datetime
from employee_module import Team

table_name = "customer_info"
columns = db_module.get_columns(table_name, True)
cache = db_module.cache
"""保存导出的excel文件的目录"""
EXCEL_PATH = os.path.join(os.path.split(__file__)[0], "static", "downloads", "excel")
if not os.path.exists(EXCEL_PATH):
    os.makedirs(EXCEL_PATH)

"""客户管理模块"""


def check_special_url(page_url):
    """检查是不是专属链接进来的，如果是，返回专属链接所属的公司的sn，否则返回0"""
    result = 0
    ses = db_module.sql_session()
    sql = "select url,company_sn from special_url_info where company_sn>0"
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        pass
    else:
        special_url_dict = {x[0]: x[1] for x in raw}
        for k, v in special_url_dict.items():
            if k in page_url:
                result = v
                break
            else:
                pass
    return result


def add_user(**kwargs):
    """添加用户"""
    kwargs['create_date'] = db_module.current_datetime()
    kwargs['employee_sn'] = 0
    message = {"message": "success"}
    company_sn = check_special_url(kwargs['page_url'])
    if company_sn != 0:  # 是否是专用链接？
        kwargs['company_sn'] = company_sn
        kwargs['in_count'] = 0
    else:
        company_sn = next_company_sn(0)  # 从分配计划获取下一个company_sn
        kwargs['company_sn'] = company_sn
    """获取team_sn"""
    team_sn = Team.allot_customer(company_sn)
    kwargs['team_sn'] = team_sn
    ses = db_module.sql_session()
    """只分配到团队，不分配到个人"""
    sql = db_module.structure_sql("add", table_name, **kwargs)
    file_path = os.path.join(os.path.split(__file__)[0], "sql.log")
    file = open(file_path, mode="a", encoding="utf8")
    print(sql, file=file)
    print(sql)
    file.flush()
    file.close()

    try:
        ses.execute(sql)
        ses.commit()
        bak_customer.delay(**kwargs)  # 备份用户
    except Exception as e:
        print(e)
        message['message'] = '注册失败'
    finally:
        ses.close()
        return message


def allot_customer(company_sn):
    """公司内部分配,现阶段平均分配，返回employee_sn"""
    ses = db_module.sql_session()
    sql = "select team_info.sn,employee_info.sn from team_info,employee_info where team_info.leader_sn=employee_info.sn and team_info.leader_sn in (select sn from employee_info where position_sn in (select sn from position_info where company_sn={} " \
          "and parent_sn=0 and has_team=1))".format(company_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()

    print(raw)
    if len(raw) == 0:
        ses.close()
        return 0
    else:
        r = list()
        for x in raw:
            r.append((x[1], count_by_team_sn(x[0])))
        ses.close()
        r.sort(key=lambda obj: obj[1])
        employee_sn = r[0][0]
        return next_employee(employee_sn)


def customer_count(the_type="all", sn=0, filter_dict: dict = {}):
    """统计总数，the_type是统计的用户类型，
    sn 是company_info.sn 。0表示所有
    filter_dict 是过滤字典
    返回int"""
    # sql = "select count(1) from {}".format(table_name)
    result = 0
    filter1 = " where in_count!=-1 "
    if the_type == "public":
        """共享用户"""
        filter1 = " where in_count=1 "
    if the_type == "private":
        """私有用户"""
        filter1 = " where in_count=0 "

    filter2 = " "
    if sn != 0:
        filter2 = "and company_sn={} ".format(sn)

    filter3 = " "
    if len(filter_dict) > 0:
        for k, v in filter_dict.items():
            if isinstance(v, (int, float)):
                temp = "and {}={}".format(k, v)
            elif isinstance(v, str):
                temp = "and {}='{}'".format(k, v)
            elif isinstance(v, (list, tuple)):
                if len(v) == 0:
                    temp = ""
                else:
                    inner_list = []
                    for item in v:
                        if isinstance(item, str):
                            inner_list.append("'{}'".format(item))
                        else:
                            inner_list.append(item)
                    temp = "and {} in ({})".format(k, ",".join(inner_list))
            else:
                raise TypeError("错误的类型:{}".format(type(v)))
            filter3 += temp
        filter3 += " "

    sql = "select count(1) from {}{}{}{}".format(table_name, filter1, filter2, filter3)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        pass
    else:
        result = raw[0]
    return result


def check_term(term):
    """检测条件语句，判断是否合法并进行适当的转换"""
    pass


def page(the_type="all", index=1, length=30, term='', sn=0, key_word_list: list=[]):
    """分页查询注册用户，后台管理用，
    the_type  是用户类型
    index是页码，
    length是每页多少条记录
    term 是查询条件表达式 类是 user_sn>10 暂时不用
    sn  公司的sn，0表示未分配
    key_word_list   customer_description的匹配数组,
    return  数组
    """
    result = []
    try:
        index = int(index)
        length = int(length)
    except ValueError:
        index = ""
    if db_module.validate_arg(term, "_") and index != "":
        """参数检查通过"""
        sql = ""
        skip = (index - 1) * length
        limit = length
        if len(key_word_list) == 0:
            desc_filter_str = ''
        else:
            temp_list = list()
            for x in key_word_list:
                if isinstance(x, int):
                    pass
                else:
                    x = "'{}'".format(x)
                temp_list.append(x)
            desc_filter_str = " customer_description in ({})".format(",".join(temp_list))

        if the_type == "all":
            """所有用户"""
            if str(sn) == "0" and desc_filter_str == "":
                sql = "select {} from {} order by create_date desc limit {},{}". \
                    format(",".join(columns), table_name, skip, limit)
            elif str(sn) == "0" and desc_filter_str != "":
                sql = "select {} from {} where {} order by create_date desc limit {},{}". \
                    format(",".join(columns), table_name, desc_filter_str, skip, limit)
            elif str(sn) != "0" and desc_filter_str != "":
                sql = "select {} from {} where company_sn={} and {} order by create_date desc limit {},{}". \
                    format(",".join(columns), table_name, sn, desc_filter_str, skip, limit)
            else:
                sql = "select {} from {} where company_sn={} order by create_date desc limit {},{}". \
                    format(",".join(columns), table_name, sn, skip, limit)

        elif the_type == "allotted":
            """已分配用户"""
            sql = "select {} from {} where team_sn!=0 and company_sn={} {} order by create_date desc limit {},{}". \
                format(",".join(columns), table_name, sn, ("" if desc_filter_str == "" else "and{}".
                                                           format(desc_filter_str)), skip, limit)
        elif the_type == "no_allot":
            """未分配用户"""
            sql = "select {} from {} where team_sn=0 and company_sn={} {} order by create_date desc limit {},{}". \
                format(",".join(columns), table_name, sn, ("" if desc_filter_str == "" else "and{}".
                                                           format(desc_filter_str)), skip, limit)
        else:
            pass
        if sql == "":
            pass
        else:
            ses = db_module.sql_session()
            proxy = ses.execute(sql)
            raw = proxy.fetchall()
            ses.close()
            if len(raw) == 0:
                pass
            else:
                result = [dict(zip(columns, x)) for x in raw]
    else:
        pass
    return result


def edit_customer(**kwargs):
    """编辑用户信息"""
    message = {"message": "success"}
    the_type = kwargs.pop("the_type")
    user_sn = kwargs.pop("user_sn")
    sql = ""
    company_sn = 0
    try:
        company_sn = kwargs.pop("company_sn")
    except KeyError:
        print("admin账户")
    finally:
        if company_sn == 0:
            term = " where user_sn={}".format(user_sn)
        else:
            term = " where user_sn={} and company_sn={}".format(user_sn, company_sn)
    if the_type == "delete":
        """删除"""
        sql = "delete from {} {}".format(table_name, term)
    elif the_type == "edit":
        query = "where user_sn={} and company_sn={}".format(user_sn, company_sn)
        sql = db_module.structure_sql("edit", table_name, query, **kwargs)
    else:
        pass
    if sql == "":
        message['message'] = "不明操作"
    else:
        ses = db_module.sql_session()
        ses.execute(sql)
        ses.commit()
        ses.close()
    return message


def count_by_company_name(parent_sn=0, url_from="public", filter_dict: dict = {}):
    """统计所有公司分配的用户数量，
    parent_sn 母公司的sn，默认为0,代表总公司
    url_from  指注册来源，有三个取值：public表示统计公用注册来源的，private表示统计专用链接的，all表示统计前两者
    filter_dict  过滤器字典
    返回已公司名为key，数量为值的字典"""
    result = dict()
    sql = "select sn,company_name from company_info where parent_sn={}".format(parent_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    if len(raw) == 0:
        """公司id错误"""
        pass
    else:
        query = ""
        if url_from == "public":
            query = " and in_count=1"
        if url_from == "private":
            query = " and in_count=0"
        filter_str = " "
        if len(filter_dict) > 0:
            for k, v in filter_dict.items():
                if isinstance(v, (int, float)):
                    temp = "and {}={}".format(k, v)
                elif isinstance(v, str):
                    temp = "and {}='{}'".format(k, v)
                elif isinstance(v, (list, tuple)):
                    if len(v) == 0:
                        temp = ""
                    else:
                        inner_list = []
                        for item in v:
                            if isinstance(item, str):
                                inner_list.append("'{}'".format(item))
                            else:
                                inner_list.append(item)
                        temp = "and {} in ({})".format(k, ",".join(inner_list))
                else:
                    raise TypeError("错误的类型:{}".format(type(v)))
                filter_str += temp
        raw = {x[0]: x[1] for x in raw}
        for k, v in raw.items():
            sql = "select count(1) from customer_info where company_sn={}{}{}".format(k, query, filter_str)
            proxy = ses.execute(sql)
            raw_2 = proxy.fetchone()
            result[v] = raw_2[0]
    ses.close()
    return result


def get_my_team_sn(team_sn, result=list()):
    if len(result) == 0:
        result = [team_sn]
    else:
        result.append(team_sn)
    ses = db_module.sql_session()
    sql = "select leader_sn from team_info where sn={}".format(team_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    sql = "select sn from employee_info where team_sn={}".format(team_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    if len(raw) == 0:
        ses.close()
    else:
        sn_list = "({})".format(",".join([str(x[0]) for x in raw]))
        sql = "select sn from team_info where leader_sn in {}".format(sn_list)
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            sn_list = [x[0] for x in raw if x[0] not in result]
            for sn in sn_list:
                get_my_team_sn(sn, result)
    return result


def count_by_team_sn(team_sn):
    result = 0
    team_sn_list = get_my_team_sn(team_sn)
    sn_list = "({})".format(",".join([str(x) for x in team_sn_list]))
    today = db_module.current_datetime(-1)
    sql = "select count(1) from {} where team_sn in {} and create_date>'{}'".format(table_name, sn_list, today)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        pass
    else:
        result = raw[0]
    return result


def count_all_my_customer(my_sn):
    """
    统计我所有的客户
    :param my_sn: team_sn or employee_sn
    :return: int
    """
    result = 0
    sql = "select count(1) from {} where employee_sn={}".format(table_name, my_sn)
    if int(my_sn) > 5000:
        team_sn_list = get_my_team_sn(my_sn)
        sn_list = "({})".format(",".join([str(x) for x in team_sn_list]))
        sql = "select count(1) from {} where team_sn in {}".format(table_name, sn_list)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        pass
    else:
        result = raw[0]
    return result


def count_by_employee_sn(employee_sn):
    result = 0
    sql = "select count(1) from {} where employee_sn={}".format(table_name, employee_sn)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchone()
    ses.close()
    if raw is None:
        pass
    else:
        result = raw[0]
    return result


def next_employee(employee_sn):
    """"""
    ses = db_module.sql_session()
    sql = "select employee_info.sn,employee_info.team_sn,has_team from employee_info,team_info,position_info where position_info.sn=employee_info.position_sn and employee_info.team_sn=team_info.sn" \
          " and team_info.leader_sn={}".format(employee_sn)
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    print(raw)
    if len(raw) == 0:
        ses.close()
        print("this")
        return employee_sn
    else:
        if raw[0][2] == 1:
            """有团队"""
            sn_list = [x[0] for x in raw]
            r = list()
            for x in sn_list:
                sql = "select sn from team_info where leader_sn={}".format(x)
                proxy = ses.execute(sql)
                r.append((x, proxy.fetchone()[0]))
            ses.close()
            r2 = list()
            for x in r:
                r2.append((x[0], count_by_team_sn(x[1])))  # 按团队统计人数
            """按团队统计分配数"""
            r2.sort(key=lambda obj: obj[1])
            return next_employee(r2[0][0])
        else:
            sn_list = [x[0] for x in raw]
            r = list()
            today = db_module.current_datetime(-1)
            for x in sn_list:
                sql = "select count(1) from customer_info where employee_sn={} and in_count_company=1 and create_date>'{}'".format(
                    x, today)
                proxy = ses.execute(sql)
                r.append((x, proxy.fetchone()[0]))
            ses.close()
            """按员工排序人数统计"""
            r.sort(key=lambda obj: obj[1])
            return r[0][0]


def page_by_team_sn(company_sn, team_sn, index=1, length=30, term='', sn=0):
    """分页查询注册用户，后台管理用，
    team_sn  团队sn
    index是页码，
    length是每页多少条记录
    term 是查询条件表达式 类是 user_sn>10 暂时不用
    sn  公司的sn，0表示未分配
    return  数组
    """
    result = []
    try:
        index = int(index)
        length = int(length)
    except ValueError:
        index = ""
    if db_module.validate_arg(term, "_") and index != "":
        """参数检查通过"""
        skip = (index - 1) * length
        limit = length
        team_sn_list = get_my_team_sn(team_sn)
        sn_list = "({})".format(",".join([str(x) for x in team_sn_list]))
        sql = "select {} from {} where team_sn in {} order by create_date desc limit {},{}". \
            format(",".join(columns), table_name, sn_list, skip, limit)

        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = [dict(zip(columns, x)) for x in raw]
    else:
        pass
    return result


def page_by_employee_sn(employee_sn, index=1, length=30, term='', sn=0):
    """分页查询注册用户，后台管理用，
    employee_sn  员工sn
    index是页码，
    length是每页多少条记录
    term 是查询条件表达式 类是 user_sn>10 暂时不用
    sn  公司的sn，0表示未分配
    return  数组
    """
    result = []
    try:
        index = int(index)
        length = int(length)
    except ValueError:
        index = ""
    if db_module.validate_arg(term, "_") and index != "":
        """参数检查通过"""
        skip = (index - 1) * length
        limit = length
        sql = "select {} from {} where employee_sn={} order by create_date desc limit {},{}". \
            format(",".join(columns), table_name, employee_sn, skip, limit)

        ses = db_module.sql_session()
        proxy = ses.execute(sql)
        raw = proxy.fetchall()
        ses.close()
        if len(raw) == 0:
            pass
        else:
            result = [dict(zip(columns, x)) for x in raw]
    else:
        pass
    return result


def show_process_excel_list() -> list:
    """
    显示所有的公司处理excel的权限状态。
    :return: 权限的list[{"sn":sn, "company_name":company_name, "export_excel":export_excel}, ...]
    """
    ses = db_module.sql_session()
    sql = "select sn,company_name,export_excel from company_info"
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()
    if len(raw) == 0:
        result = list()
    else:
        result = [dict(zip(["sn", "company_name", "export_excel"], x)) for x in raw]
    return result


def set_process_excel_status(company_sn: int, status_code: int) -> dict:
    """
    设置公司的excel的操作权限。
    :param company_sn: 公司sn
    :param status_code: 状态码，1或者0
    :return: 消息字典
    """
    message = {"message": "success"}
    ses = db_module.sql_session()
    sql = "update company_info set export_excel={} where sn={}".format(status_code, company_sn)
    try:
        ses.execute(sql)
        ses.commit()
    except Exception as e:
        print(e)
        message['message'] = "操作失败"
    finally:
        ses.close()
        return message


def can_process_excel(company_sn: int = 0) -> (int, None):
    """检查(公司)账户是否有操作excel模块的权利？
    :param company_sn: 公司的sn
    ：return： 如果有操作权限，就返回公司的sn，否则，返回None
    """
    result = None
    if company_sn == 0:
        result = company_sn
    elif isinstance(company_sn, int):
        ses = db_module.sql_session()
        sql = "select export_excel from company_info where sn={}".format(company_sn)
        proxy = ses.execute(sql)
        raw = proxy.fetchone()
        ses.close()
        if raw is None:
            pass
        else:
            flag = raw[0]
            if flag == 1:
                result = company_sn
            else:
                pass
    else:
        pass
    return result


def export_customer(company_sn: int, begin: str = None, end: str = None) -> None:
    """
    导出/生产一个用户数据的ｅｘｃｅｌ文件
    :param company_sn: 公司sn int
    :param begin: 开始时间，字符串格式 %Y-%m-%d %H:%M:%S
    :param end:   结束时间，字符串格式 %Y-%m-%d %H:%M:%S
    :return: None
    """
    end = db_module.current_datetime() if end is None or end == "" else end
    begin = "1970-01-01 :00:00:00" if begin is None or begin == "" else begin
    keys = ["user_sn", "user_name", "user_phone", "page_url", "create_date"]
    vals = ["客户id", "客户名称", "客户手机", "注册网址", "注册时间"]
    if company_sn == 0:
        par = ''
    else:
        par = "and company_sn={}".format(company_sn)
    sql = "select {0} from {1} where create_date>'{2}' and create_date<'{3}' {4} order by create_date desc".format(
        ",".join(keys), table_name, begin, end, par)
    ses = db_module.sql_session()
    proxy = ses.execute(sql)
    raw = proxy.fetchall()
    ses.close()

    wb = xlwt.Workbook()
    sheet = wb.add_sheet("客户名单")
    # 创建格式style
    style = xlwt.XFStyle()
    # 创建font，设置字体
    font = xlwt.Font()
    # 字体格式
    font.name = 'Times New Roman'
    # 将字体font，应用到格式style
    style.font = font
    # 创建alignment，居中
    alignment = xlwt.Alignment()
    # 居中
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    # 应用到格式style
    style.alignment = alignment
    style1 = xlwt.XFStyle()
    font1 = xlwt.Font()
    font1.name = 'Times New Roman'
    # 字体颜色（绿色）
    # font1.colour_index = 3
    # 字体加粗
    font1.bold = True
    style1.font = font1
    style1.alignment = alignment
    for index, item in enumerate(raw):
        if index == 0:
            for i, key in enumerate(keys):
                sheet.write(0, i, vals[i], style1)
        else:
            pass
        for i, key in enumerate(keys):
            val = item[i]
            val = val.strftime("%Y-%m-%d %H:%M:%S") if isinstance(val, datetime.datetime) else val
            sheet.write(index + 1, i, val)
    excel_path = os.path.join(EXCEL_PATH, str(company_sn))
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)
    wb.save(os.path.join(excel_path, "{}至{}.xls".format(begin, end)))


def show_excel(company_sn: int) -> list:
    """以列表形式，显示ｅｘｃｅ文件
    :param company_sn: 公司sn int
    """
    excel_path = os.path.join(EXCEL_PATH, str(company_sn))
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)
    names = os.listdir(excel_path)
    result = list()
    for name in names:
        if name.lower().endswith(".xls"):
            stat = os.stat(os.path.join(excel_path, name))
            create_date = datetime.datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d %H:%M:%S")
            last_access_date = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            file_size = stat.st_size
            result.append({"file_name": name, "last_access_date": last_access_date,
                           "create_date": create_date, "file_size": file_size})
    result.sort(key=lambda obj: datetime.datetime.strptime(obj['create_date'], "%Y-%m-%d %H:%M:%S"), reverse=True)
    return result


def delete_excel(company_sn: int, file_name: str) -> dict:
    """
    删除excel文件
    :param company_sn: 公司sn int
    :param file_name: 文件名
    :return: 消息字典
    """
    message = {"message": "success"}
    excel_path = os.path.join(EXCEL_PATH, str(company_sn))
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)
    file_path = os.path.join(excel_path, file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError as e:
            message['message'] = str(e)
    else:
        message['message'] = "{} 不存在".format(file_path)
    return message


if __name__ == "__main__":
    x = can_process_excel(2)
    print(x)
    pass