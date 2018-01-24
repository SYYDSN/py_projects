# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import random
import numpy.linalg as lg


def walk_01():
    steps = 1000
    walk = np.random.randint(0, 2, size=steps)
    walk = np.array(walk)
    max_val = walk.max()
    min_val = walk.min()
    print(min_val, max_val)
    plt.plot(range(len(walk)), walk, "b")
    plt.title("walk_01")
    plt.show()


if __name__ == "__main__":
    walk_01()
