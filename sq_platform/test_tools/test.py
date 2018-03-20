#  -*- coding: utf-8 -*-
import mongo_db
from manage.company_module import Employee




employee_list = [
    {"user_name": "zhangsan"},
    {"user_name": "lisi"}
]


Employee.insert_many(employee_list)