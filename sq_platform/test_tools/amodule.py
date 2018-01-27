import test_tools.bmodule as b

B = b.B
class A:
    def __init__(self):
        b = B()
        print(b)


if __name__ == "__main__":
    a = A()
    print(a)