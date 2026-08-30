#!/usr/bin/env python3
"""verify_dilitaoli.py — 地理套利页古籍引文与排版核验"""
import re
import sys

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/dili-taoli.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/岛夷志略.txt"

def norm(s):
    s = re.sub(r"[，。、；：「」『』（）〔〕\s？！.…·\'\"’‘]", "", s)
    for a, b in [("栁", "柳"), ("竒", "奇")]:
        s = s.replace(a, b)
    return s

src = open(SRC).read()
page = open(PAGE).read()
plain = re.sub(r"<[^>]+>", "", page)
S, P = norm(src), norm(plain)

QUOTES = [
    "故贩其地者，十去九不还也。",
    "田沃稼茂",
    "岁凡三稔",
    "每岁藉乌爹米至",
    "道不拾遗，乡里和睦",
    "每个银钱重二钱八分，准中统钞一十两，易汃子计一万一千五百二十有余",
    "以二百五十汃子籴一尖箩熟米，折官斗有一斗六升",
    "每钱收汃子，可得四十六箩米，通计七十三斗六升，可供二人一岁之食有余",
    "税收十分之一也",
    "每个银钱重二钱八分，准中统钞一十两，易汃子计一万一千五百二十有余，折钱使用。以二百五十汃子籴一尖箩熟米，折官斗有一斗六升。每钱收汃子，可得四十六箩米，通计七十三斗六升，可供二人一岁之食有余。",
]

fail = 0
for q in QUOTES:
    a, b = norm(q) in S, norm(q) in P
    tag = "✓" if (a and b) else ("⚠页缺" if a else "✗库缺")
    if not (a and b):
        fail += 1
    print(tag, q[:26])

# 页内机数断言：四十六箩、七十三斗六升、十去九不还 必在页上
for kw in ["四十六箩", "七十三斗六升", "十去九不还"]:
    r = kw in plain
    if not r:
        fail += 1
    print(("✓" if r else "✗"), "页含", kw)

# 排版红线
if re.search(r"—|–", page):
    print("✗ 长划线")
    fail += 1
visible = re.sub(r"<[^>]+>", "\n", page)
bad = [ln.strip() for ln in visible.splitlines() if ln.strip().count("·") > 1]
if bad:
    print("✗ 间隔号超限", bad)
    fail += 1
else:
    print("✓ 排版红线通过")

print("FAIL" if fail else "ALL PASS")
sys.exit(1 if fail else 0)
