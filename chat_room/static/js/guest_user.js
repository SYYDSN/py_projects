$(function(){
    guest_id=0;
    //window.sessionStorage.removeItem("session_id");
    //window.localStorage.removeItem("location_id");
    //页面加载时的脚本，获取一个id并传送到。
    url_guest="/guest_message";  //定义url请求
    var session_id=window.sessionStorage.getItem("session_id");
    var location_id=window.localStorage.getItem("location_id");
    var referer=document.referrer;
    //截断referer防止引用过长引发的sql错误，另外，完全referer虽然完全引用页能提供更多的信息。但数据提交量会太大
    if(referer.length!=0){
        referer=referer.split("://")[1].split("?")[0];
    }
    else{}

    page_url=document.location.href;
    //console.log(page_url)
    //page_url=page_url.slice(1,page_url.length-1);  //请求头地址

    //console.log("页面存储的location_id是"+location_id);
    var id=0;
    if(session_id==null && location_id==null)
    {
        //如果两个id都是空的，那就去服务器获取一个id，然后写入到这两个id中。方法在判断后执行。
    }
    else if(session_id==null && location_id!=null)
    {
        //如果本地id存在，会话id不存在，
        id=location_id;
    }
    else if(session_id!=null && location_id==null)
    {
        //如果本地id不存在，会话id存在，
        id=session_id;
    }
    else{
        //如果本地id和会话id都存在，那就以本地id为准，
       id=location_id;
    }
    //console.log("函数获得的id是"+id);
        //发送oepn_page
		var re = /^[0-9]+.?[0-9]*$/;   //判断字符串是否为数字
		if(re.test(id)){
			//nothing
		}
		else{
			id=0;
		}
    $.cookie("guest_id",id);//写入cookie

    //*****************************************自定义jq方法**********************************************************/
    $.fn.extend({
        //定义一个方法。对象在绑定是方法的时候，会触发此事件，将事件的涉及的referer，page_uel，id，以及事件的描述发送到后台。event是相关事件的参数。
        //使用示范如下$("#xyx").click(function(event){$(this).guest_event(event);});
        send_guest_event:function(event){
            var str='';
            //优先取id，因为id可以唯一确定标签，否则就取其他信息
            if($(this).attr("id")!=undefined){
                str="id:"+$(this).attr("id");
            }
            else{
                str="class:"+$(this).attr("class")+" tag_name:"+$(this)[0].tagName+" text:"+$(this).text()+" value:"+$(this).val()+" src:"+$(this).attr("src");
            }
            var event_type=str+";evnet:"+event.type;
			
            $.post(url_guest,{"id":id,"referer":referer,"page_url":page_url,"event_type":event_type},function(){});
        },
        get_guest_event:function(event){
         //返回客户操作时事件的字符串,仅包含事件对象和事件类型。
            var str='';
            //优先取id，然后是class，最后是标签名
            if($(this).attr("id")!=undefined){
                str="id:"+$(this).attr("id");
            }
            else  if($(this).attr("class")!=undefined){
                str="class:"+$(this).attr("class")+" tag_name:"+$(this)[0].tagName;
            }
            else{
                str="tag_name:"+$(this)[0].tagName;
            }
            var event_type=str+";evnet:"+event.type;
            return event_type;
        },
        get_guest_event_all:function(event){
         //返回客户操作的时候的事件字符串，包括引用页，本地页，事件对象和事件类型
            var    str="id:"+$(this).attr("id")+";class:"+$(this).attr("class")+";tag_name:"+$(this)[0].tagName;
            var event_type="referer:"+referer+";local:"+page_url+";"+str+";evnet:"+event.type;
            return event_type;
        }
    });
  /*******************************************************************************************************/
      /********************匿名跟踪事件********************************************/
	  //使用方法：只需要把需要被跟踪的对象加上一个名为track的class即可
    $(".track").click(function(event){
        $(this).send_guest_event(event);
    });
    /****************************************************************/
   /********************自定义jq公用函数***************************************/
   $.extend({
       is_number:function(num){
           //检查是否为纯数字
           var reg = new RegExp("^[0-9]*$");
           if(num.match(reg)){
               return true;
           }else{return false}
       }
   });

 /********************************************************************************/

    //end
});