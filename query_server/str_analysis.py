# -*- coding: utf-8 -*-
import ply.lex as lex
import ply.yacc as yacc


"""
语法解析模块
用途:
1. 把sql的 where table1.name1 = table2.name2 and table1.name3 = table3.name4 这样的语句解析出来.
"""

tokens = (
    "NAME", "NUMBER", "PLUS", "MINUS", "TIMES",
    "DIVIDE", "EQUALS", "LPAREN", "RPATEN"
)
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPATEN = r'\)'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]'


def t_number(t):
    r'\d+'  # 描述模式的正则表达式
    t.value = int(t.value)
    return t  # 最后必须返回t，如果不返回，这个token就会被丢弃掉