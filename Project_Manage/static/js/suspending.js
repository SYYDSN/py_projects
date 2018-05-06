
var suspending  = $('.gundong .tab tbody span'); //获取操作的时间DOM

var Prompt = $("<div id='Prompt'></div>").text("提示内容");//添加标签

Prompt.css({ //css样式
	'position':'absolute',
	'width':100+'px',
	'height':'auto',
	'border':1+'px'+ 'solid' +'#00CC66',
});

$('html').append(Prompt);//添加到html页面

Prompt.hide();

//$('#Prompt').hide();

suspending.hover(function(e){//鼠标悬浮事件
	
	Prompt.fadeIn();
	
	var top = e.pageY+5;
	
	var left = e.pageX+20;
	
	$('#Prompt').css({
	    'top': top + 'px',
	    'left': left+ 'px'
	  });
//		console.log(Prompt);
});

suspending.mouseleave(function(){
   $('#Prompt').hide();
});
