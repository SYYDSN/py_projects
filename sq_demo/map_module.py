# -*- coding: utf-8 -*-
from api.data.item_module import CarLicense
from api.data.item_module import User
from api.data.item_module import AppLoginToken
from api.data.item_module import EventRecord


"""记录了数据库表和类的对应信息"""


module_map = {"car_license_info": CarLicense,
              "app_login_token": AppLoginToken,
              "event_record": EventRecord,
              "user_info": User}