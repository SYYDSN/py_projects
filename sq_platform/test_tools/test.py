import datetime
import random
from uuid import uuid4


d1 = {"key": "value"}
d11 = {"value": "key"}
d2 = {}
d22 = {}
for x in range(10 * 10):
    key = uuid4().hex
    val = uuid4().hex
    d2[key] = val
    d2[val] = key
d2.update(d1)
d22.update(d11)
b = datetime.datetime.now()
x = d2['key']
print(x)
e = datetime.datetime.now()
print((e - b).total_seconds())
b = datetime.datetime.now()
k = d22["value"]
x = d2[k]
print(x)
e = datetime.datetime.now()
print((e - b).total_seconds())