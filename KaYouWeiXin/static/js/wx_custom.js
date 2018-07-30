function photo_img(){
    wx.chooseImage({
    count: 1, // 默认9
    sizeType: ['original', 'compressed'], // 可以指定是原图还是压缩图，默认二者都有
    sourceType: ['album', 'camera'], // 可以指定来源是相册还是相机，默认二者都有
    success: function (res) {
//                      alert(res.localIds);
    var localIds = res.localIds; // 返回选定照片的本地ID列表，localId可以作为img标签的src属性显示图片
        var $img = this.$('.imgs');
        var $src = $img[0].src;
        $img.attr('src',localIds);
    };
    });
    
    wx.getLocalImgData({
        localId: '', // 图片的localID
        success: function (res) {
            alert(res.localData);
        var localData = res.localData; // localData是图片的base64数据，可以用img标签显示
             alert(localData);
            
        }
       });

}