# 组织架构, 身份验证和权限管理

本项目地址 [https://github.com/iSpidercom/OrganizationAndAuthentication](https://github.com/iSpidercom/OrganizationAndAuthentication)

## 文件夹说明

* authorization_package 组织架构
* global_logging 全局日志
* nameko_test 微服务框架,需要RabbitMQ支持.备用
* orm_unit 持久化工具包,包含sql和mongodb的持久化工具
* socket_tools  异步socket的服务端和客户端工具,包含TCP和UDP两种方式,可以用于生产环境
* toolbox 包含: 日志工具, 邮件工具和flask工具
* views  视图部分.
* zerorpc_test  zerorpc的测试工具包

## 相关技术文档

* [api文档](/views/api文档.md)
* [rpc文档](/rpc文档.md)

## 更新日志

* 2019-2-11 增加rpc客户端的账户密码检测,token验证的api和rpc功能