/*我的函数库，包含jquery的扩展函数*/
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

function get_url_arg_dict(arg_url){
    // 从url分析参数,返回参数字典.
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

function get_url_arg(arg_name){
    // 根据arg_name,从url取对应的参数值,本函数依赖get_url_arg_dict函数,是前者的扩展之一
    if(arg_name === undefined || arg_name === ""){
        return undefined;
    }
    else{
        return get_url_arg_dict()[arg_name];
    }
}

function build_url(base_path, arg_dict) {
    // 根据基础url和参数字典拼接url,
    if(typeof(base_path) === "object" && arg_dict === undefined){
        // 第一个参数是空的.并且只有一个参数
        arg_dict = base_path;
        base_path = location.pathname;
    }
    else if(typeof(base_path) === "string" && arg_dict === undefined){
        arg_dict = {};
    }
    else{
        // nothing...
    }
    base_path += "?";
    for (let name in arg_dict) {
        let val = arg_dict[name];
        console.log(name, val);
        base_path += `${name}=${val}&`;
    }
    if (base_path.endsWith("?")) {
        base_path = base_path.slice(0, -1);
    }
    if (base_path.endsWith("&")) {
        base_path = base_path.slice(0, -1);
    }
    return base_path;
}

var __is_bottom_prev_obj = null; // 辅助判断滑动方向的对象
var is_bottom = function (jq_obj, y_val, y_threshold, callback, args) {
    /*
     * params jq_obj:      绑定滑动事件的元素的jQuery的对象.
     * params y_val:       滑动事件中去取出来的触摸点的y坐标event.touches[0].clientY
     * params callback:    回调函数, post和对dom的操作可以写在回调函数里
     * params args:        回调函数的参数组成的列表
     */
    try {
        y_threshold = parseInt(y_threshold);
        y_threshold = isNaN(y_threshold) ? 100 : y_threshold;
    } catch (e) {
        console.log(e);
        y_threshold = 100; // 在到达底部后,再滑动多少距离就激活事件? 单位像素
    }
    callback = callback == undefined ? function (s) {
        s = s == undefined ? '' : s;
        alert(s);
    } : callback;
    args = args == undefined ? ["hello world"] : args;
    // 判断是否到达底部?
    var win_height = $(window).height(); // 页面窗口高度
    var rect = jq_obj[0].getBoundingClientRect(); // 元素的宽高顶左的位置对象
    var dom_top = rect.top; // 元素顶部
    var dom_height = rect.height; // 元素高度.
    if ((win_height - (dom_top + dom_height)) < 1) {

        console.log("到达底部");
        // 如果y_val的值在持续减小.而dom_top不变的话,那就是滑到页面的底部了.
        if (__is_bottom_prev_obj == null) {
            // 第一次有效的滑动到底部
            __is_bottom_prev_obj = {
                "y": y_val,
                "date": new Date()
            };
        } else {
            // 判断是否超时?滑动距离是否足够?
            var old_y = __is_bottom_prev_obj['y'];
            var old_date = __is_bottom_prev_obj['date'];
            var now = new Date();
            var delta = now - old_date; // 时间差, 毫秒
            console.log("滑动间隔" + delta + "毫秒")
            if (delta <= 200) {
                // 连续的下滑动作,没有超时,检测滑动距离
                var l = (old_y - y_val);
                console.log("滑动距离" + l + "px")
                if (l >= y_threshold) {
                    // 滑动距离足够
                    __is_bottom_prev_obj = null; // 重置辅助判断的对象.
                    callback.apply(null, args); // 激活回调函数
                } else {
                    // pass
                }
            } else {
                // 滑动间隔超时
                __is_bottom_prev_obj = null; // 重置辅助判断的对象.
            }
        }
    } else {
        // 页面不在底部
        if (__is_bottom_prev_obj == null) {
            // pass
        } else {
            __is_bottom_prev_obj = null; // 重置辅助判断的对象.
        }
    }
}

var touch_it = function (selector, cb, args) {
    /*
    cb 回调函数
    args 回调函数的参数数组
    在touchmove事件中:
    1. 根据触摸点的y坐标的变化,判断是在往上还是往下滑动屏幕.
    */
    var $obj = $(selector);
    $obj.on("touchstart touchmove", function (event) {
        console.log(event);
        var e_name = event.type; // 时间类型
        var y = undefined;　　　　　 // 触摸点ｙ坐标
        try {
            y = event.originalEvent.touches[0].clientY; // touchend事件的touches属性是一个空的列表
        } catch (e) {
            console.warn("error!");
            console.log(`type: ${e_name}`);
            console.log(event.touches);
        }
        var dom_top = $obj.offset().top;

        is_bottom($obj, y, null, cb, args);
        var rect_top = $obj[0].getBoundingClientRect();
        var e = $(`<div>type:${e_name}, y=${parseInt(y)}, h1=${dom_top}, h2=${rect_top.top}</div>`);
        $(".tips").prepend(e);
    });
};

var pop_alert = function(title, delay){
    // 弹出提示框
    title = title==undefined?"读取中,请稍后...":title;
    var id_str = "8c8431579bbd44e6ad4758ddb3afccfd";
    var $obj = $("#" + id_str);
    if($obj.length === 0){
        var html = `<div id="${id_str}" style="width: 100%; height:100%; background-color: rgba(188,188,188,0.5);z-index:9999999;position: absolute;top:0;left:0;display:flex;flex-direction: row;justify-content: center;align-items: center">
                    <div style="width:300px;height:260px;margin-top:-100px;background-color: white;border-radius: 6px;display:flex;flex-direction: column;justify-content: flex-start;align-items: center">
                        <div style="width:100%;border-bottom:0px solid grey;margin:45px 10px 20px;font-size:24px;height:40px;line-height:1em;text-align: center">
                            <div class="8c8431579bbd44" style="font-weight:700;text-align: center; margin-bottom: 10px">
                                ${title}
                            </div>
                        </div>
                        <div style="width:100%;height:100px;text-align: center">
                            <i class="fa fa-spinner fa-spin" style="font-size:96px"></i>
                        </div>
                    </div>
                </div>`;
        $("body").append(html);
    }
    else{
       $obj.find(".8c8431579bbd44").text(title).show();
    }
    delay = delay==undefined?30000: delay;
    setTimeout(function(){
        // 最多30秒关闭窗口
        $("#" + id_str).hide();
    }, delay);
};

var close_alert = function(){
    var id_str = "8c8431579bbd44e6ad4758ddb3afccfd";
    var $obj = $("#" + id_str);
    $obj.hide();
};

function upload_progress(event, progress_cb){
    /*
    上传进度处理函数
    :params event:       文件上传事的事件,
    :params progress_cb: 回调函数,本函数会把上传完成的百分数当作地一个参数传入此回调函数.
    默认情况下.会在控制台打印上传完成度. 注意,100并不代表服务端完整的接收到了文件.
    只代表页面已经发送完了所有的文件内容.
    */
    if (event.lengthComputable) {
        var complete_percent = Math.round(event.loaded * 100 / event.total);
        var handler = progress_cb?progress_cb: function(num){console.log(`上传完成度:${num}`)};
        handler(complete_percent);
    }else{}
}

function upload_complete(event, success_cb){
    /*
    上传文件success时的事件,只要服务器返回状态码200,就会执行本函数,并并不是代表服务器返回了正确的信息.
    根据实际需要可以覆盖.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :params success_cb:   成功时的回调函数,
    :return: nothing
    */
    let str = event.target.responseText;
    let handler = success_cb? success_cb: function(a){console.log(a);};
    handler(str);
}

function upload_error(event, error_cb){
    /*
    上传文件失败时的事件,根据实际需要可以覆盖.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :params error_cb: 失败时的回调函数,
    :return: nothing
    */
    let handler = error_cb? error_cb: function(a){console.log(event);};
    handler(event);
}

function upload_abort(event, abort_cb){
    /*
    上传文件被中止时的事件,根据实际需要可以覆盖.
    :params event: 文件上传事的事件,一般由XMLHttpRequest的upload的事件监听器来传递事件.
    :params abort_cb: 被终止时的回调函数,
    :return: nothing
    */
    let handler = abort_cb? abort_cb: function(a){console.log(event);};
    handler(event);
}

function batch_upload(options){
    /*
    批量上传文件. 不限制文件大小
    options = {
    files: 数据的序列,
    url: str,
    headers: 键值对对象,
    success_cb: function,
    error_cb: function,
    progress_cb: function,
    }
    :params files:        input标签的files
    :params url:          上传的服务器url
    :params headers:      放入header的参数,是键值对形式的字典,键名不要用下划线,因为那不符合规范
    :params success_cb:   成功时的回调函数,会把服务器的返回信息作为第一个参数传入此回调函数.
    :params error_cb:     失败时的回调函数,会把错误信息作为第一个参数传入此回调函数.
    :params progress_cb:  上传时的返回上传进度的回调函数,会把页面上传文件的百分书作为第一个参数传入此回调函数..
    :return:              不返回数据,由回调函数返回.
    有关XMLHttpRequest对象的详细信息,请参考.
    https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest
    有关XMLHttpRequest.send方法的详细文档地址:
    https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest/send
    */
    let files = options['files'];
    let file_data = options['file_data'];
    let url = options['url'];
    let headers = options['headers'];
    let success_cb = options['success_cb'];
    let error_cb = options['error_cb'];
    let progress_cb = options['progress_cb'];
    let prog_func = function(event){upload_progress(event, progress_cb)};  // 进度的回调函数
    let comp_func = function(event){upload_complete(event, success_cb)};  // 成功时的回调函数
    let erro_func = function(event){upload_error(event, error_cb)};  // 失败时的回调函数

    // 构造数据容器
    let data = new FormData();
    for(let file of files){
        data.append(file.name, file);
    }
    // 新建一个请求对象
    let req = new XMLHttpRequest();
    // 添加事件监听器
    req.upload.addEventListener("progress", prog_func, false);
    req.addEventListener("load", comp_func, false);
    req.addEventListener("error", erro_func, false);
    req.addEventListener("abort", erro_func, false);
    req.open("post", url);
    // 必须在open之后才能给请求头赋值
    if(headers){
        /*
        * 传送请求头信息,目前服务端还未做对应的处理.这只是与被给后来使用的.
        * */
        for(let k in headers){
            req.setRequestHeader(k, headers[k]);
        }
    }
    try{
        req.send(data);  // 404错误会直接在此抛出
    }catch(e){
        let handler = error_cb? error_cb: function(ms){console.log(ms);};
        handler(e);
    }

}

function my_upload(options){
    /*
    上传文件.用于绑定$的方法
    options = {
    file_name: 字符串,
    file_data: DOM.files[0]对象,
    url: str,
    max_size: 整数,
    headers: 键值对对象,
    success_cb: function,
    error_cb: function,
    progress_cb: function,
    }
    :params file_name:    文件名.
    :params file_data:    文件数据,二进制对象
    :params url:          上传的服务器url
    :params max_size:     上传文件的最大尺寸,单位kb
    :params headers:      放入header的参数,是键值对形式的字典,键名不要用下划线,因为那不符合规范
    :params success_cb:   成功时的回调函数,会把服务器的返回信息作为第一个参数传入此回调函数.
    :params error_cb:     失败时的回调函数,会把错误信息作为第一个参数传入此回调函数.
    :params progress_cb:  上传时的返回上传进度的回调函数,会把页面上传文件的百分书作为第一个参数传入此回调函数..
    :return:              不返回数据,由回调函数返回.
    有关XMLHttpRequest对象的详细信息,请参考.
    https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest
    有关XMLHttpRequest.send方法的详细文档地址:
    https://developer.mozilla.org/zh-CN/docs/Web/API/XMLHttpRequest/send
    */
    let file_name = options['file_name'];
    let file_data = options['file_data'];
    let url = options['url'];
    let max_size = options['max_size'];
    let headers = options['headers'];
    let success_cb = options['success_cb'];
    let error_cb = options['error_cb'];
    let progress_cb = options['progress_cb'];
    let prog_func = function(event){upload_progress(event, progress_cb)};  // 进度的回调函数
    let comp_func = function(event){upload_complete(event, success_cb)};  // 成功时的回调函数
    let erro_func = function(event){upload_error(event, error_cb)};  // 失败时的回调函数
    let file_size = 0;
    try{
        file_size = file_data.size;
    }catch(e){
        console.log(e);
    }
    if(file_size === 0){
        let ms = "无效的文件尺寸";
        erro_func(ms);
    }
    else{
        let can_exe = false;
        if(max_size === undefined){
            can_exe = true;
        }
        else{
            file_size = file_size / 1000;
            if(file_size > max_size){
                let ms = `文件尺寸过大: 限制:${max_size}kb, 当前大小:${file_size} kb`;
                erro_func(ms);
                can_exe = false;
            }
            else{
                can_exe = true;
            }
        }
        if(can_exe){
            // 构造数据容器
            let data = new FormData();
            data.append(file_name, file_data);
            // 新建一个请求对象
            let req = new XMLHttpRequest();
            // 添加事件监听器
            req.upload.addEventListener("progress", prog_func, false);
            req.addEventListener("load", comp_func, false);
            req.addEventListener("error", erro_func, false);
            req.addEventListener("abort", erro_func, false);
            req.open("post", url);
            // 必须在open之后才能给请求头赋值
            if(headers){
                /*
                * 传送请求头信息,目前服务端还未做对应的处理.这只是与被给后来使用的.
                * */
                for(let k in headers){
                    req.setRequestHeader(k, headers[k]);
                }
            }
            try{
                req.send(data);  // 404错误会直接在此抛出
            }catch(e){
                let handler = error_cb? error_cb: function(ms){console.log(ms);};
                handler(e);
            }
        }
        else{
            // nothing...
        }
        return can_exe;
    }
}

function my_upload2($obj, url, success_cb, error_cb, headers){
    /*
    上传文件2. 用于绑定dom的方法,想对于my_upload函数,本函数功能上进行了精简,如需精细控制,请使用my_upload函数
    :params $obj:         dom的jQuery对象
    :params url:          上传的服务器url
    :params success_cb:   成功时的回调函数,会把服务器的返回信息作为第一个参数传入此回调函数.
    :params error_cb:     失败时的回调函数,会把错误信息作为第一个参数传入此回调函数.
    :return:              不返回数据,由回调函数返回.
    options = {
    file_name: 字符串,
    file_data: DOM.files[0]对象,
    url: str,
    max_size: 整数,
    headers: 键值对对象,
    success_cb: function,
    error_cb: function,
    progress_cb: function,
    }
    */
    let file_name = $obj.attr("name");
    if(file_name){
        // nothing...
    }
    else{
        file_name = "file"
    }
    let file_data = $obj[0].files[0];
    let opts = {
        file_name: file_name,
        file_data: file_data,
        max_size: 4000,
        url: url,
        success_cb: success_cb,
        error_cb: error_cb
    };
    if(headers){
        opts['headers'] = headers;
    }
    return my_upload(opts);
}


function CustomException(message, exception_name) {
    /*自定义异常类*/
   this.message = message;
   this.name = exception_name? exception_name: "UserException" ;
}

function raise (mes, exception_name) {
    /*抛出异常*/
    throw new CustomException(mes,exception_name);
}

function FoundNotDom(mes){
    /*元素没有找到的错误*/
    raise(mes, 'FoundNotDOM');
}


function PageHandler (prev_page, next_page, page_count, page_num, jump_btn){
    /*
    * 一个翻页器请把元素按照参数名作为id命名即可. 使用方法 PageHandler()即可.
    * param prev_page: 上一页元素的id 默认id是prev_page
    * param next_page: 下一页元素的id 默认id是next_page
    * param page_count: 这个是显示当前页/共计多少页的元素的id, 默认id是page_count, text必须是1/10这种格式
    * param page_num: 待跳转的页码元素的id, 默认id是page_num
    * param jump_btn: 跳转按钮的id, 默认id是jump_btn
    * */
    prev_page = prev_page === undefined? "prev_page": prev_page;
    prev_page = prev_page.startsWith("#")? prev_page: "#" + prev_page;
    next_page = next_page === undefined? "next_page": next_page;
    next_page = next_page.startsWith("#")? next_page: "#" + next_page;
    page_count = page_count === undefined? "page_count": page_count;
    page_count = page_count.startsWith("#")? page_count: "#" + page_count;
    page_num = page_num === undefined? "page_num": page_num;
    page_num = page_num.startsWith("#")? page_num: "#" + page_num;
    jump_btn = jump_btn === undefined? "jump_btn": jump_btn;
    jump_btn = jump_btn.startsWith("#")? jump_btn: "#" + jump_btn;
    this.prev_page = $(prev_page);
    this.next_page = $(next_page);
    this.page_count = $(page_count);
    this.page_num = $(page_num);
    this.jump_btn = $(jump_btn);
    if(this.page_count.length){
        var text = $.trim(this.page_count.text());
        if(text.indexOf("/") === -1){
            var ms = "统计页码的元素的页码格式不对,这个元素会以'1/10'的样式显示当前页面和全部页码";
            raise(ms);
        }
        else{
            var temp = text.split("/");
            var cur = parseInt(temp[0]);
            var count = parseInt(temp[-1]);
            this.cur = cur;
            this.max = count;
        }
    }
    else{
        var ms = "缺少统计页码的元素,一般来说,这个元素会以'1/10'的样式显示当前页面和全部页码";
        FoundNotDom(ms);
    }

    this.prev = function(){
        /*
        * 跳转到上一页
        */
        var page = this.cur - 1 ;
        if(page < 1){
            // nothing...
        }
        else{
            var args = get_url_arg_dict();
            args['page'] = page;
            location.href = build_url(args);
        }
    };

    this.next = function(){
        /*
        * 跳转到下一页
        */
        var page = this.cur + 1 ;
        if(page > this.max){
            // nothing...
        }
        else{
            var args = get_url_arg_dict();
            args['page'] = page;
            location.href = build_url(args);
        }
    };

    this.jump = function(){
        /*
        * 跳转到指定页
        */
        var page = $.trim(this.page_num.val());
        if(isNaN(page)){
            // nothing...
        }
        else{
            page = parseInt(page);
            if(page > this.max || page < 1){
                // nothing...
            }
            else{
                var args = get_url_arg_dict();
                args['page'] = page;
                location.href = build_url(args);
            }
        }
    };

    this.prev_page.click(() => this.prev());
    this.next_page.click(() => this.next());
    this.jump_btn.click(() => this.jump());
}

/*扩展函数注册区域*/

$.extend({
    batch_upload: batch_upload,                               // 批量上传文件，无尺寸限制
    upload: my_upload,                                        // 上传文件
    pop_alert: function(arg){pop_alert(arg);},                  // 弹出事件
    close_alert: function(){close_alert();}                  // 强制关闭弹出事件
});
$.fn.extend({
    upload: function(url, cb1, cb2, headers){my_upload2($(this), url, cb1, cb2, headers);},  // 上传文件.
    pull_down: function (call_back, args) {
        /*call_back 回调函数, args回调函数的参数的数组*/
        touch_it($(this), call_back, args);      // 页面下滑到底部后,继续下拉发生的事件
    }
});


