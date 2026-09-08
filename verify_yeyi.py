#!/usr/bin/env python3
# 引文核验+排版红线+mulu 连续性：野议
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/野议.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yeyi.html"
MULU = "/home/robertsong/workspace/claude/daizhige-daodu/mulu.html"
NUM = 266

def norm(s):
    return "".join(c for c in s if "一" <= c <= "鿿")

src = norm(open(SRC, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
errs = []
oks = set()

# ---------- 0. 红线：长划线 ----------
for ch, name in [("—", "EM DASH —"), ("–", "EN DASH –"), ("‒", "FIGURE DASH"), ("─", "BOX ─")]:
    if ch in html:
        errs.append("红线: 页面含 %s" % name)

# ---------- 1. 正扫：q、qbank li 与「」引文须在库内 ----------
body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)

quotes = re.findall(r"<q>(.*?)</q>", body, flags=re.S)
qb = re.search(r'<div id="qbank".*?</div>', body, flags=re.S)
if qb:
    quotes += [m for m in re.findall(r"<li>([^<]*)", qb.group(0)) if norm(m)]
quotes += re.findall(r"「([^」]*)」", body)
pos = 0
for q in quotes:
    n = norm(q)
    if not n:
        continue
    pos += 1
    if n in src:
        oks.add(n)
    else:
        errs.append("引文核验失败: %r" % n[:40])
print("== 正扫引文 %d 处（去重 %d 条）全须库内" % (pos, len(oks)))

# ---------- 2. 反扫：非引文文本不得与库本长段重合 ----------
scrub = body
scrub = re.sub(r"<q>.*?</q>", "〓", scrub, flags=re.S)
scrub = re.sub(r'<div id="qbank".*?</div>', "〓", scrub, flags=re.S)
scrub = re.sub(r"「[^」]*」", "〓", scrub)
for cls in ["qsrc", "fm", "mono", "ord", "sec-no", "dawnnote", "calnote"]:
    scrub = re.sub(r'<(\w+)[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>.*?</\1>' % cls, "〓", scrub, flags=re.S)
scrub = re.sub(r"<h1>.*?</h1>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<h2>.*?</h2>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<[^>]+>", "", scrub)
runs = re.findall(r"[一-鿓]+", scrub)
WIN = 8
hits = 0
for r in runs:
    for i in range(len(r) - WIN + 1):
        w = r[i:i + WIN]
        if w in src:
            hits += 1
            errs.append("反扫命中(%d): %r" % (WIN, r[max(0, i - 6):i + WIN + 6]))
            break
print("== 反扫 %d 字窗：runs=%d 命中=%d" % (WIN, len(runs), hits))

# ---------- 3. 红线：每行 · 最多 1 个 ----------
text = re.sub(r"<[^>]+>", "", re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S))
for ln, line in enumerate(text.split("\n"), 1):
    if line.count("·") > 1:
        errs.append("红线: 行 %d 含 %d 个·" % (ln, line.count("·")))

# ---------- 4. mulu 编号连续性（先按未更新状态检查 1..262） ----------
mu = open(MULU, encoding="utf-8").read()
nos = sorted(set(int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', mu)))
if nos != list(range(1, len(nos) + 1)):
    errs.append("mulu 编号不连续: %s..%s 缺%s" % (nos[0], nos[-1], sorted(set(range(1, nos[-1] + 1)) - set(nos))[:10]))
else:
    print("== mulu 现有编号 1..%d 连续" % nos[-1])
    if nos[-1] < NUM:
        print("   （本页应为第 %d 篇，mulu 待更新）" % NUM)

print()
if errs:
    print("!! %d 个问题" % len(errs))
    for e in errs[:40]:
        print("  -", e)
    sys.exit(1)
print("ALL PASS")
