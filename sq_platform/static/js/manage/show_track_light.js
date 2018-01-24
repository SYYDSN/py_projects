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

let listen_click = function($obj){
    /* 监听右侧边栏司机导航的点击事件,  司机最多可以选择2个人
    * */
};

// 填充人员选择select
fill_right_bar(listen_click);  // 初始化右侧边栏

