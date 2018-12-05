$(function(){
    // 是否四级联动选择框就绪? 就绪返回产品id,不就绪返回空字符串
    var select_success = function(){
        var product_id = "";
        var product_name = $.trim($("#select_product_name .current_value").text());
        var specification = $.trim($("#select_specification .current_value").text());
        var net_contents = $.trim($("#select_net_contents .current_value").text());
        var package_ratio  = $.trim($("#select_package_ratio .current_value").text());
        if(product_name === "" || specification === "" || net_contents === "" || package_ratio === ""){
            console.log("还未选择正确的产品信息!");
        }
        else {
            product_id = $.trim($("#select_package_ratio .current_value").attr("data-id"));
        }
        return product_id;
    };

    // 撤销导出的数据
    $("#cancel_export").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "cancel",
            "ids": JSON.stringify(d)
        };
        var p = confirm("这将撤销导出的数据并删除文件和日志!");
        if(p){
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("撤销成功");
                    location.reload();
                }else{
                    alert(status);
                }
            });
        }
        else{
            // ...
        }
    });

    /*删除已导出的文件和日志*/
    $("#delete_export").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete",
            "include_record": true,
            "ids": JSON.stringify(d)
        };
        var p = confirm("这将会把已导出的文件和日志一起删除!");
        if(p){
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("删除成功");
                    location.reload();
                }else{
                    alert(status);
                }
            });
        }
        else{
            // ...
        }
    });

    // 点击未填充的产品规格选择器的事件
    $("#select_specification .current_value").click(function(){
        // 相当与再次点击了上一个选择器
        var l = $(this).parents(".my_input:first").find("ul>.select_value").length;
        if(l > 0){
            // 已填充过了
        }
        else{
            var current_div = $(this).parents(".select_div:first");
            var text = $.trim(current_div.prev().find(".current_value").text());
            var a_id = $(this).attr("data-id");
            var args = {"product_name": text, "_id": a_id, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    var ul = current_div.find("ul");
                    ul.empty();
                    ul.append(lis);
                }
            });
        }
    });

    // 点击未填充的产品规格选择器的事件
    $("#select_net_contents .current_value").click(function(){
        // 相当与再次点击了上一个选择器
        var l = $(this).parents(".my_input:first").find("ul>.select_value").length;
        if(l > 0){
            // 已填充过了
        }
        else{
            var current_div = $(this).parents(".select_div:first");
            var text = $.trim(current_div.prev().find(".current_value").text());
            var a_id = $(this).attr("data-id");
            var args = {"specification": text, "_id": a_id, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    var ul = current_div.find("ul");
                    ul.empty();
                    ul.append(lis);
                }
            });
        }
    });

    // 点击未填充的产品规格选择器的事件
    $("#select_package_ratio .current_value").click(function(){
        // 相当与再次点击了上一个选择器
        var l = $(this).parents(".my_input:first").find("ul>.select_value").length;
        if(l > 0){
            // 已填充过了
        }
        else{
            var current_div = $(this).parents(".select_div:first");
            var text = $.trim(current_div.prev().find(".current_value").text());
            var a_id = $(this).attr("data-id");
            var args = {"net_contents": text, "_id": a_id, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    var ul = current_div.find("ul");
                    ul.empty();
                    ul.append(lis);
                }
            });
        }
    });

    // 选择器点击事件
    select_value = function($obj){
        var text = $.trim($obj.text());
        var $current_value = $obj.parents(".my_input:first").find(".current_value");
        $current_value.text(text);
        var a_id = $obj.attr("data-id");
        if(a_id !== undefined && a_id !== ""){
            $current_value.attr("data-id", $.trim(a_id));
        }else{
            // nothing...
        }
        $obj.parents(".select_div:first").next().find(".current_value").text("");
        var $ul = $obj.parents("ul:first");
        if($.trim($ul.attr("data-type")) === "product_name"){
            var $next_ul = $("ul[data-type='specification']");
            var args = {"product_name": text, "_id": a_id, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    $next_ul.empty();
                    $next_ul.append(lis);
                }
            });
        }
        else if($.trim($ul.attr("data-type")) === "specification"){
            var $next_ul = $("[data-type='net_contents']");
            var args = {"specification": text, "_id": a_id, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    $next_ul.empty();
                    $next_ul.append(lis);
                }
            });
        }
        else if($.trim($ul.attr("data-type")) === "net_contents"){
            var $next_ul = $("[data-type='package_ratio']");
            var args = {"net_contents": text, "_id": a_id, "type": "selector"};
            $.post("/manage/product", args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status !== "success"){
                    alert(status);
                    return false;
                }
                else{
                    var data = json['data'];
                    var lis = "";
                    for(var k in data){
                        var v = data[k];
                        lis += `<li onclick="select_value($(this))" data-id="${v}" class='select_value'>${k}</li>`;
                    }
                    lis = $(lis);
                    $next_ul.empty();
                    $next_ul.append(lis);
                }
            });
        }
        else{
            // nothing...
        }
        // 检测是否选择ok?
        var product_id = select_success();
        if(product_id === ""){
            $(".my_input .deposit").text(0);
        }
        else{
            // 查询剩余条码
            var args = {
                "type": "count",
                "product_id": product_id,
            };
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    // 查询可打印的条码余量
                    var count = json['count'];
                    $(".my_input .deposit").text(count);
                }
                else{
                    alert(status);
                }
            });
        }
    };

    // 导出打印条码
    $("#pickle_file").click(function(){
        var product_id = select_success();
        var count = parseInt($.trim($(".my_input .deposit").text()));
        if(product_id.length === 24 && count > 0){
            var cn = prompt(`请输入需要导出的条码数目(不能大于${count})`);
            var number = parseInt(cn);
            if(isNaN(number) || number > count){
                alert("导出数量必须是数字");
            }else{
                $(".modal_outer_progress").css("display", "flex");
                var args = {
                    "type": 'export',
                    "product_id": product_id,
                    "number": number
                };
                $.post(location.pathname, args, function(resp){
                    $(".modal_outer_progress").css("display", "none");
                    var json = JSON.parse(resp);
                    var status = json['message'];
                    if(status === "success"){
                        alert("生成成功!");
                        location.reload();
                    }
                    else{
                        alert(status);
                    }
                });
            }
        }
        else{
            // nothing...
            alert("请先查询条码库存");
        }
    });

    
    /*全选事件*/
    $("#check_all").click(function(){
        var checked = $("#check_all:checked").length === 1? true: false;
        if(checked){
            $(".table_outer .select >input[type='checkbox']").prop("checked", true);
        }
        else{
            $(".table_outer .select >input[type='checkbox']").prop("checked", false);
        }
    });

    // 翻页事件
    PageHandler();

});