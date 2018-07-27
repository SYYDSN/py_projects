

### 微信用户的数据结构

```python3

    type_dict['_id'] = ObjectId  # 用户id
    type_dict['phone'] = str    # 手机号码
    type_dict['nick_name'] = str
    type_dict['sex'] = int
    type_dict['openid'] = str
    type_dict['unionid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str   # 城市
    type_dict['head_img_url'] = str  # 头像地址
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
    type_dict['name'] = str  # 中介商名字/销售真实姓名.用于展示在二维码上
    type_dict['identity_code'] = str  # 中介商执照号码/销售真实身份证id.用于部分展示在二维码上
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
    type_dict['id_image'] = str  # 身份证图片id.24位字符串
    type_dict['age'] = int  # 年龄 以身份证号码为准
    """以下3个字段因为是动态的,需要在每次查询doc的时候进行计算,以保证准确性"""
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

### 上传图片

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

不依赖form上传文件的例子(完全版)
```javascript
function upload_progress(event){
    /*
    上传进度处理函数,这里只是一个示范函数,实际中要重写此函数.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :return: nothing
    */
    if (event.lengthComputable) {
        var complete_percent = Math.round(event.loaded * 100 / event.total);
        console.log(`完成度:${complete_percent}`);
    }else{}
}

function upload_complete(event){
    /*
    上传文件success时的事件,根据实际需要可以覆盖.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :return: nothing
    */
    let json = {"message": "未知的错误"};
    let status = event.target.status;
    if(status !== 200){
        json = {"message": `服务器没有作出正确的回应,返回码:${status}`};
    }
    else{
        let str = event.target.responseText;
        if(str === undefined){
            json['message'] = "上传成功,但服务器没有回应任何消息";
        }
        else{
            json = JSON.parse(str);
        }
    }
    console.log(json);
    if(json['message'] === "success"){
        alert("上传成功!");
        // 以下为定制脚本
        $("#return_url").attr("src", json['data']['url']);
    }
    else{
        alert(json['message']);
    }
}

function upload_error(event){
    /*
    上传文件失败时的事件,根据实际需要可以覆盖.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :return: nothing
    */
    let json = {"message": "error"};
    console.log(json);
}

function upload_abort(event){
    /*
    上传文件被中止时的事件,根据实际需要可以覆盖.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :return: nothing
    */
    let json = {"message": "abort"};
    console.log(json);
}

function upload(file_name, $obj, action_url, header_dict){
    /*
    上传文件.
    :params file_name:   文件名.
    :params $obj:        input的jquery对象.
    :params action_url:  上传的服务器url
    :params header_dict: 放入header的参数,是键值对形式的字典,键名不要用下划线,因为那是个禁忌
    :return:             dict类型. 一个字典对象,一般是{"message": "success"}
    */
    let data = new FormData();
    data.append(file_name, $obj[0].files[0]);
    /*
    有关XMLHttpRequest对象的详细信息,请参考.
    https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest
    */
    let req = new XMLHttpRequest();
    req.upload.addEventListener("progress", upload_progress, false);
    req.addEventListener("load", upload_complete, false);
    req.addEventListener("error", upload_error, false);
    req.addEventListener("abort", upload_abort, false);
    req.open("post", action_url);
    // 必须在open之后才能给请求头赋值
    if(header_dict){
        /*
        * 传送请求头信息,目前服务端还未做对应的处理.这只是与被给后来使用的.
        * */
        for(let k in header_dict){
            req.setRequestHeader(k, header_dict[k]);
        }
    }
    req.send(data);
}
```