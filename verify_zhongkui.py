#!/usr/bin/env python3
import re, sys, unicodedata
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/zhongkui-quanzhuan.html"
LIB = "/home/robertsong/workspace/claude/daizhige-simplified/集藏/小说/唐钟馗全传.txt"

def norm(s):
    out = []
    for c in s:
        o = ord(c)
        if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:
            out.append(c)
        elif c.isdigit():
            out.append(c)
        elif 'a' <= c.lower() <= 'z':
            out.append(c.lower())
    return ''.join(out)

html = open(PAGE, encoding="utf-8").read()
libnorm = norm(open(LIB, encoding="utf-8").read())

# ---------- raw rule audit ----------
errs, warns = [], []
for i, ch in enumerate(html):
    if ch in '—–':
        errs.append(f"长划线 {ch!r} at offset {i}")
if '·' in html:
    for ln, line in enumerate(html.split('\n'), 1):
        n = line.count('·')
        if n > 1:
            errs.append(f"line {ln}: · 出现 {n} 次")
for ln, line in enumerate(html.split('\n'), 1):
    if '—' in line or '–' in line:
        errs.append(f"line {ln}: 长划线")
pua = [(hex(ord(c)), i) for i, c in enumerate(html) if 0xE000 <= ord(c) <= 0xF8FF]
if pua:
    errs.append(f"PUA chars: {pua[:5]}")
if not re.search(r'<title>[^<]*</title>', html):
    errs.append("no title")

# ---------- stack parse ----------
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, is_channel)
        self.channels = []       # list of (normtext, lineno)
        self.scan = []           # visible scan text pieces
        self.in_script = False
        self.cur_chan = None
    def is_chan(self, tag, attrs):
        cls = (dict(attrs).get('class') or '').split()
        return tag == 'q' or any(t.startswith('q') for t in cls), cls
    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script = True
            return
        chan, cls = self.is_chan(tag, attrs)
        if chan:
            if self.cur_chan is not None:
                warns.append(f"line {self.getpos()[0]}: channel nesting")
            self.cur_chan = [self.getpos()[0], []]
        self.stack.append((tag, chan))
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
            return
        if not self.stack:
            return
        # pop to matching tag
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                closing = self.stack[i:]
                del self.stack[i:]
                if any(c[1] for c in closing) and self.cur_chan is not None:
                    self.channels.append((norm(''.join(self.cur_chan[1])), self.cur_chan[0]))
                    self.cur_chan = None
                break
    def handle_data(self, data):
        if self.in_script:
            return
        if self.cur_chan is not None:
            self.cur_chan[1].append(data)
        else:
            self.scan.append(data)

p = P()
p.feed(html)

# ---------- channel verify ----------
for text, ln in p.channels:
    if not text:
        warns.append(f"line {ln}: empty channel")
        continue
    if text not in libnorm:
        errs.append(f"line {ln}: 引文不在库本: {text[:50]}")

# ---------- anti-scan ----------
scan_all = norm(''.join(p.scan))
libset = libnorm
hits = []
for i in range(len(scan_all) - 5):
    w = scan_all[i:i+6]
    if w in libset:
        hits.append((i, w, scan_all[max(0,i-8):i+14]))
if hits:
    for i, w, ctx in hits[:30]:
        errs.append(f"反扫撞窗 [{w}] …{ctx}…")
    if len(hits) > 30:
        errs.append(f"…共 {len(hits)} 处撞窗")

# ---------- JS literals ----------
m = re.search(r'<script>(.*?)</script>', html, re.S)
if m:
    js = m.group(1)
    lits = re.findall(r'"([^"\n]*)"|\'([^\'\n]*)\'', js)
    jstext = norm(''.join(a or b for a, b in lits))
    jhits = []
    for i in range(len(jstext) - 5):
        w = jstext[i:i+6]
        if w in libset:
            jhits.append((w, jstext[max(0,i-8):i+14]))
    if jhits:
        for w, ctx in jhits[:15]:
            errs.append(f"JS字面量撞窗 [{w}] …{ctx}…")

print(f"通道引文 {len(p.channels)} 处；白话反扫 {len(scan_all)} 字；JS字面量 {len(jstext)} 字" if m else f"通道引文 {len(p.channels)} 处")
for e in errs: print("ERR", e)
for w in warns: print("WARN", w)
print("PASS" if not errs else f"FAIL ({len(errs)})")
sys.exit(0 if not errs else 1)
