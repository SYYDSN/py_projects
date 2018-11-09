# orm_module

mongodb的orm工具

使用前**需要配置**

* user  数据库用户名
* password 数据库密码
* db_name  库名称
* host  数据库主机

## 2018-11-09  

### 版本号

version 0.0.3

### 更新内容

#### 新增功能

#### query 查询

##### 设计目的

此函数设计用来替代原来的find和query_by_page函数
find 用于查询多个记录.
query_by_page 是find 的增强版,相比find,query_by_page多了分页查询和对查询结果进行处理的功能.
query函数目前可以完全替代query_by_page函数

##### 功能

* 按照过滤器指定的条件.查询多个符合条件的记录.
* 可以是用join功能进行联表查询, 相当于where 功能.目前仅仅能实现单值join查询,也就是where T1.name = T2.name 这样一对值的比较查询.而不能进行组合的多值查询(where T1.name = T2.name and T1.id = T2.id)
* 可以进行分页查询.
* 可以对查询结果直接进行加工.相当于一个callback的功能

##### 使用

调用方法

> query(filter_dict: dict, join_cond: (list, dict) = None, sort_cond: (dict, list) = None, projection: list = None, page_size: int = 10, ruler: int = 5, page_index: int = 1, to_dict: bool = True, can_json: bool = False, func: object = None, target: str = "dict")

参数说明

* param filter_dict:  查询条件字典,

```python
# 单条件查询条件.
filter_dict = {"user_name": user_name}

# 多条件查询条件.
filter_dict = {"user_name": user_name, "sex": "男"}

"""
一些用于比较关系的方式:
1. A > b   {A: {"$gt": B}}
2. A >= b   {A: {"$gte": B}}
3. A < b   {A: {"$lt": B}}
4. A =< b   {A: {"$lte": B}}
"""

```

* param join_cond:  join查询条件单个join是字典格式,多个join是数组格式,

```python
"""
T1为用户表,表名user,表中有一个外键字段role_id,指向T2表的id
T2为角色表.表名role. 字段3个,主键id, 字段是role_name, 表示角色名, time表示创建事件
单外联查询. select *, T2.*  from T1,T2 where T1.role_id = T2.id
"""
join_cond = {
              "table_name": "T2",                           # 外部表的名称
              "local_field": "role_id",                     # 本地表外键字段名
              "foreign_field": |"id",                       # 外部表主键
              "field_map": {"role_name": "role"},           # join子查询结果的名字映射.
              "sort_by": {"time": -1},                      # join子查询结果排序方式
              "flat": True,                                 # 是否合并子查询结果到主文档?
            }
"""
field_map 可以把子查询结果重命名.此字段不是必须的. 此字典除了重命名外,也可以过滤多余的字段{"role_name": "role"}就只会把子查询结果中的role_name字段重命名为role.子查询中的其他字段会被丢弃.
sort_by    是子查询的排序字典,不是必须的. 一般可以忽视这个字段.
flat  相对复杂.一般来说.flat= False的时候,查询出来的结果是这样的:
{"_id": id, user_name: jack, T2: [子查询结果数组], "role_id": role_id}
join子查询的结果作为数组保存在主文档的一个以外部表的表名作为名称的字段里.这是由于join查询可能由多个结果的原因.这时候,这是原始的结果.
如果你需要像传统的sql那样把子查询结果显示在主文档内.你需要设置flag = True,这时的显示结果是:
{"_id": id, user_name: jack, role: 角色名, "role_id": role_id}.
注意,如果子查询结果不止一条时,你将丢失除第一条子查询结果之外的记录
"""
```

* param sort_cond:  排序条件字典/数组

```python
# 先以time1正序排列, time1相等时以tim2倒序排列
sort_cond = [("time1", 1), ("time2", -1)]
```

* param projection:  投影数组,决定输出哪些字段?

```python
# 不要显示_id,输出name,age和sex字段,同时把字段sex的名字改为"性别"
sort_cond = {"_id": 0, "name": 1, "age": 1, "sex": "性别"}
```

* param page_size: 每页多少条记录 这个参数和分页查询有关,表示多少记录分为一组输出.默认是10.
* param ruler: 翻页器最多显示几个页码？ 这个参数是为了显示多个页码的前端,一般无需输入
* param page_index: 页码(当前页码)   分页查询时使用. 默认是1. 显示第一页的数据
* param to_dict: 返回的元素是否转成字典(默认就是字典.否则是类的实例) 无需传递此参数
* param can_json: 是否调用to_flat_dict函数转换成可以json的字典?   无需传递此参数
* param func: 额外的处理函数.这种函数用于在返回数据前对每条数据进行额外的处理.会把doc或者实例当作唯一的对象传入  无需传递此参数
* param target: 和func参数配合使用,指明func是对实例本身操作还是对doc进行操作(instance/dict)
* return: 字典对象. 

```python
查询结果示范:
        {
            "total_record": record_count,      # 记录总数
            "total_page": page_count,          # 共计多少页?
            "data": res,                       # 当前页记录的数组对象
            "current_page": page_index,        # 当前页页码.
            "pages": pages                     # 当前页区间的一段页码,可以忽视
        }
```