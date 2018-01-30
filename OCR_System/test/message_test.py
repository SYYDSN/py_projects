# -*- coding:utf-8 -*-
import sys
sys.path.append("..")
from message_module import message_listen


inner_author = "a38dfe37a4964e8890a86806d37a3f68"  # 内部通讯用author


def test_message_listen():
    args = {"author": inner_author, "the_type": "ocr_finish"}
    for x in range(100, 300):
        args['image_sn'] = x
        message_listen(**args)


test_message_listen()