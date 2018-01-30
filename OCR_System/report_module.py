# -*-coding:utf-8-*-
import db_module
from user_group_module import user_group_count
from supplier_group_module import supplier_group_count
import datetime


"""统计模块"""


def recode_count(the_class: str="customer") -> int:
    """
    统计报表的记录数
    :param the_class:  统计客户还是供应商的总数？
    :return: int
    """
    if the_class == "supplier":
        return user_group_count()
    else:
        return supplier_group_count()


def page(index=1, length=30, begin='', end='', the_class="customer", company_name=''):
    """分页查询批次，后台管理用，index是页码，length是每页多少条记录
    begin: 开始时间
    end： 结束时间
    the_class  取值是customer和supplier ，代表是供应商还是用户,现阶段只能查用户
    company_name: 供应商或者客户的公司名
    """
    table_name = "supplier_group_info"
    columns = ["group_sn", "company_alias"]
    if the_class == "customer":
        table_name = "user_group_info"
    message = {"message": "success"}
    if isinstance(index, (int, str)) and isinstance(length, (int, str)):
        try:
            index = index if isinstance(index, int) else int(index)
            length = length if isinstance(length, int) else int(length)
            skip = (index - 1) * length
            limit = length
            """计算起至时间"""
            try:
                datetime.datetime.strptime(begin, "%Y-%m-%d")
            except Exception:
                begin = ""
            try:
                datetime.datetime.strptime(end, "%Y-%m-%d")
            except Exception:
                end = ""

            session = db_module.sql_session()
            """先查供应商/用户的列表"""
            if company_name != "":
                sql = "select " + ",".join(columns) + (" from {} where company_name like '%{}%' order by create_date "
                                                       "desc limit {},{}".format(table_name, company_name, skip, limit))
            else:
                sql = "select " + ",".join(columns) + (" from {} order by create_date "
                                                       "desc limit {},{}".format(table_name, skip,
                                                                                 limit))
            try:
                proxy_result = session.execute(sql)
                result = proxy_result.fetchall()
                if len(result) != 0:
                    result = [db_module.str_format(x) for x in result]
                    data = {x[0]: dict(zip(columns, x)) for x in result}
                    client = db_module.get_mongodb("supplier_image")
                    for sn in data.keys():
                        """继续查关联的批次"""
                        sql = "select batch_sn from batch_info where customer_sn={}".format(sn)
                        proxy = session.execute(sql)
                        raw = proxy.fetchall()
                        batch_count = 0
                        batch_sn_tuple = tuple()
                        if len(raw) == 0:
                            pass
                        else:
                            batch_count = len(raw)
                            batch_sn_tuple = tuple([x[0] for x in raw])
                        data[sn]['batch_count'] = batch_count
                        """查询关联的赔案"""
                        sql = "select case_sn from case_info where customer_sn={}".format(sn)
                        proxy = session.execute(sql)
                        raw = proxy.fetchall()
                        case_count = 0
                        case_sn_list = list()
                        if len(raw) == 0:
                            pass
                        else:
                            case_count = len(raw)
                            case_sn_list = [x[0] for x in raw]
                        data[sn]['case_count'] = case_count
                        """查询关联的票据"""
                        image_count = 0
                        if len(batch_sn_tuple) == 0:
                            pass
                        else:
                            sql = "select count(1) from image_info where batch_sn in {}".format(batch_sn_tuple)
                            if len(batch_sn_tuple) == 1:
                                sql = "select count(1) from image_info where batch_sn={}".format(batch_sn_tuple[0])
                            proxy = session.execute(sql)
                            raw = proxy.fetchone()
                            if raw is None:
                                pass
                            else:
                                image_count = raw[0]
                        data[sn]['image_count'] = image_count
                        """查询已完成的图片数"""
                        finish_count = 0
                        if case_count == 0:
                            pass
                        else:
                            finish_count = client.find_one({"batch_sn": {"$in": case_sn_list}}).count()
                else:
                    data = []
                message['data'] = data
            except Exception as e:
                print(e)
                message['message'] = "查询错误"
            finally:
                session.close()
        except TypeError:
            message['message'] = "参数错误"
    else:
        raise TypeError("参数只能是str或者int")
        message['message'] = "参数类型错误"
    return message
