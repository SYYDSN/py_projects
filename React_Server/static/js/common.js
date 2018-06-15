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
if (typeof(String.prototype.startsWith !== "function")) {
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

if (typeof(String.prototype.endsWith !== "function")) {
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

// 检查某个日期是不是今天?
function is_today(date){
    let now1 = new Date();
    let now2 = date;
    if(date.getHours){
        // 是Date对象.
    }
    else{
        now2 = new Date(date);
    }
    if(now2 === "Invalid Date"){
        return false;
    }
    else{
        let y1 = now1.getFullYear();
        let y2 = now2.getFullYear();
        let month1 = now1.getMonth();
        let month2 = now2.getMonth();
        let day1 = now1.getDate();
        let day2 = now2.getDate();
        if(y1 === y2 && month1 === month2 && day1 === day2){
            return true;
        }
        else{
            return false;
        }
    }
}

function float_to_string(hour){
    // 把浮点制的小时换算成xx小时xx分
    let l = String(hour);
    let ls = l.split(".");
    if(ls.length === 1){
        return `${ls[0]}小时`
    }
    else{
        let h = ls[0];
        let m = Math.round(parseFloat(`0.${ls[1]}`) * 60);
        return `${h}小时${m}分钟`;
    }
}

function get_picker_date($obj){
    // 按照统一格式取时间,避免浏览器的差异,$obj是时间选择器绑定的input的jq对象.返回2018-01-01格式的日期
    let date_str = $.trim($obj.val());
    if(date_str.indexOf("-") !== -1){
        let date_list = date_str.split("-");
        let year = date_list[0];
        /*防止浏览器之间的差异,这里必须做手动转换,以保证时间字符串格式的一致性*/
        let month = String(date_list[1]).length < 1? "0" + date_list[1]:date_list[1];
        let day = String(date_list[2]).length < 1? "0" + date_list[2]:date_list[2];
        return `${year}-${month}-${day}`;
    }
    else{
        return null;
    }

}

function get_url_arg(arg_url){
    // 从url分析参数,
    let args = {};
    let url = typeof(arg_url) === "undefined"? location.href: arg_url;
    if(url.indexOf("?") !== -1){
        let arg_str = url.split("?")[1];
        arg_str = decodeURIComponent(arg_str);
        console.log(arg_str);
        let a_list = arg_str.split("&");
        for(var item of a_list){
            if(item.indexOf("=") !== -1){
                let temp = item.split("=");
                let k = temp[0];
                let v = temp[1];
                args[k] = v;

            }else{}
        }
    }
    else{
        // pass
    }
    return args;
}

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

