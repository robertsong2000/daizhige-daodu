#!/usr/bin/env python3
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/zhangcangshui-ji.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/张苍水诗文集.txt'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if (0x3400 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF) or (0x20000 <= o <= 0x3FFFF):
            out.append(ch)
    return ''.join(out)

lib = norm(open(LIB, encoding='utf-8').read())

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.qtexts = []
        self.prose = []
        self.qdepth = 0
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'q':
            self.qdepth += 1
        if tag in ('script', 'style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag == 'q':
            self.qdepth -= 1
        if tag in ('script', 'style'):
            self.skip -= 1
    def handle_data(self, data):
        if self.skip: return
        if self.qdepth > 0:
            self.qtexts.append((data, self.getpos()))
        else:
            self.prose.append((data, self.getpos()))

raw = open(PAGE, encoding='utf-8').read()
p = P(); p.feed(raw)

fails = 0
for txt, (ln, col) in p.qtexts:
    n = norm(txt)
    if not n:
        continue
    if n not in lib:
        fails += 1
        print(f'[Q-FAIL] line {ln}: {txt.strip()[:60]}')
        for k in range(len(n), 2, -1):
            if n[:k] in lib:
                print(f'   可匹配前缀至:{k}字 -> ...{n[max(0,k-10):k]}‖{n[k:k+10]}...')
                break
print(f'正查：q 元素文字 {len(p.qtexts)} 段，失败 {fails}')

prose_all = norm(''.join(t for t, _ in p.prose))
hits = []
i = 0
while i + 6 <= len(prose_all):
    w = prose_all[i:i+6]
    if w in lib:
        k = 6
        while i + k < len(prose_all) and prose_all[i:i+k+1] in lib:
            k += 1
        hits.append((i, prose_all[i:i+k]))
        i += k
    else:
        i += 1
for i, w in hits:
    print(f'[反扫命中] @{i}: {w}  上下文:…{prose_all[max(0,i-12):i+len(w)+12]}…')
print(f'反扫：白话六字窗命中 {len(hits)} 处')

bad_dash = [(ln, l) for ln, l in enumerate(raw.splitlines(), 1) if '—' in l or '–' in l]
for ln, l in bad_dash: print(f'[长划线] line {ln}')
mid_dots = [(ln, l.count('·')) for ln, l in enumerate(raw.splitlines(), 1) if l.count('·') > 1]
for ln, l in mid_dots: print(f'[·超1] line {ln}')
print(f'红线：长划线 {len(bad_dash)} 处，·超1 {len(mid_dots)} 处')

ok = fails == 0 and len(hits) == 0 and not bad_dash and not mid_dots
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
