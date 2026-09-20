#!/usr/bin/env python3
# 核验 yulanshi.html：引文容器逐句比对库本；白话 6 字窗反扫；排版红线
import re, sys
from html.parser import HTMLParser

PAGE = 'yulanshi.html'
BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/诗藏/诗集/御览诗.txt'

def norm(s):
    return re.sub(r'[^\w一-鿿㐀-䶿]', '', s)

BOOK_N = norm(open(BOOK, encoding='utf-8').read())

VOID = {'meta','link','br','hr','img','input','path','circle','stop','rect','line','ellipse','use'}

class Walk(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.quotes = []
        self.prose = []
        self.skip = 0

    @staticmethod
    def sel_for(tag, cls):
        if tag == 'q': return 'q'
        if tag == 'div' and ('q' in cls or 'poem' in cls): return 'q'  # 引文块与诗签
        if 'qv' in cls: return 'EXCLUDE'                 # 按语小注（白话）
        if 'stamp' in cls: return 'EXCLUDE'              # 印章
        return None

    def handle_starttag(self, tag, attrs):
        cls = set(dict(attrs).get('class', '').split())
        if tag in ('script', 'style'):
            self.skip += 1
            return
        if tag in VOID:
            return
        sel = self.sel_for(tag, cls)
        parent_q = self.stack and self.stack[-1][1] in ('q',)
        if not sel and parent_q:
            sel = self.stack[-1][1]
        self.stack.append((tag, sel if sel else None))

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
            return
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, d):
        if self.skip: return
        sel = None
        for _, s in reversed(self.stack):
            if s:
                sel = s
                break
        if sel == 'EXCLUDE':
            return
        if sel is None:
            self.prose.append(d)
        else:
            self.quotes.append((sel, d))

src = open(PAGE, encoding='utf-8').read()
w = Walk(); w.feed(src)
fails = []

CLAUSE = re.compile(r'[，。；！？：、·\n]+')
qcount = 0
for sel, txt in w.quotes:
    for clause in CLAUSE.split(txt):
        c = norm(clause)
        if len(c) < 2: continue
        qcount += 1
        if c not in BOOK_N:
            fails.append(f'[引文FAIL] {sel}: {clause.strip()[:40]}')

PROSE = re.compile(r'[一-鿿㐀-䶿]{6,}')
cnt = 0
for t in w.prose:
    for run in PROSE.findall(t):
        for i in range(len(run) - 5):
            win = run[i:i+6]
            cnt += 1
            if norm(win) in BOOK_N:
                fails.append(f'[白话撞窗] {win} …… {run[:26]}')

for ch, name in (('—', 'em-dash'), ('–', 'en-dash')):
    if ch in src:
        fails.append(f'[红线] 出现 {name}')
for i, line in enumerate(src.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'[红线] 第{i}行 · 超标: {line.strip()[:40]}')

print(f'引文子句核验: {qcount} 处；白话反扫窗口: {cnt} 个')
if fails:
    print('\n'.join(fails)); sys.exit(1)
print('ALL PASS')
