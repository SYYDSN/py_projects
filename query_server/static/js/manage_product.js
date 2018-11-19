$(function(){
    /*填充产品信息到摩态框*/
    var fill_user_info = function(p_id){
        var tr = $("#" + p_id);
        $("#modal_title").attr("data-current-id", p_id);
        var product_name = $.trim(tr.find(".product_name").text());
        var specification = $.trim(tr.find(".specification").text());
        var net_contents = $.trim(tr.find(".net_contents").text());
        var package_ratio = $.trim(tr.find(".package_ratio").text());
        $("#product_name").val(product_name);
        $("#specification").val(specification);
        $("#net_contents").val(net_contents);
        $("#package_ratio").val(package_ratio);
    };

    /*清除模态框输入残留*/
    var clear_modal = function(){
        $("#modal_title").attr("data-current-id", "");
        $(".modal_mid .line input").val("");
    };

    /*添加产品按钮*/
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            clear_modal();
            var text = $.trim($this.text());
            var title = "添加产品";
            if(text === "编辑"){
                title = "编辑产品";
                var _id = $this.attr("data-id");
                fill_user_info(_id);
            }
            else{
                // nothing...
            }
            $(".my_one").val(1);
            $("#modal_title").text(title);
            $(".modal_outer").css("display", "flex");
        });
    });

    /*关闭摩态框按钮*/
    $("#close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    /*添加产品*/
    var add = function(){
       var product_name = $.trim($("#product_name").val());
       var specification = $.trim($("#specification").val());
       var net_contents = $.trim($("#net_contents").val());
       var package_ratio = $.trim($("#package_ratio").val());

       if(product_name === ""){
           alert("产品名称不能为空");
           return false;
       }
       else if(specification === ""){
           alert("产品规格不能为空");
           return false;
       }
       else if(isNaN(net_contents)){
           alert("净含量必须是数值");
           return false;
       }
       else if(isNaN(package_ratio)){
           alert("包装比例必须是整数");
           return false;
       }
       else{
           var args = {
               "product_name": product_name,
               "specification": specification,
               "net_contents": parseInt(net_contents),
               "package_ratio": parseInt(package_ratio),
               "type": "add"
           };
           $.post(location.pathname, args, function(resp){
               var json = JSON.parse(resp);
               var status = json['message'];
               if(status === "success"){
                   alert("添加成功!");
                   location.reload();
               }
               else{
                   alert(status);
               }
           });
       }
    };

    /*编辑产品事件*/
    var edit = function(p_id){
        var product_name = $.trim($("#product_name").val());
       var specification = $.trim($("#specification").val());
       var net_contents = $.trim($("#net_contents").val());
       var package_ratio = $.trim($("#package_ratio").val());

       if(product_name === ""){
           alert("产品名称不能为空");
           return false;
       }
       else if(specification === ""){
           alert("产品规格不能为空");
           return false;
       }
       else if(isNaN(net_contents)){
           alert("净含量必须是数值");
           return false;
       }
       else if(isNaN(package_ratio)){
           alert("包装比例必须是整数");
           return false;
       }
       else{
           var args = {
               "_id": p_id,
               "product_name": product_name,
               "specification": specification,
               "net_contents": parseInt(net_contents),
               "package_ratio": parseInt(package_ratio),
               "type": "edit"
           };

           $.post(location.pathname, args, function(resp){
               var json = JSON.parse(resp);
               var status = json['message'];
               if(status === "success"){
                   alert("修改成功!");
                   location.reload();
               }
               else{
                   alert(status);
               }
           });
       }
    };

    /*弹出框提交按钮事件*/
    $("#submit").click(function(){
        var current_id = $.trim($("#modal_title").attr("data-current-id"));
        if(current_id === ""){
            // 添加产品
            add();
        }
        else{
            // 编辑产品
            edit(current_id);
        }
    });

    /*删除产品*/
    $("#delete_product").click(function(){
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