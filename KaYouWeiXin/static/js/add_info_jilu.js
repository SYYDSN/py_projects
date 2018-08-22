$(function(){
    $("#time").calendar({
        maxDate:new Date().getFullYear()+"-"+(new Date().getMonth() + 1) + "-" + new Date().getDate()
    });
    //删除按钮 显示隐藏 判断
    let url_head = location.search; //获取url中含"?"符后的字串
    let work_id = url_head.substring(6);
    if( work_id == "" ){
        $(".dele").hide();
    }else{
        $(".submit").hide();
    };

        function img_honor($obj){
        wx.chooseImage({
            count: 1, // 默认9
            sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
            sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
            success: function (res) {
                var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
                $obj.attr('src',localIds);
                $('.modal').modal({backdrop: 'static', keyboard: false});
                wx.uploadImage({
                    localId: localIds[0], // 需要上传的图片的本地ID，由chooseImage接口获得
                    isShowProgressTips: 1, // 默认为1，显示进度提示
                    success: function (res) {
                        // $('.modal').modal({backdrop: 'static', keyboard: false});
                        var serverId = res.serverId; // 返回图片的服务器端ID
                        if($obj.attr('id') == 'image_id'){
                            var table_name = "honor_image";
                        }
                        var  field_name =  "image_id";
                        //上传图片对应的  id信息
                        var args = {
                            "server_id":serverId,
                            "table_name": table_name,
                            "field_name": field_name,
                            "db":"mongo_db2" // 库名，固定
                        };
                        var url = "/wx/auto_download/" + table_name;
                        $.post(url, args,function(resp){
                            let  json = JSON.parse(resp);
                            let status = json['message'];
                            if(status == 'success'){
                                $obj.attr("data-id", json[field_name]);
                                $obj.attr("data-url", json[field_name + "_url"]);
                                setTimeout(function(){
                                    $('.modal').modal('hide');
                                },1000);
                                console.log($obj)
                            }else{
                                $.alert(status);
                            }
                        })
                    }
                });
            }
        });
    };
        $('.iimg').each(function(){
        let $this = $(this);
        $this.click(function(){
        let img = $this.find('.imgs');
        img_honor(img)
    })
    });

        function submit(class_name){
        let doms = $(`.${class_name}`);
        let args = {};
        let is_null = false;
        for(let dom of doms){
        let obj = $(dom);
        let tag_name = obj[0].tagName.toLowerCase();
        let arg_name = obj.attr('id');
        if(tag_name == 'input'){
        let val = $.trim(obj.val());
        if(val){
        args[arg_name] =val;
        is_null = true;
        //  微信时间格式转换
        if( arg_name == 'time'){
        var arg_name_time = val.replace(/\//g ,"-");
        args[arg_name] = arg_name_time; //存入数组替换之前的
    }
    };
    }else {
        if(arg_name == 'image_id'){
        let image_id = obj.attr("data-id");
        if(image_id){
        is_null = true;
        args["image_id"] = image_id;
        args["imge_url"] = obj.attr("data-url");
    }
    }
    }
    };
        return is_null? args:null;
    };
        // 添加信息
        $('#submit').on('touchstart', function(){
        let args = submit("inp_add");
        if(args){
        $('.modal').modal({backdrop: 'static', keyboard: false});
        args['resume_id'] = user.resume_id;
        args['opt'] = "add_honor";
        $.post("/wx/resume/extend", args, function(resp){
        let json = JSON.parse(resp);
        if(json['message'] == 'success'){
        setTimeout(function(){
        $('.modal').modal('hide');
    },3000);
        $.toast("保存成功！");
        $.confirm("本条信息添加完成，是否继续添加？",function(){
        // 继续添加操作
        setTimeout(function(){location.href = '/wx/html/add_info_jilu.html';},1000);
    },function(){
        //取消c操作
        location.href = '/wx/html/resume_detail.html'
    });
    }else{
        $.alert('保存失败');
    }
    })
    }else{
        $.alert('未保存信息！');
    }
    });
        //修改信息
        $('#modify').on('touchstart', function(){
        let args = submit("inp_add");
        if(args){
        $('.modal').modal({backdrop: 'static', keyboard: false});
        let url_head = location.search; //获取url中含"?"符后的字串
        let h_id = url_head.substring(6); //履历id
        args['h_id'] = h_id;
        args['resume_id'] = user.resume_id;
        args['opt'] = "update_honor";
        $.post("/wx/resume/extend", args, function(resp){
        setTimeout(function(){
        $('.modal').modal('hide');
    },3000);
        let json = JSON.parse(resp);
        if(json['message'] == 'success'){
        $.toast("修改成功！");
        setTimeout(function(){location.href = '/wx/html/resume_detail.html';},1000);
    }else{
        $.alert('修改失败');
    }
    })
    }else{
        $.alert('未修改信息');
    }
    });

        $("#delete").on("touchstart",function(){
        $.confirm("您确定删除本条信息？",function(){
            // 删除操作
            let url_head = location.search; //获取url中含"?"符后的字串
            let h_id = url_head.substring(6);
            let args = {};
            // let work_id = $("#work_id").text();
            args['resume_id'] = user.resume_id;
            args['h_id'] = h_id;
            args["opt"] = "delete_honor";
            $.post("/wx/resume/extend", args, function(resp){
                let json = JSON.parse(resp);
                if(json['message'] == 'success'){
                    $.toast("删除成功！");
                    setTimeout(function(){location.href = '/wx/html/resume_detail.html';},1000);
                }else{
                    $.alert('删除失败！');
                }
            })

        },function(){
            //取消c操作
        })
    })

//end !!!
});