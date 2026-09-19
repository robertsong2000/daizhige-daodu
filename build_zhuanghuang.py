#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build zhuanghuang-zhi.html: inject {Q:start~end} slices from the library file verbatim."""
import re, sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/绘画/装潢志.txt'
TPL = '/home/robertsong/workspace/claude/daizhige-daodu/zhuanghuang.tpl.html'
OUT = '/home/robertsong/workspace/claude/daizhige-daodu/zhuanghuang-zhi.html'

src = open(SRC, encoding='utf-8').read()
src = src.replace('\n', '').replace('　', '')

tpl = open(TPL, encoding='utf-8').read()

n = [0]
def repl(m):
    a, b = m.group(1), m.group(2)
    ca = src.count(a)
    assert ca == 1, ('start anchor x%d' % ca, a)
    i = src.index(a)
    j = src.index(b, i)
    piece = src[i:j + len(b)]
    assert '<' not in piece and '>' not in piece and '&' not in piece, piece
    n[0] += 1
    return piece

out = re.sub(r'\{Q:(.+?)~(.+?)\}', repl, tpl)
left = re.findall(r'\{Q:', out)
assert not left, ('unresolved markers', len(left))
open(OUT, 'w', encoding='utf-8').write(out)
print('OK quotes injected:', n[0], ' bytes:', len(out))
