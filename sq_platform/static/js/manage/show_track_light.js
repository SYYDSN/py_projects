/*重设窗口尺寸*/
function set_window() {
    /*计算并重设主显示区域高度*/
    $(".main").css("height", "100%");
    let main_height = $(".main").height();
    console.log(main_height);
    $(".main").css("height", main_height);
    $("#main_zone").css("height", main_height);
    /*计算并重设左侧导航栏宽度,影响手机界面,作罢*/
}

set_window();
window.onresize = function () {
    // 修改窗口大小事件
    set_window();
};

//
// function init_map() {
//     // 初始化高德地图事件
//     map = new AMap.Map('main_zone', {
//         resizeEnable: true,
//         center: [121.304239, 31.239981],    // 坐标位置
//         zoom: 11
//     });
// }
init_map();

// 全局变量
let track_time_list = [];  // 轨迹索引的时序，用于确认轨迹点的时间。

//加载PathSimplifier，loadUI的路径参数为模块名中 'ui/' 之后的部分
AMapUI.load(['ui/misc/PathSimplifier'], function (PathSimplifier) {
    // 加载组件
    if (!PathSimplifier.supportCanvas) {
        alert('当前环境不支持 Canvas！');
        return;
    }

    //启动页面
    initPage(PathSimplifier);
});

function initPage(PathSimplifier) {
    //创建组件实例
    pathSimplifierIns = new PathSimplifier({
        zIndex: 100,
        map: map, //所属的地图实例
        getPath: function (pathData, pathIndex) {
            //返回轨迹数据中的节点坐标信息，[AMap.LngLat, AMap.LngLat...] 或者 [[lng|number,lat|number],...]
            return pathData.path;
        },
        getHoverTitle: function (pathData, pathIndex, pointIndex) {
            //返回鼠标悬停时显示的信息
            if (pointIndex >= 0) {
                //鼠标悬停在某个轨迹节点上
                var point = pathData['path'][pointIndex];
                var cur_time = track_time_list[pointIndex].split(".")[0];
                console.log(point);
                return '第' + pointIndex + '/' + pathData.path.length + '节点。时间:' + cur_time + '';
            }
            //鼠标悬停在节点之间的连线上
            return pathData.name + '，点数量' + pathData.path.length;
        },
        renderOptions: {
            //轨迹线的样式
            pathLineStyle: {
                strokeStyle: 'red',
                lineWidth: 6,
                dirArrowStyle: true
            }
        }
    });
    setTimeout(function () {
        query_track_info();
    }, 800);
}

// 查询数据
query_track_info = function () {
    var args = {
        "phone_num": get_url_arg("phone_num"),
        "begin_date": get_url_arg("begin_date"),
        "end_date": get_url_arg("end_date")
    };
    $.post(server + "/manage/track_info", args, function (raw_data) {
        let data = JSON.parse(raw_data);
        if (data['message'] === "success") {
            let data_set = data['data'];
            let data_list = data_set['track_list'];
            let total_mileage = data_set['total_mileage'];
            let total_time = data_set['total_time'];
            let length = data_list.length;
            if (length === 0) {
                pop_tip_div("没有找到轨迹信息");
            }
            else {
                let path_list = [];
                let time_list = [];
                console.log(data_list[0]);
                console.log(data_list[-1]);
                for (let i = 0; i < length; i++) {
                    let raw = data_list[i];
                    path_list.push(raw['loc']);
                    time_list.push(raw['time']);
                }
                console.log(path_list.length);
                track_time_list = time_list;  // 给时序点数组赋值。
                pathSimplifierIns.setData([{
                    name: '轨迹0',
                    path: path_list
                }]);
                // 计算回放速度

                let nav_speed = 10;
                //创建一个巡航器
                var navg0 = pathSimplifierIns.createPathNavigator(0, //关联第1条轨迹
                    {
                        loop: true, //循环播放
                        speed: nav_speed
                    });

                navg0.start();
            }
        }
        else {
            alert(data['message']);
        }
    })
};

let selected_drivers = [];  // 被选中的司机的id的容器,
let listen_click = function($obj){
    /* 监听右侧边栏司机导航的点击事件,  司机最多可以选择2个人
    * */
    let user_id = $.trim($obj.attr("data-id"));
    let in_selected = selected_drivers.indexOf(user_id);
    if(in_selected === -1){
        selected_drivers.push(user_id);           // 添加司机
    }
    else{
        selected_drivers.splice(in_selected, 1);  // 删除这个司机就
    }
    if(selected_drivers.length > 2){
        // 数组长度大于2就截断
        selected_drivers = selected_drivers.slice(selected_drivers.length - 2);  // 最多2个司机
    }
    $("#right_bar .nav_item").each(function(){
        let $this = $(this);
        if(selected_drivers.indexOf($.trim($this.attr("data-id"))) === -1){
            $this.find(".driver_name").css("color", "#7c8ff3");
        }
        else{
            $this.find(".driver_name").css("color", "orange");
        }
    });
};

// 填充人员选择select
fill_right_bar(listen_click);  // 初始化右侧边栏

// 点击日期输入栏的时候,关闭日期选择器的day的默认点击事件.
$("#my_datetime_picker").click(function(){
    $(".day").unbind("click");
});

// 日期选择器改变日期的函数
let selected_dates = [];  // 日期最多可以选相邻的2天
function change_date(){
    /*
    * 点击日期的时候的事件.
    * */
    let first_date = $.trim($("#my_datetime_picker").val());
    console.log(`first_date is ${first_date}`);
    let in_selected = selected_dates.indexOf(first_date);
    if(in_selected === -1){
        if(selected_dates.length === 0){
            selected_dates.push(first_date);           // 添加日期
        }
        else{
            let old = selected_dates[0];
            let day = parseInt(old.split("-")[2]);
            let old_date = new Date(old);
            let new_date = new Date(first_date);

            if((old_date.setDate(day - 1) - new_date) === 0 || (old_date.setDate(day + 1) - new_date) === 0){
                selected_dates.push(first_date);           // 添加日期
            }
            else{
                selected_dates = [first_date];
            }
        }

    }
    else{
        selected_dates.splice(in_selected, 1);  // 删除这个日期
    }

    if(selected_dates.length > 2){
        // 数组长度大于2就截断
        selected_dates = selected_dates.slice(selected_dates.length - 2);  // 最多2个日期
    }
    let date_str = selected_dates.join("~");
    $("#my_datetime_picker").val(date_str);
}

// 初始化日期选择器
(function (last_date_str) {
    // 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/
    // 参数last_date_str是最后一个可用的日期,本例没有用处
    $("#my_datetime_picker").datetimepicker({
        language: "zh-CN",
        weekStart:1,  // 星期一作为一周的开始
        minView: 2,  // 不显示小时和分
        startView: 2,
        autoclose: false,  // 选定日期后是否立即关闭选择器
        format: "yyyy-mm-dd"
    }).on("show", function(ev){
        // 当选择器显示时被触发
        console.log(ev);
        console.log("选择器面板被打开");
        $('#my_datetime_picker').datetimepicker('setStartDate', selected_dates[0]);
    }).on("hide", function(ev){
        // 当选择器隐藏时被触发 示范,无实际意义
        console.log(ev);
        console.log("选择器面板被隐藏");
    }).on("changeDate", function(ev){
        // 当日期被改变时被触发
        console.log(ev);
        console.log("选择器日期被改变");
        change_date();
    }).on("hide", function(ev){
        // 当日期被隐藏时被触发
        console.log(ev);
        console.log("选择器日期被隐藏");
        // 填充日期选择器input
        let date_str = selected_dates.join("~");
        $("#my_datetime_picker").val(date_str);
    });
})();
// 查询提交按钮的事件
$("#submit_query").click(function(){
    let date_str = $.trim($("#my_datetime_picker").val());
    let date_list = date_str.split("-");
    let year = date_list[0];
    /*防止浏览器之间的差异,这里必须做手动转换,以保证时间字符串格式的一致性*/
    let month = String(date_list[1]).length < 1? "0" + date_list[1]:date_list[1];
    let day = String(date_list[2]).length < 1? "0" + date_list[2]:date_list[2];
    let query_date = `${year}-${month}-${day}`;  // 查询日期
    // 取选择的用户

});

