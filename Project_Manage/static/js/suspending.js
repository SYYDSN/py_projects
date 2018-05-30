
var suspending  = $('.gundong .tab tbody .hidden_overflow'); //获取操作的DOM

var Prompt = $("<div id='Prompt'></div>");//添加标签

console.log($(Prompt));

// td的悬浮事件发生时,填充悬浮的信息框
let fill_td = function(data){
        Prompt.empty();
        let html = `<h5>${data['name']}</h5><table class='table' style='width: 220px'>`;
        html += `<tr><td style="width:70px">开始日期:</td><td>${data['begin_date']}</td></tr>`;
        html += `<tr><td style="width:70px">结束日期:</td><td>${data['end_date']}</td></tr>`;
        html += `<tr><td style="width:70px">任务工期:</td><td>${data['date_range']}天</td></tr>`;
        html += `<tr><td style="width:70px">任务归属:</td><td>${data['category_name']}.${data['project_name']}</td></tr>`;
        html += `<tr><td style="width:70px">任务状态:</td><td>${data['status']}</td></tr>`;
        html += `<tr><td style="width:70px">任务说明:</td><td>${data['description']}</td></tr>`;
        html += "</table>";
        Prompt.html(html);
//         console.log(html.height);
};
let htmlheg = $('html').height();
let htmlwih = $('html').width();

console.log(Prompt.height());

Prompt.css({ //css样式
    'position':'absolute',
    'height':'auto',
    'padding': '10'+'px',
    // 'height': '100'+'px',
    'background': '#e9e9e9',
    'borderRadius': '5'+'px',
});


$('body').append(Prompt);//添加到html页面

Prompt.hide();

suspending.hover(function(e){//鼠标悬浮事件
    let mouseheg = e.pageY;
    let mousewih = e.pageX;
//         console.log(e);
    let task = task_dict[$(e.target).attr("data-id")];
//         console.log(task);
    fill_td(task);
    $("#Prompt p").css({
    'paddingBottom':'6px',
    'color':'#454545 ',
    });

$('.chat').css({
    'position':'absolute',
    'width':'30'+'px',
    'height':'30'+'px',
    'background':'#e9e9e9',
    'display':'inline-block',
});

    Prompt.fadeIn();
    let Promptheg = Prompt.height();
    let Promptwih = Prompt.width();

//    一般情况下显示的
    var top = e.pageY+20;
    var left = e.pageX+-120;

//     当底部空间不够   出现上方
    var lefts = e.pageX+ -120;
    var tops = e.pageY+-300;

//     当右侧空间不够  调整位置
    var lefts_wih = e.pageX+-250;
    var tops_wih = e.pageY+20;

    if(htmlheg - mouseheg > Promptheg+ 30){
        if(htmlwih - mousewih > Promptwih+10){
               $('#Prompt').css({
                'top': top + 'px',
                'left': left+ 'px',
                'max-height': '300px'

                });
           }else{
               $('#Prompt').css({
                'top': tops_wih + 'px',
                'left': lefts_wih+ 'px',
                 'max-height': '300px'
                });
           };
       }else{
             $('#Prompt').css({
            'top': tops + 'px',
            'left': lefts+ 'px',
            'max-height': '300px',
//          'max-height': '300px',
            'overflow-y': 'auto'
        });
      }
//    console.log(Prompt);
    console.log(htmlheg-mouseheg >= Promptheg,htmlheg-mouseheg,Promptheg );
});

suspending.mouseleave(function(){
   $('#Prompt').hide();
});
