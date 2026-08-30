#!/usr/bin/env python3
"""verify_jiandeng.py — 剪灯新话页引文与排版核验"""
import re
import sys

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/jiandeng-xinhua.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/剪灯新话.txt"

def norm(s):
    s = re.sub(r"[，。、；：「」『』（）\s？！.…·\'\"’‘]", "", s)
    for a, b in [("栁", "柳"), ("竒", "奇"), ("巳", "已")]:
        s = s.replace(a, b)
    return s

src = open(SRC).read()
page = open(PAGE).read()
plain = re.sub(r"<[^>]+>", "", page)
S, P = norm(src), norm(plain)

QUOTES = [
    "好事者每以近事相闻，远不出百年，近止在数载，襞积于中，日新月盛，习气所溺，欲罢不能，乃援笔为文以纪之。其事皆可喜可悲，可惊可怪者。",
    "既成，又自以为涉于语怪，近于海淫，藏之书笥。",
    "十五夜，三更尽，游人渐稀，见一丫鬟，挑双头牡丹灯前导，一美人随后，约年十七八，红裙翠袖，婷婷袅袅，迤逦投西而去。",
    "初无桑中之期，乃有月下之遇，似非偶然也。",
    "此真可谓『绿兮衣兮，绿衣黄裳』者也。",
    "儿常衣绿，但呼我为绿衣人可矣。",
]

fail = 0
for q in QUOTES:
    a, b = norm(q) in S, norm(q) in P
    tag = "✓" if (a and b) else ("⚠页缺" if a else "✗库缺")
    if not (a and b):
        fail += 1
    print(tag, q[:24])

# 字数机算
total = len(open(SRC, encoding="utf-8").read())
page_declared = "46,369" in plain
print(("✓" if page_declared else "✗"), "页内字数申报 46,369, 实测", f"{total:,}")
if total != 46369:
    fail += 1

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
