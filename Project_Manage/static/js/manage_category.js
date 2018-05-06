$(function(){
    const url = location.pathname.replace("/view","");
    // 添加category的函数
    $("#add_category").click(function(){
        let name = $.trim($("#category_name").val());
        let path = $.trim($("#category_path").val());
        let args = {"name": name, "path": path};
        $.post(`${url}/add`, args, function(resp){
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