$(function(){
    let edge_dict = {};
    let node_dict = {};
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
    let did = get_url_arg("did");

    (function(){
        // 启动时,加载数据初始化图和各种元素
        if(did){
            let args = {"did": did, "class": "digraph", "type": "view"};
            $.post("/flow_chart", args, function(resp){
                let json = JSON.parse(resp);
                draw_svg(json['data']);
            });
        }
    })();

    // svg中的元素的选中事件
    let click_event = function ($obj) {
        $obj.dblclick(function(){
            let menu = $("#mini_menu");
            let offset = $(this).offset();
            let top = offset['top'];
            let left = offset['left'];
            menu.attr("data-class", $obj.attr("class"));
            menu.attr("data-id", $obj.attr("id"));
            menu.css({"top": top + 10, "left": left + 10, "z-index": 100});
        });
    };

    // 中间空白处点击事件
    $(".middle").click(function(){
        $("#mini_menu").css("z-index", -100);
        $("#cur_digraph, #cur_node, #cur_edge").val("");
    });

    // 迷你菜单点击事件
    $(".mini_menu_item").each(function(){
        let $this = $(this);
        $this.click(function(){
            let dict = edge_dict;
            let m = $("#mini_menu");
            let the_class = m.attr("data-class");
            let the_id = m.attr("data-id");
            let obj = dict[the_id];
            let text = $this.text();
            if(text === "新 建"){
                $(".node_panel .my_label").focus();
            }
            else if(text === "编 辑"){
                if( the_class === "node"){
                    dict = node_dict;
                    obj = dict[the_id];
                    $("#select_node").click();
                    $("#cur_node").val(obj['_id']);
                    $(".node_panel .my_label").val(obj['label']);
                    let shapes = $(".node_panel input[type='radio']");
                    for(let shape of shapes){
                        shape = $(shape);
                        if(shape.attr("data-id") === obj['shape']){
                            shape.click();
                            break;
                        }
                    }
                    $(".node_panel .my_desc").val(obj['desc']);
                }
                else{
                    $("#select_edge").click();
                    $("#cur_edge").val(obj['_id']);
                    $("#tail_name").val(obj['tail_name']);
                    $("#head_name").val(obj['head_name']);
                    $(".edge_panel .my_label").val(obj['label']);
                }
            }
            else if(text === "删 除"){
                if( the_class === "node"){
                    dict = node_dict;
                    obj = dict[the_id];
                    let r = confirm(`你确实要删除 ${obj['label']} 节点吗?`);
                    if(r){
                        let init = {"name": obj['_id'], "did": did};
                        let args = {"class": the_class, "type": "delete", "init": JSON.stringify(init)};
                        $.post("/flow_chart", args, function(resp){
                            let json = JSON.parse(resp);
                            let mes = json['message'];
                            if(mes === "success"){
                                alert("删除成功");
                                draw_svg(json['data']);
                            }
                            else{
                                alert(mes);
                            }
                        });
                    }
                }
                else{
                    let r = confirm(`你确实要删除 ${obj['label']} 流向吗?`);
                    if(r){
                        let init = {"_id": obj['_id'], "did": did};
                        let args = {"class": the_class, "type": "delete", "init": JSON.stringify(init)};
                        $.post("/flow_chart", args, function(resp){
                            let json = JSON.parse(resp);
                            let mes = json['message'];
                            if(mes === "success"){
                                alert("删除成功");
                                draw_svg(json['data']);
                            }
                            else{
                                alert(mes);
                            }
                        });
                    }
                }
            }
            else{}
            $("#mini_menu").css("z-index", -100);
        });
    });

    // 初始化节点选择的select
    let init_select_node = function(n_dict){
        let tail_name = $("#tail_name");
        let head_name = $("#head_name");
        tail_name.empty();
        head_name.empty();
        tail_name.append(`<option value=""></option>`);
        head_name.append(`<option value=""></option>`);
        for(let k in n_dict){
            let html = `<option value="${k}">${n_dict[k]['label']}</option>`;
            tail_name.append(html);
            head_name.append(html);
        }
    };

    let draw_svg = function(data){
        // 绘制中间的区域
        node_dict = data['node_dict'];
        edge_dict = data['edge_dict'];
        init_select_node(node_dict);  // 初始化节点选择的select
        $("#cur_node, #cur_edge, .my_label, .my_desc").val("");
        let svg = $(data['svg']);
        svg.attr("width", "100%");
        svg.attr("height", "100%");
        $(".middle").empty().append(svg);
        $("#graph0 > title").text(data['title']);
        let nodes = $(".node");
        let edges = $(".edge");
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
                    click_event(node);
                }

            }
        }
        if(edges.length === 0){
            // nothing...
        }
        else{
            for(let edge of edges){
                edge = $(edge);
                let key = edge.attr("id");
                let e = edge_dict[key];
                if(e){
                    let s = e['desc']===""?" ":e['desc'];
                    edge.find("title").html(s);
                    click_event(edge);
                }

            }
        }
    };

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
            let _id = $("#cur_digraph").val();
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
            console.log(did);
            if(did){
                init['did'] = did;
            }
            else{
                let navs = $(".left .nav li");
                if(navs.length === 0){
                    alert("请先创建一个流程图");
                    $("#select_digraph").click();
                }
                else{
                    alert("请先选择左侧的流程图");
                }
                return false;
            }
            let _id = $("#cur_node").val();
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
                let status = $this.prop("checked");
                let val = $this.attr("data-id");
                if(status){
                    shape = val;
                    init['shape'] = shape;
                    break;
                }
            }
            if(!shape){
                alert("节点形状必选");
                return false;
            }
            let desc = $.trim($(".node_panel .my_desc").val());
            init['desc'] = desc;
            args['init'] = JSON.stringify(init);
            $.post(u, args, function(resp){
                let json = JSON.parse(resp);
                let mes = json['message'];
                if(mes === "success"){
                    alert("添加成功");
                    draw_svg(json['data']);
                }
                else{
                    alert(mes);
                }
            });
        }
        else if(the_class === 'edge'){
            // 添加弧
            args['class'] = 'edge';
            console.log(did);
            if(did){
                init['did'] = did;
            }
            else{
                let navs = $(".left .nav li");
                if(navs.length === 0){
                    alert("请先创建一个流程图");
                    $("#select_digraph").click();
                }
                else{
                    alert("请先选择左侧的流程图");
                }
                return false;
            }
            let _id = $("#cur_edge").val();
            if(_id !== ""){
                init['_id'] = _id;
            }
            init['label'] = $.trim($(".edge_panel .my_label").val());
            let tail_name = $("#tail_name").val();
            if(!tail_name){
                alert("流向的起点不能为空");
                return false;
            }
            else{
                init['tail_name'] = tail_name;
            }
            let head_name = $("#head_name").val();
            if(!head_name){
                alert("流向的终点不能为空");
                return false;
            }
            else{
                init['head_name'] = head_name;
            }
            init['desc'] = $.trim($(".node_panel .my_desc").val());
            args['init'] = JSON.stringify(init);
            $.post(u, args, function(resp){
                let json = JSON.parse(resp);
                let mes = json['message'];
                if(mes === "success"){
                    alert("添加成功");
                    draw_svg(json['data']);
                }
                else{
                    alert(mes);
                }
            });
        }
        else{}
    });

    // 删除图
    $("#delete_icon").click(function(){
        if(did){
            let r = confirm(`你确实要删除当前的流程图吗?`);
            if(r){
                let init = {"did": did};
                let args = {"class": "digraph", "type": "delete", "init": JSON.stringify(init)};
                $.post("/flow_chart", args, function(resp){
                    let json = JSON.parse(resp);
                    let mes = json['message'];
                    if(mes === "success"){
                        alert("删除成功");
                        let u = "/flow_chart";
                        let did = json['_id'];
                        if(did){
                            u += `?did=${did}`;
                        }
                        location.href = u;
                    }
                    else{
                        alert(mes);
                    }
                });
            }
        }else{}

    });

// end!
});