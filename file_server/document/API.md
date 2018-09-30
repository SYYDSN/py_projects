# 文件服务器接口文档

#### Domain: file.bhxxjs.cn / resource.bhxxjs.cn  *域名*
#### Protocol: http 1.0/2.0  *访问协议*
#### Ip: 47.99.105.196 *ip地址*
#### Port: 7001 *端口*
#### Auth:  647a5253c1de4812baf1c64406e91396  *用于身份验证的字符串*

**主机地址**

主机地址为 协议+ip+端口或者 协议+域名
主机地址使用以下2种表示方式皆可：

1. http://47.99.105.196:7001
2. http://file.bhxxjs.cn

### 一般约定

* 字符集为utf-8
* 除非另行约定，返回值都是json格式
* 一般情况下，视图都支持post和get两种方法，除非特别说明
* 参数名不区分大小写.统一使用小写.命令方法使用下划线命名法
* 不使用true和false表示布尔值,而是使用1和0的整形替代
* 除非特别说明,返回json格式的 {"message": "success", ... }(键值对对象)代表请求成功

### 接口列表

* [上传图片](#1)
* [查看图片](#2)
* [短信验证码](#3)

### 接口详细说明

#### <span id="1" style="color: #398dee">上传图片</span>

上传图片文件到数据库中

* Url: /images/obj/save/image_file
* Method: post/get
* Headers:  auth =Auth   请求头中的身份验证信息，固定的字符串,Auth就是文档顶部的定义的Auth字符串
* Args: 

>* file 字节类型  必须   待上传的图片的数据

* Request Example:

```html
.....
<!--一个上传图片的例子，html代码部分-->
<input id="select_image" type="file" accept="image/*">
<button id="upload_btn" class="btn btn-default btn-primary">上传</button>
.....
<script>
....
/*j一个上传图片的例子，avascript代码部分*/
$("#upload_btn").click(function(){
        var headers = {"auth": "647a5253c1de4812baf1c64406e91396"};               // 请求头，用于验证身份
        var url = "http://47.99.105.196:7001/images/obj/save/image_file";         // 提交地址,
        // 上传图片
        $("#select_image").upload(url, function(json){
            // 处理成功的返回
            ...
        }, function(e){
            // 处理错误的返回
            ...
        }, headers);
    });
....
</script>
```

* Return:
1. success:

```javascript
var resp = {
    "message": "success",                 // 状态，表示成功
    "url": url,                           // 图片的path，可以和host拼接成完整的地址
    "_id": id                             // 存储的文件的id，可以和其他参数拼接成图片的访问地址
}
```

2. error
    
```javascript
var resp = {
    "message": "未知的错误"                // 失败原因
}
```

* Tip: 上传文件的示范页面的url  /images/upload_demo

#### <span id="2" style="color: #398dee">查看图片</span>

上传图片文件到数据库中

* Url: /images/obj/view/image_file
* Method: get
* Headers:  
* Args: 

>* fid 字符串类型  必须   图片的id
>* size 字符串类型  非必须  图片的尺寸，格式如同： width*height 

* Request Example:

```javascript
var host = "http://47.99.105.196:7001";             // 主机地址
var api = '/images/obj/view/image_file';       // api的url
var img_id = "5bab505d17397c118bdfac9d";       // 图片的id
var size = "120*90";                           // 尺寸，表示120像素宽，90像素高

var url = host + api + "?fid=" + img_id + "&size=" + size;
/*
* 最后拼接的图片地址是 http://47.99.105.196:7001/images/obj/view/image_file?fid=5bab505d17397c118bdfac9d&size=120*90
* */

```
* Return:  文件

#### <span id="3" style="color: #398dee">短信验证码</span>

上传图片文件到数据库中

* Url: /normal/obj/view/image_file
* Method: get
* Headers:  
* Args: 

>* fid 字符串类型  必须   图片的id
>* size 字符串类型  非必须  图片的尺寸，格式如同： width*height 

* Request Example:

```javascript
var host = "http://47.99.105.196:7001";             // 主机地址
var api = '/images/obj/view/image_file';       // api的url
var img_id = "5bab505d17397c118bdfac9d";       // 图片的id
var size = "120*90";                           // 尺寸，表示120像素宽，90像素高

var url = host + api + "?fid=" + img_id + "&size=" + size;
/*
* 最后拼接的图片地址是 http://47.99.105.196:7001/images/obj/view/image_file?fid=5bab505d17397c118bdfac9d&size=120*90
* */

```
* Return:  文件