#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, sys
from html.parser import HTMLParser

HTML = 'weizheng-zhonggao.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/职官/为政忠告.txt'
QTAGS = {'q','qv','vq'}
BLOCKS = {'p','h1','h2','h3','h4','h5','h6','li','div','blockquote','cite','button','span','footer','td','th','figcaption','dt','dd','small','b','em','title','option','label','a'}

def norm(s):
    return ''.join(ch for ch in s if '一' <= ch <= '鿿')

lib_raw = open(LIB, encoding='utf-8').read()
lib = norm(lib_raw)

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes = []          # (name, text)
        self.blocks = []          # (name, text) non-quote text
        self.qdepth = 0
        self.buf = []
        self.bname = []
        self.scripts = []
        self.in_script = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script += 1; return
        if self.in_script: return
        if tag in QTAGS:
            self.qdepth += 1
            self.bname.append('Q:'+tag); self.buf.append([])
        elif tag in BLOCKS and self.qdepth == 0:
            self.bname.append(tag); self.buf.append([])
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script -= 1; return
        if self.in_script: return
        if tag in QTAGS and self.qdepth > 0:
            txt = ''.join(self.buf.pop()); self.bname.pop()
            self.qdepth -= 1
            if self.qdepth == 0:
                self.quotes.append((tag, txt))
            else:
                self.buf[-1].append(txt)
        elif tag in BLOCKS and self.bname and self.bname[-1] == tag and self.qdepth == 0:
            txt = ''.join(self.buf.pop()); self.bname.pop()
            if txt.strip():
                self.blocks.append((tag, txt))
    def handle_data(self, d):
        if self.in_script:
            self.scripts.append(d); return
        if self.buf: self.buf[-1].append(d)

html = open(HTML, encoding='utf-8').read()
p = P(); p.feed(html)

errs, ok = [], 0
print('== 引文通道 %d 处 ==' % len(p.quotes))
for i,(tag,txt) in enumerate(p.quotes,1):
    t = norm(txt)
    if not t:
        errs.append('引文%d(%s) 归一后为空' % (i, tag)); continue
    for ch in txt:
        if ch == '□' or 0xE000 <= ord(ch) <= 0xF8FF:
            errs.append('引文%d 含缺字符/私用区字 %r' % (i, ch))
    if t in lib:
        ok += 1
        print('  [%2d] %-3s %d字 ✓' % (i, tag, len(t)))
    else:
        # locate longest prefix that matches to help fix
        lo = 0
        for k in range(len(t), 0, -1):
            if t[:k] in lib: lo = k; break
        errs.append('引文%d(%s) 不在库本! 前%d字可匹配: %s | 待查: %s' % (i, tag, lo, t[:lo], t[max(0,lo-5):lo+10]))

print('== 白话反扫（块内六字窗）==')
hits = 0
for name, txt in p.blocks:
    t = norm(txt)
    if '·' in txt and txt.count('·') > 1:
        errs.append('块 <%s> 含 %d 个·: %s' % (name, txt.count('·'), txt[:40]))
    for k in range(len(t) - 5):
        w = t[k:k+6]
        if w in lib:
            hits += 1
            errs.append('反扫命中 <%s> 「%s」(上下文:…%s…)' % (name, w, t[max(0,k-6):k+12]))
print('  零撞' if hits == 0 else '  命中 %d' % hits)

print('== JS 字面量反扫 ==')
jhits = 0
for sc in p.scripts:
    for m in re.findall(r'"([^"\n]*)"|\'([^\'\n]*)\'', sc):
        s = m[0] or m[1]
        t = norm(s)
        for k in range(len(t) - 5):
            if t[k:k+6] in lib:
                jhits += 1
                errs.append('JS字面量命中 「%s」' % t[k:k+6])
print('  零撞' if jhits == 0 else '  命中 %d' % jhits)

for ch in ('—','–'):
    if ch in html:
        errs.append('页面含长划线 %r' % ch)

print()
if errs:
    print('!! %d 处问题:' % len(errs))
    for e in errs: print('  ', e)
    sys.exit(1)
print('全部通过：引文 %d 处逐字比对一致；白话与 JS 反扫零撞；无长划线；每块·至多1。' % ok)
