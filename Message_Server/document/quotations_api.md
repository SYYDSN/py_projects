# 行情推送API列表

持续更新中....

> 项目名称: 行情服务器  地址: 47.106.68.161  端口号: 8000 


* [一般性约定](#1) 

## 接口

* [推送消息](#2)

## 约定

### <span id="1">一般性约定</span>

>#### 字符集统一使用utf-8
>#### 参数名不区分大小写.统一使用小写.命令方法使用下划线命名法
>#### 不使用true和false表示布尔值,而是使用1和0的整形替代.
>#### 除非特别说明,所有的接口都支持get和post两种方式.
>#### 除非特别说明,返回值都是json格式.
>#### 除非特别说明,返回 {"message": "success"}表示请求成功

## 接口

### <span id="2">推送产品报价</span>

> 用于接收推送的产品报价

**url**: /quotations/listen

**method**: post/get

**args**: 

* platform_name:  平台名称 字符串类型 必须
* platform_account: 平台帐号 字符串类型  必须
* platform_time: 平台时间 字符串类型 格式(2018-12-12 01:01:01)  必须
* data: 产品报价数据载荷  json类型  必须
```javascript
    data = [
        {"code": "XAUUSD", "name": "黄金美元", "price": "1233.32"},
        {"code": "XAGUSD", "name": "白银美元", "price": "15.459"},
        ...
    ]

```

**request example**:

```javascript
// 一个完整的请求的例子,使用javascript演示
var url = "http://47.106.68.161:8000/quotations/listen";
var platform_name = "平台1";
var platform_account = "user_01";
var platform_time = "2018-8-8 12:00:00";
var data = [
    {"code": "XAUUSD", "name": "黄金美元", "price": "1233.32"},
    {"code": "XAGUSD", "name": "白银美元", "price": "15.459"}
];
data = JSON.stringify(data);   // 把data从数组格式转换为json格式
var args = {
    "platform_name": platform_name, 
    "platform_account": platform_account,
    "platform_time": platform_time,
    "data": data
};

/*
* 可以使用get和post两种方式发送数据.
* */

$.get(url, args, function(resp){
    // get方式发送数据的例子
    var resp = JSON.parse(resp);
    var mes = resp['message'];
    if(mes == "success"){
        // 发送成功
    }
    else{
        // 发送失败
    }
});

$.post(url, args, function(resp){
    // post方式发送数据的例子
    var resp = JSON.parse(resp);
    var mes = resp['message'];
    if(mes == "success"){
        // 发送成功
    }
    else{
        // 发送失败
    }
});

```

```python3
# 一个完整的请求的例子,使用python演示
import requests
import json


url = "http://47.106.68.161:8000/quotations/listen"
platform_name = "平台1"
platform_account = "user_01"
platform_time = "2018-8-8 12:00:00"
data = [
    {"code": "XAUUSD", "name": "黄金美元", "price": "1233.32"},
    {"code": "XAGUSD", "name": "白银美元", "price": "15.459"}
]
data = json.dumps(data)   # 把data从数组格式转换为json格式
args = {
    "platform_name": platform_name, 
    "platform_account": platform_account,
    "platform_time": platform_time,
    "data": data
}


# 可以使用get和post两种方式发送数据.

# 1. 使用post方式发送数据
r = requests.post(url, data=args)
resp = r.json()
if resp['message'] == "success":
    # 成功
    pass
else:
    # 失败
    
# 2. 使用get方式发送数据
r = requests.post(url, data=args)
resp = r.json()
if resp['message'] == "success":
    # 成功
    pass
else:
    # 失败
```
    

**return type**: json

**success example**: {"message": "success"}

**error example**: {"message": "错误原因"}

**tips**:

1. 签名错误时会返回404的错误(测试阶段没有数字签名)

