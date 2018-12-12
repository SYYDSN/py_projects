# celery 使用说明

## 相关资料

* [Celery用户指南](http://docs.celeryproject.org/en/latest/userguide/index.html)
* [Flower(Celery的监控工具)](https://flower.readthedocs.io/en/latest/)

## 运行celery 的方法.

### 最基本的方法

```shell
 celery -A my_celery worker -l info
```

### 使用后台启动

使用celery multi命令在后台启动一个或多个worker

```shell
celery multi start w1 -A my_celery -l info
```

重启

```shell
celery  multi restart w1 -A my_celery -l info
```

停止(默认是异步的)

```shell
celery multi stop w1 -A my_celery -l info
```

同步停止

```shell
celery multi stopwait w1 -A my_celery -l info
```

注意celery multi会产生pid和日志文件,最好指定文件的保存目录,因为默认会在你运行的当前目录下产生这些文件

```shell
$ celery multi start w1 -A proj -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
```

## 调用命令

### 基本的调用

```python3
from my_tasks import func
r = func.apply_async((2, 2), queue="queue_name", countdown=10)
print(r.get(timeout=11))
"""
apply_async 是异步执行.
(2, 2) 是传递的参数.
queue 是标识要发送到哪个队列
countdown 是延时, 命令不会在早于这个事件执行
r.get  是获取返回值的方法之一.
"""
```

### 返回结果的说明 class celery.result.AsyncResult

* result.get()默认情况下会传播任何错误.
* result.forget()用来忘记任务(移除结果集)
* res.state查看任务状态
* res.failed()和res.successful()返回布尔值,用于检查任务是否正确的执行.

### celery的签名

签名用于传递一个函数. 签名的使用方法和异步调用方法使用起来很像

```python3
signature = func.signature((2, 2), countdown=10)
```

签名还有个快捷方式s.是signature方法的缩写.所以上面的代码也能写成

```python3
signature = func.s((2, 2), countdown=10)
signature.delay()
```

签名实例还支持调用API：意味着它们具有delay和apply_async方法。但是区别在于签名可能已经指定了参数签名.
不过,如果你没有指定全部的参数的话,你将来还是有机会补全参数的.

```python3
signature = func.s((2, 2), countdown=10)
signature.delay((3, 4))
```

### group,Chains和Chords

#### group

用于把多个任务的返回值作为一组统一操作.或者至取这一组中的某一个返回值进行操作.

```python
def add(x, y):
    return x + y
```

```python3
from celery import group
from proj.tasks import add

group(add.s(i, i) for i in xrange(10))().get()
>>> [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

也可以之传部分 参数. 统一匹配上另一个参数

```python3
group(add.s(i) for i in xrange(10))().get()   # add有3个参数,目前只传递了一个
g(10).get()                                   # 把10作为第二个参数传入
>>> [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
```




