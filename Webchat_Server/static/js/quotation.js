$(function(){
    // 初始化socketio客户端
    var url = "http://api.91master.cn";
    console.log(url);
    var io_client = io.connect(url);
    io_client.on('connect', function() {
        io_client.emit('login', {data: 'I\'m connected!'});
    });

    // 接收报价的事件.
    io_client.on("price", function(resp){
        var prices = JSON.parse(resp);
        console.log(prices);
        show_price(prices);
    });

    function show_price (price_list){
        $(".now").text(price_list[0]['platform_time']);
        // 显示报价
        for(var price of price_list){
            var code = price['code'];
            var name = price['product'];
            var buy = price['price'];  // 买价
            var sell = price['price']; // 卖价
            var id_str =  code.toLowerCase();
            var obj = $("#" + id_str);
            if(obj.length == 0){
                // 没有这个对象,生成一个
                var html = `<div id='${id_str}' class='line'>
                                <span class='code cell'></span>
                                <span class='name cell'></span>
                                <span class='buy cell'></span>
                                <span class='sell cell'></span>
                            </div>`;
                obj = $(html);
                $(".price_list").append(obj);
            }
            obj.find(".code").text(code);
            obj.find(".name").text(name);
            obj.find(".buy").text(buy);
            obj.find(".sell").text(sell);
        }
    }

// end !!!
});