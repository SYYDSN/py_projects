# -*- coding: utf-8 -*-
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Activation


model = Sequential([
    Dense(units=32, input_shape=(784, )),
    Activation("relu"),
    Dense(units=10),
    Activation('softmax'),
])


if __name__ == "__main__":

    pass