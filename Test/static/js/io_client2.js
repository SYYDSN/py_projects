var ws_url = 'wss://' + document.domain + ':' + location.port + "/echo";
var socket = new ReconnectingWebSocket(ws_url);

var on_open = function() {
    socket.send(JSON.stringify({data: 'I\'m 中 connected!'}));
};

var on_message = function(json){
    console.log(json);
    var str = json['data'];
    if(str !== undefined && str !== ""){
        var div = $(`<div>${str}</div>`);
        $(".show").append(div);
    }

};

var init = function(){
    socket.onopen = on_open;
    socket.onmessage = on_message;
};

init();


nick_name = prompt("请输入你的昵称");
while($.trim(nick_name) === ""){
    nick_name = prompt("请输入你的昵称");
}

$("#submit").click(function(){
    var str = $.trim($("input").val());
    if(str !== ""){
        var data = {"message": `${nick_name} 说: ${str}`};

        socket.send(JSON.stringify({"mes": data}));
        $("input").val("");
    }
});

$("input").keyup(function(event){
    var key = event.keyCode;
    var str = $.trim($("input").val());
    if(key === 13 && str !== ""){
        $("#submit").click();
    }
});