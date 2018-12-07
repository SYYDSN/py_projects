
    $.post("/manage/get_employee_archives",function(data){
        var datas = JSON.parse(data).data;
        window.localStorage.setItem('data',data);
        console.log(JSON.parse(data))
        $(".num").text(datas.length)

            for(let i = 0; i<datas.length; i++) {
                var driving_experience = datas[i].driving_experience || "--";
                var scr_synt = datas[i].scr_synt || 0;
                var real_name = datas[i].real_name || data[i].user_name;
                var head_img_url = "/" + datas[i].head_img_url || "../../static/image/head_img/default_01.png";
                var str_html = '<li class="col-md-3 col-sm-6 col-xs-12" id= '+ datas[i]._id +'>'+
                    '<div class="image">'+
                        '<img src= '+ head_img_url +' alt="">'+
                   ' </div>'+
                  '  <div class="info">'+
                       ' <p>'+
                            '<span class="name">'+ real_name  +'</span>'+
                            '<span>驾龄 :  '+ driving_experience +'</span>'+
                        '</p>'+
                        '<p>'+
                           '<i class="iconfont icon-che"></i>'+
                            '<span>安全指数 ：'+ scr_synt +'</span>'+
                        '</p>'+
                        '<p>'+
                            '<i class="iconfont icon-yibiaopan"></i>'+
                            '<span>驾驶总时长：'+ datas[i].driving_hours_sum +'</span>'+
                        '</p>'+
                    '</div>'+
                '</li>';
                $(".driver-list-content ul").append(str_html);
            }

            var capable = Math.ceil(datas.length / 4);
            var hei = $(".driver-list-content ul li").height();
            $(".driver-list-content ul").height(hei * capable);
            function screenName(name){
              let key2 = $.trim($(name).val());
              $(name).val("");
              let lis = $(".driver-list-content ul li");
              if(key2 != ""){
                for(let i=0;i<lis.length;i++){
                  let li = lis[i];
                  let name = $.trim($(li).find(".info .name").text());
                  if(name.indexOf(key2) !== -1){
                    $(li).show();
                    $(li).attr("test","aaa");
                  }else{
                    $(li).removeAttr("test");
                    $(li).hide();
                  }
                }
              }
            }
            $("#btn").click(function(){
              screenName("#inp");
              if($(".driver-list-content ul li[test='aaa']").length == 0){
                  $(".driver-list-content .content").css("display","block");
              }else{
                  $(".driver-list-content .content").css("display","none");
              }
            });
            $("#inp").keyup(function(e){
              if(e.keyCode == 13){
                screenName(this);
                if($(".driver-list-content ul li[test='aaa']").length == 0){
                  $(".driver-list-content .content").css("display","block");
                }else{
                  $(".driver-list-content .content").css("display","none");
                }
              }
            })
            $(".header-left .all").click(function () {
                $(".driver-list-content .content").css("display","none");
                let lis = $(".driver-list-content ul li");
                for(let i = 0; i < lis.length; i++) {
                    $(lis[i]).attr("test","aaa");
                    $(lis[i]).show();
                }
            })

            $(".driver-list-content ul").on('click','li' ,function () {
                var phone_num = $(this).attr("id");
                location.href = location.origin + '/' + location.pathname.split('/')[1] + "/employee_detail?phone_num=" + phone_num;
            })
    })
