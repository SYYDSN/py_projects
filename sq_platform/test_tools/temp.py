# -*- coding:utf-8 -*-
import os
import json



def xx():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "json", "user_1_gps.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    print(data)



if __name__ == "__main__":
    xx()





