# API列表

持续更新中....

> 项目名称: 交易信息服务器  地址: 47.106.68.161  端口号: 8000

*参考资料*
*JWT官网地址 https://jwt.io*

JWT有很多Java的实现,具体请参考JWT观望,下面只举两个Java的JWT实现的例子:

1. java-jwt 仓库地址 https://github.com/auth0/java-jwt
2. jjwt  仓库地址 https://github.com/jwtk/jjwt



* [一般性约定](#1) 
* [加密方式](#2) 
* [请求](#3)

## 接口

* [换取服务器签名和算法](#4)
* [企业用户登录](#5)
* [分页查询司机简历](#6)

## 约定

### <span id="1">一般性约定</span>

#### 除换取signature(签名)的接口外,其他接口发送数据都需要JWT进行加密

#### 返回的数据分为加密和不加密两种.

>1. 除去换取签名和算法的接口外,都是加密接口.
>2. 服务器返回的数据原则上不使用加密(特殊协商的除外).
>3. 客户端以加密方式发起请求时,先将参数组织成键值对格式,然后加密后的密文,以payload为参数名发送到服务器.
>4. 返回的数据是转成json格式的键值对对象.
>5. 返回的键值对对象的例子{"message":"success", "data": data}其中data是返回的数据载荷,不一定有.

## <span id="2">加密方式</span>

使用jwt加密,算法默认 HS256

### 加密的步骤如下:

1. 确认参数只能是以下类型之一:整形,浮点, 数组,字符串, 字典.
2. 将所有参数打包成一个字典对象.
3. 对此字典对象使用约定的signature(签名)和algorithm(算法)进行加密.
4. 将加密后的字典(这时候应该变成了一段字符串格式的密文了),用payload做参数名发送给服务器.
5. 等待服务器返回信息.
6. 从返回结果的payload字段中取回返回的密文.
7. 使用约定的signature(签名)和algorithm(算法)进行解密.

一个javascript语言的例子

```javascript
var http = require("http");
var url = require("url");
var jwt = require('jsonwebtoken');
var cert = "bbb5fd48094942be80dbf0467be3d6f6";   // 请用实际的值替换


function start() {
    function onRequest(request, response) {
        var token = url.parse(request.url).pathname;
        token = token.slice(1); // 去掉路径的/
        /*
        jwt.verify(token, cert, { algorithms: ['HS256'] }, function(error, payload) {
            console.log(error);
            console.log(payload);
        });
        */
        var res = jwt.decode(token, { "cert": cert, algorithms: ['HS256'] });
        console.log(res);
        response.writeHead(200, { "Content-Type": "text/javascript;charset=utf-8" });
        response.write(JSON.stringify(res));
        response.end();
    }
    http.createServer(onRequest).listen(3000);
    console.log("Server has started.");
}
start();

```

## <span id="3">请求</span>

请求分加密请求和不加密请求两种.

### 非加密请求

**非加密请求会将多个参数同时发送到服务器端*

举例说明

```javascript
/*一个不需要加密的请求的例子*/
let api = "/check_something";   // 接口地址
let server = "http://192.168.0.99:7001";  // 服务器地址和端口
let url = server + api;             // 拼接请求的url
let user_name = "x_user";  
let user_password = "123455"; 
let user_sex = "male"; 
let args = {
    "user_name": user_name, 
    "user_password": user_password,
    "user_sex": user_sex
    };
$.post(url, args, function(resp){
    let result = JSON.parse(resp);  // 返回结果是json,转成字典
    let message = result['message'];
    if( message == 'success'){
        // 请求成功.
        let data = result['data'];  // 取出数据载荷
        console.log(data);
    }
    else{
        // 请求失败
        let error_reason = message;
        alert(error_reason);  // 弹出错误提醒
    }
});
```

### 加密请求

**加密请求会将所有参数封装为请求载荷后发送到服务器端*

举例说明

```javascript
/*一个需要加密的请求的例子*/
let jwt = require('jsonwebtoken');
let api = "/check_something";   // 接口地址
let server = "http://server:port";  // 服务器地址和端口
let url = server + api;             // 拼接请求的url
let user_name = "x_user";  
let user_password = "123455"; 
let user_sex = "male"; 
let args = {
    "user_name": user_name, 
    "user_password": user_password,
    "user_sex": user_sex
    };
let signature = "xxxx";   // 从服务器获取的用于加密的签名.
let algorithm = "HS256";   // 从服务器端获取的加密算法
let payload = jwt.sign(args, signature, {"alorithm": algorithm});
$.post(url, {"payload": payload}, function(resp){
    let result = JSON.parse(resp);  // 返回结果是json,转成字典
    let message = result['message'];
    if( message == 'success'){
        // 请求成功.
        let data = result['data'];  // 取出数据载荷,注意这里是密文
        // 具体解密方式请参考对应的类库文档
    }
    else{
        // 请求失败
        let error_reason = message;
        alert(error_reason);  // 弹出错误提醒
    }
});
```

## API接口说明

### <span id="4">换取服务器签名和算法</span>

>客户端在进行加密通讯之前,需要通过此接口获取服务器的数字签名和算法. 

**url**:  /identity/get_signature

**加密**: 否

**参数**：

``` javscript
sid      换取signature的id   字符串类型 目前是固定值 18336048620
```

**返回类型**： json
 
**返回结构**：

```javascript
// 成功
{
    "message": "success",
    "data": data
 }
 // 失败
{
    "message": "错误原因"
 }
```

**返回说明**：

* message: 返回状态消息，字符串类型，只有在等于字符串“success”的时候才表示返回结果正确，否则，这里出现的将是返回错误的原因。
* data: 数据字典。
 
**data**: 

```javascript
{
    "signature": signature,  // 数字签名,后继的加密要用到,请保存直到过期.
    "algorithm": algorithm   // 加密算法,后继的加密要用到,请保存直到过期.
}
```

### <span id="5">企业用户登录</span>

>企业用户的登录接口.

**url**:  /api/login_company

**加密**: 是

**参数**：

```javascript
 user_name      用户名   字符串类型  当前可用的用户名: jack
 user_password   密码    字符串类型  当前可用的密码: 123456
```

**返回类型**： json

**返回结构**：

```.javascript
    {
        "message": "success",
        "data": data
    }
```

**返回说明**：

* message: 返回状态消息，字符串类型，只有在等于字符串“success”的时候才表示返回结果正确，否则，这里出现的将是返回错误的原因。
* data: 密文数据。

**data**: 本例不返回密文数据,message的结果可判断企业登录的身份验证是否正确.

### <span id="6">分页查询司机简历</span>

>按照页码和过滤条件,分页从服务器查询司机简历.

**url**:  /api/driver_page

**加密**: 是

**参数**：

```javascript
 // 本接口查询参数为复合型.需具体商议
```

**返回类型**： json

**返回结构**：

```.javascript
    {
        "message": "success",
        "data": data
    }
```

**返回说明**：

* message: 返回状态消息，字符串类型，只有在等于字符串“success”的时候才表示返回结果正确，否则，这里出现的将是返回错误的原因。
* data: 密文数据。

**data**: 司机简历字典组成的数组对象.