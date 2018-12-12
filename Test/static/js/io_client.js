var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('mes', {data: 'I\'m 中 connected!'});
});

socket.on('mes', function(json){
    console.log(json);
    var str = json['message'];
    if(str !== undefined && str !== ""){
        var div = $(`<div>${str}</div>`);
        $(".show").append(div);
    }

});

nick_name = prompt("请输入你的昵称");
while($.trim(nick_name) === ""){
    nick_name = prompt("请输入你的昵称");
}

$("#submit").click(function(){
    var str = $.trim($("input").val());
    if(str !== ""){
        var data = {"message": `${nick_name} 说: ${str}`};

        socket.emit("mes", data);
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