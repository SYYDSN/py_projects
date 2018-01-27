# 　-*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np


x_data = np.float32(np.random.rand(2, 100))
y_data = np.dot([0.100, 0.200], x_data) + 0.300

# 线性模型
b = tf.Variable(tf.zeros([1]))
w = tf.Variable(tf.random_uniform([1, 2], -1.0, 1.0))
y = tf.matmul(w, x_data) + b

# 最小方差
loss = tf.reduce_mean(tf.square(y - y_data))
optimizer = tf.train.GradientDescentOptimizer(0.05)
train = optimizer.minimize(loss)

# 初始化变量
init = tf.global_variables_initializer()

ses = tf.Session()
ses.run(init)

# 拟合平面
for step in range(0, 201):
    ses.run(train)
    if step % 20 == 0:
        print(step, ses.run(w), ses.run(b))
