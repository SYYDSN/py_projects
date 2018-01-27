// 设定全局server post地址
const server = "";  // 本机请求

// 定义全局颜色
const color_danger_16 = "#E25050";
const color_warning_16 = "#E03F00";
const color_normal_16 = "#6EB73E";

// 设置svg图标颜色的方法
set_icon_color = function ($obj, color_type = "normal"){
    let color = color_normal_16;
    if(color_type === "warning"){
        color = color_warning_16;
    }else if(color_type === "danger"){
        color = color_danger_16;
    }
    $obj.css("color", color);
};

// 快捷键,打开屏蔽用户页面
let key_list = [];
$("html").keydown(function(e){
    let code = e.keyCode;
    console.log(key_list);
    if(key_list.indexOf(code) !== -1){
        // nothing...
    }
    else{
        key_list.push(code);
    }
    /*
    * q: 81
    * p: 80
    * 同时按下这q和p这2个键弹出屏蔽用户页面
    * */
    if(key_list.length === 2 && key_list.indexOf(81) !== -1 && key_list.indexOf(80) !== -1){
        window.open("block_employee_list");
    }
}).keyup(function(e){
    let code = e.keyCode;
    if(key_list.indexOf(code) !== -1){
        key_list.splice(0, key_list.indexOf(code));
    }
    else{
        // nothing...;
    }
});


// 验证手机号码的函数,不合法的手机号码会返回false
validate_phone = function (phone) {
    var myreg = /^(((1[3-9][0-9]{1})|(15[0-9]{1})|(18[0-9]{1}))+\d{8})$/;
    if (myreg.test(phone)) {
        return true;
    }
    else {
        return false;
    }
};

// 检查邮箱
validate_mail = function (str) {
    var reg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/;
    return reg.test(str);
};

// 检查日期是否是 1900-12-12 这种格式
validate_date = function (str) {
    var pattern = /^[12][09][0-9][0-9]-[01][0-9]-[0-3][0-9]$/;
    return pattern.test(str);
};

//一个用于绑定input输入框的回车事件的函数，需要实现的功能如下：
//当本元素处于焦点状态时，如果发生了回车事件，光标会跳到下一个。如果下一个元素是提交按钮，那就触发提交动作。
//2个参数 $obj1,被绑定的元素的jq对象  ，$obj2 下一个元素的jq对象 .
bind_enter_event = function ($obj1, $obj2) {
    var $obj1 = $obj1;
    var $obj2 = $obj2;
    $obj1.keydown(function (e) {
        if (e.keyCode == 13) {
            $obj2.trigger("focus");
        } else {
        }
    });
};

before_url = "/user_index";  // 全局变量，存放登录前的页面。
// 取登录前的页面url的方法
get_before_url = function () {
    var temp = location.href.split("?ref=");
    if (temp.length == 2) {
        /*服务端对这段字符串进行了url编码，这里必须解码*/
        var part = $.trim(temp[1].replace(location.host, ''));
        var b_str = decodeURIComponent(part);
        /*jquery base64 插件的解密方法，对应的加密方法叫$.base64.btoa，
         第二个参数的意思是支持不支持utf8，如果没有这个参数或者设置为false的话，
         就无法对中文进行加密解密*/
        before_url = $.base64.atob(b_str, true);
    }
};
get_before_url();

// 检测是否是火狐浏览器，返回布尔值
is_ff= function(){
    let num = window.navigator.userAgent.indexOf("Firefox/");
    if(num === -1){
        return false;
    }
    else{
        return true;
    }
};

// 比较08:00这样格式的字符串的时间的大小.
compare_hour_and_minute_str = function (a, b) {
    let a_0 = a.split(":");
    let b_0 = b.split(":");
    if (parseInt(a_0) > parseInt(b_0)) {
        return 1;
    }
    else if (parseInt(a_0) < parseInt(b_0)) {
        return -1;
    }
    else {
        let a_1 = null, b_1 = null;
        try {
            a_1 = a_0[1];
            a_1 = parseInt(a_1);
        } catch (e) {
            console.log(e);
            a_1 = 0;
        }
        try {
            b_1 = b_0[1];
            b_1 = parseInt(b_1);
        } catch (e) {
            console.log(e);
            b_1 = 0;
        }
        if (a_1 > b_1) {
            return 1;
        }
        else if (a_1 < b_1) {
            return -1;
        }
        else {
            return 0;
        }
    }
};

/*扩展字符串的方法,增加startsWith和endsWith两个方法(并非所有的浏览器都有这两个方法) */
    if (typeof(String.prototype.startsWith !== "functin")) {
        String.prototype.startsWith = function(key_str) {
            console.log("extend function");
            var l2 = key_str.length;
            var start = this.slice(0, l2);
            if (start === key_str) {
                return true;
            } else {
                return false;
            }
        };
    }

    if (typeof(String.prototype.endsWith !== "functin")) {
        String.prototype.endsWith = function(key_str) {
            console.log("extend function");
            var l = this.length;
            var l2 = key_str.length;
            var end = this.slice((l - l2));
            if (end === key_str) {
                return true;
            } else {
                return false;
            }
        };
    }

// 获取url参数
get_url_arg = function (name) {
let reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
let r = window.location.search.substr(1).match(reg);
return (r !== null)?decodeURI(r[2]):null;
};

// 定义高德地图样式
let current_amap_style = "normal";

// 设置高德地图的样式
function set_amap_style(style_str){
    let style_list = [
        'whitesmoke', 'normal', 'macaron', 'graffiti', 'darkblue', 'blue',
        'fresh', 'dark', 'light', 'grey'
    ];
    if(style_list.indexOf(style_str) !== -1){
        amap_style = style_str;
        map.setMapStyle(`amap://styles/${amap_style}`);
    }
}

// 初始化高德地图
function init_map() {
    // 初始化高德地图事件
    map = new AMap.Map('main_zone', {
        resizeEnable: true,
        center: [121.304239, 31.239981],    // 坐标位置
        mapStyle: 'amap://styles/'+current_amap_style,  // 样式
        showIndoorMap: false,                // 是否自动展示室内地图? 可能是造成地图卡的主要原因
        zooms: [3, 15],                      // 缩放范围
        zoom: 11
    });
    // 地图缩放事件
    AMap.event.addListener(map,'zoomend',function(){
        console.log("当前缩放级别:"+map.getZoom());
    });
}

// 填充右侧边栏司机列表部分
fill_right_bar = function (func_name) {
    $.post(`/manage/get_driver_list`, function (json) {
        let resp = JSON.parse(json);
        if (resp['message'] !== "success") {
            alert(resp['message']);
        } else {
            let data = resp['data'];
            console.log(data);
            let l = data.length;
            if (l > 0) {
                let bar = $("#right_bar");
                bar.empty();
                for (let i = 0; i < l; i++) {
                    let driver = data[i];
                    let real_name = driver['real_name'] ? driver['real_name'] : driver['user_name']; // 真实姓名
                    let head_img_url = driver['head_img_url'] ? driver['head_img_url'] : "static/image/head_img/default_01.png"; // 头像地址
                    let html = `<div onclick="" data-id="${driver._id}" class="nav_item">
                                        <img src="../${head_img_url}" class="img-sm img-circle">
                                        <div class="driver_name">${real_name}</div>
                                    </div>`;
                    let obj = $(html);
                    obj.click(function(){
                        func_name(obj);
                    });
                    bar.append(obj);
                }
            } else {
            }
        }
    });
};

