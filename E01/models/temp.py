import orm_module
import datetime

ObjectId = orm_module.ObjectId


class School(orm_module.BaseDoc):
    """
    学校类
    """
    _table_name = "school"
    type_dict = dict()
    type_dict['_id'] = ObjectId               # 学校id
    type_dict['province'] = str               # 省/直辖市,选择列表
    type_dict['city'] = str                   # 市/直辖市 选择表
    type_dict['county'] = str                 # 县/区/地级市 选择
    type_dict['primary_school'] = bool        # 小学
    type_dict['middle_school'] = bool         # 初中
    type_dict['high_school'] = bool           # 高中
    type_dict['verified'] = bool              # 是否已确认审核过
    type_dict['courses'] = list               # 课程列表
    type_dict['delete'] = bool                      # 是否删除?
    type_dict['delete_time'] = datetime.datetime    # 删除时间


class Subject(orm_module.BaseDoc):
    """
    学科类
    """
    _table_name = "subject"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str
    type_dict['delete'] = bool  # 是否删除?
    type_dict['delete_time'] = datetime.datetime  # 删除时间


class Course(orm_module.BaseDoc):
    """
    课程类.每个课程实例都会记录老师教授某一学科的起止时间
    """
    _table_name = "course"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['subject_id'] = ObjectId   # 课程id
    type_dict['teacher_id'] = ObjectId      # 教授者/老师id
    type_dict['begin'] = datetime.datetime  # 开始时间
    type_dict['end'] = datetime.datetime    # 结束时间


class HeadImage(orm_module.BaseFile):
    """
    头像图片文件
    """
    _table_name = "head_image"


class SpecialTeacher(orm_module.BaseDoc):
    """
    特聘老师
    """
    _table_name = "special_teacher"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_id'] = ObjectId  # 特聘老师的用户id
    type_dict['verifier_id'] = ObjectId  # 验证者id, 一般是系统管理员
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime


class GroupTag(orm_module.BaseDoc):
    """
    分组标签.
    用户初始化时,会添加三个默认的分组. "老师", "亲属", "朋友"
    """
    _table_name = "group_tag"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['tag_name'] = str       # 标签名
    type_dict['user_id'] = ObjectId   # 标签拥有者id
    type_dict['create_time'] = datetime.datetime  # 标签创建时间
    type_dict['delete_time'] = datetime.datetime  # 标签删除时间


class User(orm_module.BaseDoc):
    """
    用户类,包含老师账户, 学生账户,家长账户 ,特聘老师
    """
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId               # 用户id
    """
    用户类型.系统三种 老师, 一般(家长)和学生, 特聘老师专门有个表记录
    """
    type_dict['type'] = str
    type_dict['phone'] = str                  # 手机号码
    type_dict['password'] = str               # 登录密码
    type_dict['real_name'] = str              # 真实姓名
    type_dict['head_image'] = ObjectId        # 头像
    type_dict['gender'] = str                 # 性别
    type_dict['address'] = str                # 联系地址
    type_dict['id_image'] = ObjectId          # 身份证照片
    type_dict['email'] = str                  # 电子邮件
    type_dict['wx_id'] = str                  # 微信号
    type_dict['qq'] = str                     # qq号码

    @classmethod
    def get_tags(cls, user_id: ObjectId):
        """
        获取标签  未完成
        :param user_id:
        :return:
        """
        f = {"user_id": user_id}
        tags = cls.find(filter_dict=f)
        if len(tags) == 0:
            """
            插入 "老师", "亲属", "朋友" 三个分组
            """
            tags = []
            cls.insert_many()


class BuildRelate(orm_module.BaseDoc):
    """
    发起添加好友请求的记录
    BuildRelate和UserRelate两者的实例在时间上是前后相连的
    """
    _table_name = "build_relate"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict["req_id"] = ObjectId   # 发起者id
    type_dict['req_time'] = datetime.datetime
    type_dict["resp_id"] = ObjectId   # 响应者id
    type_dict['resp_time'] = datetime.datetime
    type_dict['result'] = bool        # 结果
    """
    好友标签,这个字段在加好友成功后会传递给UserRelate.tags,作为好友的类型/标签,如果此字段为空.
    那么在加好友成功后.必须提醒用户填写UserRelate.tag或者提供一个默认的值.注意UserRelate.tags是个数组对象
    """
    type_dict['tag'] = str


class UserRelate(orm_module.BaseDoc):
    """
    用户之间的关系,一次BuildRelate的成功实例会创建2个UserRelate的实例.
    """
    _table_name = "user_relate"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['owner'] = ObjectId   # 关系的拥有者
    type_dict['other'] = ObjectId   # 关系的另一方
    type_dict['tags'] = list   # 关系标签,值取自.User.get_tags()中的某一个值
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime


class Sharing(orm_module.BaseDoc):
    """
    分享, 依赖于UserRelate提供关系支持
    分享就是把自己的资源暴露给好友关系的人访问. 只有好友之间才可以分享资源.而且如果被分享的资源有限制条件的话,也受限制条件的影响.
    这些限制条件是指:
    付费的资源受是否付费的限制.
    限定身份访问的资源受访问者身份限制
    """
    _table_name = "sharing"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['owner'] = ObjectId  # 资源的拥有者
    type_dict['other'] = ObjectId  # 访问资源的一方
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime

