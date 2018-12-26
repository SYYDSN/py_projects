# 江西南昌的推送App项目

发送首页的代码

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no" />

<title>通讯录提交</title>
</head>

<body>
2018/12/26 18:38:02
<!--接收通讯录-->
<br><br>当前时间(sj)：<br>111<br><br>通讯录(tongxunlu):<br>222<br><br>坐标X(zuobiaox):<br>333<br><br>坐标Y(zuobiaoy):<br>4444<br><br>参数(canshu):<br>7343844444<br>
<!--接收通讯录结束-->
<br><br><br><br><br>
<!--启用通讯录开始-->
<script language="javascript">
function jsCallNativeUpLoad() {
alert("开始调用通讯录");
      window.injectedObject.upLoadContact();
}
</script>
<br><br>
<input type="button" name="sda" value="调用通讯录"   onclick="jsCallNativeUpLoad()" style="width:100px; height:50px;"/>
<br><br>
<input type="button" name="sda" value="查看视频"   onclick="window.open('http://www.fzgdw.com/html/2018/11-24/n93385440.html');" style="width:100px; height:50px;"/>
<!--启用通讯录结束-->
</body>
</html>
```