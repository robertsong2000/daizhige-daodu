#!/usr/bin/env python3
"""核验 yulizi.html 引文与库内原文逐字一致(去标点+NFKC+归一)"""
import re, sys, unicodedata

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/诸子/郁离子.txt"
HTML = "/home/robertsong/workspace/claude/daizhige-daodu/yulizi.html"

VARIANT = {}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VARIANT.get(c, c) for c in s)
    return re.sub(r"[^一-鿿㐀-䶿\U00020000-\U0003ffff]", "", s)

lib = norm(open(LIB, encoding="utf-8").read())
raw = open(HTML, encoding="utf-8").read()

fail = 0
seen = set()

def check(text: str, kind: str):
    global fail
    t = norm(text)
    if not t or t in seen:
        return
    seen.add(t)
    if t in lib:
        print(f"PASS {kind}: {text[:20]}... ({len(t)}字)")
    else:
        lo, hi = 0, len(t)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if t[:mid] in lib:
                lo = mid
            else:
                hi = mid - 1
        print(f"FAIL {kind}: {text[:36]}...")
        print(f"      连续匹配至第{lo}字: ...{t[max(0,lo-8):lo]}【{t[lo:lo+10]}】...")
        fail += 1

# ── 1. 屉格引文: 每个 .zh 内每个 <p> 全文必须库内连续 ──
for i, zh in enumerate(re.findall(r'<div class="zh">(.*?)</div>', raw, re.S), 1):
    for p in re.findall(r'<p>(.*?)</p>', zh, re.S):
        check(p, f"屉文{i}")

# ── 2. 页内所有「」『』与“”引语反扫 ──
for t in re.findall(r'「([^」]+)」', raw):
    check(t, "「」")
for t in re.findall(r"『([^』]+)』", raw):
    check(t, "『』")
for t in re.findall(r'“([^”]+)”', raw):
    check(t, "“”")

# ── 3. 禁用长划线 ──
for i, line in enumerate(raw.splitlines(), 1):
    if "—" in line or "–" in line:
        print(f"FAIL 禁用符: 第{i}行含长划线: {line.strip()[:40]}")
        fail += 1

# ── 4. 每行·最多1个 ──
for i, line in enumerate(raw.splitlines(), 1):
    n = line.count("·")
    if n > 1:
        print(f"FAIL 间隔号: 第{i}行含{n}个·: {line.strip()[:50]}")
        fail += 1

# ── 5. 结构断言 ──
if "殆知阁导读之一百五十四" not in raw:
    print("FAIL 结构: 标题缺导读编号之一百五十四")
    fail += 1
if "之一百五十四" not in raw.split("</title>")[1]:
    print("FAIL 结构: 正文 kicker 缺编号之一百五十四")
    fail += 1
if "mulu.html" not in raw:
    print("FAIL 结构: 页脚缺返回总目链接")
    fail += 1
for kw in ["文本来源", "时代局限", "逐字核对"]:
    if kw not in raw:
        print(f"FAIL 结构: 页脚缺「{kw}」")
        fail += 1
if re.search(r"<script", raw) or re.search(r'\ssrc=', raw) or re.search(r'@import|url\(', raw):
    print("FAIL 依赖: 存在外部依赖")
    fail += 1
for aid in range(1, 13):
    if f'id="s{aid}"' not in raw:
        print(f"FAIL 结构: 缺锚点 s{aid}")
        fail += 1

# ── 6. 柜格签牌篇名必须是库本真实篇名 ──
lines = [l.strip() for l in open(LIB, encoding="utf-8").read().splitlines()]
titles = {l for l in lines if l and len(l) <= 14}
for lab in re.findall(r'<a href="#s\d+"><em>([^<]+)</em></a>', raw):
    if norm(lab) not in {norm(t) for t in titles}:
        print(f"FAIL 柜签: 非库本篇名「{lab}」")
        fail += 1

print(f"\n共 {len(seen)} 项去重核验, 失败 {fail}")
sys.exit(1 if fail else 0)
