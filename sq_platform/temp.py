# -*- coding: utf-8 -*-

class A:
    type_dict = {}
    type_dict['name'] = str

    def __init__(self, **kwargs):
        print(self.__class__.__name__, self.type_dict)
        for k, v in kwargs.items():
            self.__dict__[k] = v


class B(A):
    type_dict = {}
    type_dict['age'] = int


a = A()
b = B()
c = A()



