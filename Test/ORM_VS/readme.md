# PonyORM 和 Peewee 对比测试

用于测试生产环境下ponyorm使用的可行性.

测试组

* django (暂不参与)
* flask + peewee
* flask + ponyORM

主要测试:

* 2种数据库处理的并发性能.(单表性能, join性能)
