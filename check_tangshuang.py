#!/usr/bin/env python3
# 核验器：引文正扫 + 白话六字窗反扫 + 排版红线 + data-t 通道
import re, sys
from html.parser import HTMLParser

PAGE = 'tangshuang-pu.html'
SRC  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/饮馔/糖霜谱.txt'

PUNCT = re.compile(r'[\W_]+', re.UNICODE)
def norm(s):
    return PUNCT.sub('', s)

src = open(SRC, encoding='utf-8').read()
sn = norm(src)

BLOCK = {'p','div','h1','h2','h3','h4','h5','h6','article','section','footer',
         'header','nav','button','li','title','text','body','html','main','td','tr'}
RAW = {'style','script'}

class Walker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes = []      # (text, line, tag)
        self.runs = []        # (text, line, kind)
        self.data_t = []
        self.stack = []       # [tag, kind, buf]  kind: q|src|el|raw
        self.cur_run = []
        self.line = 1
    def _top(self):
        return self.stack[-1] if self.stack else None
    def _sink(self):
        t = self._top()
        return t[2] if t else self.cur_run
    def handle_starttag(self, tag, attrs):
        self.line = self.getpos()[0]
        ad = dict(attrs)
        if 'data-t' in ad:
            self.data_t.append((ad['data-t'], self.line))
        cls = (ad.get('class') or '').split()
        if tag in RAW:
            self.flush_run()
            self.stack.append([tag, 'raw', []]); return
        if 'src' in cls or 'csrc' in cls:
            self.stack.append([tag, 'src', []]); return
        isq = ('q' in cls) or ('qv' in cls) or ('il' in cls)
        if isq:
            self.flush_run()
            self.stack.append([tag, 'q', []]); return
        if tag in BLOCK:
            self.flush_run()
        self.stack.append([tag, 'el', []])
    def handle_endtag(self, tag):
        if not self.stack:
            return
        if self.stack[-1][0] != tag:
            # 容错：找最近同名
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
            else:
                return
        tag2, kind, buf = self.stack.pop()
        text = ''.join(buf)
        if kind == 'raw' or kind == 'src':
            return
        if kind == 'q':
            if text.strip():
                self.quotes.append((text, self.getpos()[0], tag2))
            return
        # 普通元素：文本传播给上层 sink
        self._sink().append(text)
        if tag2 in BLOCK:
            self.flush_run()
    def handle_data(self, data):
        self.line = self.getpos()[0]
        t = self._top()
        if t and t[1] == 'raw':
            if data.strip():
                self.runs.append((data, self.line, 'raw'))
            return
        self._sink().append(data)
    def flush_run(self):
        if self.cur_run:
            t = ''.join(self.cur_run)
            if t.strip():
                self.runs.append((t, self.line, 'dom'))
        self.cur_run = []

w = Walker()
w.feed(open(PAGE, encoding='utf-8').read())
w.close()
w.flush_run()

fail = 0

# ---------- 1. 正扫：q/qv/il 逐条（先按 …… 分段再归一） ----------
frag_total = 0
for text, line, tag in w.quotes:
    t0 = re.split(r'…+', text)
    for piece in t0:
        frag = norm(piece)
        if len(frag) < 2:
            continue
        frag_total += 1
        if frag not in sn:
            fail += 1
            print('[正扫MISS] L%d <%s> 片段: %s' % (line, tag, frag[:44]))

# ---------- 2. data-t 通道 ----------
dt_total = 0
for val, line in w.data_t:
    dt_total += 1
    if norm(val) not in sn:
        fail += 1
        print('[data-t MISS] L%d: %s' % (line, val))

# ---------- 3. 反扫：白话六字窗 ----------
WIN = 6
hits = 0
for text, line, kind in w.runs:
    t = norm(text)
    for i in range(len(t) - WIN + 1):
        win = t[i:i+WIN]
        if win in sn:
            hits += 1
            fail += 1
            ctx = t[max(0, i-6):i+WIN+6]
            print('[反扫撞] L%d (%s): …%s…  窗=%s' % (line, kind, ctx, win))
            break

# ---------- 4. 红线 ----------
html = open(PAGE, encoding='utf-8').read()
if '—' in html:
    fail += 1; print('[红线] 长划线 —')
if '–' in html:
    fail += 1; print('[红线] 长划线 –')
for no, ln in enumerate(html.split('\n'), 1):
    if ln.count('·') > 1:
        fail += 1; print('[红线] L%d 一行多个 ·' % no)
for m in re.finditer(r'(?:src|href)="(?!#)([^"]*)"', html):
    u = m.group(1)
    if u.startswith('http'):
        fail += 1; print('[红线] 外部资源引用: %s' % u)

print('---')
print('引文容器 %d 个，片段 %d 条核对；data-t %d 条；反扫 %d 字窗 %d 撞；红线%s'
      % (len(w.quotes), frag_total, dt_total, WIN, hits, '全过' if '—' not in html and '–' not in html else '有撞'))
sys.exit(1 if fail else 0)
