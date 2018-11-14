$(function(){
    /*填充用户信息到摩态框*/
    var fill_user_info = function(user_id){
        var tr = $("#" + user_id);
        var nick_name = $.trim(tr.find(".nick_name").text());
        var user_name = $.trim(tr.find(".user_name").text());
        $("#user_name").val(user_name);
        $("#nick_name").val(nick_name);
    };

    /*添加用户按钮*/
    $(".pop_modal").each(function(){
        var $this = $(this);
        $this.click(function(){
            var text = $.trim($this.text());
            var title = "添加用户";
            if(text === "编辑"){
                title = "编辑用户";
                var _id = $this.attr("data-id");
                fill_user_info(_id);
            }
            else{
                // nothing...
            }
            $("#modal_title").text(title);
            $(".modal_outer").css("display", "flex");
        });
    });

    /*关闭摩态框按钮*/
    $("#close_medal").click(function(){
        $(".modal_outer").css("display", "none");
    });

});