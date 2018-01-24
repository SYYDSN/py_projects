# -*-coding:utf-8-*-
import os
from log_module import get_logger
import smtplib
from email.mime.text import MIMEText
from werkzeug.contrib.cache import RedisCache
import datetime


"""电子邮件模块"""


my_email = "583736361@qq.com"
my_auth = "xefwlduxnptnbbdf"  # 授权码
cache = RedisCache()
logger = get_logger(os.path.split(__file__)[-1].split(".", 1)[0])


def send_mail(to_email: str, title: str, content: str) -> bool:
    """
    发送邮件,
    :param to_email: 目的邮件地址
    :param title:  主题
    :param content: 正文
    :return: 是否发送成功
    """
    msg = MIMEText(content)
    msg["Subject"] = title
    msg["From"] = my_email
    msg["To"] = to_email
    flag = True
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(my_email, my_auth)
        s.sendmail(my_email, to_email, msg.as_string())
        s.quit()
    except Exception as e:
        flag = False
        ms = {"Error: {}, args:{}".format(e, {"to_email": to_email, "title": title, "content": content})}
        logger.exception(ms)
        raise e
    finally:
        return flag


def send_warning_email(title: str, content: str, interval: int = 900, to_mail: str = "583736361@qq.com") -> None:
    """
    发送警告邮件
    :param title: 邮件标题,同一类型的警告邮件,标题不应该变更.标题限制最大长度为60个字符.
    :param content: 邮件正文
    :param interval: 忽略的间隔,单位分钟,在此间隔内,相同主题的邮件不会被发送
    :param to_mail: 管理员邮箱
    :return:
    """
    if isinstance(title, str) and isinstance(content, str):
        flag = True  # 是否可以发送邮件?
        title = title if len(title) <= 60 else title[0: 60]
        key = "warning_email_title_{}".format(title)
        now = datetime.datetime.now()
        last_time = cache.get(key)
        if last_time is None:
            pass
        else:
            if isinstance(last_time, datetime.datetime):
                delta = (now - last_time).total_seconds()
                try:
                    interval = int(interval)
                except ValueError as e:
                    print(e)
                    interval = 900
                except TypeError as e:
                    print(e)
                    interval = 900
                finally:
                    if delta <= interval:
                        flag = False
                    else:
                        pass
            else:
                pass
        if flag:
            result = send_mail(to_email=to_mail, title=title, content=content)
            if result:
                cache.set(key, now, timeout=interval)
            else:
                pass
        else:
            pass
    else:
        ms = "Error:错误的参数类型: title={}, content={}".format(title, content)
        logger.exception(ms)
        raise TypeError(ms)


if __name__ == '__main__':
    pass