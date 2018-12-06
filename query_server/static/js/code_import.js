$(function(){
    /*上传成功事件*/
    var upload_success = function(resp){
        $(".file_path").text("");
        $(".modal_outer_progress").css("display", "none");
        $("#my_progress div").css("width", "0%");
        $("#my_progress .my_per").text("0%");
        $(".upload_line").css("display", "flex");
        $(".process_line").css("display", "none");

        console.log(resp);
        var json = JSON.parse(resp);
        var status = json['message'];
        if(status === "success"){
            alert("导入成功!");
        }
        else{
            alert(status);
        }
        location.reload();
    };

    /*上传失败事件*/
    var upload_error= function(resp){
        $(".file_path").text("");
        $(".modal_outer_progress").css("display", "none");
        $("#my_progress div").css("width", "0%");
        $("#my_progress .my_per").text("0%");
        $(".upload_line").css("display", "flex");
        $(".process_line").css("display", "none");

        console.log(resp);
        alert("上传失败");
    };

    /*上传进度处理函数*/
    var progress_cb = function(resp){
        console.log(resp);
        var val = `${resp}%`;
        $("#my_progress div").css("width", val);
        $("#my_progress .my_per").text(val);
        if(resp === 100){
            $(".upload_line").css("display", "none");
            $(".process_line").css("display", "flex");
        }else{}
    };

    // 弹出选择上传文件框
    $("#open_file").click(function(){
        $("#upload_file").click();
    });

    // 选择文件后,自动上传
    $("#upload_file").change(function(){
        $(".file_path").text($("#upload_file").val());
        upload();
    });

    /*上传函数*/
    var upload = function(){
        var $obj = $("#upload_file");
        let file_name = $obj.attr("name");
        if(file_name){
            // nothing...
        }
        else{
            file_name = "file"
        }
        let file_data = $obj[0].files[0];
        var product_id = $.trim($("#select_package_ratio .current_value").attr("data-id"));
        var product_name = $.trim($("#select_product_name .current_value"));
        var specification = $.trim($("#select_specification .current_value"));
        var net_contents = $.trim($("#select_net_contents .current_value"));
        var package_ratio  = $.trim($("#select_package_ratio .current_value"));
        if(product_id === "" || product_name === "" || specification === "" || net_contents === "" || package_ratio === ""){
            alert("请选择正确的产品信息!");
            location.reload();
        }
        else{
            var opts = {
                headers: {"upload-file": "1", "product_id": product_id},
                file_name: file_name,
                file_data: file_data,
                max_size: 900000,
                url: location.pathname,
                success_cb: upload_success,
                progress_cb: progress_cb,
                error_cb: upload_error
            };
            $(".modal_outer_progress").css("display", "flex");
            $.upload(opts);
        }
    };

    // 撤销导入的数据
    $("#cancel_import").click(function(){
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
        var p = confirm("这将撤销导入的数据并删除文件和日志!");
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

    /*删除导入文件和记录*/
    $("#delete_import2").click(function(){
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
        var p = confirm("这将会把导入文件和日志一起删除!");
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