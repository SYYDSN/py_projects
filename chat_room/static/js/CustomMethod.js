

//自定义一个类，用于写公共方法
var objMethod = new Object();

//自定义一个类，用于写公共验证方法
var objValidate = new Object();


/*******************************公共验证**********************************************/

//手机号码验证
//返回true or false
function ValidateTEL(TEL) {
    TEL = TEL.NoSpace().trim();
    var reg = /^0?1[3|4|5|6|7|8|9][0-9]\d{8}$/;
    if (reg.test(TEL)) {
        return true;
    } else {
        return false;
    };
}


//用户名验证，只可以用字母数字下划线做用户名，必须是字母开头，5-20字
function ValiUser(Name) {
    var patrn = /^[a-zA-Z]{1}([a-zA-Z0-9]|[._]){4,19}$/;
    if (!patrn.exec(Name)) return false
    return true
}

//用户名验证，只可以用字母数字下划线做用户名，必须是字母开头，5-20字
objValidate.ValiUser = function (Name) {

    return ValiUser(Name);
}

//手机号码验证
//返回true or false
objValidate.ValidateTEL = function (TEL) {

    return ValidateTEL(TEL);
}
//非空验证，“”，null，undefined
//null返回false
objValidate.NotNull = function (val) {

    if (typeof (intval) == typeof (undefined) || val == "" || val == '' || typeof (val) == null || typeof (val) == undefined) {
        return false;
    }
    return true;
}

//字符非空验证，"",''
//null返回false
objValidate.StrNotNull = function (val) {

    if (val == "" || val == '') {
        return false;
    }
    return true;
}

/*******************************公共方法**********************************************/


//保留小数位，intval值，num位数从1开始是一位
function ReservedDecimal(intval, num) {

    intval = intval.toString();
    num = parseInt(num);
    var str = intval;
    if (intval.indexOf(".") != -1) {
        str = intval.substring(0, intval.indexOf(".") + 1 + num);
    }
    return str.toString();
}


//截取字符,val字符值，num截取数，char标志符
function Intercept(val, num, char) {

    val = val.toString();
    num = parseInt(num);
    var str = val;
    if (val.indexOf("" + char + "") != -1) {
        str = val.substring(0, val.indexOf("" + char + "") + 1 + num);
    }
    return str.toString();
}


//获取验证码倒计时
var countdown = 120;
function settime(obj) {
    if (countdown == 0) {
        obj.removeAttribute("disabled");
        obj.value = "获取验证码";
        countdown = 120;

        $(".banner-member-content div .security-code .huoqu").css("background", "#fb8c00");
        $(".pop-up-box-box1 .border-none input:nth-child(2)").css("background", "#fb8c00");
        return;
    } else {
        obj.setAttribute("disabled", true);
        obj.value = "重新发送(" + countdown + ")";
        countdown--;
        $(".banner-member-content div .security-code .huoqu").css("background", "#b2b2b2");
        $(".pop-up-box-box1 .border-none input:nth-child(2)").css("background", "#b2b2b2");
    }
    setTimeout(function () {
        settime(obj)
    }
      , 1000)
}



//添加用户浏览记录，至少在此页面停留2分钟开始记录
function AddBrowseRecord(_PageUrl, _PageName) {
    console.log("开始执行添加");
    $.post("../HandlerAjax/UserBrowse.ashx", { go: "AddBrowseRecord", PageUrl: _PageUrl, PageName: _PageName }, function (data) {
        if (data == "true") {
            //30秒后执行修改时间操作
            setTimeout(function () { UpdateBrowseRecord(); }, 30000);
        }
    });
}


//修改用户浏览记录，至少在此页面停留30秒开始修改
function UpdateBrowseRecord() {
    console.log("开始执行修改");
    $.post("../HandlerAjax/UserBrowse.ashx", { go: "UpdateBrowseRecord" }, function (data) {
        if (data == "true") {
            setTimeout(function () { UpdateBrowseRecord(); }, 30000);
        }
    });
}



//获取Url参数值，name参数名。
function GetQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
}

//去除中间空格
String.prototype.NoSpace = function () {
    return this.replace(/\s+/g, "");
    //例子str.NoSpace()
}

//去除前后空格
String.prototype.trim = function () {
    return this.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

//生成随机数
//minNum开始数
//maxNum结束数
function randomNum(minNum, maxNum) {
    switch (arguments.length) {
        case 1:
            return parseInt(Math.random() * minNum + 1);
            break;
        case 2:
            return parseInt(Math.random() * (maxNum - minNum + 1) + minNum);
            break;
        default:
            return 0;
            break;
    }
}


/****************************************************************************/


//保留小数位，intval值，num位数从1开始是一位
objMethod.ReservedDecimal = function (intval, num) {

    return ReservedDecimal(intval, num);

}

//截取字符,val字符值，num截取数，char标志符
objMethod.Intercept = function (val, num, char) {

    return Intercept(val, num, char);
}

//获取Url参数值，name参数名。
objMethod.GetQueryString = function (name) {
    return GetQueryString(name);
}

//去除字符串中间空格
//val要去除空格的字符串
objMethod.NoSpace = function (val) {
    return val.replace(/\s+/g, "");
}

//生成随机数
//minNum开始数
//maxNum结束数
objMethod.randomNum = function (minNum, maxNum) {
    return randomNum(minNum, maxNum);
}

//获取数组最大值
//空数组返回0
objMethod.Max = function (shuzu) {
    if (objValidate.NotNull(shuzu)) {
        return Math.max.apply(Math, shuzu);
    }
    return 0;
};

//获取数组最小值
//空数组返回0
objMethod.Min = function (shuzu) {
    if (objValidate.NotNull(shuzu)) {

        return Math.min.apply(Math, shuzu);
    }
    return 0;
};

//时间转换字符
//datetime要转换的时间字符串
//separate 分隔符2009-06-12或2009/06/12 （"/","-"）
//length长度2009-06-12(10)或2009-06-12 17:18(15)或2009-06-12 17:18:05(18)
//空时间返回0000/00/00
objMethod.dateToStr = function (datetime, separate, length) {
    if (datetime == "" || datetime == null) {
        return "0000/00/00";
    }
    var datetime = new Date(datetime);
    var year = datetime.getFullYear();
    var month = datetime.getMonth() + 1;//js从0开始取 
    var date = datetime.getDate();
    var hour = datetime.getHours();
    var minutes = datetime.getMinutes();
    var second = datetime.getSeconds();

    if (month < 10) {
        month = "0" + month;
    }
    if (date < 10) {
        date = "0" + date;
    }
    if (hour < 10) {
        hour = "0" + hour;
    }
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (second < 10) {
        second = "0" + second;
    }
    var time = year + "-" + month + "-" + date + " " + hour + ":" + minutes + ":" + second;

    if (length == 10) {

        time = year + separate + month + separate + date;
    }
    if (length == 15) {

        time = year + separate + month + separate + date + " " + hour + ":" + minutes;
    }
    if (length == 18) {

        time = year + separate + month + separate + date + " " + hour + ":" + minutes + ":" + second;
    }

    //2009-06-12 17:18:05
    return time;
}


//时间转换短格式（10/26 21:29）
//datetime要转换的时间字符串
//separate 分隔符2009-06-12或2009/06/12 （"/","-"）
objMethod.dateToStrShort = function (datetime, separate) {
    if (datetime == "" || datetime == null) {
        return "0000/00/00";
    }
    var datetime = new Date(datetime);
    var year = datetime.getFullYear();
    var month = datetime.getMonth() + 1;//js从0开始取 
    var date = datetime.getDate();
    var hour = datetime.getHours();
    var minutes = datetime.getMinutes();
    var second = datetime.getSeconds();

    if (month < 10) {
        month = "0" + month;
    }
    if (date < 10) {
        date = "0" + date;
    }
    if (hour < 10) {
        hour = "0" + hour;
    }
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (second < 10) {
        second = "0" + second;
    }
    var time = year + "-" + month + "-" + date + " " + hour + ":" + minutes + ":" + second;

    time = month + separate + date + " " + hour + ":" + minutes;

    //
    return time;
}