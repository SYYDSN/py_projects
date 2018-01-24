# -*- coding:utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from db_module import engine
from db_module import current_datetime, sql_session
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.exc import ProgrammingError

"""各种模型的原始类模块"""

Base = declarative_base(bind=engine)


class User(Base):
    __tablename__ = "user_info"

    user_sn = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(45), unique=True, nullable=False)
    user_password = Column(String(200), nullable=False)
    create_date = Column(DateTime, nullable=False, default=current_datetime())

    def __repr__(self):

        return "<User(user_name={}, user_password={}, create_date={})>" \
            .format(self.user_sn, self.user_password, self.create_date)


Base.metadata.create_all()
user = User(user_name="mike", user_password="hello")
ses = sql_session()
result = ses.query(User).all()
print(result)
ses.close()
