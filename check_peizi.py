#!/usr/bin/env python3
# 引文正扫 + 白话反扫 + 排版规则检查
import re, sys
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/裴子语林.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/peizi-yulin.html'

VAR = {'亰': '京', '巻': '卷', '甞': '尝', '冩': '写', '隷': '隶'}

def norm(t):
    for k, v in VAR.items():
        t = t.replace(k, v)
    return re.sub(r'[\W_]+', '', t, flags=re.UNICODE)

lib = open(LIB, encoding='utf-8').read()
nlib = norm(lib)
page = open(PAGE, encoding='utf-8').read()

errors, warns = [], []

# ---------- 切块解析器：每个元素一个块，script/style/#qb 跳过 ----------
class Blk(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks, self.quotes = [], []
        self.stack, self.skip, self.inq = [], set(), False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '')
        if tag in ('script', 'style'):
            self.skip.add(tag)
        if 'q' in cls.split() or 'qv' in cls.split() or tag == 'q':
            self.inq = True
            self.stack.append('Q')
        else:
            self.stack.append('T')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip.discard(tag)
        if self.stack:
            k = self.stack.pop()
            if k == 'Q':
                self.inq = any(x == 'Q' for x in self.stack)
    def handle_data(self, d):
        if self.skip:
            return
        if d.strip():
            (self.quotes if self.inq else self.blocks).append(d)

# JS 字符串单独成块（JS 渲染文本也算白话，前科 343）
def js_blocks(page):
    scripts = re.findall(r'<script>(.*?)</script>', page, re.S)
    out = []
    for s in scripts:
        for m in re.finditer(r"'([^']*)'|\"([^\"]*)\"", s):
            t = m.group(1) if m.group(1) is not None else m.group(2)
            if re.search(r'[一-鿿]', t):
                out.append(t)
    return out

p = Blk()
p.feed(page)

# ---------- 1. 引文正扫 ----------
quotes = [q for q in p.quotes if len(norm(q)) >= 2]
miss = 0
for q in quotes:
    nq = norm(q)
    if nq not in nlib:
        miss += 1
        errors.append(f'引文 MISS: {q[:40]}')
print(f'引文正扫: {len(quotes)} 条, MISS {miss}')

# ---------- 2. 白话反扫（6 字窗） ----------
hits = 0
allprose = p.blocks + js_blocks(page)
for b in allprose:
    nb = norm(b)
    for i in range(len(nb) - 5):
        w = nb[i:i+6]
        if w in nlib:
            hits += 1
            ctx = b[max(0, i-6):i+12]
            errors.append(f'反扫命中 [{w}]: …{ctx}…')
print(f'反扫 6 字窗: {len(allprose)} 块, 命中 {hits}')

# ---------- 3. 排版规则 ----------
vis = p.blocks + p.quotes + js_blocks(page)
joined = '\n'.join(vis)
if '—' in joined or '–' in joined:
    errors.append('出现长划线')
for line in joined.split('\n'):
    if line.count('·') > 1:
        errors.append(f'一行多·: {line.strip()[:40]}')
for ch in joined:
    if 0xE000 <= ord(ch) <= 0xF8FF:
        errors.append('页面出现 PUA 字符')
        break

print(f'\n== {len(errors)} 错误, {len(warns)} 警告 ==')
for e in errors[:40]:
    print('ERR', e)
sys.exit(1 if errors else 0)
