# -*- coding: utf-8 -*-
import random


"""随机产生密码"""


upper_seq = list(range(65, 92))  # 大写字母对应的ASCII码的范围，65-91
lower_seq = list(range(97, 124))  # 小写字母对应的ASCII码的范围，97-123
symbol_seq = "~!@#$%^&*()-=_+[]{}\|/?"[:]  # 特殊符号的序列


def get_letter(seq: list = None)->str:
    """
    获取一个字母
    :param seq: 参与选择的序列，默认为空。
    :return: str  """
    return chr(random.choice(seq))


def generator_password(pw_length: int = 12, upper_count: int = 1, symbol_count: int = 1, num_count: int = 3)->str:
    """
    生成密码
    :param pw_length: 密码长度。
    :param upper_count: 大写字母个数
    :param symbol_count: 符号个数
    :param num_count: 数字个数
    :return: 密码字符串
    """
    if not (isinstance(pw_length, int) and isinstance(upper_count, int) and isinstance(symbol_count, int)
            and isinstance(num_count, int)):
        raise TypeError("所有的参数都必须是int类型")
    elif pw_length < (upper_count + symbol_count + num_count):
        raise ValueError("密码长度不能小于设定的各类型字符之和!")
    else:
        num_list = [str(random.choice(range(0, 10))) for x in range(num_count)]
        symbol_list = [random.choice(symbol_seq) for x in range(symbol_count)]
        upper_list = [get_letter(upper_seq) for x in range(upper_count)]
        lower_count = pw_length - upper_count - symbol_count - num_count
        lower_list = list()
        current_seq = lower_seq.copy()
        while len(lower_list) < lower_count:
            seq_length = len(current_seq)
            if seq_length > 0:
                pass
            else:
                current_seq = lower_seq.copy()
                seq_length = len(current_seq)
            temp = current_seq.pop(random.randint(0, seq_length - 1))
            lower_list.append(chr(temp))
        lower_list.extend(upper_list)
        lower_list.extend(symbol_list)
        lower_list.extend(num_list)
        pw_list = [random.choice(lower_list) for x in range(pw_length)]
        pw_str = ''.join(pw_list)
        return pw_str


if __name__ == "__main__":
    print("新密码是: {}".format(generator_password(36)))