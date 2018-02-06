# -*-coding:utf-8-*-
from f_server import app, port
import bjoern


bjoern.run(app, '0.0.0.0', port)