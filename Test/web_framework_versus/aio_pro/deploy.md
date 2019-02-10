# 部署文档

aio 最佳部署需要gunicorn, 而在ubuntu下面,后者需要virtualenv支持.
需要先进入virtualenv 安装gunicorn,然后在虚拟环境下,运行:

```shell
# 进入虚拟环境
source /home/walle/work/my_env/bin/activate
# 然后运行
gunicorn aio_pro_server:my_web_app --bind 0.0.0.0:8084 --workers 7 --worker-class aiohttp.GunicornWebWorker
# 或者(UVLoop,本例没有成功)
gunicorn aio_pro_server:my_web_app --bind 0.0.0.0:8084 --workers 7 --worker-class aiohttp.GunicornUVLoopWebWorkerworker
```