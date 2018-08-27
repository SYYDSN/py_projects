$(function(){
    var p_names = [
        {"title": "HK50 恒指", "value": "恒指"},
        {"title": "XTIUSD 原油", "value": "原油"},
        {"title": "XAUUSD 黄金", "value": "黄金"},
        {"title": "XAGUSD 白银", "value": "白银"},
        {"title": "GBPUSD 英镑", "value": "英镑"},
        {"title": "EURUSD 欧元", "value": "欧元"},
        {"title": "USDCAD 加元", "value": "加元"},
        {"title": "AUDUSD 澳元", "value": "澳元"},
        {"title": "USDJPY 日元", "value": "日元"}

    ];  // 产品名称的列表

    // 初始化产品选择输入框
    var init_select = function(){
        $("#select_product").select({
            "title": "",
            "items": p_names,
            onChange: function(){
                var temp = $.trim($("#select_product").val()).split(" ");
                $(".price_zone > .product_name").attr("data-id", temp[0]).text(temp[1]);
            }
        });
    };
    init_select();

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
        $(".now").text(price_list[0]['platform_time']);  // 当前时间
        // 显示报价
        var set_code = $(".price_zone > .product_name").attr("data-id").toLowerCase();
        if(set_code.length >= 4){
            for(var price of price_list){
                var temp_code = price['code'];
                var buy_price = price['buy'];  // 买价
                var sell_price = price['sell']; // 卖价
                var temp_code =  temp_code.toLowerCase();
                if(set_code == temp_code)
                {
                    $(".price_zone > .buy_price").text(buy_price);
                    $(".price_zone > .sell_price").text(sell_price);
                }
                else{}
            }
        }
    }

    // 进场函数函数
    var enter = function(direction){
        /*
        * args action: 方向, 买入/卖出
        * */
        var product = $.trim($(".product_name").text());
        var enter_price = direction == "买入"? parseFloat($.trim($(".buy_price").text())):
            parseFloat($.trim($(".sell_price").text()));
        var enter_time = $.trim($(".now").text());
        $.confirm(`${enter_price}价位, ${direction}${product}, 你确定吗?`, "建仓操作", function(){
            var args = {
                "product": product, "direction": direction,
                "enter_price": enter_price, "enter_time": enter_time
            };
            $.post("/teacher/process_case.html", args, function(resp){
                var resp = JSON.parse(resp);
                var status = resp['message'];
                if(status == "success"){
                    $.alert("建仓成功！");
                    location.href = "/teacher/process_case.html?product=" + product;
                }
            });
        });
    };

// end !
});