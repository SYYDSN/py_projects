# Test项目

此项目为练习之用.所有的东西都不保证是最新的.主要用于:

* 技术验证
* 方案测试
* bug重现

## 几种不同的部署方案的测试结果

第一轮

### 500并发 5000连接

* waitress 200          耗时7.50秒  成功率100%  每秒处理666.67个请求
* waitress 400          耗时4.39秒  成功率100%  每秒处理1138.95个请求
* waitress 600          耗时4.22秒  成功率100%  每秒处理1184.83个请求
* waitress 800          耗时4.95秒  成功率100%  每秒处理1010.10个请求
* bjoern                耗时3.43秒  成功率100%  每秒处理1457.73个请求
* meinheld              耗时3.61秒  成功率100%  每秒处理1385.04个请求
* gevent                耗时3.71秒  成功率100%  每秒处理1344.09个请求
* tornado 4核           耗时3.25秒  成功率100%  每秒处理1538.64个请求
* sanic 4核             耗时3.24秒  成功率100%  每秒处理1543.21个请求
* sanic+gunicorn 4核    耗时2.31秒  成功率100%  每秒处理2164.50个请求
* aio+gunicorn 4核心    耗时1.50秒  成功率100%  每秒处理3333.33个请求
* flask+gunicorn+gevent 9w2t   耗时2.12秒  成功率100%  每秒处理2358.49个请求
* flask+gunicorn+meinheld 4w   耗时2.36秒  成功率100%  每秒处理2118.64个请求
* flask+gunicorn+meinheld 8w   耗时2.34秒  成功率100%  每秒处理2136.75个请求
* flask+uwsgi 9w2t      耗时2.52秒  成功率100%  每秒处理1984.13个请求
* flask+uwsgi 4w2t      耗时2.42秒  成功率100%  每秒处理2066.12个请求

第一轮下来:

* 裸奔的基本都是垫底儿的.
* gunicorn和uwsgi旗鼓相当,gunicorn略占优势
* 目前是aio+gunicorn 4核心有明显的优势.


第二轮

接下来主要比较gunicorn和uwsgi和几种开发框架的搭配,包括aiohttp, sanic, flask

### 1000并发 20000连接

* flask+gunicorn+gevent 8w2t   耗时7.78秒  成功率100%  每秒处理2570.69个请求
* flask+gunicorn+meinheld 8w   耗时6.75秒  成功率100%  每秒处理2962.96个请求
* aio+gunicorn 4核心            耗时7.32秒  成功率100%  每秒处理2732.24个请求
* sanic+gunicorn 4核            耗时9.76秒  成功率100%  每秒处理2049.18个请求
* flask+uwsgi 9w2t             耗时4.84秒  成功率100%  每秒处理4132.23个请求
* flask+uwsgi 4w2t             耗时7.40秒  成功率100%  每秒处理2702.70个请求

最终是flask+uwsgi 9w2t(9进程2线程)拔得头筹