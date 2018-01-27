/**
 * Created by walle on 17-2-8.
 */
$(function () {
    // 启用账户
    up_user = function ($obj) {
        var user_id = $obj.attr("data-id");
        $.post("/manage/company", {"sn": user_id, "the_type": "up"}, function (data) {
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
        $.post("/manage/company", {"sn": user_id, "the_type": "down"}, function (data) {
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
            $.post("/manage/company", {"sn": user_id, "the_type": "delete"}, function (data) {
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
        $("#myModalLabel").text("添加公司");
        $("#pop_modal").click();
    };

    // 弹出编辑框
    edit_user = function($obj){
        $("#myModalLabel").text("编辑公司信息");
        var group_sn = $.trim($obj.attr("data-id"));
        copy_info(group_sn);
        $("#pop_modal").click();

    };

    // 把当前用户信息复制到编辑模态框，
    copy_info = function(sn){
        $("#sn").val(sn);
        var str = "#group_" + sn;
        var $obj = $(str);
        var tds = $obj.find("td[data-type='item']");

        tds.each(function(){
            var key = "#" + $.trim($(this).attr("class"));
            var value = $.trim($(this).text());
            $(key).val(value);
        });

    };


    // 弹出添加框
    edit_ticket = function ($obj) {
        var file_md5 = $obj.attr("data-id");
        var tds = $("#" + file_md5 + ">td").not(".owner_id,.file_md5,.file_name,.not");
        console.log(tds);
        $("#pop_modal").click();
        $.each(tds, function (i, n) {

            var c_id = $(n).attr("class");
            var c_val = $.trim($(n).text());
            $("#" + c_id).val(c_val);
        });

    };

    // 保存按钮事件
    $("#save_user").click(function () {
        var the_type = "edit";
        var all = $(".modal-body input");
        if ($.trim($("#myModalLabel").text()) == "添加公司") {
            the_type = "add";
            var all = $(".modal-body input").not("#sn");
        } else {}

        var args = {"the_type": the_type};
        all.each(function () {
            var $this = $(this);
            args[$this.attr("id")] = $.trim($this.val());
        });
        $.post("/manage/company", args, function (message) {
            var message = message['message'];
            if (message == "success") {
                alert((the_type == "edit" ? "编辑" : "添加") + "成功");
                location.reload();
            }
            else {
                alert(message);
            }
        });
    });


    //end !
});