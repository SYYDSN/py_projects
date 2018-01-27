$(function(){
    // 主区域最小高度
    console.log($(window).height(),$("#main_zone").css("top"));
    $("#main_zone").css("min-height", $(window).height() - $("#main_zone").offset().top);


    // 填充中间的司机列表区域
    let fill_list = function(drivers_list){
        let l = drivers_list.length;
        $("#driver_count").text(l);
        if(l > 0){
            let ul = $(".driver-list-content");
            ul.empty();
            for(let i=0;i<l;i++){
                let driver = drivers_list[i];
                let driving_hours_sum = driver['driving_hours_sum']?driver['driving_hours_sum']:"--";                    // 总驾驶时长,单位小时
                let real_name = driver['real_name']?driver['real_name']:driver['user_name'];                             // 真实姓名
                let head_img_url = driver['head_img_url']?driver['head_img_url']:"static/image/head_img/default_01.png"; // 头像地址
                let drive_age = driver['drive_age']?driver['drive_age']:"--";                                            // 驾龄
                head_img_url = `../${head_img_url}`;
                // head_img_url = "../static/image/head_img/2015111093556890.jpg";
                let str_html = `<div class="item_div_outer col-lg-3 col-md-4 col-sm-6 col-xs-12" id="${driver._id}">
                                    <div class="row item_div">
                                        <div class="col-lg-3 col-md-3 col-sm-3 col-xs-3">
                                            <img onclick="to_driver_detail($(this))" class="img img-circle" src= "${head_img_url}" alt="">
                                        </div>
                                        <div class="col-lg-9 col-md-9 col-sm-9 col-xs-9">
                                        
                                            <div class="row">
                                                <div class="col-lg-6 col-md-6 col-sm-6 col-xs-6">
                                                <span onclick="to_driver_detail($(this))" class="driver_name">${real_name}</span>
                                                </div>
                                                <div class="col-lg-6 col-md-6 col-sm-6 col-xs-6">
                                                    <span style="margin-right:0.3rem" >驾龄: </span><span>${drive_age}</span>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                                                <i style="margin-right:0.5rem" class="iconfont icon-che"></i>
                                                <span style="margin-right:0.3rem" >车辆类型:</span><span>重型厢式货车</span>
                                                </div>
                                            </div>
                                            
                                            <div class="row">
                                                <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                                                <i  style="margin-right:0.5rem" class="fa fa-clock-o"></i>
                                                <span style="margin-right:0.3rem" >驾驶总时长:</span><span>${driving_hours_sum}</span>
                                                </div>
                                            </div>
                                            
                                        </div>
                                    </div>
                                </div>`;
                ul.append(str_html);
            }
        }else{}
    };

    // 启动页面时加载司机档案
    $.post(`${server}/manage/get_employee_archives`, function(json){
        let resp = JSON.parse(json);
        if(resp['message']!=="success"){
            alert(resp['message']);
        }
        else{
            let data = resp['data'];
            console.log(data);
            fill_list(data);  // 填充中间的区域
        }
    });

    // 隐藏给定姓/姓名之外的司机
    let hide_other_drivers = function(the_name){
        let drivers = $(".item_div_outer");
        if(typeof(the_name) === "undefined" || $.trim(the_name) === ""){
            drivers.show();
        }else{
           let re_name = $.trim(the_name);
            let l = drivers.length;
            for(let i=0;i<l;i++){
                let cur = $(drivers[i]);
                let cur_name = $.trim(cur.find(".driver_name").text());
                if(cur_name.indexOf(re_name) === 0){
                   cur.show();
                }
                else{
                    cur.hide();
                }
            }
        }

    };

    // 立即搜索按钮事件
    $("#btn").click(function(){
        let name = $.trim($("#inp").val());
        hide_other_drivers(name);
    });

    // 精确搜索输入框的事件
    let delay_submit = null;
    $("#inp").keyup(function(e){
        clearTimeout(delay_submit);
        let code = e.keyCode;
        if(code === 13){
            let first_name = $.trim($(this).val());
            hide_other_drivers(first_name);
        }else{
            // 清除输入框显示全部司机
            let first_name = $.trim($(this).val());
            if(first_name === ""){
                hide_other_drivers(first_name);
            }else{
                delay_submit = setTimeout(function(){
                    hide_other_drivers(first_name);
                },400);
            }
        }
    });

    // 跳转到司机详情页面
    to_driver_detail = function($obj){
        // $obj就是$(this);
        let user_id = $.trim($obj.parents(".item_div_outer:first").attr("id"));
        let redirect_url = `${server}/manage/driver_detail?user_id=${user_id}`;
        location.href = redirect_url;
    };

// end!
});