$(function(){
    /*重置权限设置区域所有的值为最低的权限,也就是默认用户权限*/
    var reload_status = function(){
        $("#modal_title").attr("data-current-id", ""); // 防止上一次编辑角色的遗留信息
        $(".rule_value").removeClass("select_value");
        $(".first_value").addClass("select_value");
    };

    /*填充角色信息到摩态框*/
    var fill_user_info = function(user_id){
        var tr = $("#" + user_id);
        var nick_name = $.trim(tr.find(".nick_name").text());
        var user_name = $.trim(tr.find(".user_name").text());
        $("#user_name").val(user_name);
        $("#nick_name").val(nick_name);
    };

    /*添加角色按钮*/
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            var text = $.trim($this.text());
            var title = "添加角色";
            if(text === "编辑"){
                title = "编辑角色";
                var _id = $this.attr("data-id");
                fill_user_info(_id);
            }
            else{
                reload_status();
            }
            $("#modal_title").text(title);
            $(".modal_outer").css("display", "flex");
        });
    });

    /*关闭摩态框按钮*/
    $("#close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

    /*选择值的按钮事件*/
    $(".rule_value").each(function(){
        var $this = $(this);
        $this.click(function(){
            var values = $this.parents(".right:first").find(".rule_value");
            values.removeClass("select_value");
            $this.addClass("select_value");
        });
    });

    /*添加角色*/
    var add = function(){
       var rules = $(".all_rules > .rule");
       var data = {};
       rules.each(function(){
           var $this = $(this);
           var url = $this.attr("data-url");
           var val = parseInt($.trim($this.find(".select_value").text()));
           data[url] = val;
       });
       console.log(data);
       var role_name = $.trim($("#role_name").val());
       if(role_name === ""){
           alert("角色名称不能为空");
           return false;
       }
       else{
           var args = {
               "role_name": role_name,
               "type": "add",
               "rules": JSON.stringify(data)
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

    /*编辑角色*/
    var edit = function(){
       var rules = $(".all_rules > .rule");
       var data = {};
       rules.each(function(){
           var $this = $(this);
           var url = $this.attr("data-url");
           var value = parseInt($.trim($this.find(".select_value").text()));
           data[url] = value;
       });
       console.log(data);
       var role_name = $.trim($("#role_name").val());
       if(role_name === ""){
           alert("角色名称不能为空");
           return false;
       }
       else{
           var args = {
               "role_id": $.trim($("#modal_title").attr("data-current-id")),
               "role_name": role_name,
               "type": "edit",
               "rules": JSON.stringify(data)
           };
           $.post(location.pathname, args, function(resp){
               var json = JSON.parse(resp);
               var status = json['message'];
               if(status === "success"){
                   alert("编辑成功!");
                   location.reload();
               }
               else{
                   alert(status);
               }
           });
       }
    };

    /*编辑角色按钮点击事件*/
    $(".edit_role").each(function(){
        var $this = $(this);
        $this.click(function(){
            var role_id = $this.attr("data-id");
            var role_name = $this.attr("data-name");
            var args = {"type": "rules", "role_id": role_id};
            $.post(location.pathname, args, function(resp){
                var json = JSON.parse(resp);
                var status = json['message'];
               if(status === "success"){
                   $("#modal_title").attr("data-current-id", role_id);
                   var rules = json['data'];
                   console.log(rules);
                   $("#role_name").val(role_name);
                   $(".all_rules .right").each(function(){
                       var $self = $(this);
                       var cur_val = rules[$self.attr("data-url")];
                       $self.find(".rule_value").each(function(){
                           var item = $(this);
                           // console.log($.trim(item.text()), cur_val);
                           if($.trim(item.text()) === String(cur_val)){
                               item.addClass("select_value");
                           }
                           else{
                               item.removeClass("select_value");
                           }
                       });
                   });
               }
               else{
                   alert(status);
               }
            });
        });
    });

    /*弹出框提交按钮事件*/
    $("#submit").click(function(){
        var current_id = $.trim($("#modal_title").attr("data-current-id"));
        if(current_id === ""){
            // 添加角色
            add();
        }
        else{
            // 编辑角色
            edit();
        }
    });

    /*删除角色*/
    $("#delete_role").click(function(){
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