# NewISpider 接口文档格式约定

NewISpider 系统以微服务的方式进行部署.其中微服务的部署方式分为2种:

* RESTFUL
* RPC

两种部署方式的接口文档描述略有不同


## RESTFUL 接口

描述由以下部分组成

* 参数和规范  必须
* 行为说明 必须
* 请求和返回示范  非必须
* 例外的情况   非必须

各部分的内容如下:

* Host:  主机地址. 也可以在文档头部一次性制定.
* Port: 访问端口. 也可以在文档头部一次性制定.
* Method:  访问方法. 可能是get, post 或者同时支持 get/post
* Request Args:  请求参数 可能为空.如果不为空的情况下.请使用代码片段逐个描述参数的名称. 类型, 说明和 是否必须.(如果是前后端都需要使用的接口,请使用javascript代码片段描述, 如果仅仅是后端使用的接口,可以使用python语言来描述)

```javascript
var user_name = "zhangsan";   // 用户名 字符串格式  用户的登录账户  必须
var password = "123456";      // 用户密码  字符串格式  必须是用md5加密后的密码 必须
```

* Response Args:  返回参数 请把返回体中,除去使用无序列表逐个描述参数的名称. 类型, 说明和 是否必须..(如果是前后端都需要使用的接口,请使用javascript代码片段描述, 如果仅仅是后端使用的接口,可以使用python语言来描述)

```javascript
var resp = {
    "message": "success",
    "data": {
        "id": 12,
        "user_name": "zhangsan", // 用户名 字符串格式 
        "password": "123456",    // 用户密码  字符串格式
        "role_id": 1,            // 角色id  整形  用户所在的权限组的id
        "role_name": "root",     // 角色名  字符串 用户所在权限组的名称
        "wx": "ere34343-"        // 为信号  字符串 用户微信号 不一定有
    }
};
```


