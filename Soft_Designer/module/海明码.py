#  -*- coding:utf-8 -*-
import math


class HammingCode:

    def __init__(self, raw):
        """
        :param raw: 原始字串,不要使用数字,以免和校验码混淆影响展示效果,注意高位在左.低位在右,和教科书保持一致
        """
        self.raw = raw

    def calculate_check_code_length(self) -> int:
        """
        计算校验码长度,海明码的校验码长度的公式是:
        (2^k) - 1 >= n + k
        其中,数据的长度是n, 校验码长度是k
        :return: 校验码的长度
        """
        n = len(self.raw)
        k = 0
        flag = -1
        while flag < 0:
            k += 1
            flag = (math.pow(2, k)) - (n + k)
        return k

    def create_check_code(self) -> list:
        """
        计算校验码序列并返回,这里用1~9的数字来代表校验码
        :return:
        """
        k = self.calculate_check_code_length()
        r = list(range(1, k + 1))
        return r

    def blend(self):
        """
        把原始字符串和校验码混合在一起
        :return:
        """
        raw_code = list(self.raw)
        check_code = self.create_check_code()
        l = len(raw_code) + len(check_code)
        seq = [None] * l
        """先添加校验码"""
        for index, item in enumerate(check_code):
            """
            校验码在海明码里的位置是 2^index(原公式是2^(index-1),因为这里的index从0开始,所以不用减1)
            但由于数学上索引是从1开始的,所以最后的索引要减1
            """
            code_index = int(math.pow(2, index) - 1)
            seq.pop(code_index)
            seq.insert(code_index, item)
        """数据位从第盗号占据海明码中剩下的位置"""
        for item in raw_code:
            temp_index = seq.index(None)
            seq.pop(temp_index)
            seq.insert(temp_index, item)
        """由于教科书上高位在左,所以需要倒序一下"""
        seq.reverse()
        return seq


if __name__ == "__main__":
    hamming_code = HammingCode("ABCDEFGH")
    print(hamming_code.blend())