## jwt参数获取接口

======
> 接口地址：www.bhxxjs.cn:8080/bhxx/VerificationJwt
> 请求方式：get/post

**请求参数**
| 参数名 | 是否必须 | 类型 | 说明 |
|-----|-----|-------|-----|
| Auth（Headers） | 是 | String |http 请求头（647a5253c1de4812baf1c64406e9139） |

**用户登录账号请求成功**
```
{
    "message":"success",
    "signature": "加密用的key",
    "algorithm": "加密用的算法",
    "expire": "过期时间",
    "time": "key的生成时间, 2018-12-12 01:00:00 格式"
}
```

**auth头小于15分钟后生成新的token令牌** 同上
```
{
    "message":"success",
    "signature": "加密用的key",
    "algorithm": "加密用的算法",
    "expire": "过期时间",
    "time": "key的生成时间, 2018-12-12 01:00:00 格式"
}
```

**错误信息**
```
{
    "message":"错误信息"
}
```

**返回的错误编码**
| 错误编码 | 说明 |
|-----|-----|
| 401 | 请求头找不到Auth |
| 403 | 请求头Auth无效 |

## 登录接口
==========

> 接口地址：www.bhxxjs.cn:8080/bhxx/
> 请求方式：get/post
> 完整请求示范：www.bhxxjs.cn:8080/bhxx/login?login_name=17775127904&password=123456

**请求参数**
| 参数名 | 是否必须 | 类型 | 说明 |
|-----|-----|-------|-----|
| login_name | 是 | String | 用户登录名（手机号） |
| password | 是 | String | 登录密码 |
| auth（Headers） | 是 | String | http 请求头指定(647a5253c1de4812baf1c64406e91396) |

**请求成功**

* 系统给登录成功的用户分配一个登录id
* 系统将此登录id使用jwt加密后,放入token字段中,返回给客户端

```
{
    "message": "success",
    "token": "eyJhbGciOiJIUzI1NiJ9.ecCI6MTUzOTMxMDNH0.rFMO6FMBDPLqrIrQogA"  // 加密后的登录id
}
```
请求成功后.客户端每次请求都把token放入请求Headers的Token字段中用作身份凭证.
就像这样:

```
headers = {
    "Auth": "647a5253c1de4812baf1c64406e91396",
    "Token": "eyJhbGciOiJIUzI1NiJ9.ecCI6MTUzOTMxMDNH0.rFMO6FMBDPLqrIrQogA"
}
response = request.post(url, headers=headers)
```

**请求失败**
```
{
    "message": "错误信息"
}
```

##用户注册接口
============
> 接口地址: www.bhxxjs.cn:8080/bhxx/register
> 请求方式：post
> 完整请求: www.bhxxjs.cn:8080/bhxx/register?phone=177777777777&password=123456

**请求参数**
| 参数名 | 是否必须 | 类型 | 说明 |
|-----|-----|-------|-----|
| phone | 是 | String | 用户登录名（手机号） |
| password | 是 | String | 登录密码 |
| Auth（Headers） | 是 | String | http 请求头指定(647a5253c1de4812baf1c64406e91396) |

**请求成功**
```
{
    "message": "success"
}
```

**请求失败**
```
{
    "message": "错误信息"
}
```