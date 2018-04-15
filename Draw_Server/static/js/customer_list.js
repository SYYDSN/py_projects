// 删除mongodb中的手机号码
const delete_phone = function (_id, phone){
    let flag = confirm("你确实要删除 " + phone + " 这个号码吗?");
    if(flag){
        let args = {"type": "delete", "_id": _id};
        $.post("customer_list", args, function(resp){
            let json = JSON.parse(resp);
            if(json['message'] === "success"){
                alert("删除成功!");
                location.reload();
            }
            else{
                alert(json['message']);
            }
        });
    }
    else{
        return false;
    }
};
