/**
 * Created by walle on 17-2-8.
 */
$(function () {
    // 弹出添加团队
    add_team = function(){
        $("#myModalLabel").text("添加团队");
        $("#sn,#team_name,#leader_sn").val('');
        $("#pop_modal").click();
    };

    // 弹出编辑团队
    edit_team = function($obj){
        $("#myModalLabel").text("编辑团队");
        $("#sn,#team_name,#leader_sn").val('');
        var id_str = $.trim($obj.attr("data-id"));
        var $tr = $("#" + id_str);
        $("#sn").val(id_str);
        $("#team_name").val($.trim($tr.find(".team_name").text()));
        console.log($.trim($tr.find(".leader_sn").attr('data-val')))
        $("#leader_sn").val($.trim($tr.find(".leader_sn").attr('data-val')));
        $("#pop_modal").click();
    };

    // 删除
    drop_team = function ($obj) {
        var r = confirm("你确实要删除此团队吗？");
        if (r) {
            var sn = $obj.attr("data-id");
            $.post("/company/team", {"sn": sn, "the_type": "delete"}, function (data) {
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

    // 提交添加/修改团队信息
    $("#save_team").click(function(){
        var the_type = $.trim($("#myModalLabel").text()) == "添加团队" ? "add" : "edit";
        var welcome = the_type == "add" ? "添加" : "编辑";
        var team_name = $.trim($("#team_name").val());
        var leader_sn = $.trim($("#leader_sn").val());
        var args = {"leader_sn": leader_sn, "team_name": team_name, "the_type": the_type};
        if(the_type == "edit"){
            args['sn'] = $.trim($("#sn").val());
        }else{}
        $.post("/company/team", args, function(data){
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