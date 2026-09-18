# -*- coding: utf-8 -*-
"""勿庵历算书记 checker：q核验 + 白话反扫 + 排版规则"""
import re, sys, json
from html.parser import HTMLParser

SRC = "daizhige-simplified/子藏/算法/勿庵历算书记.txt"
PAGE = "daizhige-daodu/wuan-lisuan-shuji.html"
libs = open(SRC).read()
page = open(PAGE).read()

def norm(s):
    out = []
    for c in s:
        o = ord(c)
        if 0xE000 <= o <= 0xF8FF:      # PUA 剥
            continue
        if c.isspace() or o == 0x3000 or c == "　":
            continue
        if c.isascii() and re.match(r"[\W_]", c, re.ASCII):
            continue
        if not c.isascii() and not re.match(r"[一-鿿]", c):
            continue
        if o in (0xFF01,0xFF0C,0xFF1B,0xFF1A,0xFF1F,0xFF08,0xFF09,0xFF0E,0x2018,0x2019,0x201C,0x201D,0x2026,0x2014,0x2013,0x00B7):
            continue
        out.append(c)
    return "".join(out)

LIB = norm(libs)

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes = []      # (tag, normtext)
        self.prose = []       # 白话流（不含 q）
        self.stack = []
        self.skip = 0         # style
        self.script = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("style",): self.skip += 1
        if tag == "script": self.script += 1
        if tag in ("q","qv"):
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in ("style",): self.skip = max(0, self.skip-1)
        if tag == "script": self.script = max(0, self.script-1)
        if tag in ("q","qv") and self.stack:
            self.stack.pop()
    def handle_data(self, data):
        if self.skip: return
        if self.script:
            # JS 字符串里的中文段也参与反扫
            for m in re.findall(r"[一-鿿]{2,}", data):
                self.prose.append(m)
            return
        t = norm(data)
        if not t: return
        if self.stack:
            self.quotes.append((self.stack[-1], t))
        else:
            self.prose.append(t)

p = P(); p.feed(page)

fails = 0
# 1) q 核验
seen = {}
for tag, t in p.quotes:
    seen[t] = seen.get(t, 0) + 1
    if t not in LIB:
        fails += 1
        print(f"[QFAIL] <{tag}> {t[:40]}")
qcount = len(p.quotes)
print(f"q核验：{qcount} 处，未过 {fails}")

# 2) 白话反扫：6字滑窗
stream = norm("".join(p.prose))
hits = []
for i in range(len(stream)-5):
    w = stream[i:i+6]
    if w in LIB:
        hits.append((i, w))
print(f"白话反扫：流长 {len(stream)}，六字窗命中 {len(hits)}")
for i, w in hits[:15]:
    print("  [HIT]", w, "…", stream[max(0,i-10):i+16].replace(w, f"<{w}>"))

# 3) 排版规则
raw = page
bad = []
for ch, name in [("—","长划—"), ("–","短划–")]:
    if ch in raw: bad.append(name)
for ln, line in enumerate(raw.split("\n"), 1):
    if line.count("·") > 1:
        bad.append(f"L{ln} · x{line.count('·')}")
print("排版：", bad if bad else "过（无长划线，每行·≤1）")

# 4) 结构
for token in ["第458篇", "殆知阁简体库", "时代局限", "引文经脚本"]:
    if token not in raw:
        print("结构缺：", token)
print("结构检查完")
sys.exit(1 if (fails or hits or bad) else 0)
