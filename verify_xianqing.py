#!/usr/bin/env python3
"""核验 xianqing-ouji.html 引文与殆知阁库内《闲情偶寄》逐字一致，并查排版规则。"""
import re, unicodedata, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/艺藏/综合/闲情偶寄.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/xianqing-ouji.html"

VAR = {"掲": "揭", "頺": "颓", "頽": "颓", "髙": "高", "竒": "奇", "渉": "涉",
       "箒": "帚", "彚": "汇", "鬛": "鬣", "偹": "备", "恠": "怪", "麄": "粗",
       "冩": "写", "浄": "净", "礲": "砻", "崄": "险", "児": "儿", "巻": "卷"}
PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■◎○　]")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VAR.get(c, c) for c in s)
    return PUNCT.sub("", s)

raw = open(SRC, encoding="utf-8").read()
body = norm(raw)
html = open(PAGE, encoding="utf-8").read()
fail = 0

def check(q, where):
    global fail
    frags = [f for f in re.split(r"……|\.\.\.", q) if norm(f)]
    bad = [f for f in frags if norm(f) not in body]
    ok = not bad
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    for b in bad:
        print("   不匹配片段：", b[:50])
    fail += 0 if ok else 1

quotes = re.findall(r"「([^」]*)」", html)
print(f"页面「」引文 {len(quotes)} 个：")
for i, q in enumerate(quotes, 1):
    check(re.sub(r"<[^>]+>", "", q), f"引文{i}")

# 页面声称的字符数
n = len(raw)
print(f"\n库内总字符数：{n:,}")
for num in (f"{n:,}", "157,115"):
    ok = num in html
    print(("PASS" if ok else "FAIL"), f"页面声称字符数 {num}")
    fail += 0 if ok else 1

# 八部书架字数
SHELF = {"词曲": ("30,829", "六节"), "演习": ("20,054", "五节"), "声容": ("24,530", "四节"),
         "居室": ("15,487", "五节"), "器玩": ("15,726", "两节"), "饮馔": ("11,109", "三节"),
         "种植": ("17,869", "五节"), "颐养": ("20,524", "四节")}
import math
lines = raw.split("\n")
marks = {"词曲": 26, "演习": 220, "声容": 456, "居室": 592, "器玩": 782, "饮馔": 866, "种植": 1002, "颐养": 1296}
ks = list(marks)
for i, k in enumerate(ks):
    a = marks[k] - 1
    b = (marks[ks[i + 1]] - 1) if i + 1 < len(ks) else len(lines)
    n2 = len(re.sub(r"\s", "", "".join(lines[a:b])))
    num, _ = SHELF[k]
    ok = f"{n2:,}" == num and num in html
    print(("PASS" if ok else "FAIL"), f"书架 {k} {num}（实测 {n2:,}）")
    fail += 0 if ok else 1

# 排版规则：长划线；每行·至多一个
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

# 页脚要素
for k in ["殆知阁", "daizhigev20", "核验", "时代局限", "mulu.html", "xueyi-xiupu.html"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
