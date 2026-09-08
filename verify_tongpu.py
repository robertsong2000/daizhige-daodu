#!/usr/bin/env python3
"""核验 tongpu.html：引文与库本逐字比对 + 排版红线。"""
import re, sys, unicodedata

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/tongpu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/草木鸟兽虫鱼/桐谱.txt'

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

lib = open(LIB, encoding='utf-8').read()
libn = norm(lib)
page = open(PAGE, encoding='utf-8').read()

quotes = re.findall(r'<q\b[^>]*>(.*?)</q>', page, re.S)
ok = True
for i, q in enumerate(quotes, 1):
    q = re.sub(r'<span class="src">.*?</span>', '', q, flags=re.S)
    q = re.sub(r'<[^>]+>', '', q)
    qn = norm(q)
    if not qn:
        print(f'Q{i:02d} EMPTY'); ok = False; continue
    if qn in libn:
        print(f'Q{i:02d} PASS  ({len(qn)}字) {qn[:18]}...')
    else:
        print(f'Q{i:02d} FAIL  {qn[:40]}')
        for j in range(0, len(qn), 10):
            seg = qn[j:j+10]
            print('      找不到:', seg, '在库中' if seg in libn else '不在库中')
        ok = False

raw = open(PAGE, encoding='utf-8').read()
for bad, name in [('—', 'em dash'), ('–', 'en dash')]:
    if bad in raw:
        print(f'REDLINE {name} found'); ok = False

text = re.sub(r'<[^>]+>', '', raw)
for ln, line in enumerate(text.split('\n'), 1):
    if line.count('·') > 1:
        print(f'REDLINE 行{ln} 中点超过1个'); ok = False

print('RESULT:', 'ALL PASS' if ok else 'FAILED')
sys.exit(0 if ok else 1)
