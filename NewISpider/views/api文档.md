# 前端接口文档

这里的视图提供的是Restful的准标准接口文档.主要是为前端提供接口参考. 后端的接口文档,请参看根目录下的[rpc文档](/rpc文档.md)

## 用过身份验证的接口部分.

### 用户登录接口

url组成: /oauth/v1.0/user/user_login
请求参数:

```javascript
var login_type = "page";  // 登录方式,字符串,共计有网页登录/page,微信登录/wx,面部识别登录/face等多种.目前仅支持网页登录(使用参数"page")
var hotel_id = 1; // 酒店id, 整数格式. 调试阶段可以不传此参数.
var user_name = "user_name";  // 用户名, 字符串格式.
var password = "password";  // 用户密码, 字符串格式
```

