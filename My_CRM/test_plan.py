# -*- coding:utf-8 -*-
from customer_module import add_user
import random


for x in range(10):
    user_name = "测试用户_{}".format(x)
    user_phone = random.randint(18800000000, 18999999999)
    add_user(user_name=user_name, user_phone=user_phone,page_url='')