/**
 * Created by walle on 17-2-8.
 */
$(function () {
    // 弹出添加职务
    add_position = function(){
        $("#myModalLabel").text("添加职务");
        $("#sn,#position_name,#parent_sn").val('');
        $("#has_team").removeProp("checked");
        $("#pop_modal").click();
    };

    // 弹出编辑职务
    edit_position = function($obj){
        $("#myModalLabel").text("编辑职务");
        $("#sn,#position_name,#parent_sn").val('');
        var id_str = $.trim($obj.attr("data-id"));
        var $tr = $("#" + id_str);
        $("#sn").val(id_str);
        $("#position_name").val($.trim($tr.find(".position_name").text()));
        $("#parent_sn").val($.trim($tr.find(".parent_sn").attr('data-val')));
        $("#has_team").removeProp("checked");
        if($.trim($tr.find(".has_team").attr('data-val')) == "1"){
            $("#has_team").prop("checked", true);
        }else{}
        $("#pop_modal").click();
    };

    // 删除账户
    drop_position = function ($obj) {
        var r = confirm("你确实要删除此职务吗？");
        if (r) {
            var sn = $obj.attr("data-id");
            $.post("/company/position", {"sn": sn, "the_type": "delete"}, function (data) {
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

    // 提交添加/修改职务信息
    $("#save_position").click(function(){
        var the_type = $.trim($("#myModalLabel").text()) == "添加职务" ? "add" : "edit";
        var welcome = the_type == "add" ? "添加" : "编辑";
        var position_name = $.trim($("#position_name").val());
        var parent_sn = $.trim($("#parent_sn").val());
        var has_team = $("#has_team:visible").length;
        var args = {"has_team": has_team, "parent_sn": parent_sn, "position_name": position_name, "the_type": the_type};
        if(the_type == "edit"){
            args['sn'] = $.trim($("#sn").val());
        }else{}
        $.post("/company/position", args, function(data){
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