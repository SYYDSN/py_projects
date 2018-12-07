/*
* 基础的jquery脚本，为基础模板使用，通用性较强
* */
$(function(){
    // 修正个人中心按钮弹出时在右侧边栏之下的问题,弹出个人面板就要收回侧边栏
    $("#pop_personal_center").click(function(){

    });
// end!

    var lis = $(".sidebar-menu li");
    for(let i = 0; i < lis.length; i++){
        $(lis[i]).attr('class','');
        if($(lis[i]).children("a").attr("href") == location.pathname.split("/")[2]){
            $(lis[i]).attr("class",'active');
        }
    }
});