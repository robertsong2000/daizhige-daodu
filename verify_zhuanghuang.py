#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""checker for zhuanghuang-zhi.html: 正扫 q/qv channels, 反扫 6-char windows."""
import re, sys, unicodedata
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/zhuanghuang-zhi.html'
SRC  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/绘画/装潢志.txt'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0xE000 <= o <= 0xF8FF: continue
        if ch.isspace() or ch == '　': continue
        if unicodedata.category(ch).startswith('P'): continue
        if unicodedata.category(ch).startswith('S'): continue
        out.append(ch)
    return ''.join(out)

src = norm(open(SRC, encoding='utf-8').read())
SRC6 = set(src[i:i+6] for i in range(len(src)-5))

html = open(PAGE, encoding='utf-8').read()

for ch, name in [('—','em-dash'), ('–','en-dash')]:
    if ch in html:
        print(f'FAIL: {name} found'); sys.exit(1)

bad = 0
for n, line in enumerate(html.split('\n'), 1):
    c = line.count('·')
    if c > 1:
        print(f'FAIL: line {n} has {c} ·'); bad += 1
if bad: sys.exit(1)

VOID = {'meta','link','br','hr','img','input','path','line','circle','text','rect'}
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.prose = []
        self.channels = []
        self.in_skip = 0
        self.cur = None
        self.depth_chan = 0
        self.title_buf = []
        self.in_title = False
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class','') or ''
        toks = set(cls.split())
        chan = tag == 'q' or 'q' in toks or 'qv' in toks
        if tag in ('script','style'):
            self.in_skip += 1
            self.stack.append((tag, 'skip'))
            return
        if tag == 'title': self.in_title = True
        if chan:
            self.depth_chan += 1
            if self.depth_chan == 1:
                self.cur = []
            self.stack.append((tag, 'chan'))
            return
        self.stack.append((tag, 'plain'))
    def handle_startendtag(self, tag, attrs): pass
    def handle_endtag(self, tag):
        if tag in VOID: return
        if tag == 'title': self.in_title = False
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                kind = self.stack[i][1]
                if kind == 'skip':
                    self.in_skip -= 1
                elif kind == 'chan':
                    self.depth_chan -= 1
                    if self.depth_chan == 0 and self.cur is not None:
                        t = norm(''.join(self.cur))
                        if t: self.channels.append(t)
                        self.cur = None
                del self.stack[i:]
                break
    def handle_data(self, data):
        if self.in_skip: return
        if self.in_title:
            self.title_buf.append(data)
        if self.depth_chan > 0 and self.cur is not None:
            self.cur.append(data)
        elif self.depth_chan == 0:
            self.prose.append(data)

p = P()
p.feed(html)
prose = norm(''.join(p.prose) + ''.join(p.title_buf))

scripts = re.findall(r'<script>(.*?)</script>', html, re.S)
js = norm(''.join(scripts))

fails = 0
for i, c in enumerate(p.channels):
    if c not in src:
        print(f'FAIL 正扫 channel #{i}: {c[:60]}')
        fails += 1

for i in range(len(prose)-5):
    w = prose[i:i+6]
    if w in SRC6:
        print(f'FAIL 反扫 prose window: {w!r} ctx=…{prose[max(0,i-8):i+14]}…')
        fails += 1
        if fails > 15: break

jf = 0
for i in range(len(js)-5):
    w = js[i:i+6]
    if w in SRC6:
        print(f'FAIL 反扫 js window: {w!r} ctx=…{js[max(0,i-8):i+14]}…')
        fails += 1; jf += 1
        if jf > 10: break

print(f'channels: {len(p.channels)}  prose: {len(prose)} chars  js: {len(js)} chars')
print('QCOUNT =', len(p.channels))
if fails:
    print('FAILED'); sys.exit(1)
print('ALL PASS')
