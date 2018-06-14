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

    // 获取url参数
    let get_url_arg = function (name) {
        let reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        let r = window.location.search.substr(1).match(reg);
        return (r !== null)?decodeURI(r[2]):null;
    };

    let draw_svg = function(html){
        // 绘制中间的区域
        if(html === ''){
            // nothing...
        }
        else{
            let svg = $(html);
            svg.attr("width", "100%");
            svg.attr("height", "100%");
            $(".middle").empty().append(svg);
            let ns = Object.keys(node_dict).join(",#");
            ns = "#" + ns;
            let es = Object.keys(edge_dict).join(",#");
            es = "#" + es;
            let nodes = ns==="#"?[]:$(ns);
            let edges = es==="#"?[]:$(es);
            if(nodes.length === 0){
                // nothing...
            }
            else{
                for(let node of nodes){
                    node = $(node);
                    let key = node.attr("id");
                    let d = node_dict[key];
                    if(d){
                        let s = d['desc']===""?" ":d['desc'];
                        node.find("title").html(s);
                    }

                }
            }
        }
    };

    (function(){
        let did = get_url_arg("did");
        if(did){
            let args = {"did": did, "class": "digraph", "type": "view"};
            $.post("/flow_chart", args, function(resp){
                let json = JSON.parse(resp);
                draw_svg(json['svg']);
            });
        }
    })();

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
        else if(the_class === 'node'){
            // 添加节点
            args['class'] = 'node';
            let did = $(".left .nav .active").attr("data-id");
            console.log(did);
            if(did){
                init['did'] = did;
            }
            else{
                alert("请先选择左侧归属的流程图");
                return false;
            }
            let _id = $("cur_node").val();
            if(_id !== ""){
                // Node对象使用name做唯一性判定
                init['name'] = _id;
            }
            let name = $.trim($(".node_panel .my_label").val());
            if(name === ""){
                alert("节点的名字不能为空");
                return false;
            }
            else{
                init['label'] = name;
            }
            let shape = null;
            for(let x of $(".node_panel input[type='radio']")){
                let $this = $(x);
                let status = $this.attr("checked");
                let val = $this.attr("data-id");
                if(status){
                    shape = val;
                    init['shape'] = shape;
                    break;
                }
            }
            let desc = $.trim($(".node_panel .my_desc").val());
            init['desc'] = desc;
            args['init'] = JSON.stringify(init);
            $.post(u, args, function(resp){
                let json = JSON.parse(resp);
                let mes = json['message'];
                if(mes === "success"){
                    alert("添加成功");
                    draw_svg(json['svg']);
                }
                else{
                    alert(mes);
                }
            });
        }
        else{}
    });

// end!
});