/**
 * Created by walle on 17-2-8.
 */
$(function () {
    // 弹出添加员工
    add_employee = function(){
        $("#myModalLabel").text("添加员工");
        $("#sn,#real_name,#user_phone,#team_sn,#position_sn,#user_mail,#born_date").val('');
        $("#pop_modal").click();
    };

    // 弹出编辑员工
    edit_employee = function($obj){
        $("#myModalLabel").text("编辑员工");
        $("#sn,#real_name,#user_phone,#team_sn,#position_sn,#user_mail,#born_date").val('');
        var id_str = $.trim($obj.attr("data-id"));
        var $tr = $("#" + id_str);
        $("#sn").val(id_str);
        $("#real_name").val($.trim($tr.find(".real_name").text()));
        $("#user_phone").val($.trim($tr.find(".user_phone").text()));
        $("#team_sn").val($.trim($tr.find(".team_sn").attr('data-val')));
        $("#position_sn").val($.trim($tr.find(".position_sn").attr('data-val')));
        $("#user_mail").val($.trim($tr.find(".user_mail").text()));
        $("#born_date").val($.trim($tr.find(".born_date").text()));
        $("#pop_modal").click();
    };

    // 删除账户
    drop_employee = function ($obj) {
        var r = confirm("你确实要删除此员工吗？");
        if (r) {
            var sn = $obj.attr("data-id");
            $.post("/company/employee", {"sn": sn, "the_type": "delete"}, function (data) {
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

    // 提交添加/修改员工信息
    $("#save_employee").click(function(){
        var the_type = $.trim($("#myModalLabel").text()) == "添加员工" ? "add" : "edit";
        var welcome = the_type == "add" ? "添加" : "编辑";
        var real_name = $.trim($("#real_name").val());
        var user_phone = $.trim($("#user_phone").val());
        var team_sn = $.trim($("#team_sn").val());
        var position_sn = $.trim($("#position_sn").val());
        var user_mail = $.trim($("#user_mail").val());
        var born_date = $.trim($("#born_date").val());
        var args = {"real_name": real_name, "user_phone": user_phone, "the_type": the_type,
        "team_sn": team_sn, "position_sn": position_sn, "user_mail": user_mail, "born_date": born_date};
        if(the_type == "edit"){
            args['sn'] = $.trim($("#sn").val());
        }else{}
        $.post("/company/employee", args, function(data){
            if(data['message'] == "success" ){
                alert(welcome + "成功");
                location.reload();
            }
            else{
                alert(data['message']);

            }
        });
    });


    //end !
});