# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db


ObjectId = mongo_db.ObjectId


class RawWebChatMessage(mongo_db.BaseDoc):
    """
    原始微信的记录
    """
    _table_name = "raw_webchat_message"
    type_dict = dict()
    type_dict['_id'] = ObjectId

