/*重设窗口尺寸*/
function set_window() {
    /*计算并重设主显示区域高度*/
    $(".main").css("height", "98.5%");
    let main_height = $(".main").height();
    console.log(main_height);
    $("#main_zone").css("height", main_height);
    $("#driver_box").css("max-height", main_height - $("#driver_box").offset().top);
    /*计算并重设左侧导航栏宽度,影响手机界面,作罢*/
}

set_window();
window.onresize = function () {
    // 修改窗口大小事件
    set_window();
};

function get_offset_for_nav() {
    /*
     * 获取因浏览器差异造成的偏移不同的数组。
     * */
    if(is_ff()){
        return new AMap.Pixel(63, -19);
    }
    else{
        return new AMap.Pixel(73, -23);
    }
}

// 把司机们的姓填入筛选司机区域
let add_first_name = function(first_names){
    // 参数是姓的数组
    let first_name_container = $("#right_bar_handler_bottom>ul");
    first_name_container.empty();
    let html = "";
    for(let first_name of first_names){
        html += `<li onclick="show_cur_first_name($(this))">${first_name}</li>`;
    }
    first_name_container.append(html);
};

// 隐藏除给定姓氏之外的司机
hide_other_first_name_drivers = function(first_name){
    let drivers = $("#driver_list>.my_li");
    if(typeof(first_name) === "undefined" || $.trim(first_name) === ""){
        drivers.show();
    }else{
       let re_name = $.trim(first_name);
        let l = drivers.length;
        for(let i=0;i<l;i++){
            let cur = $(drivers[i]);
            let cur_name = $.trim(cur.find(".real_name span").text());
            if(cur_name.indexOf(re_name) === 0){
               cur.show();
            }
            else{
                cur.hide();
            }
        }
    }

};

// 点击的时候只显示当前选中的姓氏的列表
function show_cur_first_name($obj){
    // $obj 实际上就是 $(this)
    let first_name = $.trim($obj.text());
    $("#search").val(first_name);
    hide_other_first_name_drivers(first_name);
}

// 放大镜搜索按钮事件
$("#btn").click(function(){
    let first_name = $.trim($("#search").val());
    hide_other_first_name_drivers(first_name);
});

// 姓氏输入框的事件
let delay_submit = null;
$("#search").keyup(function(e){
    clearTimeout(delay_submit);
    let code = e.keyCode;
    if(code === 13){
        let first_name = $.trim($(this).val());
        hide_other_first_name_drivers(first_name);
    }else{
        // 清除输入框显示全部司机
        let first_name = $.trim($(this).val());
        if(first_name === ""){
            hide_other_first_name_drivers(first_name);
        }else{
            delay_submit = setTimeout(function(){
                hide_other_first_name_drivers(first_name);
            },400);
        }
    }
});

// 显示全部司机
$("#right_bar_handler .icon-quanbu").click(function(){
    $("#search").val('');
    hide_other_first_name_drivers('');
});

// 函数字典，用于最小化全局污染。
func_dict = {};
function get_marker(arg_dict) {
    /*
    * 获取一个AMap.Marker的实例。
    * arg_dict为字典格式的参数。
    * marker.setMap(map);
    * */
    let res = new AMap.Marker({
        position: arg_dict === undefined ? [121.504239, 31.239981] : arg_dict['position'],  // 经纬度
        title: arg_dict === undefined ? "name" : arg_dict['position'], // 名字
    });
    return res;
}
func_dict['get_marker'] = get_marker;  // 加入函数集

// 为每个自定义标记点增加鼠标事件
let custom_maker_hover = function(custom_marker_obj){
    // 参数是高德的自定义marker对象.
    AMap.event.addListener(custom_marker_obj, "mouseover", function(e) {
        // 鼠标进入自定义标记点时
        let user_id = this.G.extData;
        console.log("user_id is " + user_id);
        let label = $(`#marker_table_${user_id}`);
        label.css("display", "block");
        label.parents(".amap-marker-label:first").find("img").css("display", "block");
        label.parents(".amap-marker-label:first").animate({"width": 220}, 200);
        let tips_html = '<li><span>暂无相关警示信息</span></li>';
        $(".alarm_tips").html(tips_html);
        let cur_img_src = label.parents(".amap-marker-label:first").find("img").attr("src");
        if (cur_img_src === "./image/head_img/lan.png") {
            $('.inner_left img').attr("src", "../static/image/icon/anquan.png");
            $(".inner_left img").attr("class", "anquan_img");
        } else {
            $('.inner_left img').attr("src", "../static/image/icon/alarm_big_circle.png");
            $(".inner_left img").attr("class", "alarm_img");
        }
    });

        AMap.event.addListener(custom_marker_obj, "mouseout", function(e){
            // 鼠标移动出自定义标记点时
        let user_id = this.G.extData;
        // console.log("user_id is "+user_id);
        let label = $(`#marker_table_${user_id}`);
        setTimeout(function(){
            label.css("display","none");
            label.parents(".amap-marker-label:first").find("img").css("display","none");
        }, 200);
        label.parents(".amap-marker-label:first").animate({"width":0},200);
        let tips_html = '<li><span>沪宁高速路口有交通事故发生</span></li>' + '<li><span>心率偏高危险</span></li>' + '<li><span>前方有事故请绕道行驶，注意安全。</span></li>' + '<li><span>司机已长时间驾驶，注意休息。</span></li>';
        $(".alarm_tips").html(tips_html);
        $('.inner_left img').attr("src", "../static/image/icon/alarm_big_circle.png");
        $(".inner_left img").attr("class", "alarm_img");

    });
};
func_dict['custom_maker_hover'] = custom_maker_hover;  // 加入函数集

// 初始化ui库
initAMapUI();
let ui_init_success = false; // ui组件是否初始化完成的标志位
AMapUI.loadUI(['overlay/AwesomeMarker'], function (AwesomeMarker) {
    /*
    * 加载ui插件
    * */
    let get_awe_marker = function (arg_dict) {
        /*
        *有关ａｗｅ图标的细节，请参看http://fontawesome.io/examples/
        * 下举个例子：
        *卡车图标。
        * <i class='fa fa-truck fa-2x fa-flip-vertical' aria-hidden='true'></i>
        * ２倍大小的卡车图标向右。
        * fa-truck　　卡车图标名
        * fa-2x　　２倍尺寸，　fa-1g 原始大小
        * fa-flip-vertical　向右，默认是向左。
        * <i class='fa fa-truck fa-2x ' style='background:black;color:white' aria-hidden='true'></i>
        * ２倍大小的卡车图标，设置背景色为黑色，卡车为白色。
        * 利用fa-stack类，还可以实现图标的堆叠。
        * <span class="fa-stack fa-lg">
        *   <i class="fa fa-square-o fa-stack-2x"></i>
        *   <i class="fa fa-twitter fa-stack-1x"></i>
        * </span>
        * */
        let user_id = typeof(arg_dict['user_id']) === "undefined"? "guest" : arg_dict['user_id'] ;
        let real_name = typeof(arg_dict['real_name']) === "undefined"? arg_dict['phone_num'] : arg_dict['real_name'] ;
        let security_score = typeof(arg_dict['security_score']) === "undefined"? 80 : arg_dict['security_score'] ;
        let time = typeof(arg_dict['time']) === "undefined"? '' : arg_dict['time'] ;

        let icon_img = [
            "/static/image/head_img/lan.png",
            "/static/image/head_img/hong.png",
        ];
        let cur_user_id = arg_dict['user_id'];
        let custom_marker = new AMap.Marker({
            map: map,
            position: arg_dict === undefined ? [121.504239, 31.239981] : arg_dict['loc'],
            extData: cur_user_id,
            icon: new AMap.Icon({
                size: new AMap.Size(46, 64),  // 图标大小
                image: icon_img[0]            // 都是蓝色的图标
            })
        });


        let imgs = ["/static/image/head_img/zMsb-fximeyv2774914.jpg","/static/image/head_img/2015111093556890.jpg","/static/image/head_img/2014092116375761ad6.jpg","/static/image/head_img/16080904183524.jpg","/static/image/head_img/16072910584233.jpg"];
        let num = parseInt(Math.random() * imgs.length);
        let content=[];
        content.push(`<ul id='marker_table_${cur_user_id}'><li><span>姓名</span>
                      <span>${real_name}</span></li><li><span>部门</span>
                      <span>华新分拨公司</span></li><li><span>电话</span>
                      <span>${arg_dict.phone_num}</span></li></ul>
                      <img src="${imgs[num]}">`);
        // 图片图标，由于这个图片方向性太强，实用需要同时选择图标，比较复杂，稍后再处理。
        // track_content = "<img class='img' src='/static/image/icon/normal_truck.png'/>";
        // obj.setContent(track_content);   // 设置定义点样式。
        // 设置label，也就是自定义点的信息框体
        custom_marker.setLabel({
            offset: new AMap.Pixel(-1, -2),  // 调整偏移量
            isCustom: true,
            content: content
        });
        custom_maker_hover(custom_marker);
        custom_marker.setMap(map);
        return custom_marker;
    };

    func_dict['get_awe_marker'] = get_awe_marker;  // 加入函数集

    // 定义一个修改地图中心位置的函数。全局函数，不加入函数集
    let set_map_center = function (position){
        map.setCenter(position);
    };

    // 定义右侧边栏元素的头像的点击事件--点击头像调整地图坐标到中心位置。全局函数，不加入函数集
    to_map_center = function($obj){
        let position = $obj.parents(".item_main:first").attr("data-position").split(",");
        set_map_center(position);
    };
    // 定义一个追加右侧边栏元素的函数
    let add_right_side_bar_item = function(arg_dict){
        // 用户id
        let user_id = arg_dict['_id'] !== undefined? arg_dict['_id']: arg_dict['user_id'];
        // 用户头像
        let head_img_url = arg_dict['head_img_url'] === undefined ? "/static/image/head_img/default_01.png": "/"+arg_dict['head_img_url'];
        // 用户手机
        let phone_num = arg_dict['phone_num'] === undefined ? "1580080080": arg_dict['phone_num'];
        // 真实姓名
        let real_name = typeof(arg_dict['real_name']) === "undefined" ? phone_num: arg_dict['real_name'];
        real_name = real_name === ""?phone_num: real_name;
        // 当前位置
        let position = arg_dict['position'] === undefined ? [121.304239, 31.239981]: arg_dict['position'];
        // 车辆型号
        let car_model = arg_dict['car_model'] === undefined ? "9.6m": arg_dict['car_model'];
        // 驾驶时长
        let drive_time = arg_dict['drive_time'] === undefined ? "4h": arg_dict['drive_time'];
        // 行驶里程
        let mileage = arg_dict['mileage'] === undefined ? "3k+": arg_dict['mileage'];
        // 不良记录/跟安全有关的事件
        let event_count = arg_dict['event_count'] === undefined ? "0": arg_dict['event_count'];
        // 最后通信时间
        let time = arg_dict['time'] === undefined ? "未知": arg_dict['time'].split(".")[0];
        // 版本信息
        let app_version = arg_dict['app_version'] === undefined ? "未知": arg_dict['app_version'];
        // 最后一个数据到现在的时间差，单位秒
        let time_delta =  arg_dict['time_delta'] === undefined ? 0: parseInt(arg_dict['time_delta']);
        // 计算颜色
        let name_color = "#408DBC";
        if(time_delta < 60 * 10){
            // pass
        }
        else if(time_delta < 60 * 60){
            name_color = color_normal_16;
        }
        else if(time_delta < 60 * 60 * 12){
            name_color = "#FFA500";
        }
        else{
            name_color = color_danger_16;
        }

        let right_bar_html_str = `<li class="my_li" data-id="${user_id}">
            <div class="item_main" data-position="${position}">
            <div class="left_side">
                <img title="最后通信时间:${time}\napp版本:${app_version}" onclick="to_map_center($(this))" class="side_bar_img"src="${head_img_url}">
            </div>
            <ul class="my_ul">
                <li class="my_li real_name my_flex">
                    <span  style="color:${name_color}">${real_name}</span>
                    <a target="_blank" href='/manage/track?ids=["${user_id}"]'>
                        <i title="查看轨迹" class="fa fa-dot-circle-o icon_mouse_leave" aria-hidden="true"></i>
                    </a>
                </li>
                <li class="my_li my_flex">
                    <span>车型:</span><span>${car_model}</span>
                    <span class="margin-right">驾驶时长:</span><span>${drive_time}</span>
                </li>
                <li class="my_li my_flex">
                    <span>里程:</span><span>${mileage}</span>
                    <span class="margin-right">不良记录:</span><span>${event_count}</span>
                </li>
            </ul>
            </div>
            <div class="item_bottom">
                <svg style="margin-bottom:2px" class="xs_icon yujing_mian normal_status" aria-hidden="true">
                    <use xlink:href="#icon-yujing_mian"></use>
                </svg>
                <span class="current_message">当前路况良好</span>
            </div>
            <hr>
            </li>`;

        $("#driver_list").append(right_bar_html_str);
    };

    func_dict['add_right_side_bar_item'] = add_right_side_bar_item;  // 加入函数集

    check_map_init([init_right_bar, last_positions]); // 启动时检查map,并加载一次

});
console.log("end init AwesomeMarker...");

// 检查map是否初始化结束?,如果map正常,则运行func,否则等待.
check_map_init = function(func){
    let interval = setInterval(function(){
        let check = typeof(map);
        if(check === "undefined"){
            // waiting....
        }
        else{
            if(typeof(func) === "function"){
                func();
            }
            else{
                for(let f of func){
                    f();
                }
            }
            clearInterval(interval);
        }
    }, 200);
};


// 一个按照人数多少排序的函数,用于只选择人数最多的前20个姓氏排序显示
let compare_name = function(obj1, obj2){
    let count1 = obj1['count'];
    let count2 = obj2['count'];
    if(count2 > count1){
        return 1;
    }
    else if(count2 < count1){
        return -1;
    }
    else{
        return 0;
    }
};

// 从司机姓氏字典中取出人数最多的前20个,然后组成数组返回
let top_20 = function(name_dict){
    let list = [];
    for(let k in name_dict){
        let temp = {"name": k, "count": name_dict[k]};
        list.push(temp);
    }
    list.sort(compare_name);
    let res = [];
    let l = list.length;
    l = l > 20? 20: l;
    for(let i=0;i<l;i++){
        console.log(i);
        let temp = list[i];
        res.push(temp['name']);
    }
    return res;
};


// 初始化右边栏
let init_right_bar = function() {
    /*
    * 和common.js的fill_right_bar方法不同,本方法是电子地图首页专用的.
    * fill_right_bar填充的右边栏更简单
    * */
    $.post("/manage/driver_list", function (resp) {
        let data = JSON.parse(resp)['data'];
        console.log(data);
        $("#driver_list").empty();  // 清除旧的右侧导航
        $("#driver_count").text(data.length);
        let name_dict = {};
        let add_right_side_bar_item_func = func_dict['add_right_side_bar_item'];
        for (let p of data) {
            add_right_side_bar_item_func(p);  // 添加右侧边栏
            let real_name = p['real_name'];
            if(isNaN(real_name) && real_name !== ""){
                // 如果用户没有真名,那就不做此项操作
                if(real_name !== undefined && real_name.length > 0){
                    let first_name = real_name[0];
                    let count = name_dict[first_name];
                    if(count === undefined){
                        count = 1
                    }
                    else{
                        count += 1;
                    }
                    name_dict[first_name] = count;
                }
            }
        }
        console.log(name_dict);
        //从司机姓氏字典中取出人数最多的前20个姓氏的数组
        let first_names = top_20(name_dict);
        add_first_name(first_names); // 把司机们的姓填入筛选司机区域
    });
};


// 从数据库请求最后的位置
last_positions = function(){
    $.post(server + "/manage/last_positions",function(json){
        let response = JSON.parse(json);
        console.log(response);
        let data_list = response['data'];
        let l = data_list.length;
        if(l > 0){
            map.clearMap();  // 清除覆盖物
            global_markers = {};  // 全局自定义标记点容器.用于后继对全局自定义标记点的操作.
            // 添加自定义标记
            for(let i=0;i<l;i++){
                let data = data_list[i];
                console.log(data);
                update_last_date(data['user_id'], data['last_update']);  // 更新最后的通讯时间
                /*
                let add_right_side_bar_item_func = func_dict['add_right_side_bar_item'];
                add_right_side_bar_item_func(data);  // 添加右侧边栏
                */
                let get_awe_marker_func = func_dict['get_awe_marker'];
                let custom_marker = get_awe_marker_func(data);       // 自定义标记点重置
                let user_id = data['user_id'];
                global_markers[user_id] = custom_marker;
            }
        }else{}
    });
};

// 更新最后的通讯时间
let update_last_date = function(user_id, update_date){
    let a_str = '最后通信时间:2018-01-09 07:37:08\n' +
        'app版本:1.2.0.1229';
    a_str = `最后通信时间:${update_date}\n` + a_str.split("\n")[1];
    let finder = `.my_li[data-id='${user_id}']`;
    console.log("update_last_date function's finder is " + finder);
    $(finder).find("img").first().attr("title", a_str);
    let a = $(`.my_li[data-id='${user_id}'] a`);
    console.log(a);
    let raw_href = a.attr("href");
    let href = `${raw_href}&date=["${update_date.split(" ")[0]}"]`;
    a.attr("href", href);
};

// 修改自定义标记点, 此函数目前未被调用  2018-5-16
update_custom_markers = function(debug){
    $.post(server + "/manage/last_positions",function(json) {
        let response = JSON.parse(json);
        let data_list = response['data'];
        let l = data_list.length;
        if (l > 0) {
            for(let i=0;i<l;i++){
                let data = data_list[i];
                let loc = typeof(data['loc']) === "undefined" ? [121.504239, 31.239981] : data['loc'];
                let date = typeof(data['time']) === "undefined" ? "未知": data['time'].split(".")[0];
                let user_id = data['user_id'];
                update_last_date(user_id, date);  // 更新最后更新时间
                let marker = global_markers[user_id];
                if(debug){
                    loc = [
                        String(loc[0]).slice(0, 5) + String(Math.random()).split(".")[1],
                        String(loc[1]).slice(0, 5) + String(Math.random()).split(".")[1]
                        ];
                    console.log(`虚拟坐标: ${loc}`);
                }
                else{
                    // nothing...
                }

                marker.moveTo(loc, 5000);  //移动,第二个从参数是速度,单位公里/小时
            }
        }else{}
    });
};

let move_marker = function(loc_data){
    // 移动单个自定义标记点的位置.
    let user_id = loc_data['user_id'];
    let last_update = loc_data['ts'].split(".")[0];
    update_last_date(user_id, last_update);  // 更新最后更新时间
    let longitude = loc_data['longitude'];  // 经度
    let latitude = loc_data['latitude'];  // 纬度

    let info = `接收到实时坐标信息,user_id:${user_id},纬度:${latitude},经度:${longitude},${last_update}`;
    console.log(info);
    let marker = global_markers[user_id];
    if(marker !== undefined){
        marker.moveTo([longitude, latitude], 5000);  //移动,第二个从参数是速度,单位公里/小时
    }
};

// 收到最后的坐标信息的事件.
let client = get_io_client();
client.on("last_position", function(resp){
    let data = resp;
    move_marker(data);
});

// 右侧边滑动栏收放事件.
$("#right_side_bar_handler").click(function(e){
    var class_str = $("#right_side_bar").attr("class");
    if(class_str === undefined || class_str === ""){
        // 第一次
        $("#right_side_bar").addClass("bar_to_right");
        $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-left fa-flip-horizontal");
        $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-right fa-flip-horizontal");
    }
    else if(class_str === 'bar_to_right'){
        // 已经滑动到左边了。
        $("#right_side_bar").removeClass("bar_to_right");
        $("#right_side_bar").addClass("bar_to_left");
        $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-right fa-flip-horizontal");
        $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-left fa-flip-horizontal");
    }
    else if(class_str === 'bar_to_left'){
        // 已经滑动到右边了。
        $("#right_side_bar").removeClass("bar_to_left");
        $("#right_side_bar").addClass("bar_to_right");
        $("#right_side_bar_handler i").removeClass("fa fa-1 fa-angle-double-left fa-flip-horizontal");
        $("#right_side_bar_handler i").addClass("fa fa-1 fa-angle-double-right fa-flip-horizontal");
    }
    else{
        console.log(class_str);
    }
    e.stopPropagation();
});
