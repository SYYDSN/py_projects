/**
 * Created by walle on 17-8-23.
 * 一些常用的自定义插件和函数。这里的插件和函数都是通用性较强的
 */
$(function(){

    /*一组拖动事件*/
    allowDrop = function (ev) {
        ev.preventDefault();
    };

    drag = function (ev) {
        // nothing...
    };

    drop = function(ev){
        ev.preventDefault();
        var $obj = $("#suspend_outer");
        var top = ev.pageY;
        var left = ev.pageX;
        var width = $obj.width();
        var all_width = $("body").width();
        var right = all_width - left - width;
        console.log(top, right);
        $obj.css({"top": top - offset_y, "right": right + offset_x});
    };

    mouse_down = function(ev){
        var $obj = $("#suspend_outer");
        var x1 = ev.pageX;
        var y1 = ev.pageY;
        var x2 = $obj.position().left;
        var y2 = $obj.position().top;
        offset_x = x1 - x2;
        offset_y = y1 - y2;
    };

    /*点击改变搜索的类型*/

    /*创建一个输入框的dom*/
    create_input_dom = function(){
        var dom ="<div onmousedown='mouse_down(event)' ondragstart='drag(event)' id='suspend_outer' style='opacity:0.7;top:100px; right:10px;z-index:200;position:fixed;' draggable='true'>" +
            "<div id='suspend_div' style='margin:20px;width:360px;box-shadow: 6px 6px 6px lightgrey;display:block;background-color: white'>" +
            "<div class='input-group'>" +
            "<input type='text' style='' class='form-control' id='suspend_input'>" +
            "<div class='input-group-btn'>" +
            "<button style='border-radius:0px;' type='button' class='btn btn-default dropdown-toggle' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>" +
            "phone " +
            "<span class='caret'></span>" +
            "</button>" +
            "<ul class='dropdown-menu dropdown-menu-right'>" +
            "<li><a onclick='change_search_type($(this))' data-val='phone_num' href='javascript:;'>phone</a></li>" +
            "<li><a onclick='change_search_type($(this))' data-val='real_name'  href='javascript:;'>name</a></li>" +
            "<li><a onclick='change_search_type($(this))' data-val=user_name'  href='javascript:;'>user ID</a></li>" +
            "<li style='display:none'  role='separator' class='divider'></li>" +
            "<li style='display:none' ><a href='javascript:;'>Separated link</a></li>" +
            "</ul>" +
            "</div>" +
                "<span class='input-group-btn'><button style='' class='btn btn-default' type='button'>Go!</button></span>"+
            "</div>" +
            "</div>" +
            "</divondragstart></div>";
        
        var res = $(dom);
        $("body").append(res);
        return res;
    };

    /*一个悬浮输入框*/
    suspend_inut_init = function(top, right){
        /*
        * top，right框体距离顶部和右边的距离。
        * */
        var res = create_input_dom();


    };
    /*此输入框，暂时没有决定是否使用*/
    // suspend_inut_init();  // 执行
//end!
});