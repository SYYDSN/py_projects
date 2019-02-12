# rpc文档

这里的视图提供的是rpc文档.主要是为后端提供远程调用参考. 前端的接口文档,请参看views目录下的[api文档](/views/api文档.md)

## 远程调用函数

需要一个客户端支持.点此下载即可[rpc_client.py](/authorization_package/rpc_client.py)

### rpc客户端使用方法

1. 将下载下来的rpc_client.py保存到你的项目中.
2. 修改文件中的server地址为实际的地址.
3. 使用import引入你要使用的函数.
4. call it 即可.

下面举个例子说明

```python3
from rpc_client import RPC


def some_view(request):
    """某视图函数"""
    checked = RPC(request)  # 检查请求的authorization是否合法?
    if checked:
        """authorization合法"""
        user_id = checked['user_id']  # 用户id
        role_id = checked['role_id']  # 角色id
        ....
        response = some_function(*arg, **kwargs)  # 业务逻辑处理
        response = checked.after(response)  # 记录处理结果, after函数会自动处理json数据
        return response
    else:
        """authorization不合法"""
        return checked.to_json()  # 返回错误的提示信息

```

### 类和函数说明

#### RPC 

远程调用的工具类,本身是dict的子类.扩充了方法.

##### RPC.before 

行为:

接受一个request参数.检查参数中的请求头的authorization信息是否合法?是否合法可以直接用if判定.

* 如果authorization信息不合法, 返回一个RPC类的实例. 包含错误的提示信息,直接调用实例的to_json方法转成json格式后返回即可.
* 如果authorization信息合法. 可以把这个RPC的实例当作字典处理,取出user_id和role_id(角色id),然后配合request中的其他参数送入业务逻辑函数进行处理.


##### RPC.after

行为:

本函数用于记录合法请求的结果,接受一个response参数.这个参数一般是业务逻辑的处理结果.可以是dict或者json格式.
函数本身仅仅是记录的功能.

