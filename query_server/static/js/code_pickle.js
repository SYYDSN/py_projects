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
    $("#cancel_output").click(function(){
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
    $("#delete_output").click(function(){
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
            var product_name = $.trim($("#select_product_name .current_value").text());
            var args = {
                "type": "selector",
                "product_name": product_name
            };
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
            var product_name = $.trim($("#select_product_name .current_value").text());
            var specification = $.trim($("#select_specification .current_value").text());
            var args = {
                "type": "selector",
                "product_name": product_name,
                "specification": specification
            };
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
            var product_name = $.trim($("#select_product_name .current_value").text());
            var specification = $.trim($("#select_specification .current_value").text());
            var args = {
                "net_contents": text, "type": "selector",
                "product_name": product_name,
                "specification": specification
            };
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
            var args = {"product_name": text, "type": "selector"};
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
            var product_name = $.trim($("#select_product_name .current_value").text());
            var args = {
                "specification": text,
                "product_name": product_name,
                "type": "selector"
            };
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
            var product_name = $.trim($("#select_product_name .current_value").text());
            var specification = $.trim($("#select_specification .current_value").text());
            var args = {
                "net_contents": text, "type": "selector",
                "product_name": product_name,
                "specification": specification
            };
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
            alert("请先查询已生产的条码数量!");
        }
    });

    /**以下是工具类函数,用于搜索,替换和重置**/

    // 清除搜索结果框内容
    var clear_result = function(){
        $(".modal_outer_search_result .show_result span").text("");
        $(".modal_outer_search_result .show_result .item").attr("data-id", "");
    };

    // 弹出搜寻结果模态框
    var pop_search_status = function(){
        clear_result(); // 清除上次搜索结果
        $(".modal_outer_search_result").css("display", "flex");
        $(".modal_outer_search_result .wait_result").css("display", "flex");
        $(".modal_outer_search_result .result_zone").css("display", "none");
    };

    // 显示搜索条码结果
    var show_search_result = function(data, side){
        side = (side === undefined || side === "left")? "left": "right";
        var raw = $(".modal_outer_search_result .raw_code");
        if(side === "left"){
            $(".modal_outer_search_result .wait_result").css("display", "none");
            $(".modal_outer_search_result .result_zone").css("display", "flex");
        }
        else{
            raw = $(".modal_outer_search_result .new_code");
        }
        raw.attr("data-id", data['_id']); // id
        raw.find(".code").text(data['_id']);  // 条码
        raw.find(".product_info").text(data['product_info']);  // 产品信息
        raw.find(".batch_sn").text(data['batch_sn']);  // 生产批号
        raw.find(".print_time").text(data['print_time']);  // 打印日期
        raw.find(".sync_time").text(data['sync_time']);  // 回传日期
        raw.find(".output_time").text(data['output_time']);  // 导出日期
        raw.find(".status").text(parseInt(data['status']) ===1?"已使用": (parseInt(data['status'])===0?"未使用": "废止"));  // 状态
        raw.find(".level").text(data['level']);  // 码级
    };

    // 顶部条码信息搜索事件
    var search_code = function(code){
        var args = {
            "type": "query",
            "_id": code
        };
        var url = "/manage/code_info";
        pop_search_status();
        $.post(url, args, function(resp){
            var json = JSON.parse(resp);
            var status = json['message'];
            if(status === "success"){
                show_search_result(json['data']);
            }
            else{
                alert(status);
                $(".modal_outer_search_result").css("display", "none");
            }
        });
    };

    // 搜索条码框后面的go按钮的点击事件
    $(".right_top .search_code_btn").click(function(){
        var code = $.trim($(".right_top .search_code_input").val());
        if(code === ""){
            // nothing...
        }
        else{
            search_code(code);
        }
    });

    // 搜索条码框回车事件
    $(".right_top .search_code_input").keydown(function(event){
        var key = event.keyCode;
        if(key === 13){
            $(".right_top .search_code_btn").click();
        }else{}
    });

    // 关闭搜索结果模态框
    $("#close_search_result").click(function(){
        $(".modal_outer_search_result").css("display", "none");
    });

    // 重置条码按钮事件
    $("#reset_btn").click(function(){
        var _id = $.trim($(".modal_outer_search_result .raw_code").attr("data-id"));
        if(_id === ""){
            // nothing....
        }
        else{
            var con = confirm("这将重置条码信息为未使用状态,你确定吗?");
            if(con){
                var url = "/manage/code_info";
                var args = {
                    "type": "reset",
                    "_id": _id
                };
                $(".modal_process").css("display","flex");
                $.post(url, args, function(resp){
                    $(".modal_process").css("display","none");
                    var json = JSON.parse(resp);
                    var status = json['message'];
                    if(status === "success"){
                        alert("成功");
                        clear_result();  // 清除上次搜索结果
                        show_search_result(json['data'], "left");
                    }
                    else{
                        alert(status);
                    }
                });
            }else{}
        }
    });

    // 替换条码按钮的点击事件.
    $("#replace_btn").click(function(){
        var new_id = prompt("请输入新的条码");
        if(new_id.length < 12){
            alert("请输入正确的条码信息");
            return false;
        }
        else{
            replace_code(new_id);
        }
    });

    // 替换条码函数
    var replace_code = function(new_id){
        var old_id = $.trim($(".modal_outer_search_result .raw_code").attr("data-id"));
        if(old_id === "" || new_id === ""){
            alert("条码信息不能为空");
        }
        else if(old_id === new_id){
            alert("无需替换");
        }
        else{
            var con = confirm("这将交换2个条码的状态信息,你确定吗?");
            if(con){
                var url = "/manage/code_info";
                var args = {
                    "type": "replace",
                    "old_id": old_id,
                    "new_id": new_id
                };
                $(".modal_process").css("display","flex");
                $.post(url, args, function(resp){
                    $(".modal_process").css("display","none");
                    var json = JSON.parse(resp);
                    var status = json['message'];
                    if(status === "success"){
                        alert("成功");
                        var data = json['data'];
                        clear_result();  // 清除上次搜索结果
                        show_search_result(data[0], "left");
                        show_search_result(data[1], "right");
                    }
                    else{
                        alert(status);
                    }
                });
            }else{}
        }
    };
    
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