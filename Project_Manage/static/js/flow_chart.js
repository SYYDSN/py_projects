$(function(){
    // 调整窗口大小的函数
    let set_size = function(){
        let b = $("body").height();
        let w = $(window).height();
        if( w > b){
            $("body").css("height", w);
        }
    };

    set_size();
    window.onresize = set_size;

    // 选择节点/流向/图的按钮事件.
    $("#select_node, #select_edge, #select_digraph").each(function(){
        let $this = $(this);
        $this.click(function(){
            $("#select_node, #select_edge, #select_digraph").not($this).removeClass("active");
            $this.addClass("active");
            let id_str = $this.attr("id");
            id_str = id_str.split("_")[1];
            let class_str = "." + id_str + "_panel";
            $(".node_panel, .edge_panel, .digraph_panel").not(class_str).hide();
            $(class_str).show();
        });
    });

    // 提交按钮事件
    $(".submit_btn").click(function(){
        let $this = $(this);
        let the_class = $this.attr("data-type");
        let u = "/flow_chart";
        let args = {"type": "save"};
        let init = {};
        if(the_class === 'digraph'){
            args['class'] = 'digraph';
            let _id = $("cur_digraph").val();
            if(_id !== ""){
                init['_id'] = _id;
            }
            let name = $.trim($(".digraph_panel .my_label").val());
            if(name === ""){
                alert("流程图的名字不能为空");
                return false;
            }
            else{
                init['name'] = name;
            }
            let desc = $.trim($(".digraph_panel .my_desc").val());
            init['desc'] = desc;
            args['init'] = JSON.stringify(init);
            $.post(u, args, function(resp){
                let json = JSON.parse(resp);
                let mes = json['message'];
                if(mes === "success"){
                    alert("添加成功");
                    u += `?did=${json['_id']}`;
                    location.href = u;
                }
                else{
                    alert(mes);
                }
            });
        }
    });

// end!
});