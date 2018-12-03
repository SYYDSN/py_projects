$(function(){
    // 是否四级联动选择框就绪? 就绪返回产品id,不就绪返回空字符串
    var select_success = function(){
        var product_id = "";
        var product_name = $.trim($("#select_product_name .current_value"));
        var specification = $.trim($("#select_specification .current_value"));
        var net_contents = $.trim($("#select_net_contents .current_value"));
        var package_ratio  = $.trim($("#select_package_ratio .current_value"));
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
            $next_ul.empty();
            var data = l1[text];
            var lis = "";
            for(var x of data){
                lis += `<li onclick="select_value($(this))" class='select_value'>${x}</li>`;
            }
            lis = $(lis);
            $next_ul.append(lis);
        }
        else if($.trim($ul.attr("data-type")) === "specification"){
            var $next_ul = $("[data-type='net_contents']");
            $next_ul.empty();
            var data = l2[text];
            var lis = "";
            for(var x of data){
                lis += `<li onclick="select_value($(this))" class='select_value'>${x}</li>`;
            }
            lis = $(lis);
            $next_ul.append(lis);
        }
        else if($.trim($ul.attr("data-type")) === "net_contents"){
            var $next_ul = $("[data-type='package_ratio']");
            $next_ul.empty();
            var data = l3[text];
            var lis = "";
            for(var x of data){
                lis += `<li onclick="select_value($(this))" data-id="${x[1]}" class='select_value'>${x[0]}</li>`;
            }
            lis = $(lis);
            $next_ul.append(lis);
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