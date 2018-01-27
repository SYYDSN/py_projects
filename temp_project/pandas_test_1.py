# -*- coding: utf-8 -*-
from pandas import Series, DataFrame
import pandas as pd
import datetime


s1 = Series(data=[1, 3, 7], index=["name", "key", "prefix"])
s2 = Series(data=[4, 5, 2, 6], index=["name", 'city', "key", "prefix"])
print(s2)
print(s1 + s2)