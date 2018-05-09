$(function(){
    const url = location.pathname.replace("/view","");

    // 弹出添加类别的模态框前,修改模态框标题未添加类别
    $("#pop_add_user_modal").mousedown(function(){
        $("#add_user_modal .modal-title").text("添加用户").removeAttr("data-id");
    });

    // 弹出修改类别对话框
    $(".edit_btn").each(function(){
        let $this = $(this);
        $this.click(function(){
            $("#add_category_modal .modal-title").text("编辑用户");
            let _id = $this.attr("data-id");
            let id_str = "#" + _id;
            let user_name = $(`${id_str} td:eq(1)`).text();
            let nick_name = $(`${id_str} td:eq(2)`).text();
            // 获取用户权限设置.
            let tds = $()

            $("#category_name").val(category_name);
            $("#category_path").val(category_path);
            $("#add_user_modal .modal-title").attr("data-id", _id);
        });
    });


    // 添加/编辑用户
    $("#add_user").click(function(){
        let nick_name = $.trim($("#nick_name").val());
        let user_name = $.trim($("#user_name").val());
        let user_password = $.trim($("#user_password").val());
        let repeat_password = $.trim($("#repeat_password").val());
        let view_group = $("#view_group input:checked");
        let edit_group = $("#edit_group input:checked");
        let allow_view= [];
        let allow_edit = [];
        for(let i of view_group){
            let temp = $(i);
            let v = temp.val();
            allow_view.push(v);
        }
        for(let i of edit_group){
            let temp = $(i);
            let v = temp.val();
            allow_edit.push(v);
        }
        if(user_password === "" || user_password !== repeat_password){
            alert("密码不能为空且两次输入的密码必须一致");
            return false;
        }
        else if(user_name === ""){
            alert("用户名不能为空");
            return false;
        }
        else{
            let args = {
                "nick_name": nick_name,
                "user_name": user_name,
                "user_password": user_password,
                "allow_view": JSON.stringify(allow_view),
                "allow_edit": JSON.stringify(allow_edit)
            };
            $.post(`${url}/add`, args, function(resp){
                let json = JSON.parse(resp);
                console.log(json);
                alert(json['message']);
                if(json['message'] === "success"){
                    location.reload()
                }
                else{
                    // nothing ...
                }
            });
        }

    });


// end !!!
});