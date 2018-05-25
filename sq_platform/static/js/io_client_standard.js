$(function () {
    /*socketio客户端*/
    io_client = io.connect(`${location.protocol}//${document.domain}:5006`);
    io_client.on("connect", function () {
        // 连接时发送一个hello.
        // io_client.emit("last_position", {"data": "I an coming!"});
    });

    // io_client.on("last_position", function (resp) {
    //     console.log(resp);
    // });

// end!
});