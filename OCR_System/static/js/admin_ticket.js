/**
 * Created by walle on 17-2-8.
 */
$(function(){
    /*根据href确定哪一个导航标签被激活*/
    function action_small_nav(){
        var pathname = location.href;
        var as = $(".small_nav>a");
        var alist = pathname.split("?");
        if(alist.length == 1){
            as.eq(0).addClass("btn-primary").find("span").css("color", "white");
        }
        else{
            var dict = {};
            alist = alist[1].split("&");
            for(var i=0, l=alist.length; i<l;i++){
                var temp = alist[i].split("=");
                if(temp.length == 2){
                    dict[temp[0]] = temp[1];
                }else{}
            }
            var val = dict['zone'];
            if (typeof(val) != 'undefined') {
                as.each(function () {
                    var $this = $(this);
                    if ($this.attr("href").indexOf(val) != -1) {
                        $this.addClass("btn-primary").find("span").css("color", "white");
                    } else {
                    }
                });
            } else {
            }
        }
    }
    action_small_nav();

    // 搜索选择按钮
    $("#select_class a").click(function(){
        $("#current_class").attr("data-name", $(this).attr("data-name"));
        $("#current_class").html($(this).text() + "<span class='caret'></span>");
    });

    // 搜索按钮
    $("#launch_search").click(function(){
        var key_word = $.trim($("#key_word").val());
        key_word = key_word.split(" ")[0]; // 只搜索第一个空格前面的关键词
        var term = $("#current_class").attr("data-name");
        location.href = "manage_tickets?zone=shanghai&term="+term+"&key_word="+key_word;
    });

    // 点击编辑票据基本信息按钮
    edit_ticket = function($obj){
        var file_md5 = $obj.attr("data-id");
        var body = $(".modal-body");
        var md5_str = "<input style='display:none' id='file_md5' type='text' value='"+file_md5+"'>";
        body.append($(md5_str));
        var tds = $("#"+file_md5+">td").not(".owner_id,.file_md5,.file_name,.not");
        console.log(tds);
        $("#pop_modal").click();

        $.each(tds, function(i, n){

            var c_id = $(n).attr("class");
            var c_val = $.trim($(n).text());
            $("#"+c_id).val(c_val);
        });

    };

    // 保存发票信息
    $("#save_ticket").click(function(){
        var items = $(".modal-body input");
        var args = {"the_type": "edit"};
        items.each(function(){
            var $this = $(this);
            console.log($this)
            console.log($this.attr("id"))
            args[$this.attr("id")] = $.trim($this.val());
        });
        $.post("/manage_tickets", args, function(message){
            var message = JSON.parse(message);
            if(message['message'] == "success"){
                alert("编辑成功");
                location.href = location.href;
            }
            else{
                alert(message['message']);
            }
        });
    });





    //end !
});