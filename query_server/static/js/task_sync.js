$(function(){
    // 弹出模态框
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            var $this = $(this);
            var sync_id = $.trim($this.attr("data-id"));   // 同步id
            var task_id = "";    // 生产任务id
            var batch_sn = "";   // 生产任务的产品批号
            if($this.hasClass("relate_task")){
                // 关联任务
            }
            else{
                // 重新关联
                task_id = $.trim($this.attr("data-task-id"));
                batch_sn = $.trim($this.attr("data-batch-sn"));
            }
            $(".modal_outer .current_value").text(batch_sn).attr("data-id", task_id);
            $("#submit_sync").attr("data-id", sync_id);
            $(".modal_outer").css("display", "flex");
        });
    });


    // 关闭模态框
    $(".close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    // 模态框提交按钮的事件
    $("#submit_sync").click(function(){
        var $this = $(this);
        var sync_id = $.trim($this.attr("data-id"));   // 同步id
        var task_id = $.trim($(".modal_outer .current_value").attr("data-id"));   // 同步id

        if(sync_id === ""){
            alert("还没选择同步任务!");
            return false;
        }
        else{
            var args = {
                "task_id": task_id,
                "_id": sync_id,
                "type": "edit"
            };

            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
                if(status === "success"){
                    alert("操作成功");
                    location.reload();
                }else{
                    alert(status);
                }
            });
        }
    });

    // 选择器点击事件
    select_value = function($obj){
        var batch_sn = $.trim($obj.text());
        var task_id = $.trim($obj.attr("data-id"));
        $(".modal_outer .current_value").attr("data-id", task_id).text(batch_sn);
    };

    /*清除已回传的条码*/
    $("#cancel_sync").click(function(){
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
        var p = confirm("这将清除本次条码回传操作,你确定吗!");
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

    /*删除回传的文件和日志*/
    $("#delete_sync").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete",
            "ids": JSON.stringify(d)
        };
        var p = confirm("只会删除回传的文件和日志(回传的条码信息会保留),确定吗!");
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