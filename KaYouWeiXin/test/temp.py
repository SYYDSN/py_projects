

def change(status: str, a: str) -> list:
    """
    根据一个状态(status)和一个输入(a),获得一组后继状态
    :param status:
    :param a:
    :return:
    """
    res = list()
    if status == "start":
        if a == "a":
            res.append("s1")
        elif a == "b":
            res.append("s2")
        else:
            res.append(status)
    elif status == "s1":
        if a == "a":
            res.append("s2")
        elif a == "b":
            res.append("s2")
            res.append("s1")
        else:
            res.append(status)
    elif status == "s2":
        if a == "a":
            res.append("s1")
        elif a == "b":
            res.append("end")
        else:
            res.append(status)
    return res

class NFA:
    def __init__(self):
        self.status = "start"
        self.status_set = ["start", "s1", "s2", "end"]
        self.letter_set = ["a", "b"]

    def accept(self, s: str) -> str:
        res = ''
        for i, x in enumerate(s):
            status_list = change(self.status, x)
            self.status = status_list[0]
            if self.status == "end":
                res = s[0: i + 1]
                break
            else:
                pass
        return res


if __name__ == "__main__":
    nfa1 = NFA()
    x = nfa1.accept("bba")
    print(x)