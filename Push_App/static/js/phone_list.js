$(function(){

    // 弹出消息发送模态框
    $("#push_message").click(
        function(){
            $("#message_module").css("display", "flex");
        }
    );

    // 关闭模态框
    $(".close_modal").click(
        function(){
            $(".modal_outer").css("display", "none");
        }
    );

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

    // 批量推送消息的函数
    var push_message = function(id_str){
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
                "ids": ids,
                "title": title,
                "alert": desc,
                "url": mes_url
            };
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("推送成功");
                    $(".close_modal").click();
                }
                else{
                    alert(status);
                    return false;
                }
            });
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