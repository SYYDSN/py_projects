$(function(){
    // 分页选择按钮事件
    var sub_page = function($obj){
        $(".crunchy-tabList > li").removeClass("on");
        $obj.parents("li:first").addClass("on");
        var id_str = "#" + $obj.attr("data-div");
        $(".show_zone").not(id_str).hide(0);
        $(id_str).show(0);
    };

    // 分页选择按钮绑定事件.
    $(".crunchy-tabList > li > a").each(function(){
        var $this = $(this);
        $this.click(function(){
            sub_page($this);
        });
    });



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

    // 自动根据url参数选择产品
    (function(){
        var product = get_url_arg("p");
        console.log(product);
        if(product == undefined || product == ""){
            // nothing...
        }
        else{
            $("#select_product").val(product.toUpperCase());
        }
    })();

    // 初始化产品选择输入框
    // var init_select = function(){
    //     alert(1)
    //     $("#select_product").select({
    //         "title": "",
    //         "items": p_names,
    //         onChange: function(){
    //             var temp = $.trim($("#select_product").val()).split(" ");
    //             $(".price_zone > .product_name").attr("data-id", temp[0]).text(temp[1]);
    //         }
    //     });
    // };
    // init_select();

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

    var price_dict = {};   // 价格容器
    function show_price (price_list){
        $(".now").text(price_list[0]['platform_time']);  // 当前时间
        // 显示报价
        var set_code = $("#select_product").val().toLowerCase();
        for(var price of price_list){
            var temp_code = price['code'];
            var product = price['product'];
            var buy_price = price['buy'];  // 买价
            var sell_price = price['sell']; // 卖价
            var time = price['platform_time'];
            price_dict[product] = {"buy": buy_price, "sell": sell_price, "time": time};  // 价格容器更新
            temp_code =  temp_code.toLowerCase();
            if(set_code == temp_code)
            {
                $("#buy_price").text(buy_price);
                $("#sell_price").text(sell_price);
            }
            else{}
            var obj = $(`.now_price[data-id='${temp_code.toLowerCase()}']`);
            var obj_d = obj['data-d'];
            if(obj_d == "买入"){
                obj.text(sell_price);
            }
            else{
                obj.text(buy_price);
            }
        }
    }

    // 进场函数
    var enter = function(direction){
        /*
        * args action: 方向, 买入/卖出
        * */
        var product = $.trim($(".product_name").text());
        var code = $.trim($(".product_name").attr("data-id")).toLowerCase();
        var enter_price = direction == "买入"? parseFloat($.trim($(".buy_price").text())):
            parseFloat($.trim($(".sell_price").text()));
        var enter_time = $.trim($(".now").text());
        if(product == "" || isNaN(enter_price)){
            $.alert("请先选择产品", function(){return false;});
        }
        else if($(".case_block .case_line").length > 5){
            $.alert("持仓过多,无法继续开单", function(){return false;});
        }
        else{
            $.confirm(`${enter_price}价位, ${direction}${product}, 你确定吗?`, "建仓操作", function(){
                var args = {
                    "product": product, "direction": direction, "code": code,
                    "enter_price": enter_price, "enter_time": enter_time
                };
                $.post("/teacher/process_case.html", args, function(resp){
                    var resp = JSON.parse(resp);
                    var status = resp['message'];
                    if(status == "success"){
                        $.alert("建仓成功！", function(){
                            location.href = "/teacher/process_case.html?p=" + code;
                        });
                    }
                });
            });
        }
    };

    // 多单
    $("#buy_it").click(function () {
        enter("买入");
    });

    // 空单
    $("#sell_it").click(function () {
        enter("卖出");
    });

    // 离场函数
    var exit = function($obj){
        var _id = $.trim($obj.attr("data-id"));
        var direction = $.trim($obj.attr("data-d"));
        var type = direction=="买入"? "多单": "空单";
        var product = $.trim($obj.attr("data-n"));
        var obj = price_dict[product];
        if(obj){
            var price = direction=='买入'?obj['sell']: obj['buy'];
            $.confirm(`对此${product}${type}进行平仓操作, 你确定吗?`, "平仓操作", function(){
                var args = {
                    "_id": _id,
                    "direction": direction,
                    "exit_time": obj['time'],
                    "exit_price": price,
                    "product": product
                };
                $.post("/teacher/process_case.html", args, function(resp){
                    var resp = JSON.parse(resp);
                    var status = resp['message'];
                    if(status == "success"){
                        $.alert("平仓成功！", function(){
                            location.href = "/teacher/process_case.html";
                        });
                    }
                });
            });
        }else{}
    };

    // 平仓按钮事件
    $(".close_case").each(function(){
        var $this = $(this);
        $this.click(function(){exit($this);});
    });

// end !
});