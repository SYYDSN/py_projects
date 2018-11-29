$(function(){
    /*清除模态框输入残留*/
    var clear_modal = function(){
        $(".modal_title").attr("data-current-id", "");
        $(".modal_mid .line input").val("");
    };

    /*关闭摩态框按钮*/
    $(".close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    /*填充信息到生产线模态框*/
    var fill_line_info = function(id_str){
        console.log(id_str);

    };

    /*弹出生产线模态框*/
    $(".pop_modal_line").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var text = $.trim($this.text());
            var title = "添加生产线";
            if(text === "编辑"){
                title = "编辑生产线";
                var _id = $this.attr("data-id");
                fill_line_info(_id);
            }
            else{
                // nothing...
            }
            $(".modal_outer_line .modal_title").text(title);
            $(".modal_outer_line").css("display", "flex");
        });
    });

    /*弹出主控板模态框*/
    $(".pop_modal_control").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var text = $.trim($this.text());
            var title = "添加主控板";
            if(text === "编辑"){
                title = "编辑主控板";
                var _id = $this.attr("data-id");
                fill_line_info(_id);
            }
            else{
                // nothing...
            }
            $(".modal_outer_control .modal_title").text(title);
            $(".modal_outer_control").css("display", "flex");
        });
    });

    /*弹出框提交按钮事件*/
    $(".submit").each(function(){
        var $this = $(this);
        $this.click(function(){
            var l_id = $.trim($this.attr("data-id"));
            var c_id = $.trim($this.attr("data-control-ip"));
            var line_name = $.trim($(".modal_outer .line_name").val());
            var args = {};
            if(l_id === ""){
                // 添加生产线

                if(line_name === ""){
                    alert("生产线名必须!");
                    return false;
                }
                else{
                    args['name'] = line_name
                }
            }
            else{
                // 编辑主控板或者添加编辑子设备
            }
        });
    });



    /*删除生产线*/
    $("#delete_line").click(function(){
        var d = [];
        $(".select > input[type='checkbox']:checked").each(function(){
            var $this = $(this);
            var _id = $.trim($this.attr("data-id"));
            d.push(_id);
        });
        var args = {
            "type": "delete",
            "ids": JSON.stringify(d)
        }
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

});