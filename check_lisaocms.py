# -*- coding: utf-8 -*-
"""核验 lisao-caomushu.html：引文逐字比对 + 白话六字窗反扫 + 版式红线"""
import io, re, sys
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/lisao-caomushu.html"
BOOK = "/home/robertsong/workspace/claude/daizhige-simplified/诗藏/楚辞/离骚草木疏.txt"

VAR = {"宻": "密", "髙": "高", "呉": "吴", "巻": "卷", "隠": "隐", "扵": "于",
       "歴": "历", "鐡": "铁", "黒": "黑", "劔": "剑", "莵": "兔", "渇": "渴"}

def norm(s):
    out = []
    for ch in s:
        ch = VAR.get(ch, ch)
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0x20000 <= o <= 0x2EBEF:
            out.append(ch)
    return "".join(out)

page = io.open(PAGE, encoding="utf-8").read()
book_norm = norm(io.open(BOOK, encoding="utf-8").read())

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag)
        self.quotes = []         # finished quote strings
        self.plain = []          # finished non-quote text runs
        self.cur_q = None
        self.attrs_text = []
    def handle_starttag(self, tag, attrs):
        if self.cur_q is not None:
            self.cur_q.append("\x00")
        if tag == "q":
            assert self.cur_q is None, "nested q"
            self.cur_q = []
        if tag in ("script", "style"):
            self.stack.append(tag)
        for k, v in attrs:
            if k == "data-t" and v:
                self.attrs_text.append(v)
    def handle_endtag(self, tag):
        if tag == "q" and self.cur_q is not None:
            self.quotes.append("".join(self.cur_q))
            self.cur_q = None
        elif tag == "q":
            pass
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
    def handle_data(self, data):
        if self.cur_q is not None:
            self.cur_q.append(data)
            return
        if self.stack and self.stack[-1] in ("script", "style"):
            self.plain.append(data)
            return
        self.plain.append(data)

p = P()
p.feed(page)
if p.cur_q is not None:
    sys.exit("FAIL: unclosed q")
for a in p.attrs_text:
    p.plain.append(a)

fails = []

# 1) every quote must appear in book (normalized)
nq = 0
for q in p.quotes:
    qn = norm(q)
    if not qn:
        continue
    nq += 1
    if qn not in book_norm:
        fails.append("QUOTE MISS: %s" % q[:60])

# 2) anti-scan: 6-char windows of plain text must not hit book
hits = []
for run in p.plain:
    r = norm(run)
    for i in range(len(r) - 5):
        w = r[i:i + 6]
        if w in book_norm:
            hits.append((w, run[max(0, i - 10):i + 16]))
hits = sorted(set(hits))
for w, ctx in hits:
    fails.append("ANTISCAN HIT [%s] near ...%s..." % (w, ctx.replace("\n", "")))

# 3) red lines
if "—" in page or "–" in page:
    fails.append("long dash present")
for node in p.plain:
    if node.count("·") > 1:
        fails.append("multi-dot node: %s" % node.strip()[:60])
if "@@" in page:
    fails.append("unresolved token")

print("quotes checked: %d" % nq)
print("plain nodes: %d, antiscan hits: %d" % (len(p.plain), len(hits)))
if fails:
    print("\n".join(fails[:40]))
    sys.exit("FAIL %d" % len(fails))
print("ALL PASS")
