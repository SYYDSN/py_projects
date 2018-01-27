/**
 * Created by walle on 17-2-8.
 */
$(function () {
    // 查看提醒
    alert_self = function($obj){
        alert($obj.parents(".customer_description").attr("data-description"));
    };

    // 删除账户
    drop_user = function ($obj) {
        var r = confirm("你确实要删除此帐户吗？");
        if (r) {
            var user_id = $obj.attr("data-id");
            $.post("/company/user", {"user_sn": user_id, "the_type": "delete"}, function (data) {
                if (data['message'] == 'success') {
                    alert("删除成功");
                    location.href = location.href;
                }
                else {
                    alert(data['message']);
                }
            });
        } else {
        }
    };

    // 标记分配/不分赔
    change_customer = function ($obj) {
        var s = $.trim($obj.text());
        var str = (s == "未分配"? "已分配" : "未分配");
        var val = (s == "未分配"? 1 : 0);
        var r = confirm("你确实要标记此帐户为" + str + "吗？");
        if (r) {
            var user_id = $obj.attr("data-id");
            $.post("/company/user", {"user_sn": user_id, "the_type": "allotted", "val": val}, function (data) {
                if (data['message'] == 'success') {
                    alert("标记成功");
                    location.href = location.href;
                }
                else {
                    alert(data['message']);
                }
            });
        } else {
        }
    };

    // 改变客户team_sn
    change_team = function($obj){
        var team_sn = $.trim($obj.attr("data-team-val"));
        var user_sn = $.trim($obj.attr("data-customer-val"));
        $.post("/company/user", {"user_sn": user_sn, "the_type": "edit", "team_sn": team_sn}, function (data) {
            if (data['message'] == 'success') {
                $("#" + user_sn).find(".current_text").html($.trim($obj.text()) + "<span class='caret'></span>");
            }
            else {
                alert(data['message']);
            }
        });

    };

    // 自动刷新的循环
    let auto_refresh_handler = 0;

    // 自动刷新按钮
    $("#auto_refresh").click(function(){
        let status = $(this).prop("checked");
        console.log(status);
        if(status){
            if(auto_refresh_handler){
                // 自动刷新已经启动了。
            }
            else{
                auto_refresh_handler = setInterval(function(){
                    console.log("刷新页面");
                    location.reload();
                    }, 1000*60);
            }
        }
        else{
            if(auto_refresh_handler){
                clearInterval(auto_refresh_handler);
                auto_refresh_handler = 0;
            }
            else{
                // 自动刷新已经关闭了
            }
        }
    }).trigger("click");

    //end !
});