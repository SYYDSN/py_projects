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

init_map();

// 全局变量
let global_track_time_list = [];  // 轨迹索引的时序，用于确认轨迹点的时间。
let global_track_data_list = [];  // 轨序列，用于保存多条轨迹

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
                let track_time_list = global_track_time_list[pathIndex];
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
        "ids": get_url_arg("ids"),
        "date": get_url_arg("date")
    };
    $.post(server + "/manage/track_info", args, function (raw_data) {
        let data = JSON.parse(raw_data);
        if (data['message'] === "success") {
            let data_list = data['data'];
            let count = data['count'];
            if (count === 0) {
                pop_tip_div("没有找到轨迹信息");
            }
            else {
                let nav_index = 0;
                for (let item of data_list) {
                    // 可能有多个轨迹
                    let user_id = item['user_id'];
                    let track_dict = item['track_dict'];
                    let tracks = track_dict['track_list'];   // 轨迹点数组
                    let total_mileage = track_dict['total_mileage'];  // 轨迹总里程.单位km
                    let total_time = track_dict['total_time'];  // 轨迹总耗时 单位秒
                    console.log(user_id, total_mileage, total_time, tracks.length);
                    let path_list = [];  // 路径点集合
                    let time_list = [];  // 时序集合
                    let length = tracks.length;
                    if (length > 1) {
                        nav_index += 1;
                        for (let i = 0; i < length; i++) {
                            let raw = tracks[i];
                            path_list.push(raw['loc']);
                            time_list.push(raw['time']);
                        }
                        global_track_time_list.push(time_list);  //  时序点数组入全局变量 。
                        global_track_data_list.push({
                            "name": $(`#right_bar>div[data-id='${user_id}'] .driver_name`).text(),
                            "path": path_list
                        });  //  轨迹点数组入全局变量 。
                    } else {
                        // pass
                    }
                }
                pathSimplifierIns.setData(global_track_data_list);
                // 计算回放速度

                let nav_speed = 3000;
                //创建一个巡航器
                let colors = ['orange', 'blue'];
                for(let i=0;i<nav_index;i++){
                    var navg = pathSimplifierIns.createPathNavigator(i, //关联第1条轨迹
                        {
                            loop: true, //循环播放
                            speed: nav_speed,
                            pathNavigatorStyle:{              // 巡航器样式
                                fillStyle: colors[i],
                                strokeStyle: colors[i],
                                pathLinePassedStyle: {         // 经过的路径样式
                                    ineWidth: 2,
                                    strokeStyle: '#b39696',
                                    borderWidth: 1,
                                    borderStyle: '#b39696',
                                    dirArrowStyle: false
                                }
                            }
                        });

                    navg.start();
                }
            }
        }
        else {
            alert(data['message']);
        }
    })
};

let selected_drivers = [];  // 被选中的司机的id的容器,
let listen_click = function ($obj) {
    /* 监听右侧边栏司机导航的点击事件,  司机最多可以选择2个人
    * */
    let user_id = $.trim($obj.attr("data-id"));
    let in_selected = selected_drivers.indexOf(user_id);
    if (in_selected === -1) {
        selected_drivers.push(user_id);           // 添加司机
    }
    else {
        selected_drivers.splice(in_selected, 1);  // 删除这个司机就
    }
    if (selected_drivers.length > 2) {
        // 数组长度大于2就截断
        selected_drivers = selected_drivers.slice(selected_drivers.length - 2);  // 最多2个司机
    }
    $("#right_bar .nav_item").each(function () {
        let $this = $(this);
        if (selected_drivers.indexOf($.trim($this.attr("data-id"))) === -1) {
            $this.removeClass("selected_driver");
        }
        else {
            $this.addClass("selected_driver");
        }
    });
};

// 填充人员选择select
fill_right_bar(listen_click);  // 初始化右侧边栏

// 点击日期输入栏的之前,清除input的值,防止显示1899年份的bug

$("#my_datetime_picker").mousedown(function () {
    $(this).val("");
});

// 这个日期插件有少许问题,必须要点击右侧空白的地方才有效.弹出和隐藏日期选择区域的功能暂时搁置.
//
// // 输入框失焦事件
// $("#main_zone").click(function(){
//     console.log(1);
//     if($("#my_datetime_picker:visible").length > 0){
//         console.log("click");
//         $("#right_bar").click();  // 隐藏日期选择区域
//     }
// });

// 日期选择器改变日期的函数
let selected_dates = [];  // 日期最多可以选相邻的2天
function change_date() {
    /*
    * 点击日期的时候的事件.
    * */
    let first_date = $.trim($("#my_datetime_picker").val());
    console.log(`first_date is ${first_date}`);
    let in_selected = selected_dates.indexOf(first_date);
    if (in_selected === -1) {
        if (selected_dates.length === 0) {
            selected_dates.push(first_date);           // 添加日期
        }
        else if (selected_dates.length === 1) {
            let old = selected_dates[0];
            let day = parseInt(old.split("-")[2]);
            let old_date = new Date(old);
            let new_date_0 = new Date(first_date);

            if ((old_date.setDate(day - 1) - new_date_0) === 0 || (old_date.setDate(day + 1) - new_date_0) === 0) {
                selected_dates.push(first_date);           // 添加日期
            }
            else {
                selected_dates = [first_date];
            }
        }
        else {
            let old_0 = selected_dates[0];
            let day_0 = parseInt(old_0.split("-")[2]);
            let old_date_0 = new Date(old_0);
            let old_1 = selected_dates[1];
            let day_1 = parseInt(old_1.split("-")[2]);
            let old_date_1 = new Date(old_1);
            let new_date_0 = new Date(first_date);

            if ((old_date_0.setDate(day_0 - 1) - new_date_0) === 0 || (old_date_1.setDate(day_1 + 1) - new_date_0) === 0) {
                selected_dates.push(first_date);           // 添加日期
            }
            else {
                selected_dates = [first_date];
            }
        }

    }
    else {
        selected_dates = [first_date];  // 只选择这个日期
    }

    selected_dates.sort();  // 排序

    if (selected_dates.length > 2) {
        // 数组长度大于2就截断
        if (selected_dates.indexOf(first_date) === 0) {
            // 判断新加的数组是在头部还是在尾部?
            selected_dates = selected_dates.slice(0, 2);  // 截取头部 最多2个日期
        }
        else {
            selected_dates = selected_dates.slice(selected_dates.length - 2);  // 截取尾部 最多2个日期
        }

    }
    let date_str = selected_dates.join(" ");
    $("#my_datetime_picker").val(date_str);
}

// 初始化日期选择器
(function (last_date_str) {
    // 日期插件文档 http://www.bootcss.com/p/bootstrap-datetimepicker/
    // 参数last_date_str是最后一个可用的日期,本例没有用处
    $("#my_datetime_picker").datetimepicker({
        language: "zh-CN",
        weekStart: 1,  // 星期一作为一周的开始
        minView: 2,  // 不显示小时和分
        startView: 2,
        autoclose: false,  // 选定日期后是否立即关闭选择器
        format: "yyyy-mm-dd",
    }).on("show", function (ev) {
        // 当选择器显示时被触发
        console.log(ev);
        console.log("选择器面板被打开");
        let begin_date = null;
        if (selected_dates.length > 1) {
            begin_date = selected_dates[0];
            /*防止浏览器之间的差异,这里必须做手动转换,以保证时间字符串格式的一致性*/
            let list = begin_date.split("-");
            let y = list[0];
            let m = list[1];
            let d = parseInt(list[2]);
            begin_date = `${y}-${m}-01`;
            $('#my_datetime_picker').datetimepicker('setStartDate', begin_date);
            // 选中2个日期?因为和删除日期有逻辑矛盾,搁置.
            // let index_1 = d - 1;
            // let index_2 = parseInt(selected_dates[1].split("-")[2]) - 1;
            // let days = $(".day:not(.old):not(.new)");
            // $(days[index_1]).addClass("active");
            // $(days[index_2]).addClass("active");
        }
        else {
            // 默认行为即可
        }
    }).on("changeDate", function (ev) {
        // 当日期被改变时被触发
        console.log(ev);
        console.log("选择器日期被改变");
        change_date();
    }).on("hide", function (ev) {
        // 当日期被隐藏时被触发
        console.log(ev);
        console.log("选择器日期被隐藏");
        // 填充日期选择器input
        let date_str = selected_dates.join(" ");
        $("#my_datetime_picker").val(date_str);
    });
})();
// 查询提交按钮的事件
$("#submit_query").click(function () {
    let date_str = $.trim($("#my_datetime_picker").val());
    let date_list = date_str.split(" ");  // 拆分成开始和结束时间
    let result_dates = [];    // 起终点日期容器
    let result_drivers = [];   // 选择的司机的容器
    for (let i = 0; i < date_list.length; i++) {
        let cur = date_list[i];
        /*防止浏览器之间的差异,这里必须做手动转换,以保证时间字符串格式的一致性*/
        let char_list = cur.split("-");
        let year = char_list[0];
        let month = String(char_list[1]).length < 1 ? "0" + char_list[1] : char_list[1];
        let day = String(char_list[2]).length < 1 ? "0" + char_list[2] : char_list[2];
        let query_date = `${year}-${month}-${day}`;  // 查询日期
        if (typeof(query_date) !== "undefined") {
            result_dates.push(query_date);
        } else {
        }

    }
    // 取选择的用户
    $("#right_bar .selected_driver").each(function () {
        let cur = $(this);
        let user_id = $.trim(cur.attr("data-id"));
        result_drivers.push(user_id);

    });
    if (result_drivers.length === 0) {
        alert("至少选择一名司机");
        return false;
    }
    else if (result_dates.length === 0) {
        alert("必须选择日期");
        return false;
    }
    else {
        let to_url = `/manage/show_track?ids=${JSON.stringify(result_drivers)}&date=${JSON.stringify(result_dates)}`;
        location.href = to_url;
    }
});

// 根据url参数对页面初始化
let user_id_list = JSON.parse(get_url_arg("ids"));
let date_list = JSON.parse(get_url_arg("date"));
console.log(user_id_list);
console.log(date_list);
if (date_list !== null) {
    $("#my_datetime_picker").val(date_list.join(" "));
}
if (user_id_list !== null) {
    let flag = true;
    let interval = setInterval(function () {
        if (flag) {
            if ($("#right_bar>div").length > 0) {
                flag = false;
            }
        } else {
            $("#right_bar>div").each(function () {
                let $this = $(this);
                if (user_id_list.indexOf($this.attr("data-id")) !== -1) {
                    $this.click();
                }
            });
            clearInterval(interval);
        }
    }, 200);
}

