/**
 * Created by walle on 2017/9/18.
 * 这是一个 web-socket的客户端基础脚本，定义了：
 * 1.web-socket的初始化方法 。
 * 2.一些基础的方法和函数。
 *在本例中，需要在高德地图初始化之后加载。
 * 此脚本可以被其他脚本调用和扩展。
 * 此脚本依赖于reconnecting-websocket.min.js 脚本和jquery框架(非必须)
 */

const host_name = location.hostname;
const port = 8001;
const url = `ws://${host_name}:${port}/ws`;
global_members = {};
global_ws_finish = false;
showed_marker_dict = {};

/*
* ws_client提供四个主要方法。
* onopen   : 打开连接
* onclose  : 关闭连接
* onmessage: 收到消息时
* send     : 发送消息
* 另外还有常见的处理事件监听器的方法。
* addEventListener   :  加一个事件监听器
* removeEventListener:  删除一个事件监听器
* */

let get_awe_marker_func = func_dict['get_awe_marker'];
let func_type = typeof(get_awe_marker_func);
console.log("func_type: " + func_type);

let ws_client = new ReconnectingWebSocket(url);

// 更新最后的通讯时间
let update_last_date = function(user_id, update_date){
    let a_str = '最后通信时间:2018-01-09 07:37:08\n' +
        'app版本:1.2.0.1229';
    a_str = `最后通信时间:${update_date}\n` + a_str.split("\n")[1];
    let finder = `.my_li[data-id='${user_id}']`;
    console.log("update_last_date function's finder is " + finder);
    $(finder).find("img").first().attr("title", a_str);
};

/*实时显示自定义标记点*/
let show_gps = function (args) {

        get_awe_marker_func = func_dict['get_awe_marker'];

    let user_id = args['_id'];
    console.log("show gps function's args:");
    console.log(args);
    if (user_id in showed_marker_dict) {
        console.log("show gps! 1");
        let marker = showed_marker_dict[user_id];
        marker.moveTo(args['loc'], 100); // 参数1是坐标,参数2是运动的速度.
    }
    else {
        console.log("show gps! 2");
        let marker = get_awe_marker_func(args);
        showed_marker_dict[user_id] = marker;
        map.setFitView();  // 调整地图缩放
    }
    // 修改右侧导航栏的data-position属性,为to_map_center函数服务
    $(`.my_li[data-id='${user_id}']>.item_main`).attr("data-position", args['loc'].join(","));
    // 更新最后的通讯时间
    update_last_date(user_id, args['gps_time']);
};

// 发送消息的函数
function send_message(message) {
    /*
    * 参数必须是字典格式，而且必须遵照以下格式：
    * {
    * mes_type: string,    消息类型 字符串格式，用于区别不同的操作。
    * data_dict: dict     消息内容，字典格式，自行约定，不一定有
    * }
    * */
    ws_client.send(JSON.stringify(message));
    console.log(message, "消息已发送");
}

// 客户端连接建立函数
ws_client.onopen = function () {
    console.log("客户端已连接！");
    let mes = {"mes_type": "prev_gps"};
    send_message(mes);
};

// 客户端连接断开函数
ws_client.onclose = function () {
    console.log("客户端已断开");
};

// 客户端收到消息
ws_client.onmessage = function (json) {
    /*
    * 服务器发来的消息一定是字典格式，并且遵照一定的格式。
    * {
    * mes_type: string    消息类型 字符串格式，用于区别不同的操作。
    * message: "success",  消息状态，判断成败
    * data_dict: dict     消息内容，字典格式，自行约定
    * }
    * 比如，连接上服务器的欢迎信息
    * {"mes_type":"welcome", "data_dict":{},"message":"你好，用户"}
    * */
    let resp = JSON.parse(json['data']);  // data属性本身是字符串，要转成字典对象
    let mes_type = resp['mes_type'];
    console.log(resp);
    console.log();
    if (mes_type === "prev_gps") {
        // 第一次请求
        for(let item of resp['data']){
           check_map_init(show_gps, item);
        }

    }
    else if(mes_type === "real_time"){
        // 实时数据
        check_map_init(show_gps, resp['data']);
    }else{
        // pass
    }

};




