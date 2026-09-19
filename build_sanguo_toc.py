#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从库本目录区零誊写提取24卷240则，注入 sanguo-yanyi.html 的 <!--TOC24--> 标记"""
import sys

SRC = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/三国志通俗演义嘉靖壬午本.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/sanguo-yanyi.html'

lines = [l.strip() for l in open(SRC, encoding='utf-8').read().split('\n')]

# 定位目录区：第一个精确的 卷之X 行 到 前言标题行 之前
start = next(i for i, l in enumerate(lines) if l == '卷之一')
end = next(i for i, l in enumerate(lines) if l.startswith('前言') and i > start)

blocks = []   # (卷名, [则目…])
cur = None
for l in lines[start:end]:
    if not l:
        continue
    if l.startswith('卷之'):
        assert cur is None or len(cur[1]) == 10, f'{cur} 则目数异常'
        cur = (l, [])
        blocks.append(cur)
    else:
        assert cur is not None, f'卷前出现则目: {l!r}'
        cur[1].append(l)
assert len(cur[1]) == 10, '最后一卷则目数异常'
assert len(blocks) == 24, f'卷数 {len(blocks)} != 24'
total = sum(len(b[1]) for b in blocks)
assert total == 240, f'总则目 {total} != 240'

frag = []
for name, mus in blocks:
    body = '<br>'.join(mus)
    frag.append(f'      <details>\n        <summary>{name}</summary>\n'
                f'        <div class="mu"><q>{body}</q></div>\n      </details>')
fragment = '\n'.join(frag) + '\n'

html = open(PAGE, encoding='utf-8').read()
assert html.count('<!--TOC24-->') == 1, 'TOC标记异常'
html = html.replace('<!--TOC24-->\n', fragment)
open(PAGE, 'w', encoding='utf-8').write(html)

n = len(''.join(c for c in open(SRC, encoding='utf-8').read() if not c.isspace()))
print(f'已注入 24 卷 240 则；库本去空白 {n} 字')
