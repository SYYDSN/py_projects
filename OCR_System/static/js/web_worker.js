/**
 * Created by walle on 17-5-31.
 */
$(function(){
    var ws_url = "ws://" + location.hostname + ":" + 8010 + "/ws_handler";
    console.log(ws_url);
    ws = new WebSocket(ws_url);

    // 建立连接事件
    ws.onopen = function(event){
        console.log("web-socket 连接已建立!");
    };

    // 接收到消息的事件
    ws.onmessage = function(data){
        var data = JSON.parse(data['data']);
        var channel = data['channel'];
        if(channel == "message"){
            console.log(data['message']);
        }
    };

});