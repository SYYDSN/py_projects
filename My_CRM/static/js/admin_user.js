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
            $.post("/manage/user", {"user_sn": user_id, "the_type": "delete"}, function (data) {
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


    //end !
});