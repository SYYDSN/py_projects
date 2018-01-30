/**
 * Created by walle on 17-2-8.
 */
$(function () {
    // 启用账户
    up_user = function ($obj) {
        var user_id = $obj.attr("data-id");
        $.post("/manage_suppliers", {"sn": user_id, "the_type": "up"}, function (data) {
            var data = JSON.parse(data);
            if (data['message'] == 'success') {
                alert("启用成功");
                location.reload();
            }
            else {
                alert(data['message']);
            }
        });
    };

    // 禁用账户
    down_user = function ($obj) {
        var user_id = $obj.attr("data-id");
        $.post("/manage_suppliers", {"sn": user_id, "the_type": "down"}, function (data) {
            var data = JSON.parse(data);
            if (data['message'] == 'success') {
                alert("禁用成功");
                location.reload();
            }
            else {
                alert(data['message']);
            }
        });
    };

    // 删除账户
    drop_user = function ($obj) {
        var r = confirm("你确实要删除此帐户吗？");
        if (r) {
            var user_id = $obj.attr("data-id");
            $.post("/manage_suppliers", {"sn": user_id, "the_type": "delete"}, function (data) {
                var data = JSON.parse(data);
                if (data['message'] == 'success') {
                    alert("删除成功");
                    location.reload();
                }
                else {
                    alert(data['message']);
                }
            });
        } else {
        }
    };

    // 弹出添加框
    add_user = function () {
        $("#myModalLabel").text("添加供应商");
        $("#group_sn").val('');
        $(".modal-body>table input").val('');
        $("#pop_modal").click();
    };

    // 弹出编辑框
    edit_user = function($obj){
        $("#myModalLabel").text("编辑供应商信息");
        var group_sn = $.trim($obj.attr("data-id"));
        copy_info(group_sn);
        $("#pop_modal").click();

    };

    // 把当前用户信息复制到编辑模态框，
    copy_info = function(sn){
        $("#group_sn").val(sn);
        var str = "#group_" + sn;
        var $obj = $(str);
        var tds = $obj.find("td[data-type='item']");

        tds.each(function(){
            var key = "#" + $.trim($(this).attr("class"));
            var value = $.trim($(this).text());
            $(key).val(value);
        });

    };

    // 保存按钮事件
    $("#save_user").click(function () {
        var the_type = "edit";
        var all = $(".modal-body input");
        if ($.trim($("#myModalLabel").text()) == "添加供应商") {
            the_type = "add";
            var all = $(".modal-body input").not("#group_sn");
        } else {}

        var args = {"the_type": the_type};
        all.each(function () {
            var $this = $(this);
            args[$this.attr("id")] = $.trim($this.val());
        });
        $.post("/manage_suppliers", args, function (message) {
            var message = JSON.parse(message)['message'];
            if (message == "success") {
                alert((the_type == "edit" ? "编辑" : "添加") + "成功");
                location.reload();
            }
            else {
                alert(message);
            }
        });
    });

    // 显示sftp相关信息。
    show_sftp = function(sn){
        var args = {"the_type": "show_sftp",
        "group_sn": sn, "user_class": 2};
        $.post("/manage_suppliers", args, function(data){
            var data = JSON.parse(data);
            if(data['message'] != "success"){
                alert(data['message']);
                return false;
            }
            else{
                var result = data['result'];
                var keys = Object.keys(result);
                var i = 0;
                for(i in keys){
                    var key =  keys[i];
                    $("#" + key).text(result[key]);
                }
                $(".sftp-outer").show();
            }
        });
    };

    // 关闭sftp信息弹出框
    $("#close_sftp_div").click(function(){
        $(".sftp-outer").hide();
    });

    //end !
});