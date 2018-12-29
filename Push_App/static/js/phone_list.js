$(function(){

    // 弹出模态框
    $(".pop_modal").click(
        function(){
            $(".modal_outer").css("display", "flex");
        }
    );

    // 点击点击上传图标input事件
    $("#mes_icon_url").click(function(){$("#upload_img").click();});

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