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

$.extend({
    pop_alert: function(arg){pop_alert(arg);},                  // 弹出事件
    close_alert: function(){close_alert();}                  // 强制关闭弹出事件
});
$.fn.extend({
    pull_down: function (call_back, args) {
        /*call_back 回调函数, args回调函数的参数的数组*/
        touch_it($(this), call_back, args);      // 页面下滑到底部后,继续下拉发生的事件
    }
});


