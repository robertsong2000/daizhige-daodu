#!/usr/bin/env python3
"""单刀会导读页核验：q切片与库本去标点归一逐字比对 + 白话六字窗反扫 + 排版规则"""
import sys, re
from html.parser import HTMLParser

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/dandaohui.html"
LIB  = "/home/robertsong/workspace/claude/daizhige-simplified/诗藏/剧曲/关大王独赴单刀会.txt"

def norm(s):
    return "".join(ch for ch in s if "一" <= ch <= "鿿")

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes = []
        self.plain = []
        self.skip = 0
        self.qdepth = 0
        self.qbuf = []
        self.cur = None
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "q":
            self.qdepth += 1
            if self.qdepth == 1:
                self.qbuf = []
        self.cur = tag
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if tag == "q" and self.qdepth > 0:
            self.qdepth -= 1
            if self.qdepth == 0:
                self.quotes.append("".join(self.qbuf))
    def handle_data(self, data):
        if self.skip:
            return
        if self.qdepth:
            self.qbuf.append(data)
        else:
            if data.strip():
                self.plain.append((self.cur or "?", data))

lib = open(LIB, encoding="utf-8").read()
libn = norm(lib)
wins = {libn[i:i+6] for i in range(len(libn) - 5)}

html = open(PAGE, encoding="utf-8").read()
p = P()
p.feed(html)
p.close()

fails = 0
print(f"库本归一 {len(libn)} 字；页面 q {len(p.quotes)} 条")
for i, txt in enumerate(p.quotes, 1):
    n = norm(txt)
    if not n:
        print(f"[空q] #{i}")
        fails += 1
        continue
    if n not in libn:
        k = 0
        while k < len(n) and "".join(n[:k+1]) in libn:
            k += 1
        print(f"[未命中] #{i} 「{txt.strip()[:40]}」 命中前缀{k}/{len(n)} 断点后：{n[max(0,k-4):k+10]}")
        fails += 1

hits = []
for ctx, txt in p.plain:
    n = norm(txt)
    for j in range(len(n) - 5):
        if n[j:j+6] in wins:
            hits.append((ctx, n[j:j+6], txt.strip()[:30]))
if hits:
    print(f"\n白话反扫命中 {len(hits)} 处：")
    for ctx, w, t in hits:
        print(f"  [{ctx}] 窗口「{w}」 于「{t}」")
    fails += len(hits)
else:
    print("白话反扫六字窗：零撞")

if "—" in html or "–" in html:
    print("[排版] 发现长划线")
    fails += 1
for ctx, txt in p.plain:
    if txt.count("·") > 1:
        print(f"[排版] 一行多·：{txt.strip()[:40]}")
        fails += 1

# PUA 残字检查
for m in re.finditer(r"[-\U00020000-\U0003ffff]", html):
    print(f"[PUA] {m.group(0)!r}")
    fails += 1

print("\n结果：" + ("全部通过" if fails == 0 else f"{fails} 处失败"))
sys.exit(0 if fails == 0 else 1)
