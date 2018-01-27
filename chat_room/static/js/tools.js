/**
 * Created by Administrator on 2016/4/1.
 */
//一个用于input输入框的回车事件的函数，需要实现的功能如下：
//当本元素处于焦点状态时，如果发生了回车事件，光标会跳到下一个。如果下一个元素是提交按钮，那就触发提交动作。
//三个参数 $obj1,被绑定的元素的jq对象  ，$obj2 下一个元素的jq对象 ，type，是否提交？值为fasle或者true，
function bind_enter_event($obj1,$obj2,type){
    var $obj1=$obj1;
    var $obj2=$obj2;
    var type=type;
    $obj1.keydown(function(e){
        if(e.keyCode==13){
            if(type==false){
                $obj2.trigger("focus");
            }
            else{
                $obj2.trigger("click");
            }

        }else{}
    });
}
//查询ip地址的函数,第一个参数是ip地址，第二个参数是回调函数，用于把IP地址的查询结果赋值给对象
//全局变量ip_query_result用于存放查询结果，以复用结果集。
ip_query_result={};  //全局变量，存放ip地址查询的结果，是ip地址为key，查询结果为value的字典。
jquery_ip=function(ip,func){
    var result_str='';//ip查询结果
    if(typeof(ip_query_result["112.64.1.144"])=="undefined"){
        //如果以前的查询结果中找不到此ip的查询结果
        aurl="http://apis.baidu.com/apistore/iplookupservice/iplookup?ip="+ip;
        $.ajax({
            type:"get",
            url:aurl,
            beforeSend: function(xhr){xhr.setRequestHeader('apikey', '5e9fe5825f7ac9b376d717655543da26');},
            success:function(data){
                var data=JSON.parse(data);
                if(data["retData"]!="无效的IP地址"){
                    //console.log(data);
                    var result=data["retData"];
                    var carrier=result["carrier"];//运营商
                    var province=result["province"];//省份
                    var city=result["city"];//城市
                    var country=result["country"];//国家
                    var district=result["district"];//区
                    result_str="<code style='font-size:0.9em'>运营商:</code><tt>"+(carrier=="None"?"未知":carrier)+"</tt><code  style='font-size:0.9em'> 位置:</code><tt>"+country+(province=="None"?'':province)+(province==city?'':(city=="None"?'':city))+(district=="None"?'':district+"区</tt>");
                    ip_query_result[ip]=result_str;
                    //执行回调函数。
                    func(result_str);
                }else{
                    console.log(data["errMsg"]);
                }
            }
        });
    }
    else{
        result_str=ip_query_result[ip];
        //执行回调函数。
        func(result_str);
    }
}