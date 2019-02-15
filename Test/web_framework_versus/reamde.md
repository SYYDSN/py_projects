# Python web开发框架性能对比

## 参与性能对比的框架有

* django 8080
* flask  8081
* Bottle 8082  
* Sanic  8083
* AioHttp 8084
* Tornado 8085
* Falcon 8086

## 测试方法

使用siege 以200客户端起步,进行压力测试.

```shell
siege -i -c 200 -t 5s http://127.0.0.1:8086/query/
```

注意，测试机器很弱鸡，不要看绝对的测试指标，只看他们之间的大概位置即可．

先从Falcon开始

###　Falcon

* 200 2765.92 trans/sec
* 400 2648.09 trans/sec
* 600 2473.63 trans/sec
* 800 2208.10 trans/sec
* 1000 2150.66 trans/sec

### Tornado

* 200 1205.73 trans/sec
* 400 1172.93 trans/sec
* 600 1115.94 trans/sec
* 800 1073.15 trans/sec
* 1000  922.44 trans/sec

### AioHttp

* 200 1578.71 trans/sec
* 400 2150.40 trans/sec
* 600 1809.52 trans/sec
* 800 1712.12 trans/sec
* 1000 1688.20 trans/sec

### Sanic

* 200 1774.11 trans/sec
* 400 1642.02 trans/sec
* 600 1623.61 trans/sec
* 800 1679.22 trans/sec
* 1000 1745.89 trans/sec

### Bottle

* 200 2653.27 trans/sec
* 400 2529.59 trans/sec
* 600 2371.08 trans/sec
* 800 2148.65 trans/sec
* 1000  2089.93 trans/sec

### Flask

* 200 1844.97 trans/sec
* 400 1743.01 trans/sec
* 600 1697.30 trans/sec
* 800 1582.79 trans/sec
* 1000 1472.12 trans/sec

### Django

* 200 1400.65 trans/sec
* 400 1378.10 trans/sec
* 600 1293.36 trans/sec
* 800 1283.90 trans/sec
* 1000  1216.56 trans/sec