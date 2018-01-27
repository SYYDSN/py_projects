$(function(){
    // 打开页面的时候检测url,并改变导航按钮的active状态
    (function action_nav(){
        let cur_path_list = location.pathname.split("/manage/");
        let l = cur_path_list.length;
        let path = cur_path_list[l - 1];
        let lis = $("#left_main_nav ul li");
        let len = lis.length;
        for(let i=0;i<len;i++){
            let temp = $(lis[i]);
            let cur_path = temp.find("a").attr("href");
            // console.log(cur_path, path);
            if(cur_path === path){
                console.log("find_nav");
                temp.addClass("active");
            }
            else{
                temp.removeClass("active");
            }
        }
    })();

    // 注销按钮弹窗事件
    $("#logout_btn").click(function(){
        $("#logout_trigger").click();
    });

    // 注销事件
    $("#logout_modal .logout").click(function(){
        location.href = "/manage/logout";
    });

    // 弹出提醒消息
    pop_tip_div = function(ms){
        $(".cue_info>p").text(ms);
        $(".cue_info").animate({"opacity": 1},400);
        setTimeout(function(){$(".cue_info").animate({"opacity": 0},300);}, 2600);
    };

    // 弹出提醒消息增强版
    pop_tip_div_plus = function(type, html){
        if(type === "show"){
           $(".cue_info>p").html(html);
        $(".cue_info").animate({"opacity": 1},300);
        }
        else{
            $(".cue_info").animate({"opacity": 0},200);
        }
    };

// end!
});
