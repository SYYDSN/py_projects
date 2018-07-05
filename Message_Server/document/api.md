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
* [推送事件消息](#5)
* [事件字段约定](#6)

## 约定

### <span id="1">一般性约定</span>

#### 参数名不区分大小写.建议使用小写.命令建议使用下划线命名法

#### 除换取signature(签名)的接口外,其他接口发送数据都需要JWT进行加密

#### 返回的数据分为加密和不加密两种.

>1. 除去换取签名和算法的接口外,都是加密接口.
>2. 服务器返回的数据原则上不使用加密(特殊协商的除外).
>3. 客户端以加密方式发起请求时,先将参数组织成键值对格式,然后加密后的密文,以payload为参数名发送到服务器.
>4. 返回的数据是转成json格式的键值对对象.
>5. 返回的键值对对象的例子{"message":"success", "data": data}其中data是返回的数据载荷,不一定有.

## <span id="2">加密方式</span>

**使用jwt加密**
**算法默认 HS256**
**signature最长有效期7200秒**
**signature在到期前五分钟就会生产新的signature,在这5分钟内,新旧signature都是有效的**

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
/*一个不需要加密的请求的例子(换取signatrue和algorithm)*/
let api = "/mt4/secret";   // 接口地址
let server = "http://47.106.68.161:8000";  // 服务器地址和端口
let url = server + api;             // 拼接请求的url
let sid = "bbb5fd48094942be80dbf0467be3d6f6";  
let args = { "sid": sid };
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
/*一个需要加密的请求的例子(提交出入金事件)*/
let jwt = require('jsonwebtoken');
let api = "/mt4/message/push";   // 接口地址
let server = "http://47.106.68.161:8000";  // 服务器地址和端口
let url = server + api;             // 拼接请求的url
let args = {
    "title": "提交入金",                          // 出入金事件
    "mt4_account": "800123",                     // MT4账号
    "user_name": "张三",                          // 客户姓名
    "user_parent_name": "李四",                   // 上级姓名
    "deposit_order": "121222222222222",          // 入金单号
    "deposit_money": 1500.00,                    // 出入金金额
    "status": "待支付",                           // 状态
    "operate_time": "2018-07-5 12:45:30"         // 操作事件
    };
let signature = "a5a0c6c151f7485ebbc416bcd0c278b5";   // 从服务器(/mt4/secret接口)获取的用于加密的签名.
let algorithm = "HS256";                              // 从服务器(/mt4/secret接口)端获取的加密算法
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

**url**:  mt4/secret

**method**:  get/post

**加密**: 否

**参数**：

``` javscript
sid      换取signature的id   字符串类型 目前是固定值 bbb5fd48094942be80dbf0467be3d6f6
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
    "algorithm": algorithm,  // 加密算法,后继的加密要用到,请保存直到过期.
    "expire": 7100           // 还有多少秒签名到期? 要配合接收签名的时间来计算是否过期?
}
```

### <span id="5">推送事件消息</span>

>推送事件到服务器.

**url**:  /api/login_company

**method**:  get/post

**加密**: 是

**参数**：

```javascript
 payload      加密后的密文   字符串类型  
```

**返回类型**： json

**返回结构**：

```.javascript
    {
        "message": "success"     // 成功
    }
    /*
    {
        "message": "signature验证失败"     // 失败
    }
    */
```

**返回说明**：

* message: 返回状态消息，字符串类型，只有在等于字符串“success”的时候才表示返回结果正确，否则，这里出现的将是返回错误的原因。

**一般逻辑步骤**

> 1. 检查signature是否存在?
> 1.1. 不存在.转到2.
> 1.2. 存在.检查signature是否过期?
> 1.2.1 signature过期,转到2
> 1.2.1 signature有效.转到3
> 2. 从服务器获取signature和algorithm.
> 3. 使用JWT加密事件信息向服务器推送.
> 3.1 返回{"message": "success"} 转到5
> 3.2 返回的错误的消息,转到4
> 4. 检查错误消息,进行对应的处理.转到3
> 5. 成功

### <span id="6">事件字段约定</span>

提交入金事件
```javascript
"title": "提交入金",                          // 事件标题    字符串       必须
"mt4_account": "800123",                    // MT4账号    字符串        必须
"user_name": "张三",                         // 客户姓名    字符串       必须
"user_parent_name": "李四",                  // 上级姓名    字符串       必须
"deposit_order": "121222222222222",         // 入金单号    字符串       必须
"deposit_money": 1500.00,                   // 出入金金额   带符号浮点,正代表入金,负代表出金 必须
"status": "待支付",                          // 状态        字符串       必须
"operate_time": "2018-07-5 12:45:30"        // 操作时间     字符串格式时间 必须
```
入金成功事件
```javascript
"title": "入金成功",                          // 事件标题    字符串       必须
"mt4_account": "800123",                    // MT4账号    字符串        必须
"user_name": "张三",                         // 客户姓名    字符串       必须
"user_parent_name": "李四",                  // 上级姓名    字符串       必须
"deposit_order": "121222222222267",         // 入金单号    字符串       必须
"deposit_money": 1500.00,                   // 入金金额   带符号浮点     必须
"status": "已支付",                          // 状态        字符串       必须
"operate_time": "2018-07-5 12:45:30"        // 操作时间     字符串格式时间 必须
```
出金处理事件
```javascript
"title": "	出金处理",                        // 事件标题    字符串       必须
"mt4_account": "800123",                    // MT4账号    字符串        必须
"user_name": "张三",                         // 客户姓名    字符串       必须
"user_parent_name": "李四",                  // 上级姓名    字符串       必须
"withdrawal_order": "12122222456221",       // 入金单号    字符串       必须
"withdrawal_money": 1500.00,                // 入金金额   带符号浮点     必须
"status": "已扣款",                          // 状态        字符串       必须
"operate_time": "2018-07-5 12:45:30"        // 操作时间     字符串格式时间 必须
```
待审核客户事件
```javascript
"title": "	待审核客户",                      // 事件标题    字符串       必须
"user_name": "张三",                         // 客户姓名    字符串       必须
"user_parent_name": "李四",                  // 上级姓名    字符串       必须
"update_time": "2018-07-5 12:45:30"         // 更新时间    字符串格式时间 必须
```
""