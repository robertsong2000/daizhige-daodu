#!/usr/bin/env python3
# verify_qishengji.py — 骑省集导读页核验（引文正向 + 白话反扫6字窗 + 机数 + mulu联检 + 排版红线）
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/qisheng-ji.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/骑省集.txt'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'

def norm(t):
    return re.sub(r'[\W_]+', '', t)

lib_raw = open(LIB, encoding='utf-8').read()
lib_n = norm(lib_raw)
page = open(PAGE, encoding='utf-8').read()

# ---------- 引文提取（DOM 顺序，q/qv/i；豁免 script/style/title） ----------
class QP(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []      # (kind, text)
        self.other = []    # 非引文文本（反扫用）
        self.skip = 0
        self.stack = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip += 1
        self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip = max(0, self.skip-1)
        if self.stack and self.stack[-1] == tag: self.stack.pop()
    def handle_data(self, d):
        if self.skip: return
        if 'q' in self.stack or 'qv' in self.stack or 'i' in self.stack:
            self.out.append(('q' if 'q' in self.stack else 'i', d))
        else:
            self.other.append(d)

qp = QP(); qp.feed(page)
quotes = [norm(t) for _,t in qp.out if norm(t)]
whites = norm(''.join(qp.other))

errs = []
# ---------- 1. 引文正向 ----------
lib_pos = {}
cur = 0
for idx, qt in enumerate(quotes):
    p = lib_n.find(qt)
    if p < 0:
        errs.append(f'引文#{idx+1} 未见于库本: {qt[:28]}…')
    else:
        lib_pos[idx] = p
nq = len(quotes)

# ---------- 2. 白话反扫 6 字窗 ----------
G = 6
grams = set(lib_n[i:i+G] for i in range(len(lib_n)-G+1))
hits = []
for i in range(len(whites)-G+1):
    w = whites[i:i+G]
    if w in grams:
        hits.append(w)
if hits:
    errs.append(f'反扫撞窗 {len(hits)} 处: ' + ' / '.join(hits[:6]))

# ---------- 3. 机数 ----------
cnt = len(re.sub(r'\s', '', lib_raw))
if cnt != 132240:
    errs.append(f'库本去空白 {cnt} != 132240')

# ---------- 4. 排版红线 ----------
if '—' in page or '–' in page:
    errs.append('出现长划线')
for ln, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        errs.append(f'源码行{ln} · 超1')
if '殁知阁' in page:
    errs.append('错字：殁知阁')
if not re.search(r"<title>DD\d+</title>", page):
    errs.append('title 未令牌化')

# ---------- 5. mulu 联检 ----------
mulu = open(MULU, encoding='utf-8').read()
m = re.search(r'<a class="entry" href="qisheng-ji\.html">\s*<span class="no mono">(\d+)</span>', mulu)
if not m:
    errs.append('mulu 缺 qisheng-ji 条目')
else:
    no = int(m.group(1))
    nos = sorted(int(x) for x in re.findall(r'class="no mono">(\d+)</span>', mulu))
    if nos != list(range(1, len(nos)+1)):
        errs.append('mulu 编号不连续')
    if no != len(nos):
        errs.append(f'mulu 本条编号 {no} != max {len(nos)}')
    if '五百篇' not in mulu:
        errs.append('mulu 计数锚未更新为五百')

print(f'引文 {nq} 处正向比对，反扫 6 字窗，机数 {cnt}')
if errs:
    print('FAIL')
    for e in errs: print(' -', e)
    sys.exit(1)
print('PASS')
