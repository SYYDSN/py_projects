#  -*- coding: utf-8 -*-
from mongo_db import get_db
from pymongo import mongo_client
import datetime
from bson.objectid import ObjectId


def get_prefix(client: mongo_client, user_id: (str, ObjectId)) -> str:
    """
    根据用户id获取用户所在公司的前缀,这用于向AI模块查询报告和排名

    根据用户id查找查询前缀涉及三个表:
    Employee: 员工类的表                            表名: user_info
    Company:  公司类的表                            表名: company_info
    EmployeeCompanyRelation: 员工和公司的关系类的表   表名: employee_company_relation

    用户和公司之间的约束关系如下:
    EmployeeCompanyRelation作为桥梁,建立起Employee和Company之间的关系.
    Employee-->EmployeeCompanyRelation<---Company

    EmployeeCompanyRelation的属性说明如下:
    EmployeeCompanyRelation.company_id 是一个DBRef对象,指向Company对象的id
    EmployeeCompanyRelation.employee_id 是一个DBRef对象,指向Employee对象的id
    EmployeeCompanyRelation.create_date 是一个datetime对象,是指关系建立的时间.
    EmployeeCompanyRelation.end_date  是一个datetime对象,是指关系终结的时间.这个属性如果为不存在,为None或者大于当前的时间,
    都可以认为员工和公司间的关系处于有效的状态.

    Employee有一个company_relation_id的属性,DBRef类型.,指向EmployeeCompanyRelation的id.这是个非必须的属性.
    存在的目的在于快速检索EmployeeCompanyRelation对象.

    函数的逻辑如下:
    1. 确认user_id有效.
    2. 确认对应的user记录有company_relation_id属性.
    3. 确认确认对应的user记录有company_relation_id对应的EmployeeCompanyRelation记录处于有效关系状态.
    4. 查找EmployeeCompanyRelation.company_id对应的Company对象.
    5. 取出Company对象的prefix属性.

    :param client: 数据库的操作handler, mongodb client对象,
    :param user_id: 用户id, str或者ObjectId对象.
    :return: 前缀, 字符串格式, 散户是以xxx作为prefix
    """
    user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
    user = client.user_info.find_one(filter={"_id": user_id})
    prefix = "xxx"
    if isinstance(user, dict):
        """用户存在"""
        company_relation_dbref = user.get("company_relation_id")
        if company_relation_dbref is None:
            ms = "用户{}没有company_id信息".format(str(user_id))
            print(ms)
        else:
            company_relation_id = company_relation_dbref.id
            """查找关系对象"""
            company_relation = client.employee_company_relation.find_one(filter={"_id": company_relation_id})
            if isinstance(company_relation, dict):
                """EmployeeCompanyRelation对象存在"""
                now = datetime.datetime.now()
                if company_relation.get("end_date") is None or company_relation.get("end_date") < now:
                    """EmployeeCompanyRelation对象有效"""
                    company = client.company_info.find_one(filter={"_id": company_relation['company_id'].id})
                    if isinstance(company, dict):
                        """公司存在"""
                        prefix = prefix if company.get("prefix") is None else company.get("prefix")
                    else:
                        ms = "company对象错误, {}".format(company_relation['company_id'].id)
                        print(ms)
            else:
                ms = "company_relation_dbref:{}错误".format(str(company_relation_dbref))
                print(ms)
    else:
        raise ValueError("错误的用户id:{}".format(str(user_id)))
    return prefix


if __name__ == "__main__":
    """根据用户的id获取公司的前缀信息,散户的前缀是xxx"""
    cli = get_db()
    print(get_prefix(cli, '598d6ac2de713e32dfc74796'))