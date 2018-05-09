$(function(){
    const url = location.pathname.replace("/view","");

    // 弹出添加类别的模态框前,修改模态框标题未添加类别
    $("#pop_add_category_modal").mousedown(function(){
        $("#add_category_modal .modal-title").text("添加类别").removeAttr("data-id");
    });

    // 弹出修改类别对话框
    $(".edit_btn").each(function(){
        let $this = $(this);
        $this.click(function(){
            $("#add_category_modal .modal-title").text("编辑类别");
            let _id = $this.attr("data-id");
            let id_str = "#" + _id;
            let category_name = $(`${id_str} td:eq(1)`).text();
            let category_path = $(`${id_str} td:eq(2)`).text();
            $("#category_name").val(category_name);
            $("#category_path").val(category_path);
            $("#add_category_modal .modal-title").attr("data-id", _id);
        });
    });

    // 添加/编辑category的函数
    $("#add_category").click(function(){
        let name = $.trim($("#category_name").val());
        let path = $.trim($("#category_path").val());
        let args = {"name": name, "path": path};
        let process_type = $("#add_category_modal .modal-title").text().indexOf("添加") === -1? "edit": "add";
        let _id = $("#add_category_modal .modal-title").attr("data-id");
        if(_id !== undefined){
            args['_id'] = _id;
        }else{}
        $.post(`${url}/${process_type}`, args, function(resp){
            let json = JSON.parse(resp);
            alert(json['message']);
            if(json['message'] === "success"){
                location.reload()
            }
            else{
                // nothing ...
            }
        });
    });

    // 改变状态 启用/停用
    $(".change_status").each(function(){
        let $this = $(this);
        $this.change(function(){
            let _id = $this.attr("data-id");
            let status = $this.val();
            console.log(_id, status);
            let args = {
                "o_id": _id,
                "update_dict": JSON.stringify({"status": status})
            };
            $.post(`${url}/edit`, args, function(resp){
                let json = JSON.parse(resp);
                console.log(json);
            });
        })
    });

    // 删除记录
    $(".delete_btn").each(function(){
        let $this = $(this);
        $this.click(function(){
            let name = $this.attr("data-name");
            let c = confirm(`你是否要删除 ${name} ?`);
            if(c){
                let args = {"o_id": $this.attr("data-id")};
                $.post(`${url}/delete`, args, function (resp) {
                    let json = JSON.parse(resp);
                    alert(json['message']);
                    if(json['message'] === "success"){
                        location.reload()
                    }
                    else{
                        // nothing ...
                    }
                })
            }else{}
        });
    });

// end!!!
});