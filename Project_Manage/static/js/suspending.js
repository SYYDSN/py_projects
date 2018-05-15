
var suspending  = $('.gundong .tab tbody .hidden_overflow'); //获取操作的时间DOM

var Prompt = $("<div id='Prompt'></div>");//添加标签
console.log($(Prompt));

$(Prompt).append('<p>!项目提示</p>');
$(Prompt).append('<p>后台保驾犬安全平台项目,生成顺丰测试人员报告excel 推进中</p>');
$(Prompt).append('<p>注意事项</p>');
$(Prompt).append("<span class='chat'></span>");

// td的悬浮事件发生时,填充悬浮的信息框
let fill_td = function(data){
	Prompt.empty();
	let html = "<table class='table' style='width: 360px'>";
    // for(let name in data){
	 //    html += `<p>${name}: ${data[name]}</p>`;
    // }
    // Prompt.html(html);
    for(let name in data){
	    html += `<tr><td style="width:120px">${name}</td><td>${data[name]}</td></tr>`;
    }
    html += "</table>";
    Prompt.html(html);
};




console.log($("#Prompt"));
Prompt.css({ //css样式
	'position':'absolute',
	'height':'auto',
    'padding': '10'+'px',
    // 'height': '100'+'px',
    'background': '#e9e9e9',
    'borderRadius': '5'+'px',
});


$('html').append(Prompt);//添加到html页面

Prompt.hide();

suspending.mouseover(function(e){//鼠标悬浮事件
        console.log(e);
        let task = task_dict[$(e.target).attr("data-id")];
        console.log(task);
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

	var top = e.pageY+20;

	var left = e.pageX+-180;

	$('#Prompt').css({
	    'top': top + 'px',
	    'left': left+ 'px'
	  });
//		console.log(Prompt);
});

suspending.mouseleave(function(){
   $('#Prompt').hide();
});
