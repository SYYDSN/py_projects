$(function(){
    var post_url = "/teacher/process_case.html";  // post地址

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
        {"code": "HK50", "name": "恒指"},
        {"code": "XTIUSD", "name": "原油"},
        {"code": "XAUUSD", "name": "黄金"},
        {"code": "XAGUSD", "name": "白银"},
        {"code": "GBPUSD", "name": "英镑"},
        {"code": "EURUSD", "name": "欧元"},
        {"code": "USDCAD", "name": "加元"},
        {"code": "AUDUSD", "name": "澳元"},
        {"code": "USDJPY", "name": "日元"}

    ];  // 产品名称的列表

    // 产品选择select的change事件
    var select_p = function(){
        var code = $("#select_product").val();
        for(var p of p_names){
            var temp_code = p['code'];
            if(temp_code == code){
                $("#cur_product_name").text(p['name']);
                $("#cur_product_code").text(temp_code);
                break;
            }
        }
    };
    // 绑定选择事件
    $("#select_product").change(function(){select_p();});
    // 初始化页面时候初始化产品选择
    select_p();

    // 自动根据url参数选择产品
    (function(){
        var product = get_url_arg("p");
        var div = get_url_arg("div");
        console.log(`current product is ${product}`);
        if(product == undefined || product == ""){
            // nothing...
        }
        else{
            $("#select_product").val(product.toUpperCase());
            select_p();
        }
        $(`a[data-div='${div}']`).click();
    })();

    // 初始化socketio客户端
    var url = "http://api.91master.cn";
    console.log(url);
    var io_client = io.connect(url);
    io_client.on('connect', function() {
        io_client.emit('login', {data: 'I\'m connected!'});
        console.log("socketio连接成功");
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
                $("#price_div").attr("data-id", set_code)
            }
            else{}
            $(`.now_p[data-p_name='${temp_code}'][data-p_direction='买入']`).text(sell_price);
            $(`.now_p[data-p_name='${temp_code}'][data-p_direction='卖出']`).text(buy_price);
            /*
            var obj = $(`.now_price[data-id='${temp_code.toLowerCase()}']`);
            var obj_d = obj['data-d'];
            if(obj_d == "买入"){
                obj.text(sell_price);
            }
            else{
                obj.text(buy_price);
            }
            */
        }
    }

    // 进场函数
    var enter = function(direction){
        /*
        * args action: 方向, 买入/卖出
        * */
        var product = $.trim($("#cur_product_name").text());
        var code =  $.trim($("#cur_product_code").text()).toLowerCase();
        var enter_price = direction == "买入"? parseFloat($.trim($("#buy_price").text())):
            parseFloat($.trim($("#sell_price").text()));
        var enter_time = $.trim($(".now").text());
        if(product == "" || isNaN(enter_price)){
            $.alert("请先选择产品");
            return false;
        }
        else if(code != $.trim($("#price_div").attr("data-id"))){
            alert("价格尚未同步,请稍后.");
            return false;
        }
        else if($(".case_block .case_line").length > 5){
            alert("持仓过多,无法继续开单");
            return false;
        }
        else {
            var c = confirm(`${enter_price}价位, ${direction}${product}, 你确定吗?`);
            if(c){
                var args = {
                    "the_type": 'operate_trade',
                    "product": product, "direction": direction, "code": code,
                    "enter_price": enter_price, "enter_time": enter_time
                };
                $.pop_alert();
                $.post(post_url, args, function (resp) {
                    $.close_alert();
                    var resp = JSON.parse(resp);
                    var status = resp['message'];
                    if (status == "success") {
                        alert("建仓成功！");
                        location.href = "/teacher/process_case.html?p=" + code;
                    }
                    else{
                        alert(status);
                    }
                });

            }
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
        if(obj) {
            var price = direction == '买入' ? obj['sell'] : obj['buy'];
            var c = confirm(`对此${product}${type}进行平仓操作, 你确定吗?`);
            if (c) {

                var args = {
                    "the_type": 'operate_trade',
                    "_id": _id,
                    "direction": direction,
                    "exit_time": obj['time'],
                    "exit_price": price,
                    "product": product
                };
                $.pop_alert();
                $.post(post_url, args, function (resp) {
                    $.close_alert();
                    var resp = JSON.parse(resp);
                    var status = resp['message'];
                    if (status == "success") {
                        alert("平仓成功！");
                        location.href = "/teacher/process_case.html";
                    }
                    else{
                        alert(status);
                    }
                });
            }
            else {}
        }else{}
    };

    // 平仓按钮事件
    $(".close_case").each(function(){
        var $this = $(this);
        $this.click(function(){exit($this);});
    });

    // 获取搜索的关键字
    var get_keyword = function(){
        var kw = $.trim($("#search_kw").val()).toUpperCase();
        var product = null;
        if(kw == ""){
            return kw;
        }
        else{
            for(var p of p_names){
                var code = p['code'];
                var name = p['name'];
                if(kw == code || kw == name){
                    product = name;
                    break;
                }
                else{}
            }
            return product;
        }
    };

    // 搜索喊单历史按钮. 使用搜索按钮总是清空原有的喊单历史
    $("#search_history").click(function(){
        var product = get_keyword();
        if(product == null){
            // 输入了错误的关键字
        }
        else{
            if(product != ""){
                var args = {
                    "the_type": "trade_history",
                    "product": product
                };
                $.pop_alert();
                $.post(post_url, args, function(resp){
                    $.close_alert();
                    var resp = JSON.parse(resp);
                    var status = resp['message'];
                    if(status != "success"){
                        alert(status);
                    }
                    else{
                        $("#search_kw").attr("data-search", product); // post后更新字段
                        var trade_list = resp['data'];
                        fill_history(trade_list, product, true);  // 填充历史列表
                    }
                });
            }
            else{
                // 无关键字的搜索
                $("#search_kw").attr("data-search", product); // 更新字段
                $("#searched_history").hide();
                $("#default_history").show();
            }
        }
    });

    $("#search_kw").keyup(function(){
        // 监视关键字输入框
        if($.trim($(this).val()) == ""){
            $("#searched_history").hide();
            $("#default_history").show();
        }
    });

    // 填充喊单历史的函数.
    var fill_history = function(a_list, p_name, empty){
        /*
        * params a_list:      list      喊单历史的数组
        * params p_name:      字符串     搜索的产品名字
        * params empty:       Boolean   是否清除以前的数据?
        * */
        var is_default = p_name==""?true: false;  // 是不是默认的喊单历史?(没有指明产品的)
        var c =  is_default?$("#default_history") : $("#searched_history");
        if(empty){
            c.empty();
        }
        for(var i of a_list){
            var exit_time = i['exit_time'];
            var time = exit_time.split(" ");
            var md = time[0].split("-");
            var hh = time[1].split(":");
            var m = md[1];
            var d = md[2];
            var h = hh[0];
            var m2 = hh[1];
            var t = `<li id="${i._id}" data-time="${exit_time}">
                        <div class="textList">
                            <p class="textTitle">
                                ${i.product}
                                <span class="${i.direction=='买入'?'colore35e57': 'color17b640'}  pl01">
                                    ${i.direction=='买入'?'buy':'sell'}
                                </span>
                            </p>
                            ${m}月${d}日 ${h}时${m2}分
                        </div>   
                        <div class="priceText">
                        ${String(i.enter_price).slice(0,6)} - ${String(i.exit_price).slice(0,6)}
                        </div>
                        <div class="earnings">
                        ${i.each_profit.toFixed(2)}/手
                        </div>
                     </li>`;
            c.append(t);
        }
        if(p_name==""){
            $("#searched_history").hide();
            $("#default_history").show();
        }
        else{
            $("#default_history").hide();
            $("#searched_history").show()
        }
    };

    // 懒加载更多喊单历史的函数
    var more_history = function(){
        // 获取最早一条记录.就是历史列表中最下面一条(列表是倒序排列的)
        var p = $("#search_kw").attr("data-search");
        var first_exit_time = null;  // 最早的一个历史的离场时间
        if(p == ""){
            // 默认历史
            first_exit_time = $("#default_history > li:last").attr("data-time");
        }
        else{
            // 带参数过滤器的
        }
        // alert(`最后的历史id=${first_exit_time}`);
        var args = {
            "the_type": "trade_history",
            "product": p
        };
        if(first_exit_time != null){
            args['first_exit_time'] = first_exit_time;
        }
        $.pop_alert();
        $.post(post_url, args, function(resp){
            $.close_alert();
            var resp = JSON.parse(resp);
            console.log(resp);
            var status = resp['message'];
            if(status != "success"){
                alert(status);
            }
            else{
                $("#search_kw").attr("data-search", p); // post后更新字段
                var trade_list = resp['data'];
                $("#default_history").hide();
                fill_history(trade_list, p, false);
            }
        });
    };


    // 下滑到页面底部的事件.
    $("#history_outer").pull_down(more_history);



// end !
});