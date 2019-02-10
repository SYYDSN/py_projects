# 组织架构, 身份验证和权限管理

## 文件夹说明

* authorization_package 组织架构
* global_logging 全局日志
* nameko_test 微服务框架,需要RabbitMQ支持.备用
* orm_unit 持久化工具包,包含sql和mongodb的持久化工具
* socket_tools  异步socket的服务端和客户端工具,包含TCP和UDP两种方式,可以用于生产环境
* toolbox 包含: 日志工具, 邮件工具和flask工具
* views  视图部分.
* zerorpc_test  zerorpc的测试工具包