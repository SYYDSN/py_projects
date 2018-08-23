/*
 * @Author: mikey.zhaopeng 
 * @Date: 2018-07-31 09:39:07 
 * @Last Modified by: mikey.zhaopeng
 * @Last Modified time: 2018-07-31 13:17:47
 */
/*
 * @Author: mikey.zhaopeng 
 * @Date: 2018-07-31 09:38:58 
 * @Last Modified by:   mikey.zhaopeng 
 * @Last Modified time: 2018-07-31 09:38:58 
 */


### 微信用户的数据结构

```python3
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str
    type_dict['email'] = str
    type_dict['address'] = str  # 地址
    type_dict['nick_name'] = str
    type_dict['sex'] = int
    type_dict['openid'] = str
    type_dict['unionid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str
    type_dict['head_img_url'] = str  # 头像图片地址
    type_dict['subscribe'] = int   # 是否已关注本微信号
    type_dict['subscribe_scene'] = str   # 用户关注的渠道来源
    type_dict['subscribe_time'] = datetime.datetime   # 用户关注的时间
    type_dict['access_token'] = str  # 访问access_token
    type_dict['expires_in'] = int  # access_token的过期时间
    type_dict['time'] = datetime.datetime  # access_token的获取时间
    type_dict['refresh_token'] = str  # access_token的refresh_token
    type_dict['role'] = int  # 角色: 1为销售人员 2为中介商 3为黄牛 为空/0是一般人员
    """以下是一般用户/司机专有属性"""
    type_dict['resume_id'] = ObjectId  # 简历id
    type_dict['relate_time'] = datetime.datetime  # 和人力资源中介的关联时间
    type_dict['relate_id'] = ObjectId  # 人力资源中介_id,也就是Sales._id,用于判断归属.
    """以下Sales类专有属性"""
    type_dict['checked'] = int  # 是否已通过兼职/销售/中介的审核? 0/不存在忽略, 1是申请中未通过. 2是申请通过, -1是驳回.
    type_dict['reject_reason'] = str  # 申请驳回原因,只有在checked字段是-1状态,本字段才有效
    type_dict['authenticity'] = bool  # 中介商/黄牛/销售 的真实性确认. 在审核通过后这个字段为真
    type_dict['relate_image'] = str  # 中介商名字/销售二维码图片地址,这个图片保存在微信服务器上.
    type_dict['name'] = str  # 中介商名字/销售真实姓名.用于展示在二维码上
    type_dict['contacts'] = str  # 中介公司联系人,如果是黄牛/销售,那么这里可以和注册用户的real_name是同一人
    type_dict['contacts_num'] = str  # 中介公司联系电话,如果是黄牛/销售,那么这里可以和注册用户的phone一致
    type_dict['contacts_email'] = str  # 中介公司/黄牛/销售联系邮箱,这个是专门用来发送结算信息的
    type_dict['identity_code'] = str  # 中介商执照号码/销售真实身份证id.用于部分展示在二维码上
    type_dict['business_license_image_url'] = str  # 营业执照照片的地址,
    type_dict['business_license_image'] = ObjectId  # 营业执照照片的id, 指向BusinessLicenseImage._id
```

### 简历模型

基础字段是指除去

1. (list和dict)
2. 动态生成的字段

之外的非复合字段

```python3
    type_dict['_id'] = str           # id. 24位字符串
    type_dict['app_id'] = str     # app用户的id,24位字符串
    type_dict['wx_id'] = str     # 微信用户的id,24位字符串
    type_dict['user_name'] = str  # 用户名,唯一判定,默认和手机相同,可以登录司机招聘网(功能未实现)
    type_dict['real_name'] = str  # 真实姓名 ,可以从驾驶证取
    type_dict['head_image'] = str  # 头像id, 24位字符串
    type_dict['gender'] = str   # 以驾驶证信息为准. 男/女
    type_dict['married'] = int  # 婚否? 0/1/-1 未婚/已婚/离异  None 空白
    type_dict['birth_place'] = str   # 籍贯/出生地
    type_dict['living_place'] = str   # 居住地,
    type_dict['address'] = str  # 家庭地址
    type_dict['phone'] = str  # 手机号码
    type_dict['email'] = str  # 邮箱
    type_dict['birth_date'] = datetime.datetime  # 出生日期,以身份证号码为准
    type_dict['id_num'] = str  # 身份证号码
    type_dict['id_image_face'] = ObjectId  # 身份证正面图片
    type_dict['id_image_face_url'] = str  # 身份证正面图片
    type_dict['id_image_back'] = ObjectId  # 身份证背面图片
    type_dict['id_image_back_url'] = str  # 身份证背面图片
    type_dict['age'] = int  # 年龄 以身份证号码为准
    type_dict['driving_experience'] = int  # 驾龄 单位 年 用驾驶证信息中的首次领证日期计算
    type_dict['industry_experience'] = int  # 从业年限 单位 年 用道路运输从业资格证信息中的首次领证日期计算
    type_dict['work_experience'] = int  # 工作年限 单位 年 依赖first_work_date属性

    """
    学历分以下几种:
    1. 初等教育(小学及以下)
    2. 中等教育(中学,含初中,高中,职高,中专,技校)
    3. 高等教育(大专)
    4. 高等教育(本科及以上)
    """
    type_dict['education'] = int  # 学历,学历代码见注释
    """教育经历部分,是Education的ObjectId的list对象"""
    type_dict['education_history'] = list
    type_dict['status'] = int  # 任职/经营 状态. -1 个体经营/0 离职/ 1 在职
    """驾驶证信息 Driving License,简称dl"""
    type_dict['dl_image'] = str  # 驾驶证图片,.24位字符串
    type_dict['dl_image_url'] = str  # 驾驶证图片 url 地址
    type_dict['dl_license_class'] = str  # 驾驶证信息.驾驶证类型,准驾车型 英文字母一律大写
    type_dict['dl_first_date'] = datetime.datetime  # 驾驶证信息 首次领证日期
    type_dict['dl_valid_begin'] = datetime.datetime  # 驾驶证信息 驾照有效期的开始时间
    type_dict['dl_valid_duration'] = int  # 驾驶证信息 驾照有效持续期,单位年
    """道路运输从业资格证部分,Road transport qualification certificate 简称rtqc"""
    type_dict['rtqc_image'] = str  # 道路运输从业资格证信息,照片 24位字符串
    type_dict['rtqc_license_class'] = str  # 道路运输从业资格证信息.货物运输驾驶员/危险货物运输驾驶员
    type_dict['rtqc_first_date'] = datetime.datetime  # 道路运输从业资格证信息 首次领证日期,用于推定从业年限
    type_dict['rtqc_valid_begin'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的开始时间
    type_dict['rtqc_valid_end'] = datetime.datetime  # 道路运输从业资格证信息 资格证的有效期的结束时间
    """某些司机自己有车辆"""
    type_dict['vehicle'] = list  # 车辆信息, Vehicle.的ObjectId对象
    """求职意愿"""
    type_dict['want_job'] = bool  # 是否有求职意向?有求职意向的才会推荐工作,可以认为这是个开关.
    type_dict['remote'] = bool  # 是否原因在外地工作?
    type_dict['target_city'] = str  # 期望工作城市,这是一个临时性的字段,地区编码库完善后,此阻断将由 expected_regions替代.
    """留下,暂时不用,只有愿意不愿意取外地工作这个选项"""
    type_dict['expected_regions'] = list    # 期望工作地区,list是区域代码的list,
    """
     期望待遇,2个int元素组成的数组.第一个元素表示待遇下限,第二个元素表示待遇上限.  
     如果只有一个元素,则代表下限.
     如果没有元素,代表待遇面议.
     超过2个的元素会被抛弃.
     元素必须是int类型
    """
    type_dict['expected_salary'] = list   # 期望待遇
    """熟悉线路"""
    type_dict['routes'] = list  # 熟悉线路,城市名称组成的数组的的list
    """工作履历部分,是WorkHistory.的ObjectId的list对象"""
    type_dict['work_history'] = list
    type_dict['last_company'] = str  # 最后工作的公司,仅仅为列表页而添加,需要更新工作经历时同步
    type_dict['first_work_date'] = datetime.datetime  # 最早的工作时间,由最早的工作经历确定.可以用来计算工龄.需要更新工作经历时同步
    """
    最后的工作截至时间. 需要配合status字段使用:
    1. 如果这个值不存在.status==1,那就是在职没添加过工作简历. 
    2. 如果这个值不存在.status!=1,那就是离职没添加过工作简历. 
    由于目前的ORM的datetime字段不能赋值为None,所以在清除所有的工作经历时需要删掉此字段
    """
    type_dict['end_work_date'] = datetime.datetime
    type_dict['self_evaluation'] = str  # 自我评价
    """获奖/荣誉证书 Honor._id的list对象"""
    type_dict['honor'] = list
    type_dict['update_date'] = datetime.datetime  # 简历的刷新时间
    type_dict['create_date'] = datetime.datetime  # 简历的创建时间
```

### 获取短信验证码

地址: /wx/sms/get
方法: post/get
参数:

* phone 手机号码 字符串类型

返回类型: json
成功返回:

```javascript
{"message": "success"}
```

失败返回:

```javascript
{"message": "错误的手机号码"}
```

### 验证短信验证码

地址: /wx/sms/check
方法: post/get
参数:

* phone 手机号码 字符串类型
* code  验证码  字符串类型

返回类型: json
成功返回:

```javascript
{"message": "success"}
```

失败返回:

```javascript
{"message": "验证码错误"}
```

### 添加/修改简历基本信息

说明:

* 简历分为基础信息和扩展信息2部分,本接口是对基础信息的操作
* 简历一旦建立,只能修改不能删除
  
地址: /wx/resume/opt
方法: post/get
参数:

* 所有简历的数据模型的基本字段都可以作为字段传入,简历的字段请参考简历模型

举例说明:

```javascript
    let args = {
        "real_name": "张三",
        "married": 1,
        ...
    }
    $.post("/wx/resume/opt", args, function(resp){
        let json = JSON.parse(resp);
        if(json['message'] === "success"){
            // 成功
        }
        else{
            // 失败
        }
    });
```

返回类型: json
成功返回:

```javascript
{"message": "success"}
```

失败返回:

```javascript
{"message": "错误原因"}
```

### 添加/修改简历基本信息

以下信息属于扩展信息：

1. 工作经历
2. 所获荣誉
3. 自有车辆
4. 教育经历

说明:

* 简历分为基础信息和扩展信息2部分,本接口是对扩展信息的操作
* 扩展信息可以增加/删除/修改
  
地址: /wx/resume/extend
方法: post/get
参数:
此接口的参数分为三大类：

1. resume_id 简历id， 由后台传入，取简历id的方法如下：
```html
<body>
    ...
    <span id="resume_id" style="display:none">{{ user.resume_id }}</span>
    ...
</body>
<script>
...
var resume_id = $("#resume_id").text();  
/*
注意：扩展信息接口的简历id的参数名叫：resume_id,
基本信息接口的简历id的参数叫_id
*/
...
</script>
```

2. opt 操作类型， 字符串。目前共有9类，代表不同的操作。还在不断扩展中

```javascript
1. 添加工作经历  add_work
2. 编辑工作经历  update_work
3. 删除工作经历  delete_work

4. 添加教育经历  add_education
5. 修改教育经历  update_education
6. 删除教育经历  delete_education

7. 添加荣誉  add_honor
8. 修改荣誉  update_honor
9. 删除荣誉  delete_honor

10. 添加车辆  add_vehicle
11. 修改车辆  update_vehicle
12. 删除车辆  delete_vehicle
```

3. 其他参数部分，如果是删除操作，就不需要其他参数，如果是添加扩展信息，这里就是扩展信息的对应的字段。

* 所有简历的扩展信息的字段都可以作为字段传入,字段请参考对应的模型

举例说明:

```javascript
    // 新增一段工作履历
    let args = {
        "resume_id": "你的简历id",
        "opt": "add_work",    // 表明这是新增工作经历
        "begin": "2010-12-1",  // 工作开始时间
        "end": "2015-12-1",  // 工作结束时间
        "enterprise_name": "顺丰速运", // 公司名称
        "post_name": "司机",       // 岗位名称
        ...
    }
    // 修改一段工作经历
    let args = {
        "resume_id": "你的简历id",
        "opt": "update_work",    // 表明这是修改工作经历
        "w_id": "rrt4545454121212",  // 履历id
        "begin": "2010-12-1",  // 工作开始时间
        "end": "2015-12-1",  // 工作结束时间
        "enterprise_name": "顺丰速运", // 公司名称
        "post_name": "司机",       // 岗位名称
        ...
    }
    // 删除一段工作经历
    let args = {
        "resume_id": "你的简历id",
        "opt": "delete_work",    // 表明这是修改工作经历
        "w_id": "rrt4545454121212",  // 履历id
    }
    // 新增一段教育经历
    let args = {
        "resume_id": "你的简历id",
        "opt": "add_education",    // 表明这是新增教育经历
        "begin": "2010-12-1",  // 开始时间
        "end": "2015-12-1",  // 结束时间
        "school_name": "xx大学", // 教育机构名称
        ...
    }
    // 修改一段教育经历
    let args = {
        "resume_id": "你的简历id",
        "opt": "update_education",    // 表明这是修改教育经历
        "e_id": "rrt4545454121212",  // 教育经历id
        "begin": "2010-12-1",  // 开始时间
        "end": "2015-12-1",  // 结束时间
        "school_name": "xx大学", // 教育机构名称
        ...
    }
    // 删除一段教育经历
    let args = {
        "resume_id": "你的简历id",
        "opt": "delete_education",    // 表明这是删除教育经历
        "e_id": "rrt4545454121212",  // 教育经历id
    }
    // 新增一段荣誉
    let args = {
        "resume_id": "你的简历id",
        "opt": "add_honor",    // 表明这是新增荣誉
        "begin": "2010-12-1",  // 开始时间
        "end": "2015-12-1",  // 结束时间
        "title": "先进工作者", // 荣誉名称
        ...
    }
    // 修改一段荣誉
    let args = {
        "resume_id": "你的简历id",
        "opt": "update_honor",    // 表明这是修改荣誉
        "h_id": "rrt4545454121212",  // 荣誉id
        "begin": "2010-12-1",  // 开始时间
        "end": "2015-12-1",  // 结束时间
        "title": "先进工作者", // 荣誉名称
        ...
    }
    // 删除一段荣誉
    let args = {
        "resume_id": "你的简历id",
        "opt": "delete_honor",    // 表明这是删除荣誉
        "h_id": "rrt4545454121212",  // 荣誉id
    }
    // 新增车辆
    let args = {
        "resume_id": "你的简历id",
        "opt": "add_vehicle",    // 表明这是新增车辆
        "vehicle_model": "一汽解放J6",  // 车辆型号
        "plate_number": "沪A12345", // 车牌
        ...
    }
    // 修改车辆
    let args = {
        "resume_id": "你的简历id",
        "opt": "update_vehicle",    // 表明这是修改车辆
        "v_id": "rrt4545454121212",  // 车辆id
        "vehicle_model": "一汽解放J6",  // 车辆型号
        "plate_number": "沪A12345", // 车牌
        ...
    }
    // 删除车辆
    let args = {
        "resume_id": "你的简历id",
        "opt": "delete_vehicle",    // 表明这是删除车辆
        "v_id": "rrt4545454121212",  // 车辆id
    }

    // 扩展信息的增/删/改的提交方式都是一样的.
    $.post("/wx/resume/extend", args, function(resp){
        let json = JSON.parse(resp);
        if(json['message'] === "success"){
            // 成功
        }
        else{
            // 失败
        }
    });
```

返回类型: json
成功返回:

```javascript
{"message": "success"}
```

失败返回:

```javascript
{"message": "错误原因"}
```

#### 简历扩展信息的数据模型。
注意，其中涉及的driver_id参数后台会自动抓取。一般不需要传递

##### 工作经历

```python3
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime
    type_dict['enterprise_name'] = str  # 企业名称
    type_dict['enterprise_class'] = str  # 企业性质
    type_dict['industry'] = str  # 所属行业
    """
    企业规模
    50/100/500/1000  50表示小于等于50人规模 -1表示大于1000人规模
    """
    type_dict['enterprise_scale'] = int  # 企业规模
    type_dict['dept_name'] = str  # 部门名称
    """
    预置几个岗位名称,留给客户自己填写的机会.
    驾驶员/车队经理/其他
    """
    type_dict['post_name'] = str  # 岗位名称.
    type_dict['team_size'] = int  # 团队/下属人数
    """
    相关标准参考GB1589
    车型提供下拉选项,也可以手动填写.
    小型轿车、小型客车、中型客车、大型客车、平板式货车、栏板式货车、厢式货车、仓栅式货车、罐式车、自卸车、其他（手动填写）
    """
    type_dict['vehicle_type'] = str  # 车型
    """
    载重量,只有货车有这个选项.
    1.8/6/14三档 6代表1.8<t<6,以此类推,None代表没有此项数据,-1代表大于14
    """
    type_dict['vehicle_load'] = float  # 车辆载重量,单位吨.
    """
    车长,只有货车有这个选项.
    6/9.6/17.5 三档 None代表没有此项数据,-1代表大于17.5
    """
    type_dict['vehicle_length'] = float  # 车辆载重量,单位米.
    type_dict['description'] = str  # 工作描述.带换行符和空格的字符串格式.
    type_dict['achievement'] = str  # 工作业绩.带换行符和空格的字符串格式.
    type_dict['create_date'] = datetime.datetime  # 创建时间
```

##### 所获荣誉

```python3
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['time'] = datetime.datetime  # 获奖时间
    type_dict['title'] = str    # 荣誉称号
    type_dict['info'] = str    # 荣誉信息
    type_dict['image_id'] = ObjectId  # 荣誉图片
    type_dict['image_url'] = str  # 荣誉图片的地址,
    type_dict['create_date'] = datetime.datetime  # 创建时间
```

##### 车辆信息

```python3
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict["image_id"] = ObjectId  # 车辆照片
    type_dict["image_url"] = str  # 车辆照片的url,.
    type_dict["plate_number"] = str  # 车辆号牌, 英文字母必须大写,允许空,不做唯一判定
    """
    相关标准参考GB1589
    直接扫描行车证可得到,另外修正时提供下拉选项, 也可以手动填写.
    小型轿车、小型客车、中型客车、大型客车、平板式货车、栏板式货车、厢式货车、仓栅式货车、罐式车、自卸车、其他（手动填写）
    """
    type_dict["vehicle_type"] = str  # 车辆类型
    """
    载重量,只有货车有这个选项.
    1.8/6/14三档 6代表1.8<t<6,以此类推,None代表没有此项数据,-1代表大于14
    """
    type_dict['vehicle_load'] = float  # 车辆载重量,单位吨.
    """
    车长,只有货车有这个选项.
    6/9.6/17.5 三档 None代表没有此项数据,-1代表大于17.5
    """
    type_dict['vehicle_length'] = float  # 车辆载重量,单位米.
    type_dict["owner_name"] = str  # 车主姓名/不一定是驾驶员
    type_dict["address"] = str  # 地址
    type_dict["vehicle_model"] = str  # 车辆型号  比如 一汽解放J6
    type_dict["vin_id"] = str  # 车辆识别码/车架号的后六位 如果大于6，查询违章的时候就用后6位查询
    type_dict["engine_id"] = str  # 发动机号
    type_dict["register_date"] = datetime.datetime  # 注册日期
    type_dict["issued_date"] = datetime.datetime  # 发证日期
    type_dict["create_date"] = datetime.datetime
```

##### 教育经历

```python3
    type_dict['_id'] = ObjectId
    type_dict['driver_id'] = ObjectId  # 关键的(司机)简历的ObjectId
    type_dict['level'] = str  # 用户选择,  小学/初中/高中/高等教育/培训机构/其他
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime
    type_dict['school_name'] = str  # 学校名称
    type_dict['major'] = str  # 主修专业
```

### 上传图片(暂停使用)

>##### <span style="color: red">由于微信强制先上传文件到微信服务器，然后再下载到本地的模式，所以在公众号上传图片无法使用此接口，此接口保留，以备他用</span>

上传简历头像地址: /wx/resume_image/save/head_image
上传身份证地址: /wx/resume_image/save/id_image
上传荣誉证书图片地址: /wx/resume_image/save/honor_image
上传车辆照片地址: /wx/resume_image/save/vehicle_image
上传驾照图片地址: /wx/resume_image/save/driving_license_image
上传从业许可证地址: /wx/resume_image/save/rtqc_image

方法: post

返回类型: json
成功返回:

```javascript
{"message": "success", "url": "图片地址"}
```

失败返回:

```javascript
{"message": "错误原因"}
```

### 上传图片

主要分两步： 1.上传图片到微信服务器并通知自家服务器下载 2. 更新对应的建立信息

微信上传图片的详细步骤

1. 打开摄像头或者本地图片并选择。
2. 上传到微信服务器，获得微信服务器返回的serverId
3. 按照发送serverId给本api对应的接口
4. 专用api根据serverId去下载图片，成功后返回图片的id和url
5. 前端接收到id和url后，提交到对应的接口
6. 保存_id和url等待提交

**简历头像**

1. 通知下载图片地址: /wx/auto_download/head_image
参数：
table_name : head_image 固定值
server_id: 微信服务器回传的图片id

2. 修改简历头像信息地址：/wx/resume/opt
参数：
_id： 简历id ，会由后端传值到页面
head_image 简历头像信息的id，由自身服务器传回，24位字符串
head_image_url： 简历头像信息的url，由自身服务器传回

**身份证**

1. 通知下载图片地址: /wx/auto_download/id_image
参数：
table_name : id_image 固定值
field_name： id_image_face/id_image_back  身份证正面/背面
server_id: 微信服务器回传的图片id

2. 修改身份证信息地址：/wx/resume/opt
参数：
_id： 简历id ，会由后端传值到页面，详情见update_id.html
id_image_face： 身份证正面图片的id，由自身服务器传回，24位字符串
id_image_face_url： 身份证正面图片的url，由自身服务器传回
id_image_back： 身份证背面图片的id，由自身服务器传回，24位字符串
id_image_back_url： 身份证背面图片的url，由自身服务器传回

**荣誉证书图片**

1. 通知下载图片地址: /wx/auto_download/honor_image
参数：
table_name : honor_image 固定值
field_name： image_id 固定值
server_id: 微信服务器回传的图片id

2. 修改荣誉证书图片信息地址：/wx/resume/extend
参数：
resume_id： 简历id ，
h_id: 荣誉证书对象的_id,
opt: add_hobor/update_honor  操作类型，添加/修改
image_id 荣誉证书图片的id，由自身服务器传回，24位字符串
image_url： 荣誉证书图片的url，由自身服务器传回
... 其他参数

**车辆照片**: 

1. 通知下载图片地址: /wx/auto_download/vehicle_image
参数：
table_name : vehicle_image 固定值
field_name： image_id 固定值
server_id: 微信服务器回传的图片id

2. 修改车辆照片信息地址：/wx/resume/extend
参数：
resume_id： 简历id ，
v_id: 车辆对象的_id,
opt: add_vehicle/update_vehicle  操作类型，添加/修改
image_id 车辆照片的id，由自身服务器传回，24位字符串
image_url： 车辆照片的url，由自身服务器传回
... 其他参数

**驾照图片** driving_license_image

1. 通知下载图片地址: /wx/auto_download/driving_license_image
参数：
table_name : driving_license_image 固定值
field_name： dl_image 固定值
server_id: 微信服务器回传的图片id

2. 修改驾照图片地址：/wx/resume/opt
参数：
_id： 简历id ，会由后端传值到页面
dl_image 驾照图片的id，由自身服务器传回，24位字符串
dl_image_url： 驾照图片的url，由自身服务器传回

**从业许可证图片**  rtqc_image

1. 通知下载图片地址: /wx/auto_download/rtqc_image
参数：
table_name : rtqc_image 固定值
field_name： rtqc_image 固定值
server_id: 微信服务器回传的图片id

2. 修改从业许可证信息地址：/wx/resume/opt
参数：
_id： 简历id ，会由后端传值到页面
rtqc_image 从业许可证图片的id，由自身服务器传回，24位字符串
rtqc_image_url： 从业许可证片的url，由自身服务器传回

**营业执照图片** business_license_image

1. 通知下载图片地址: /wx/auto_download/business_license_image
参数：
db: mongo_db   固定值 **特有参数** 
table_name : business_license_image 固定值
field_name： business_license_image 固定值
server_id: 微信服务器回传的图片id

1. 修改营业执照图片信息地址：/wx/self_info/update
参数：
_id： 简历id ，会由后端传值到页面
business_license_image 营业执照图片的id，由自身服务器传回，24位字符串
business_license_image_url： 营业执照图片的url，由自身服务器传回

方法: post

返回类型: json
成功返回:

```javascript
{"message": "success", "url": "图片地址"}
```

失败返回:

```javascript
{"message": "错误原因"}
```

现在以上传身份证图片举例说明，这里是javascript代码片段。还需要html作出对应修改。详情请参考update_id.html页面

```javascript
        /*
        * 整体逻辑如下：
        * 1. 上传图片到然后，得到微信服务器返回的serverId                       chose_and_upload 函数
        * 2. 把serverId发给自身服务器，通知自身服务器去微信服务器下载临时素材。     chose_and_upload 函数
        * 3. 等待自身服务器返回的图片id和url                                   chose_and_upload 函数
        * 4. 把字符串格式的id和url作为参数提交到简历基础/扩展接口                 $("#submit").click() 提交事件
        * */

        var chose_and_upload = function($dom){
            /*
            * 选择图片并上传：
            * 1. 打开摄像头或者本地图片并选择。
            * 2. 上传到微信服务器
            * 3. 发送serverId给专用的api
            * 4. 专用api根据serverId去下载临时素材
            * 5. api下载完毕后回传_id和url。
            * 6. 保存_id和url等待提交
            * */
            wx.chooseImage({
                count: 1, // 默认9
                sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
                sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
                success: function (res) {
                    var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
                    $dom.attr('src',localIds);
                    // 上传图片到微信服务器
                    wx.uploadImage({
                        localId: localIds[0],  // 微信官方文档有误，请照此填写
                        isShowProgressTips: 1,
                        success: function(res){
                            // alert("localIds: " + res.serverId);

                            var id = res.serverId;
                            // alert("server_id: "+ id);

                            // 请求api接口去下载临时素材
                            var table_name = "id_image";  // 上传身份证对应的表名
                            var field_name = $dom.attr("id");
                            var args = {
                                "server_id": id,    // server_id 下载素材用
                                "table_name": table_name,
                                "field_name": field_name,  // 字段名
                                "db": "mongo_db2"            // 库名，固定
                            }
                            var url = "/wx/auto_download/" + table_name;
                            $.post(url, args, function(resp){
                                var json = JSON.parse(resp);
                                var status = json['message'];
                                console.log(json);
                                if(status == "success"){
                                    // 成功，保存返回值
                                    $dom.attr("data-id", json[field_name]);
                                    $dom.attr("data-url", json[field_name + "_url"]);
                                }
                                else{
                                    alert(status);
                                }
                            });

                        }
                    });
                }
            });
        };

        // 给上传按钮加上事件
        $(".p_mag").each(function(){
            var $this = $(this);
            $this.click(function(){
                chose_and_upload($this.find(".imgs"));
            });
        });

        // 提交事件
        $("#submit").click(function(){
            var $id_image_face = $("#id_image_face");
            var $id_image_back = $("#id_image_back");
            var args = {};
            var need_submit = false;
            var id_image_face = $id_image_face.attr("data-id");
            if(id_image_face){
                need_submit = true;
                args['id_image_face'] = id_image_face;
                args['id_image_face_url'] = $id_image_face.attr("data-url");
            }
            var id_image_back = $id_image_back.attr("data-id");
            if(id_image_back){
                need_submit = true;
                args['id_image_face'] = id_image_back;
                args['id_image_back_url'] = $id_image_back.attr("data-url");
            }
            if(need_submit){
                args['_id'] = $("#resume_id").text();  // 简历id，这里是修改简历
                var url = "/wx/resume/opt";
                $.post(url, args, function(resp){
                    var json = JSON.parse(resp);
                    var status = json['message'];
                    console.log(json);
                    if(status == "success"){
                        // 成功，下一步
                        alert("上传成功");
                        location.href = "/wx/html/resume.html";
                    }
                    else{
                        alert(status);
                    }
                });
            }
            else{
                location.href = "/wx/html/resume.html";
            }
        });
```

### 用户查看或者修改自己的信息

> 这个接口是提供给用户自己调用的,用于用户查看自己的信息或者修改自己的私人资料,所以进行了限制,屏蔽了一些字段

#### 用户查看自己的身份新消息

url: /wx/self_info/view
参数: 无
method: post/get
返回类型: json
成功: {"message": "success", 'data': 用户个人信息的字典}
失败: {"message": "错误原因"}
由于安全原因,下列字段被忽略这些字段将不会被返回:
'openid', 'unionid', 'subscribe', 'subscribe_scene', 'subscribe_time',
'access_token', 'expires_in', 'time', 'refresh_token'

#### 用户修改自己的身份新消息

url: /wx/self_info/update
参数: wx_user数据模型中,不在被忽略字段中的都可以作为参数.
method: post/get
返回类型: json
成功: {"message": "success", 'data': 用户个人信息的字典}
失败: {"message": "错误原因"}
由于安全原因,下列字段被忽略,对他们的修改无效:
'openid', 'unionid', 'subscribe', 'subscribe_scene', 'subscribe_time',
'access_token', 'expires_in', 'time', 'refresh_token', 'role',
'resume_id', 'relate_time', 'relate_id', 'relate_image', 'authenticity',
'relate_image', 'name', 'identity_code'
request example:
```javascript
// 修改营业执照
var args = {
    "business_license_image": business_license_image, 
    "business_license_image_url": business_license_image
}
$.post("/wx/self_info/update", args, function(resp){});

```
