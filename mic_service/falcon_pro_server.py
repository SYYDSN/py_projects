# -*- coding: utf-8 -*-
import falcon
from wsgiref import simple_server


app = falcon.API()


class ThingsResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ("Hello Falcon!")


things = ThingsResource()
app.add_route('/query/', things)


if __name__ == "__main__":
    httpd = simple_server.make_server('127.0.0.1', 9519, app)
    httpd.serve_forever()