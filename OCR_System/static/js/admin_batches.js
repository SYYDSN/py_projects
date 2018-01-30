/**
 * Created by walle on 17-2-8.
 */
$(function () {

    // 搜索选择按钮
    $("#select_class a").click(function () {
        $("#current_class").attr("data-name", $(this).attr("data-name"));
        $("#current_class").html($(this).text() + "<span class='caret'></span>");
        var key_word = $("#key_word");
        if ($.trim($(this).attr("data-name")) == "end_date") {
            key_word.attr("placeholder", "格式： 2017-05-05");
        }
        else if ($.trim($(this).attr("data-name")) == "customer_sn") {
            key_word.attr("placeholder", "输入客户的简称，比如 万达");
        }
        else {
            key_word.attr("placeholder", "");
        }
    });

    // 搜索按钮
    $("#launch_search").click(function () {
        var key_word = $.trim($("#key_word").val());
        key_word = key_word.split(" ")[0]; // 只搜索第一个空格前面的关键词
        var term = $("#current_class").attr("data-name");
        location.href = "manage_batches?&term=" + term + "&key_word=" + key_word;
    });

    // 弹出发送邮件的窗口
    pop_mail = function ($obj) {
        var batch_sn = $.trim($obj.attr("data-sn"));
        var $tr = $("#" + batch_sn);
        var customer_sn = $.trim($tr.find(".customer_sn").text());
        $("#mail_customer_sn").val(customer_sn);
        var batch_name = $.trim($tr.find(".batch_name").text());
        var datetime = $.trim($tr.find(".begin_datetime").text());
        var title = "通知邮件";
        var content = "尊敬的用户,贵司于 " + datetime + " 上传的批次名为 " + batch_name + "的压缩包出现问题被退回，问题原因是：";
        $("#title").val(title);
        $("#content").val(content);
        $(".sftp-outer").show();
    };

    // 发送邮件
    $("#send_mail_btn").click(function () {
        var customer_sn = $.trim($("#mail_customer_sn").val());
        var title = $.trim($("#title").val());
        var content = $.trim($("#content").val());
        // the_type代表是给客户发邮件还是给供应商发邮件
        var args = {
            "the_sn": customer_sn,
            "title": title, "content": content, "the_type": "customer"
        };
        $("#send_mail_btn").attr("disabled", true);
        $.post("/send_mail", args ,function(data){
            var result = JSON.parse(data);
            console.log(result);
            if(result['message'] == "success"){
                alert("发送成功");
                $("#close_sftp_div").click();
            }
            else{
                alert(result['message']);
            }
            $("#send_mail_btn").removeProp("disabled");
        });
        // 如果出现发送异常，在6秒后也会解除发送按钮的锁定。
        setTimeout(function(){$("#send_mail_btn").removeProp("disabled");}, 6000);
    });

    // 关闭邮件编辑框
    $("#close_sftp_div").click(function () {
        $(".sftp-outer").hide();
    });

    // 弹出备注框
    pop_description = function ($obj) {
        $("#batch_description").val($.trim($obj.attr("data-description")));
        $(".description-outer").show();
    };

    // 关闭备注框
    $("#close_description_div").click(function(){
         $(".description-outer").hide();
    });

    // 转换批次状态为通过质检。
    check = function($obj){
        var $tr = $obj.parents("tr:first");
        var batch_sn = $tr.attr("id");
        var to_checked = 1;
        if($.trim($obj.text()) == "blocked"){
            // nothing...
        }
        else{
            to_checked = 0;
        }
        var args = {"the_type": "change_status", "batch_sn": batch_sn, "to_checked": to_checked};
        $.post("/manage_batches", args, function(data){
            var result = JSON.parse(data);
            var word = to_checked == 1 ? "审核" : "解除审核";
            if(result['message'] == "success"){
                alert(word + "成功");
                location.reload();
            }
            else{
                alert(word + "失败");
                return false;
            }
        });
    };


    //end !
});