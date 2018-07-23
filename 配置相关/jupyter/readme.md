supervisor下面运行jupyter
注意配置文件的密码,当前密码是 Suqin@123456

下面是详细的说明


### jupyter服务器搭建

1. 安装    pip3 install jupyter
2. 生成配置文件  jupyter notebook --generate-config
会在 /root/.jupyter/jupyter_notebook_config.py 生成一个默认的配置文件
拷贝一份到当前目录 /root/.jupyter/jupyter_notebook_config.py .           (不要忘记最后那个点)
3. 生成密码
在ipython使用ipyhon的内置命令生产密码
In [1]: from notebook.auth import passwd
In [2]: passwd()
Enter password:
Verify password:
Out[2]: 'sha1:67c9e60bb8b6:9ffede0825894254b2e042ea597d771089e11aed'
4. 编辑 配置此文件.
修改 # c.NotebookApp.password_required = False
为    c.NotebookApp.password_required = True
这个意思是密码必须.
修改 # c.NotebookApp.password = ''
为 c.NotebookApp.password =  'sha1:67c9e60bb8b6:9ffede0825894254b2e042ea597d771089e11aed'
这一步的操作是配置密码.
然后保存退出.
5. 运行
jupyter notebook --ip=0.0.0.0 --port 8998 --config=jupyter_notebook_config.py --allow-root

--ip=0.0.0.0  开启远程访问,默认只允许本机访问
--port 8998  设置访问端口
--config=jupyter_notebook_config.py  使用配置文件
--allow-root   jupyter 默认是不允许管理员身份运行,加上这一项就好了.

附送一个supervisor的配置文件
```
[program: jupyter]

command = /usr/local/bin/jupyter notebook --ip=0.0.0.0 --port 8998 --config=/home/web/jupyter_notebook_config.py --allow-root ;

directory = /home/web/                                  ; 运行的脚本的目录

autostart = true                                      ;  随supervisor自动启动

autorestart = unexpected                              ; 出错重启

startsecs = 3                         ; 启动后3秒不报错就认为程序启动成功

startretries = 3                      ; 程序失败的重试次数                           

```
