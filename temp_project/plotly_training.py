# -*- coding: utf-8 -*-
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np


def t_01():
    data_x = np.array([np.random.random() for i in range(1000)])
    data_y = np.sqrt(data_x)
    aes = go.Scatter(x=data_x, y=data_y, mode="markers", marker={
        "showscale": True
    })
    py.plot([aes])


if __name__ == "__main__":
    t_01()
