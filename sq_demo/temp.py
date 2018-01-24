# -*- coding: utf-8 -*-

import threading
import time

a = [1, 2, 3]
count_dict = {"t_1": 0, "t_2": 0}
def xx(name):
    global a
    if name == "t_1":
        time.sleep(1)
        print("sleep! {}'s list: {}".format(name, a))
    else:
        print("{}'s list: {}".format(name,a))
    a.append(a[-1] + 1)
    count_dict[name] = count_dict[name] + 1

def x(name):
    while count_dict[name] < 5:
        xx(name)


if __name__ == "__main__":
    for i in range(2):
        t = threading.Thread(target=x, args=("t_{}".format(i + 1),), daemon=False)
        t.start()




