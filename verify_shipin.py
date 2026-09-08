#!/usr/bin/env python3
# 引文核验+排版红线+mulu 连续性：诗品
import re, sys

SRC = "daizhige-simplified/诗藏/诗话/诗品.txt"
PAGE = "daizhige-daodu/shipin.html"
MULU = "daizhige-daodu/mulu.html"

def norm(s):
    return "".join(c for c in s if "一" <= c <= "鿿")

src = norm(open(SRC, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
errs = []

# ---------- 1. 正扫：q 与「」引文须在库内 ----------
body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)

quotes = re.findall(r"<q>(.*?)</q>", body, flags=re.S)
quotes += re.findall(r"「([^」]*)」", body)
pos_total = 0
for q in quotes:
    n = norm(q)
    if not n:
        continue
    pos_total += 1
    if n in src:
        pass
    else:
        errs.append("引文核验失败: %r" % n[:42])
print("== 正扫引文 %d 处" % pos_total)

# ---------- 2. 反扫：非引文文本不得与库本长段重合 ----------
scrub = body
scrub = re.sub(r"<q>.*?</q>", "〓", scrub, flags=re.S)
scrub = re.sub(r"「[^」]*」", "〓", scrub)
scrub = re.sub(r"<[^>]+>", "", scrub)
runs = re.findall(r"[一-鿿]+", scrub)
WIN = 8
hits = 0
for r in runs:
    for i in range(len(r) - WIN + 1):
        w = r[i:i+WIN]
        if w in src:
            hits += 1
            errs.append("反扫撞库 窗口=%s 上下文=%s" % (w, r[max(0,i-8):i+WIN+8]))
if hits == 0:
    print("== 反扫 0 撞库（%d 个汉字段）" % len(runs))

# ---------- 3. 排版红线 ----------
if "—" in html or "–" in html:
    errs.append("出现长划线")
for i, ln in enumerate(html.splitlines(), 1):
    if ln.count("·") > 1:
        errs.append("第%d行·超1个: %s" % (i, ln.strip()[:50]))
bad_chars = sorted({c for c in html if ord(c) > 0xFFFF or (0xE000 <= ord(c) <= 0xF8FF) or (0x20000 <= ord(c) <= 0x3FFFF)})
if bad_chars:
    errs.append("PUA/扩展区字符: %s" % [hex(ord(c)) for c in bad_chars])
ext = re.findall(r'<(link|img|iframe|embed|object)\b|@import|src="http|href="http[^"]*\.(css|js|woff|ttf|png|jpg)', html)
if ext:
    errs.append("外部资源依赖: %s" % ext[:5])
else:
    print("== 零外部资源依赖 / 零长划线 / ·≤1 / 零PUA")

# ---------- 4. mulu 连续性与计数 ----------
mulu = open(MULU, encoding="utf-8").read()
nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
uniq = sorted(set(nos))
N = max(uniq)
dup = [x for x in set(nos) if nos.count(x) > 1]
if dup: errs.append("mulu 编号重复: %s" % dup)
if uniq != list(range(1, N + 1)):
    missing = sorted(set(range(1, N + 1)) - set(uniq))
    errs.append("mulu 编号断号: 缺 %s" % missing[:10])
else:
    print("== mulu 编号 1..%d 连续无重复（共 %d 条）" % (N, len(nos)))
expected = N  # mulu 在本页提交前更新，最大号应为本篇编号
def num2cn(n):
    d="零一二三四五六七八九"
    s=""
    if n>=100:
        s+=d[n//100]+"百"; n%=100
        if n==0: return s
    if n>=10:
        if n//10>1: s+=d[n//10]
        s+="十"; n%=10
    if n: s+=d[n]
    return s
anchor=num2cn(N)+"篇"
anchors = re.findall(anchor, mulu)
if len(anchors) < 2:
    errs.append("mulu 计数锚未更新为%s（现 %d 处）" % (anchor, len(anchors)))
else:
    print("== mulu 计数锚两处均为 %s" % anchor)
if 'href="shipin.html"' not in mulu:
    errs.append("mulu 未链接本页")
if '<span class="no mono">%d</span>' % expected not in mulu:
    errs.append("mulu 缺 %d 号条目" % expected)

nq = len(re.findall(r"<q>", body))
if errs:
    print("\nFAIL %d:" % len(errs))
    for e in errs: print("  ×", e)
    sys.exit(1)
print("\nALL PASS ✔  引文 %d 处全过" % pos_total)
