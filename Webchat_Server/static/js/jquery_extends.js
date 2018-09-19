/*我的jquery的扩展函数*/


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
    if($obj.size() == 0){
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

var ajax_error = function(req, status, error, req_args, u){
    /*
     ajax请求错误回调
     error = NOT FOUND                404
     error = FORBIDDEN                403
     error = FORBIDDEN                401
     error = INTERNAL SERVER ERROR    500
     ...
     每次ajax出错的时候,会记录下出错的信息.发送到日志接口.
     如果发送到日志接口出错.那就保存在本地的会话里,不再由本函数发送.
     日志接口请自行实现


     (将由其他的函数进行批量处理,暂时不实现 2018-9-13)
      */
    console.log("Ajax_Error start");
    // console.log(req);
    // console.log(status);
    console.log(u);
    console.log(error);
    console.log(req_args);
    console.log("Ajax_Error end");
    var now = new Date();
    var error_time = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()} ${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}.${now.getMilliseconds()}`;
    console.log(`error time is ${error_time}`);
    // 这是其他函数post失败的情况
    var args = {
        "args": JSON.stringify(req_args),
        "url": u,
        "ajax_error_count": 1,
        "error": error,
        "error_time": error_time
    };
    $.post("/teacher/log", args, function(r){
        close_alert();
        alert("操作失败");
        try{
            var a = JSON.parse(r);
            console.log(a);
        }
        catch(e){
            console.log(r);
        }
    });

};

var post_plus = function (url, args, callback){
    var setting = {
        url: url,
        type: "POST",
        error:function(arg1, arg2, arg3){ajax_error(arg1, arg2,arg3, args, url)}, // 请求完成时的回调.
        data: args,                                 // 参数
        success: callback                           // 成功时的回调
    };
    $.ajax(setting);
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

function my_upload2($obj, url, success_cb, error_cb){
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
        error_cb: error_cb,
    };
    return my_upload(opts);
}


/*扩展函数注册区域*/

$.extend({
    upload: my_upload,                                        // 上传文件
    post: post_plus,                                          //重定义post
    pop_alert: function(arg){pop_alert(arg);},                  // 弹出事件
    close_alert: function(){close_alert();}                  // 强制关闭弹出事件
});
$.fn.extend({
    upload: function(url, cb1, cb2){my_upload2($(this), url, cb1, cb2);},  // 上传文件.
    pull_down: function (call_back, args) {
        /*call_back 回调函数, args回调函数的参数的数组*/
        touch_it($(this), call_back, args);      // 页面下滑到底部后,继续下拉发生的事件
    }
});


