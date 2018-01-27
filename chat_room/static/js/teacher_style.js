// JavaScript Document

$(document).ready(function(){


    //--------------大师排行榜/直播室管理/新闻数据tab切换----------------//
    $("#tab_header ul li").click(function(){
        var tablist = $(this).index();
        $(this).addClass("active").siblings().removeClass("active");
        $("#tab_content .list").eq(tablist).addClass("show").siblings().removeClass("show");

        //-------------------新闻数据-------------------//
        //滚动效果：以下插件滚动效果不要放在加载事件中，因为div2默认为none时会取不到隐藏元素的宽度
        $('#demo5').unbind();  //初始化时先解除所有事件
        var liwidth = $(".div2 ul li .master_data").width() + 3; //获取滚动效果每个li的宽度
        $('#demo5').scrollbox({
            direction: 'h',
            distance:liwidth
        });
        $('#demo5-backward').click(function () {
            $('#demo5').trigger('backward');
        });
        $('#demo5-forward').click(function () {
            $('#demo5').trigger('forward');
        });

    });


    //-------------------大师排行榜---------------//
    /*右侧信息houve显示效果*/
    $(".info_marker_icon img").hover(function(){
        $(this).siblings(".info_marker_cont").fadeIn(300);
    },function(){
        $(this).siblings(".info_marker_cont").fadeOut(300);
    });

    //关闭建仓按钮弹出窗
    $(".close").click(function(){
        $(".popcont").hide();
    });

    //交易指令下拉框改变事件
    $(".jyzhiling select").change(function(){
        if($(this).find("option:selected").text() == "挂多" ||  $(this).find("option:selected").text() == "挂空"){
            $(".jiage").hide();
            $(".nowvalue .select_bt").text("挂单价格");
            $(".shurukuang").show();
        }else{
            $(".jiage").show();
            $(".nowvalue .select_bt").text("商品现价");
            $(".shurukuang").hide();
        }
    });

    //点击建仓/平仓/取消按钮弹出窗
    var _jiancang_no;

    $("#ranklist_nr .jiancang").click(function(){
        console.log($(this).text());
        if($(this).text() == "建仓"){
            $(".popcont").show();
            $(".bulidcang").show().siblings().hide();
        }
       else if($(this).text() == "平仓"){
            $(".popcont").show();
            $(".ifping").show().siblings().hide();
        }
       else if($(this).text() == "编辑"){
            //$(".popcont").show();
            //$(".ifguadan").show().siblings().hide();
            $(".popcont").show();
            $(".bulidcang").show().siblings().hide();
        }
        _jiancang_no=$(this).data("no");//获取建仓的序列号
    });

    //点击确定按钮，如果是买入和卖出的话，操作栏变成平仓，如果是挂单的话，草错栏变成取消
    /*
    $(".determine").click(function(){
        $(".popcont").hide();
        if($(".jyzhiling select").find("option:selected").text() == "挂多" ||  $(".jyzhiling select").find("option:selected").text() == "挂空"){
            $("#ranklist_nr .jiancang[data-no='"+_jiancang_no+"']").addClass("pingcang").text("编辑");
            return;

        }
        if($(".jyzhiling select").find("option:selected").text() == "买入" || $(".jyzhiling select").find("option:selected").text() == "卖出") {
            $("#ranklist_nr .jiancang[data-no='"+_jiancang_no+"']").addClass("pingcang").text("平仓");
            return;
        }
    });
    */
    //获取当前时间
    function gettime(){
        var mydate = new Date();
        var str = "" + mydate.getFullYear() + "年" + (mydate.getMonth()+1) + "月" + mydate.getDate() + "日";
        return str;
    }
    function gethour(){
        var mydate = new Date();
        var strh = + mydate.getHours() + ":" + mydate.getMinutes();
        return strh;
    }

    //点击确定平仓弹窗关闭,显示右侧时间信息
    $(".qdping").click(function(){
        $(".popcont").hide();
        $(".jiancang").removeClass("pingcang");
        //$(".jiancang").text("建仓");
        $(".info_marker[data-no='"+_jiancang_no+"']").show().find(".year").html(gettime());
        $(".info_marker[data-no='"+_jiancang_no+"']").show().find(".time").html(gethour());
    });

    //点击确定取消订单弹窗关闭,显示右侧时间信息
    $(".qdquxiao").click(function(){
        $(".popcont").hide();
        $(".jiancang").removeClass("pingcang");
        $(".jiancang").text("建仓");
    });

    //点击暂停转为开启
    /*
    $("#stop").click(function(){
        $(this).hide();//聊天管理按钮隐藏
        $("#upon").show().css({display:"inline-block"});
    });*/
    $("#upon").click(function(){
        $(this).hide();//实时聊天按钮隐藏
        $("#stop").show().css({display:"inline-block"});
    });

    //点击四种模式其中一个的时候，其他的按钮则禁止
    $("#setting_all button.allbut").click(function(){
        $(this).addClass("xuanzhong").siblings(".allbut").addClass("hui").removeClass("allbut");
        $("#setting_all button.hui").click(function(){
            $(this).addClass("xuanzhong").addClass("allbut").removeClass("hui").siblings(".hui").addClass("hui").removeClass("xuanzhong");
        });
    });



    //---------------------直播室管理-------------------//
    //实时聊天切换到聊天管理
    $("#chat_manage").click(function(){
        $(this).hide();//聊天管理按钮隐藏
        $("#chat_realtime").show();//实时聊天按钮出现
        $("#chatnowtime").hide();
        $("#chatmanage").show();
        $(".fobid1").css({display:"inline-block"});//禁止按钮出现
    });
    //聊天管理切换到实时聊天
    $("#chat_realtime").click(function(){
        $(this).hide();//实时聊天按钮隐藏
        $("#chat_manage").show();//聊天管理按钮出现
        $("#chatnowtime").show();
        $("#chatmanage").hide();
        $(".fobid1").css({display:"none"});//禁止按钮隐藏
    });

    //点击禁止图标切换效果
    /*
    $ (".fobid1").click (function (){
        $ (this).toggleClass ("fobid2");
    });
    */
    //直播室管理界面中点击向上箭头展开机器人设置选项
    $("#arrow_up").click(function(){
        $("#setting_robot").slideDown(300);
        $("#arrow_down").click(function(){
            $("#setting_robot").slideUp(300);
        });
    });
    //选中自定义，弹窗输入自定义命名
    $("#bottom_send_cont select").change(function(){
        if($(this).find("option:selected").text() == "自定义") {
            var selfdefind = prompt("输入自定义名称:", "");
            if(selfdefind!=null && selfdefind!=""){
               var opt = "<option selected>" + selfdefind  + "</option>";
            $("#bottom_send_cont select").append(opt);
            }else{}

        }
    });




})


	