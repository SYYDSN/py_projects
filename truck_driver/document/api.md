# API列表

*[hello](#login_func2")

# API接口说明

### <span id="login_func">企业用户登录</span>

>企业用户的登录接口. 

url:  /web/login_company

参数：

 * user_name     用户名 字符串类型
 * user_password 密码   整形
 
 返回类型： json
 
 返回结构：
 
 {
    "message": "success",
    "data": data  
 
 }
 
返回说明：

 * message: 返回状态消息，字符串类型，只有在等于字符串“success”的时候才表示返回结果正确，否则，这里出现的将是返回错误的原因。
 * data: 返回的数据，一般是字典类型，特殊约定也可以返回数组类型。注意，此字段只有在成功返回时才存在。
 

### <span id="login_func2">企业用户登录</span>