#  -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from celery_module.my_tasks import *
from celery import group


g1 = group([add.s(x=x, y=x) for x in range(4)])
print(add.delay(3, 3).get(timeout=1))
# g2 = group([add.s(x=x) for x in range(4)])
# print(g2(y=10).get())