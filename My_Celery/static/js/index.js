var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('mes', {data: 'I\'m 中 connected!'});
});

socket.on("mes", function(resp){
    console.log(resp);
    var mes = resp['mes'];
    if(mes !== undefined){
        var $d = $(`<div class="line">${mes}</div>`);
        $(".show").append($d);
    }else{}

});