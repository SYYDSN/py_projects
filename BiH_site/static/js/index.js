
////轮播图
//function LP(){
//    var banner = document.getElementById("banner");
//    var btn2=document.getElementById("btn");
//    btn2.children[0].style.background="#fff";
//    btn2.children[0].style.width="10px";
//    btn2.children[0].style.height="10px";
//    btn2.children[0].style.margin="0";
//
//    function slider(num){
//        for(var x=0;x<btn2.children.length;x++){
//            btn2.children[x].style.background="";
//            btn2.children[x].style.width="";
//            btn2.children[x].style.height="";
//            btn2.children[x].style.margin="1px";
//            banner.children[x].style.zIndex=0;
//            banner.children[x].style.opacity=0;
//        };
//        btn2.children[num].style.background="#fff";
//        btn2.children[num].style.width="10px";
//        btn2.children[num].style.height="10px";
//        btn2.children[num].style.margin="0";
//        banner.children[num].style.zIndex=1;
//        banner.children[num].style.opacity=1;
//    }
//
//    for(var i=0;i<btn2.children.length;i++){
//        btn2.children[i].num=i;
//        btn2.children[i].onclick=function(){
//            slider(this.num);
//            numbers=this.num;
//        }
//    };
//
////加定时器
//    var numbers=0;
//    var T=setInterval(function(){
//        numbers++;
//        if(numbers>=btn2.children.length){
//            numbers=0;
//        }
//        slider(numbers);
//    },4000);
//
////移入轮播停掉定时器
//    var sliders=document.getElementById("br");
//    sliders.onmouseover=function(){
//        //prev.style.display="block";
//        //next.style.display="block";
//        clearInterval(T);
//    };
////移开轮播继续执行
//    sliders.onmouseout=function(){
//        //prev.style.display="none";
//        //next.style.display="none";
//        T=setInterval(function(){
//            numbers++;
//            if(numbers>=btn2.children.length){
//                numbers=0;
//            }
//            slider(numbers);
//        },4000)
//    }
//}
//LP();

//setInterval(function () {
//    var n = ['rgb(235, 214, 214)', 'rgb(233, 233, 200)', 'rgb(201, 201, 235)', 'rgb(194, 229, 194)', 'rgb(207, 205, 205)']
//    $('body').css({
//        background : n[Math.floor(Math.random() * n.length)]
//    });
//}, 2000);


////var colors=["#ff6632","blue","yellow"];
//function set(i)
//{
//    //var c = colors[i];
//    //var col=document.getElementById("colors");
//   // console.log(col);
//    var banner = document.getElementById("banner");
//    var btn=document.getElementById("btn");
//    btn.children[0].style.background="#fff";
//    btn.children[0].style.width="10px";
//    btn.children[0].style.height="10px";
//    btn.children[0].style.margin="0";
//    //col.children[0].style.color=c;
//    //console.log(col[0].style.color);
//    for(var x=0;x<banner.children.length;x++)
//    {
//        if(i == x)
//        {
//            btn.children[x].style.background="#fff";
//            btn.children[x].style.width="10px";
//            btn.children[x].style.height="10px";
//            btn.children[x].style.margin="0";
//            banner.children[x].style.opacity = 1;
//            banner.children[x].style.zIndex = 1;
//            banner.children[x].style.transition = "all 0.5s";
//        }else{
//            banner.children[x].style.opacity = "";
//            banner.children[x].style.zIndex = "";
//            btn.children[x].style.width="";
//            btn.children[x].style.height="";
//            btn.children[x].style.margin="1px";
//            btn.children[x].style.background="";
//
//            //console.log(c)
//        }
//        c=x;
//        console.log(c)
//    }
//}
//set(0);
//var c=0;
//var T=setInterval(function(){
//    c++;
//    //console.log(c);
//    if(c==2){
//        c=0
//    }
//    set(c)
//},3000)



var con=document.getElementsByName("color");

console.log(con);
for(var a=0;a<con.length;a++){
    con[a].love=a;
    con[a].onclick=function(){
        for(var s=0;s<con.length;s++){
            con[s].style.background="";
            con[s].style.color="";
            con2[s].style.background="";
            con2[s].style.color="";
        }
        this.style.background="rgba(255,255,255,0.3)";
        this.style.color="#5808ef";
        con2[this.love].style.background="rgba(255,255,255,0.3)";
        con2[this.love].style.color="#5808ef";

    }
}
var con2=document.getElementsByName("color2");

for(var q=0;q<con2.length;q++){
    con2[q].love2=q;
    con2[q].onclick=function(){
        for(var f=0;f<con2.length;f++){
            con[f].style.background="";
            con[f].style.color="";
            con2[f].style.background="";
            con2[f].style.color="";
        }
        this.style.background="rgba(255,255,255,0.3)";
        this.style.color="#5808ef";
        con[this.love2].style.background="rgba(255,255,255,0.3)";
        con[this.love2].style.color="#5808ef";

    }
}

//切换注册登录
var reg_box=document.getElementById("reg-box1");//获取注册盒子标签
var su_login=document.getElementById("su-login");//获取底部快速登录标签
var reg_box2=document.getElementById("reg-box2");//获取登录盒子标签
var su_login2=document.getElementById("su-login2");//获取底部快速注册标签
var Resgi=document.getElementById("resgi")//获取注册标题标签
var Logi=document.getElementById("logi")//获取登录标题标签
Resgi.style.display="block";//注册标题盒子显示


reg_box.style.display="block";//注册盒子显示
su_login.onclick=function(){//点击底部快速登录标签
    reg_box2.style.display="block";//显示登录盒子内容
    Logi.style.display="block";//显示登录标题文字
    reg_box.style.display="none";//隐藏注册盒子内容
    Resgi.style.display="none";//隐藏注册标题
};

su_login2.onclick=function(){//点击底部快速注册标签
    reg_box2.style.display="none";//登录盒子隐藏
    Logi.style.display="none";//登录标题隐藏
    reg_box.style.display="block";//注册盒子内容显示
    Resgi.style.display="block";//注册标题显示
};


//点击注册显示弹窗

var regis=document.getElementById("res");//获取注册按钮标签
var reg=document.getElementById("reg");//获取注册盒子标签
function Res(){
    reg.style.display="block";//注册登录弹窗显示
    reg_box.style.display="block";//注册盒子内容显示
    reg_box2.style.display="none";//登录盒子内容隐藏
    Resgi.style.display="block";//注册标题显示
    Logi.style.display="none"//登录标题隐藏

}
regis.onclick=Res; //点击注册按钮

var guanbi=document.getElementById("guanbi")//获取关闭登录注册盒子标签
guanbi.onclick=function(){
    reg.style.display="none"//点击关闭按钮  关闭登录注册盒子标签
}


var regis2=document.getElementById("res2");//获取下拉导航注册按钮
function Res2(){
    reg.style.display="block";//注册登录盒子内容显示
    reg_box.style.display="block";//注册内容盒子显示
    reg_box2.style.display="none";//登录内容盒子隐藏
    Resgi.style.display="block";//注册标题显示
    Logi.style.display="none"//登录标题隐藏
}
regis2.onclick=Res2 //点击下拉导航注册按钮标签

var logins=document.getElementById("login");//获取登录按钮
function Log(){
    reg.style.display="block";//注册登录盒子内容显示
    reg_box2.style.display="block";//登录内容显示
    reg_box.style.display="none";//注册内容隐藏
    Logi.style.display="block";//登录标题显示
    Resgi.style.display="none"//注册标题隐藏

}
logins.onclick=Log;//点击下拉导航登录按钮


var logins2=document.getElementById("login2");//获取下拉导航登录按钮

function Log2(){
    reg.style.display="block";//注册登录盒子内容显示
    reg_box2.style.display="block";//登录内容显示
    reg_box.style.display="none"//注册内容隐藏
    Logi.style.display="block";//登录标题显示
    Resgi.style.display="none"//注册标题隐藏

}
logins2.onclick=Log2;//点击下拉导航登录按钮











//联系我们跳转js
var lx=document.getElementById("lx");
lx.onclick=function(){
    location.href="about.html"
};

//点击回到头部
function D(em){
    var x;
    em.onclick=function(){
        x=setInterval(function(){
            if((document.body.scrollTop||document.documentElement.scrollTop)==0){
                clearInterval(x);
            }
            document.documentElement.scrollTop=document.documentElement.scrollTop-document.documentElement.scrollTop/20;
            document.body.scrollTop=document.body.scrollTop-document.body.scrollTop/20;
            console.log( document.body.scrollTop);
        },1);
    }
}
D(document.getElementById("gd-nav-top-hide"));


/*固定导航*/

//下载app
//var gd_nav_sj=document.getElementById("gd-nav-sj");
//var sj_hide=document.getElementById("sj-hide");
//
//gd_nav_sj.onmouseover=function(){
//    sj_hide.style.display="block"
//};
//
//gd_nav_sj.onmouseout=function(){
//    sj_hide.style.display="none"
//};


////小程序
//var gd_nav_wx=document.getElementById("gd-nav-wx");
//var wx_hide=document.getElementById("wx-hide");
//gd_nav_wx.onmouseover=function(){
//    wx_hide.style.display="block"
//};
//
//gd_nav_wx.onmouseout=function(){
//    wx_hide.style.display="none"
//};


//var gd_nav_jd=document.getElementById("gd-nav-jd");
//var jd_hide=document.getElementById("jd-hide");
//
//gd_nav_jd.onmouseover=function(){
//    jd_hide.style.display="block"
//};
//
//gd_nav_jd.onmouseout=function(){
//    jd_hide.style.display="none"
//};


//滚到指定位置出现返回向上按钮
function X(){
    var hd_top=document.getElementById("gd-nav-top-hide");
    var s=false;

    window.addEventListener("scroll",function(){
        if(document.documentElement.scrollTop+document.body.scrollTop>=500){
            hd_top.style.visibility="visible";
            s=true;
        }else{
            if(s){
                hd_top.style.visibility="hidden";
            }
            s=false;
        }
    });

}
X();




//输入框得到焦点事件
var texts=document.getElementById("text");

texts.onfocus=function(){
    texts.style.width="235px"
}
texts.onblur=function(){
    texts.style.width="170px";
}
var texts2=document.getElementById("text2")

texts2.onfocus=function(){
    texts2.style.width="235px";
}
texts2.onblur=function(){
    texts2.style.width="170px";
}



/*图片叠加选项卡*/

var box_left=document.getElementById("tabs-center").children;
var box_right=document.getElementById("title-content").children;
var box_top=document.getElementById("tabs-top").children;
box_right[0].style.display="block";
box_top[0].style.display="block";
box_left[0].style.zIndex=1;
box_left[0].style.top="-20px";
box_left[0].style.left="-10px";

////效果函数
function slider2(num){
    for(var x=0;x<box_left.length;x++){
        box_left[x].style.zIndex=0;
        box_left[x].style.backgroundColor="";
        box_left[x].style.top="0";
        box_left[x].style.left="0";
        box_right[x].style.display="";
        box_top[x].style.display="";
    }

    box_left[num].style.transition=" all 0.5s";
    box_left[num].style.left="-10px";
    box_left[num].style.top="-20px";
    box_left[num].style.backgroundColor="#6e8af5";
    box_left[num].style.zIndex=1;
    box_right[num].style.display="block";
    box_top[num].style.display="block";

}

for(var s=0;s<box_left.length;s++){
    box_left[s].num=s;
    box_left[s].onclick=function(){
        slider2(this.num);
        numbers2=this.num;
    }
};

//加定时器
var numbers2=0;
var Ts=setInterval(function(){
    numbers2++;
    if(numbers2>=box_left.length){
        numbers2=0;
    }
    slider2(numbers2);
},4000);


//移入轮播停掉定时器
var sliders2=document.getElementById("tab-center");
sliders2.onmouseover=function(){
    clearInterval(Ts);
};

//移开轮播继续执行
sliders2.onmouseout=function(){
    Ts=setInterval(function(){
        numbers2++;
      if(numbers2>=box_left.length){
            numbers2=0;
        }
        slider2(numbers2);
    },4000)
};

////左边的按钮
//var prev=document.getElementById("btn-left");
//prev.onclick=function(){
//    numbers2--;
//    if(numbers2<0){
//        numbers2=box_left.length-1;
//    }
//    slider2(numbers2);
//};
//
////右边的按钮
//var next=document.getElementById("btn-right");
//next.onclick=function(){
//    numbers2++;
//    if(numbers2>=box_left.length){
//        numbers2=0;
//    }
//    slider2(numbers2);
//}




/*导航栏滚动条*/

function A(){
    var header=false;
    $(document).ready(function(){
        $(window).scroll(function(){
                if(document.documentElement.scrollTop+document.body.scrollTop>=150){
                    $("#hidden").css({top:0});
                    $("#hidden").css({transition:"all 0.5s ease-out"});
                    header=true
                }else{
                    if(header){
                        $("#hidden").css({top:-80});
                        $("#hidden").css({transition:"all 0.5s ease-out"});
                    }
                    header=false;
                }
            }
        );
    })
}
A();

/*案例展示放大图片*/
/*第一张*/
var visible1=document.getElementById("visible1");//点击显示盒子按钮
var v_hidden=document.getElementById("v_hidden");//显示盒子

function Visible(){
    v_hidden.style.display="block";//显示盒子
}
visible1.onclick=Visible;

var hide=document.getElementById("hide"); //关闭按钮

function Hide(){
    v_hidden.style.display="none"; //隐藏盒子

}
hide.onclick=Hide;

/*第二张*/
var visible2=document.getElementById("visible2");//点击显示盒子按钮
var v_hidden2=document.getElementById("v_hidden2");//显示盒子

function Visible2(){
    v_hidden2.style.display="block";//显示盒子
}
visible2.onclick=Visible2;


var hide2=document.getElementById("hide2"); //关闭按钮

function Hide2(){
    v_hidden2.style.display="none"; //隐藏盒子
}
hide2.onclick=Hide2;


/*第三张*/
var visible3=document.getElementById("visible3");//点击显示盒子按钮
var v_hidden3=document.getElementById("v_hidden3");//显示盒子

function Visible3(){
    v_hidden3.style.display="block";//显示盒子
}
visible3.onclick=Visible3;


var hide3=document.getElementById("hide3"); //关闭按钮

function Hide3(){
    v_hidden3.style.display="none"; //隐藏盒子
}
hide3.onclick=Hide3;


/*第四张*/
var visible4=document.getElementById("visible4");//点击显示盒子按钮
var v_hidden4=document.getElementById("v_hidden4");//显示盒子

function Visible4(){
    v_hidden4.style.display="block";//显示盒子
}
visible4.onclick=Visible4;


var hide4=document.getElementById("hide4"); //关闭按钮

function Hide4(){
    v_hidden4.style.display="none"; //隐藏盒子
}
hide4.onclick=Hide4;




/*第五张*/
var visible5=document.getElementById("visible5");//点击显示盒子按钮
var v_hidden5=document.getElementById("v_hidden5");//显示盒子

function Visible5(){
    v_hidden5.style.display="block";//显示盒子

}
visible5.onclick=Visible5;

var hide5=document.getElementById("hide5"); //关闭按钮

function Hide5(){
    v_hidden5.style.display="none"; //隐藏盒子

}
hide5.onclick=Hide5;

/*第六张*/
var visible6=document.getElementById("visible6");//点击显示盒子按钮
var v_hidden6=document.getElementById("v_hidden6");//显示盒子

function Visible6(){
    v_hidden6.style.display="block";//显示盒子

}
visible6.onclick=Visible6;

var hide6=document.getElementById("hide6"); //关闭按钮

function Hide6(){
    v_hidden6.style.display="none"; //隐藏盒子

}
hide6.onclick=Hide6;

/*第七张*/
var visible7=document.getElementById("visible7");//点击显示盒子按钮
var v_hidden7=document.getElementById("v_hidden7");//显示盒子

function Visible7(){
    v_hidden7.style.display="block";//显示盒子

}
visible7.onclick=Visible7;

var hide7=document.getElementById("hide7"); //关闭按钮

function Hide7(){
    v_hidden7.style.display="none"; //隐藏盒子

}
hide7.onclick=Hide7;



/*第八张*/
var visible8=document.getElementById("visible8");//点击显示盒子按钮
var v_hidden8=document.getElementById("v_hidden8");//显示盒子

function Visible8(){
    v_hidden8.style.display="block";//显示盒子

}
visible8.onclick=Visible8;

var hide8=document.getElementById("hide8"); //关闭按钮

function Hide8(){
    v_hidden8.style.display="none"; //隐藏盒子

}
hide8.onclick=Hide8;



















var aImages = document.getElementById("img").getElementsByTagName('img'); //获取id为img的文档内所有的图片
var aImages2 = document.getElementById("img2").getElementsByTagName('img'); //获取id为img的文档内所有的图片
var aImages3 = document.getElementById("img3").getElementsByTagName('img'); //获取id为img的文档内所有的图片
var aImages4 = document.getElementById("tabs-center").getElementsByTagName('img'); //获取id为img的文档内所有的图片
loadImg(aImages);
loadImg(aImages2);
loadImg(aImages3);
loadImg(aImages4);
window.onscroll = function() { //滚动条滚动触发
    loadImg(aImages);
    loadImg(aImages2);
    loadImg(aImages3);
    loadImg(aImages4);
};
//getBoundingClientRect 是图片懒加载的核心
function loadImg(arr) {
    for(var i = 0, len = arr.length; i < len; i++) {
        if(arr[i].getBoundingClientRect().top < document.documentElement.clientHeight && !arr[i].isLoad) {
            arr[i].isLoad = true; //图片显示标志位
            //arr[i].style.cssText = "opacity: 0;";
            (function(i) {
                setTimeout(function() {
                    if(arr[i].dataset) { //兼容不支持data的浏览器
                        aftLoadImg(arr[i], arr[i].dataset.imgurl);
                    } else {
                        aftLoadImg(arr[i], arr[i].getAttribute("data-imgurl"));
                    }
                    arr[i].style.cssText = "transition: 1s; opacity: 1;" //相当于fadein
                }, 300)
            })(i);
        }
    }
}

function aftLoadImg(obj, url) {
    var oImg = new Image();
    oImg.onload = function() {
        obj.src = oImg.src; //下载完成后将该图片赋给目标obj目标对象
    }
    oImg.src = url; //oImg对象先下载该图像
}

var validate_phone = function (phone) {
    /*
    * 检查手机号码是否合法?合法返回真,
    * */
    var myreg = /^(((1[3-9][0-9]{1})|(15[0-9]{1})|(18[0-9]{1}))+\d{8})$/;
    if (myreg.test(phone)) {
        return true;
    }
    else {
        return false;
    }
};



$("#v_container").click(function(){
    // 注册框点击发送短信按钮事件.
    var phone = $.trim($("#iphone").val());
    if(validate_phone(phone)){
        var url = "http://www.bhxxjs.cn/sms/get";
        var args = {"phone": phone, "csrf_token": $("#csrf_token").val()};
        $.post(url, args, function(resp){
            var resp = JSON.parse(resp);
            var status = resp['message'];
            if(status === "success"){
                alert("短信已发送,请注意查收.");
                return  true;

            }
            else{
                alert(status);
                return false;
            }
        });

        var clock = '';
        var nums = 60;
        var col="#bbb";
        var v_container=document.getElementById("v_container");

        function sendCode()
        {
           v_container.disabled = true; //将按钮置为不可点击
           v_container.style.background= col; //将按钮置为不可点击
           v_container.value = nums+'秒后可重新获取';
            clock = setInterval(doLoop, 1000); //一秒执行一次
        }
        function doLoop()
        {
            nums--;
            if(nums > 0){
                v_container.value = nums+'秒后可重新获取';
            }else{
                clearInterval(clock); //清除js定时器
                v_container.disabled = false;
                v_container.style.background=""
                v_container.value = '点击发送验证码';
                nums = 60; //重置时间
            }
        }
        sendCode()




    }
    else{
        var str = `手机号码不正确!`;
        alert(str);
        return false;
    }
});

$("#su_mit").click(function(){
    /*提交注册信息的函数*/
    var phone = $.trim($("#iphone").val());
    var password = $.trim($("#password").val());
    var password2 = $.trim($("#password2").val());
    var code = $.trim($("#code_input").val());
    if(phone === ""){
        alert("手机号码必须");
        return false;
    }
    else if(!validate_phone(phone)){
        alert("手机号码不正确");
        return false;
    }
    else if(password === "" || password !== password2){
        alert("密码不能为空且两次输入的密码必须一致");
        return false;
    }
    else if(code === ""){
        alert("短信验证码不能为空");
        return false;
    }
    else if(code.length !== 4){
        alert("短信验证码是4位数字");
        return false;
    }
    else{
        password = $.md5(password);
        var args = {
            "phone": phone,
            "password": password,
            "code": code,
            "csrf_token": $("#csrf_token").val()
        };
        var url = "/register";
        $.post(url, args, function(resp){
            var json = JSON.parse(resp);
            var status = json['message'];
            if(status === "success"){
                alert("注册成功!");
                location.reload();
            }
            else{
                alert(status);
                return false;
            }
        });
    }
});


$("#su_mit2").click(function(){
    var phone = $.trim($("#iphone2").val());
    var password = $.trim($("#password3").val());
    if(phone === "" || password === ""){
        alert("账户和密码不能为空!");
        return false;
    }
    else{
        var url = "/login";
        var args = {
            "phone": phone,
            "password": $.md5(password),
            "csrf_token": $("#csrf_token").val()
        };
        $.post(url, args, function(resp){
            var json = JSON.parse(resp);
            var status = json['message'];
            if(status === "success"){
                console.log("登录成功");
                /*执行登录成功后的函数*/
            }
            else{
                alert(status);
                return false;
            }
        });
    }
});

/*/!*轮播*!/
var arrimg = ['img/9.JPG', 'img/2.jpg', 'img/3.jpg', 'img/4.JPG', 'img/5.JPG', 'img/6.jpg']

var arrcolor = ['#8cddfa', '#7da6c6', '#394052', '#6288b5', '#4f8da4','#a87a7a']
var num = 0;

function change() {
    num += 1;
    if (num >= arrimg.length) {
        num = 0;
    }
    $(".img").css("background-image", "url(" + arrimg[num] + ")");
    $(".content").css("background", arrcolor[num]);
    $(".img").css("background-size", "100% 100%");
}
timer = setInterval(
    function () {
        change()
    }, 2000);

$(".set").mouseover(function () {
    clearInterval(timer)

    $('.prev').css("display", "block")
    $('.next').css("display", "block")
})

$(".set").mouseleave(function () {
    $('.prev').css("display", "none")
    $('.next').css("display", "none")
    timer = setInterval(
        function () {
            change()
        }, 2000);
})

$('.prev').click(function () {
    num--;
    if (num<0) {
        num = arrimg.length - 1
    }
    $(".img").css("background-image", "url(" + arrimg[num] + ")");
    $(".content").css("background", arrcolor[num]);
    $(".img").css("background-size", "100% 100%");
})

$('.next').click(function () {
    change()
})*/


/*//底部轮播图
var bottom_banner_lp=document.getElementById("bottom_banner_lp")
function F(num){
    bottom_banner_lp.style.marginLeft=-num*(bottom_banner_lp.clientWidth/16)+"px";
    //console.log(num)
    LP=num
}

// 定时器
var LP=0;
var TD=setInterval(function(){
    LP++;
    //console.log(LP)
    //console.log(bottom_banner_lp.offsetLeft);
    if(LP==11){
        LP=0;
    }
    F(LP);
},2000);

//移入图片暂停定时器
var bottom_banner_content=document.getElementById("bottom_banner_content");
bottom_banner_content.onmouseover=function(){
    clearInterval(TD);
};

// 移出图片开始定时器
bottom_banner_content.onmouseout=function(){
    TD=setInterval(function(){
        LP++;
        if(LP==11){
            LP=0;
        }
        F(LP);
    },2000);
};

//点击向左
var btn_left=document.getElementById("btn-left");
btn_left.onclick=function(){
    LP--;
    if(LP<0){
        LP=10
    }
    F(LP);
};

//点击向右
var btn_right=document.getElementById("btn-right");
btn_right.onclick=function(){
    LP++;
    if(LP==11){
        LP=0;
    }
    F(LP);
};*/