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
        let opts = {
            headers: {"upload-file": "1"},
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
    };

    /*导入数据*/
    $(".import_btn").each(function(){
        var $this = $(this);
        $this.click(function(){
            var key = $.trim($this.attr("data-id"));
            var args = {"key": key, "type": "import"};
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert(`成功导入${json['inserted']}条数据`);
                    location.reload();
                }
                else{
                    alert(status);
                }
            });
        });
    });

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

    // 选择器点击事件
    select_value = function($obj){
        var text = $.trim($obj.text());
        $obj.parents(".my_input:first").find(".current_value").text(text).trigger("change_value");
    };

    // 初始绑定选择器点击事件
    $(".dropdown-menu .select_value").each(function(){
        var $this = $(this);
        $this.click(function(){
            select_value($this);
        });
    });

    // 绑定多级联动选择器,l1
    $("#select_product_name .current_value").on("change_value", function(){
        var text = $.trim($(this).text());
        var $div = $("#select_specification");

        $div.find(".current_value").text("");
        var ul = $div.parents(".my_input:first").find("ul");
        ul.empty();
        var data = l1[text];
        var lis = ""
        for(var x of data){
            lis += `<li onclick="select_value($(this))" class='select_value'>${x}</li>`;
        }
        lis = $(lis);
        ul.append(lis);

        // 绑定多级联动选择器,l2
        lis.on("change_value", function(){
            var text = $.trim($(this).text());
            var $div = $("#select_net_contents");

            $div.find(".current_value").text("");
            var ul = $div.parents(".my_input:first").find("ul");
            ul.empty();
            var data = l2[text];
            for(var x of data){
                var li = $(`<li onclick="select_value($(this))" class='select_value'>${x}</li>`);
                ul.append(li);
            }
        });
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