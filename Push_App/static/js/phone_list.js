$(function(){
    // 操作处理进度模态框
    var progress = function(verb, title){
        if (verb === "show"){
            // 显示处理进度模态框
            $("#modal_title_progress").text(title);
            $(".modal_outer_progress").css("display", "flex");
        }
        else{
            $(".modal_outer_progress").css("display", "none");
        }
    };

    // 弹出消息发送模态框
    $("#push_message").click(
        function(){
            $("#message_module").css("display", "flex");
        }
    );

    // 点击图片地址输入框事件
    $("#img_url").click(function(){
        $("#select_image").click();
    });

    // 弹出启动参数模态框
    $("#start_args").click(
        function(){
            $("#start_module").css("display", "flex");
        }
    );

    // 选择文件后,自动上传
    $("#select_image").change(function(){
        $("#img_url").val($("#upload_file").val());
        upload();
    });

    // 关闭模态框
    $(".close_modal").click(
        function(){
            $(".modal_outer").css("display", "none");
        }
    );

    // 批量推送消息
    $("#batch_push").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        if(d.length === 0){
            alert("你还未选择需要发送的设备.");
            return false;
        }
        else{
            var s = d.join(" ");
            $("#push_ids").val(s);
            $("#push_message").click();
        }

    });

    /*删除设备和联系人*/
    $("#delete_device").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete_device",
            "ids": JSON.stringify(d)
        };
        var p = confirm("删除操作不可恢复, 确认吗?");
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

    // 批量推送消息的函数
    var push_message = function(){
        // ids待发送消息的客户端的极光id的和空格组成的字符串
        var id_str = $.trim($("#push_ids").val()).split(" ");
        var ids = [];
        for(var id of id_str){
            if(id === ""){
                // nothing...
            }
            else{
                ids.push(id);
            }
        }
        console.log(ids);
        if(ids.length === 0){
            alert("请输入有效的推送id,id之间用空格隔开!");
            return false;
        }
        else{
            var title = $.trim($("#mes_title").val());
            var desc = $.trim($("#mes_alert").val());
            var mes_url = $.trim($("#mes_url").val());
            var args = {
                "type": "push_message",
                "ids": JSON.stringify(ids),
                "title": title,
                "alert": desc,
                "url": mes_url
            };
            progress("show", "发送消息");
            $.post(location.pathname, args, function(resp){
                progress("hide");
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("推送成功");
                    $(".close_modal").click();
                    $("#check_all").prop("checked", false);
                    $(".table_outer .select >input[type='checkbox']").prop("checked", false);  // 取消选择
                }
                else{
                    alert(status);
                    return false;
                }
            });
        }
    };

    // 模态框发送按钮点击事件
    $("#submit_message").click(function(){
        push_message();
    });

    /*上传成功事件*/
    var upload_success = function(resp){
        console.log(resp);
        var json = JSON.parse(resp);
        var status = json['message'];
        if(status === "success"){
            alert("上传成功!");
            $("#img_url").val(json['img_url']);
        }
        else{
            alert(status);
        }
        progress("close");
    };

    /*上传失败事件*/
    var upload_error= function(resp){
        $("#img_url").val("");
        console.log(resp);
        alert("上传失败");
        progress("close");
    };

    /*上传函数*/
    var upload = function(){
        var $obj = $("#select_image");
        let file_name = $obj.attr("name");
        if(file_name){
            // nothing...
        }
        else{
            file_name = "file"
        }
        let file_data = $obj[0].files[0];
        var opts = {
            "app-key": "affa687b-faed-45b8-b69b-17fdddea40fb",
            file_name: file_name,
            file_data: file_data,
            max_size: 4000,  // 最大4M
            url: "/manage/image/upload",
            success_cb: upload_success,
            error_cb: upload_error
        };
        progress("show", "上传图片");
        $.upload(opts);
    };

    // 提交启动参数
    $("#submit_args").click(function(){
        var delay = $.trim($("#start_delay").val());
        delay = parseInt(delay);
        if(delay === undefined || isNaN(delay)){
            alert("启动延迟必须是一个整数");
        }
        else{
            if(delay > 10){
                alert("最大启动延迟不能超过10秒.");
            }
            else{
                var redirect = $.trim($("#redirect_url").val());
                var img_url = $.trim($("#img_url").val());
                var args = {
                    "type": "start_args",
                    "delay": delay,
                    "redirect": redirect,
                    "img_url": img_url
                };
                $.post(location.pathname, args, function(resp){
                    var json = JSON.parse(resp);
                    var status = json['message'];
                    if(status === "success"){
                        alert("设置成功");
                        location.reload();
                    }
                    else{
                        alert(status);
                    }
                });
            }
        }
    });

    // 图片点击事件
    $("#preview_img").click(function(){
        var url = $(this).attr("src");
        window.open(url);
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