/**
 * Created by walle on 17-2-8.
 */
$(function () {

    // 添加计划
    add_url = function () {
        $("#myModalLabel").text("添加链接");
        $("#pop_modal").click();
        var members = $("#sn,#url,#url_name,#company_sn,#channel_sn,#pattern_sn,#platform_sn");
        members.val('');
    };

    // 弹出调整计划面板
    edit = function ($obj) {
        $("#myModalLabel").text("编辑链接");
        var id_str = $.trim($obj.attr('data-id'));
        var $tr = $("#" + id_str);
        $("#url").val($tr.find(".url").text());
        $("#url_name").val($tr.find(".url_name").text());
        $("#company_sn").val($tr.find(".company_sn").attr('data-id'));
        $("#channel_sn").val($tr.find(".channel_sn").attr('data-id'));
        $("#pattern_sn").val($tr.find(".pattern_sn").attr('data-id'));
        $("#platform_sn").val($tr.find(".platform_sn").attr('data-id'));
        $("#is_3th").val($tr.find(".is_3th").attr('data-id'));
        $("#sn").val($tr.attr('id'));
        $("#pop_modal").click();
    };

    // 保存
    $("#save_url").click(function () {
        var the_type = $.trim($("#myModalLabel").text()) == "添加链接" ? "add" : "edit";
        var url_name = $.trim($("#url_name").val());
        var url= $.trim($("#url").val());
        var company_sn = $.trim($("#company_sn").val()) == '' ? 0 : $.trim($("#company_sn").val());
        var channel_sn = $.trim($("#channel_sn").val());
        var pattern_sn = $.trim($("#pattern_sn").val());
        var platform_sn = $.trim($("#platform_sn").val());
        var is_3th = $("#is_3th:checked").length;
        if (url_name == "") {
            alert("链接名称不能为空");
            return false;
        }
        else if (url == "") {
            alert("url不能为空");
            return false;
        }
        else if (company_sn == "") {
            alert("所属公司不能为空");
            return false;
        }
        else if (channel_sn == "") {
            alert("推广渠道不能为空");
            return false;
        }
        else if (pattern_sn == "") {
            alert("引流方式不能为空");
            return false;
        }
        else if (platform_sn == "") {
            alert("推广端口不能为空");
            return false;
        }
        else {
            var args = {"url": url, "url_name": url_name, "channel_sn": channel_sn, "pattern_sn": pattern_sn,
                "the_type": the_type, "company_sn": company_sn, "platform_sn": platform_sn, "is_3th": is_3th};
            if(the_type == "edit"){
                args['sn'] = $.trim($("#sn").val());
            }
            $.post("/manage/url", args, function(data){
                var welcome = the_type == "add" ? "添加" : "编辑";
                if(data['message'] == 'success'){
                    alert(welcome + "成功");
                    location.reload();
                }
                else{
                    alert(data['message']);
                    return false;
                }
            });
        }
    });

    // 删除
    delete_url = function($obj){
        var url_sn = $.trim($obj.attr("data-id"));
        var r = confirm("你确实向删除此计划吗？");
        if (r) {
            var args = {"the_type": "delete", "sn": url_sn};
            $.post("/manage/url", args, function (data) {
                if (data['message'] == "success") {
                    alert("删除成功");
                    location.reload();
                }
                else {
                    alert(data["message"]);
                }
            });
        } else {}
    };


    //end !
});