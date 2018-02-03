#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.realpath(__file__))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import firefox_module
from log_module import get_logger
from celery_module import to_jiandao_cloud_and_send_mail
import datetime


"""模型模块"""


logger = get_logger()


class CsrfError(mongo_db.BaseDoc):
    """csrf错误记录"""
    _table_name = "csrf_error_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId  # id,唯一
    type_dict['host_url'] = str  # 链接地址
    type_dict['base_url'] = str  # 完整url
    type_dict['referrer'] = str  # referrer
    type_dict['user_agent'] = str  # 浏览器信息
    type_dict['args'] = dict  # 参数字典
    type_dict['client_ip'] = str  # 客户端ip
    type_dict['reason'] = str  # 错误原因
    type_dict['time'] = datetime.datetime  # 时间


class SpreadKeyword(mongo_db.BaseDoc):
    """推广频道的关键词"""
    _table_name = "spread_keyword"
    type_dict = dict()             # 属性字典
    type_dict['_id'] = mongo_db.ObjectId     # id,唯一
    type_dict['english'] = str     # 英文词汇,唯一
    type_dict['chinese'] = str     # 中文词汇


class SpreadChannel(mongo_db.BaseDoc):
    """宣传/推广渠道"""


class AllowOrigin(mongo_db.BaseDoc):
    """允许跨域注册的域名，域名要待http的"""
    _table_name = "customer_info"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId  # id 唯一
    type_dict["origin"] = mongo_db.ObjectId  # 域名，理论上唯一
    type_dict['valid'] = bool   # 域名是否有效？

    @classmethod
    def list(cls, only_valid: bool = True) -> list:
        """
        获取允许跨域注册的域名的列表
        :param only_valid:  只包含有效域名？无效的域名也列出？
        :return: 域名列表
        """
        if only_valid:
            filter_dict = {"only_valid": True}
        else:
            filter_dict = {}

        result = cls.find_plus(filter_dict=filter_dict, projection=['origin'])
        return result

    @classmethod
    def allow(cls, origin: str, loosely: bool = True, only_valid: bool = True) -> bool:
        """
        验证一个域名是否允许访问？
        :param origin: 域名
        :param loosely: 宽松模式？如果是宽松模式的，空列表就是全部放行
        :param only_valid: 只包含有效域名？无效的域名也列出？
        :return:
        """
        origins = cls.list(only_valid=only_valid)
        if len(origins) == 0 and loosely:
            return True
        elif origin in origins:
            return True
        else:
            return False


class Customer(mongo_db.BaseDoc):
    """客户表"""
    _table_name = "customer_info"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId  # id 唯一
    type_dict['user_name'] = str    # 用户名 ,为空的话,默认手机号码
    type_dict['nick_name'] = str    # 昵称
    type_dict['real_name'] = str    # 真实姓名
    type_dict['phone'] = list    # 手机,用户可能有多个手机 CustomerExtendInfo实例的数组
    type_dict['qq'] = list    # qq ,CustomerExtendInfo实例的数组
    type_dict['wx'] = list    # wx  CustomerExtendInfo实例的数组
    type_dict['email'] = list    # email  CustomerExtendInfo实例的数组
    type_dict['description'] = str    # 注册时的备注
    type_dict['search_keyword'] = str    # 注册时的搜索关键词
    type_dict['host_url'] = str    # 注册地址,不包含参数
    type_dict['base_url'] = str    # 注册地址,包含参数
    type_dict['referrer'] = str    # referrer
    type_dict['user_agent'] = str    # user_agent
    type_dict['time'] = datetime.datetime  # 注册时间

    @classmethod
    def reg(cls, **kwargs):
        """注册用户,
        1.保存到mongo数据库.
        2.保存到简道云
        """
        message = {"message": "success"}
        reg_dict = kwargs.copy()
        try:
            if "phone" in kwargs:
                phone = kwargs.pop('phone')
                filter_dict = {"phone": {"$all": [phone]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的手机号码:{}".format(phone))
                else:
                    kwargs['phone'] = [phone]
            if "qq" in kwargs:
                qq = [kwargs.pop('qq')]
                filter_dict = {"qq": {"$all": [qq]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的qq号码:{}".format(qq))
                else:
                    kwargs['qq'] = [qq]
            if "wx" in kwargs:
                wx = [kwargs.pop('wx')]
                filter_dict = {"wx": {"$all": [wx]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的微信号码:{}".format(wx))
                else:
                    kwargs['wx'] = [wx]
            if "email" in kwargs:
                email = [kwargs.pop('email')]
                filter_dict = {"email": {"$all": [email]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的邮件地址:{}".format(email))
                else:
                    kwargs['email'] = [email]
        except ValueError as e:
            message['message'] = str(e)
            print(e)
        except Exception as e:
            message['message'] = str(e)
            print(e)
            logger.exception(exc_info=True, stack_info=True)
        finally:
            if message['message'] == "success":
                customer = cls(**kwargs)
                save = None
                try:
                    save = customer.save()
                except Exception as e:
                    print(e)
                    message['message'] = str(e)
                    logger.exception(exc_info=True, stack_info=True)
                finally:
                    if isinstance(save, mongo_db.ObjectId):
                        message['user_id'] = str(save)
                        """转发到简道云"""
                        to_jiandao_cloud_and_send_mail.delay(**reg_dict)
                    else:
                        pass
            else:
                pass
        return message


if __name__ == "__main__":
    AllowOrigin.list()
    pass