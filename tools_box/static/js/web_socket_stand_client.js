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
const port = parseInt(location.port) + 1;
const url = `ws://${host_name}:${port}/ws`;
let ws_client = new ReconnectingWebSocket(url);
global_members = {};
global_ws_finish = false;

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
// 客户端连接建立函数
ws_client.onopen = function () {
    console.log("客户端已连接！");
    let href = location.href.split("?")[1];
    let is_debug = false;
    if(href === undefined || href.indexOf("debug") === -1){
        //nothing..
    }
    else{
        let val = href.split("debug=")[1].split("&")[0];
        is_debug = val === "debug" ? true: false;
        console.log(`is_debug is ${is_debug}`);
    }
    let arg_dict = {
        "mes_type": "all_last_position",
        "data_dict": {
            "is_debug": is_debug
        }
    };
    /*
    * 获取所有自己能看到的最后一次更新数据的位置点信息，一般是在客户端刚刚连接上的
    * 时候发送这个请求。
    * */
    send_message(arg_dict);
};

// 客户端连接断开函数
ws_client.onclose = function () {
    console.log("客户端已断开");
};

// 客户端收到消息
ws_client.onmessage = function(json) {
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
    let data = JSON.parse(json['data']);  // data属性本身是字符串，要转成字典对象
    window.localStorage.setItem("datas",JSON.stringify(data))
    let mes_type = data['mes_type'];
    let message = data['message'];
    let data_dict = data['data_dict'];
    const type_list = ["all_last_position"];
    if(message !== "success"){
        console.log(message);
    }
    else if(type_list.indexOf(mes_type) === -1){
        console.log("错误的类型:" + mes_type);
    }
    else{
        process_message(mes_type, data_dict);
    }
};

// 发送消息的函数
function send_message(message){
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

// 处理事web-socket接受到的消息的函数，此函数经常被扩展的很庞大。
let process_message = function(mes_type, arg_dict){
    /*
    *
    * */
    let type = mes_type;
    let data_dict = arg_dict;
    if(type === "all_last_position"){
        // 获取所有自己能看到的最后一次更新数据的位置点信息，也就是第一次连接上的时候
        // 先获取高德地图初始化自定义标记点的函数。
        let func = undefined;
        global_members = data_dict;
        global_ws_finish = true;
            let interval = setInterval(function(){
                func = func_dict['get_awe_marker'];
                if(typeof(func) === "function"){
                    // 插件库已初始化完成。
                    clearInterval(interval);
                    for (let data of data_dict) {
                        /*
                        * for(let x of list)和for(let [key,val] of dict)是es6的新语法。
                        * */
                        let phone_num = data['phone_num'];
                        let head_img_url = data['head_img_url'];
                        let real_name = data['real_name'] === undefined ? phone_num: data['real_name'];
                        let car_model = data['car_model'];
                        let drive_time = data['drive_time'];
                        let mileage = data['mileage'];
                        let event_count = data['event_count'];
                        let time = data['time'].split(".")[0];
                        let app_version = data['app_version'];
                        let user_id = data['user_id'];
                        let loc = data['loc'];
                        let time_delta = data['time_delta'];
                        /*组合参数*/
                        let args = {"user_id": user_id,
                        "position": loc, "phone_num": phone_num,
                        "security_score": 80, "time": time,
                         "app_version": app_version,
                        "real_name": real_name,
                        "head_img_url": head_img_url,
                        "car_model": car_model,
                        "drive_time": drive_time,
                        "mileage": mileage,
                        "time_delta":time_delta,
                        "event_count": event_count};

                        func(args); // 添加自定义标记点
                        let add_right_side_bar_item = func_dict['add_right_side_bar_item'];

                        add_right_side_bar_item(args);  // 添加右侧边栏元素
                    }
                    $("#driver_count").text(data_dict.length); // 统计并显示在右侧边栏顶部
                    window.localStorage.setItem("len",data_dict.length);
                }else{
                    // nothing...
                }
            }, 200);
    }
    else if(0 !== 0)
    {
        /*各种消息类型的处理**/
    }
    else{
        console.log("错误的消息类型:"+ mes_type);
    }
};