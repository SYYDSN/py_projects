import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
from pymongo import WriteConcern


ObjectId = orm_module.ObjectId
BaseDoc = orm_module.BaseDoc


"""身份验证模块"""



if __name__ == "__main__":
    
    pass




