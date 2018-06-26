# APP端接口文档

## 约定

### 一般性约定

* 下文中提到的"为空"的含义是指某一个变量/对象不存在，或者值为：null / None / undefined之类的情况.
* 除非特别说明，否则使用UTF-8字符集。
* 参数的命名方式采用下划线命名法，比如一个表示用户名的参数，应该命名为 user_name而不是userName或者username。
* 接口返回值一定是JSON化的键值对类型
* JSON格式的数据要进行urlencode，比如{"name":"张三"}转为JSON后应该是：{"name": \\u5f20\\u4e09}
* 尽量不使用布尔值而是使用字符串或者数字(比如:"1"和"0")来替代.

### 返回值约定

类型: json对象.
返回字段: 
> 1.message: 返回状态,字符串类型,只有在此字段等于字符串"success"时才表示服务器正确的响应了请求.可以用此返回字段验证请求是否成功.
> 2.error_code: 错误代码, 整数类型, *只有在服务器返回了已知错误的时候才会有此字段*.由于可以使用message返回错误原因,所以此参数其实处于冗余的状态.可能会在以后取消.
> 3.args: 本次请求的的参数,字典类型 *此参数只有在服务器没有正确响应的时候才会出现*,配合error_code返回客户端.由于可以使用message返回错误原因,所以此参数其实处于冗余的状态.可能会在以后取消.
> 4.data: 数据载荷, 字典类型.请求的结果被封装在此字典(键值对)对象中.并非所有的请求都会返回此字段.服务器出错时,不会返回此字段.

*使用javascript做示范*
```javascript
/*使用post方式请求接口,resp为服务器接口返回的对象*/
$.post(url,function(resp){
    let result = JSON.parse(resp);  // 把json对象转成字典(dict/object)对象.
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

### 身份验证机制

客户端在每次从服务器请求的数据的时候在request的headers中，添加一个auth_token的字符串(token)。用作身份验证.

>1.此token在登录成功后会从服务器返回.可以保存下来在日后的请求中使用.
>2.目前token的有效期为半年.不必每次打开程序都进行请求.

**出于安全原因,在请求头中只允许使用带中划线而不是下划线的字段名,此字段可以和客户端开发团队进行协商后重新定义**

## 接口

### <div id="1">(注册/登录)发送验证码</div>
url: /api/get_sms
method: get/post
args: phone_num //手机号码
request example： {"phone_num": 15989312321}
return: json对象。
success：{"message":"success"}  // 短信发送成功
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}

### <div id="2">用户注册</div>
url: /api/reg
method: post/get
args: username 用户名，password 密码， phone_num 手机号码 必须， random_code 短信验证码 必须
request example: {"phone_num": 15023231294, "random_code": 5839}
return: json对象
success：{"message":"success"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
description：注册成功后短信验证码失效，验证码最大有效期30分钟

### <div id="3">用户登录</div>
url: /api/login 
method: post/get
args: username 用户名，password 密码， phone_num 手机号码 必须， random_code 短信验证码 必须
request example: {"phone_num": 15023231294, "random_code": 5839}
return: json对象
success：{"message":"success"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
description：注册成功后短信验证码失效，验证码最大有效期30分钟

### <div id="4">用户登出</div>
url: /api/logout 
method: post/get
status: complete
args: token 登录凭证 必须
request example: {"token": ”4f4sfgff2343439kdrda“}
return: json对象
success：{"message":"success"}

### <div id="5">推送GPS数据</div>
api: /api/gps_push 
method: post/get
status: complete
args: 任意键值对格式
request example: {"latitude":1.2,"speed":12.4,"altitude":-7,….}
return: json对象
success：{"message":"success"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
args detail：
latitude = float # 纬度 
speed = float # 速度
token = str # token
user_id = str 用户的id
time = datetime.datetime # 时间
altitude = float # 海拔
longitude = float # 经度
**目前使用的是http协议,计划改为socket通讯,具体细节协商后定义.另外,客户端开发人员也可提出自己的需求订制接口**

### <div id="6">获取用户信息</div>
api: /api/get_user_info 
method: post/get
status: complete
args: token 登录token
request example: {"token":token}
return: json对象
success：{'message': 'success', 'data':个人信息的字典}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
个人信息的字典可能包含如下内容:
_id = str # 用户id，唯一
user_name = str # 登录名，唯一
user_password = str
head_img_url = str # 头像路径
real_name = str # 真实姓名
nick_name = str # 昵称
gender = str # 性别 男性，女性
age = int # 年龄
country = str # 国家
province = str # 省份
city = str # 城市
email = str # 电子邮件，可用来登录，唯一
phone_num = str # 手机号码，可用来登录，唯一
born_date = datetime.date # 出生日期
cars = list # 名下车辆的id，是一个牌照信息的id的List对象，默认为空 
user_status = int # 用户状态，1表示可以登录，0表示禁止登录
wx_id = str # 微信id 
weibo_id = str # 微博id 
create_date = datetime.datetime # 用户的注册/创建日期

### <div id="7">编辑用户信息</div>
api: /api/edit_user_info 
method: post/get
status: complete
args: token 登录token
request example: {"token":token}
return: json对象
success：{'message': 'success', 'data':个人信息的字典}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
可在请求中包含的参数如下:
user_password = str
head_img_url = str # 头像路径
real_name = str # 真实姓名
nick_name = str # 昵称
gender = str # 性别 男性，女性
age = int # 年龄
country = str # 国家
province = str # 省份
city = str # 城市
email = str # 电子邮件，可用来登录，唯一
phone_num = str # 手机号码，可用来登录，唯一
born_date = datetime.date # 出生日期
wx_id = str # 微信id 
weibo_id = str # 微博id 

### <div id="8">检查版本</div>
api: /api/check_version 
method: post/get
status: complete
args:无
request example: 无
return: json对象
success：{"version": 版本号, "url": 下载地址,"message": "success"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}

### <div id="9">用户上传头像/其他图片</div>
**此接口的url语法有歧义,建议与客户端开发人员协商后重新定义,**
url: /api/upload_[key]    
method: post
status: complete
注意,此接口支持表达式路由.已知的的表达式路由如下:
/api/upload_avatar 用户上传头像
args: avatar 头像文件 必须
/api/upload_permit_image 用户上传行车证照片
args: permit_image 行车证照片文件 必须
request example： 无
return: json对象。
success：{"message":"success"，"data": "​http://图片全路径"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
description:此接口可以扩展

### <div id="10">用户查询/编辑行车证信息</div>
url: /api/[key]_vehicle_info
method: post
status: complete
注意,此接口支持表达式路由.已知的的表达式路由如下:
/api/get_vehicle_info 用户获取行车证信息
args: 无 
return: json对象。
success：{"message":"success"，"data": 行车证数据字典}
行车证数据字典={
"_id": str类型 # id 唯一
"user_id": str类型 # 关联用户id 和plate_number构成了联合唯一主键。
"permit_image_url": str类型 # 车辆照片url
"plate_number": str格式 # 车辆号牌 和user_id构成了联合唯一主键。
"car_type": str格式 # 车辆类型 比如 重型箱式货车
"owner_name": str格式 # 车主姓名/不一定是驾驶员
"address"] = str # 地址
"use_nature: str格式 # 使用性质
"car_model": str格式 # 车辆型号 比如 一汽解放J6
"vin_id": str格式 # 车辆识别码/车架号 
"engine_id": str格式 # 发动机号
"register_city": str格式 # 注册城市,
"register_date": str格式 类似"2017-12-12" # 注册日期
"issued_date": str格式 类似"2017-12-12" # 发证日期
"create_date": str格式 类似"2017-12-12" # 创建日期
}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
/api/edit_vehicle_info 用户获取行车证信息
args: 任何合法的字段,具体字段名参考上面的'行车证数据字典',必须包含"_id"这个参数 必须
request example： 无
return: json对象。
success：{"message":"success"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
description:此接口可以扩展

### <div id="11">根据地址查询经纬度</div>
*此接口本质上是调用了高德地图的接口,在app端也可以直接调用,更便捷.*
api: /api/query_geo_coordinate 
method: post/get
status: complete
args:
1.token headers登录标识 必须
2.city 城市名 必须
3.address 地址 必须
request example: {"city":"上海市", "address":"新源路昌吉东路"}
return: json对象
success：{"message": "success"， “longitude”： “经度”, "latitude": "纬度"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}

### <div id="12">安全指数相关接口</div>
**此类接口目前返回的都是虚拟数据,建议重新约定**

### <div id="13">添加违章查询器</div>
**此类接口(违章查询相关接口)业务逻辑不太合理,建议重新设计**
api: /api/add_violation_shortcut 
method: post/get
status: complete
args:
1.token 登录标识 必须
2.plate_number 车牌 必须
3.city 查询城市 必须
4.engine_id 发动机号 必须
5.vin_id 车架号 必须,
request example: {"token": token, "plate_number":plate_number, "city": city, "engine_id": engine_id, "vin_id": vin_id}
return: json对象
success：{"message": "success", "data": violation_shortcut_id}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
args detail:
violation_shortcut_id : violation_shortcut对应的id

### <div id="14">删除违章查询器</div>
**此类接口(违章查询相关接口)业务逻辑不太合理,建议重新设计**
api: /api/delete_violation_shortcut 
method: post/get
status: complete
args:
1.token headers登录标识 必须
2._id 查询器id 必须
request example: {"_id":查询器id}
return: json对象
success：{"message": "success"}
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}

### <div id="15">查询违章</div>
**此类接口(违章查询相关接口)业务逻辑不太合理,建议重新设计**
api: /api/query_violation 
method: post/get
status: complete
args:\ 1.token 登录标识 必须
2._id 查询器id 必须
request example: {"token": token, "_id":_id}
return: json对象
success：{"message": "success", "data": 查询结果的字典 }
error：{“message": "错误原因", "error_code":"错误代码", "args": "相关参数"}
result description:
_id: 查询的结果集id
generator_id: 查询器id，这个和请求阐述中的_id保持一致
amount: 违章共计 
create_date: 查询结果的生成时间，注意，返回的可能是历史的查询记录
total_fine: 未处理违章共计需缴纳的罚金
untreated : 未处理违章次数
user_id: 关联用户的id。
violations: violation_list 违章记录的数据对象。
单个违章记录的参数如下：
_id: 违章记录id
address： 违章时间发生的地址
latitude: 事发地的纬度
longitude: 事发地的经度
real_value: true 是否真实经纬度 ，布尔值
can_select : 能否进行处理？1为可以0为不可以
city: 违章时间发生的城市
code: 违章编码，交管局备案号码 同一交管局唯一
fine： 罚金 
payment_status：支付状态，2表示已支付
point: 扣分 
process_status: 处理状态 1，未处理，2.处理中， 3.已处理，4不支持操作
reason：违章内容
violation_num: 违章编码，类型错误码
time: 违章时间