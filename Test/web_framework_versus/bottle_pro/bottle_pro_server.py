# -*- coding: utf-8 -*-
from bottle import route, run, default_app


app = default_app()


@route('/query/')
def index():
    return "Hello Bottle!"


if __name__ == "__main__":
    """
    Name	Homepage	Description
    cgi	 	Run as CGI script
    flup	flup	Run as FastCGI process
    gae	gae	Helper for Google App Engine deployments
    wsgiref	wsgiref	Single-threaded default server
    cherrypy	cherrypy	Multi-threaded and very stable
    paste	paste	Multi-threaded, stable, tried and tested
    rocket	rocket	Multi-threaded
    waitress	waitress	Multi-threaded, poweres Pyramid
    gunicorn	gunicorn	Pre-forked, partly written in C
    eventlet	eventlet	Asynchronous framework with WSGI support.
    gevent	gevent	Asynchronous (greenlets)
    diesel	diesel	Asynchronous (greenlets)
    fapws3	fapws3	Asynchronous (network side only), written in C
    tornado	tornado	Asynchronous, powers some parts of Facebook
    twisted	twisted	Asynchronous, well tested but… twisted
    meinheld	meinheld	Asynchronous, partly written in C
    bjoern	bjoern	Asynchronous, very fast and written in C
    auto	 	Automatically selects an available server adapter
    以上服务器都可以用于生产环境.
    但是推荐使用uwsgi部署
    """
    run(app=app, host='0.0.0.0', port=8082, server="tornado")