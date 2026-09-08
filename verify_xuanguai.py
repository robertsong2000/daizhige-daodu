#!/usr/bin/env python3
# 引文核验+排版红线+mulu 连续性：玄怪录
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/玄怪录.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/xuanguai-lu.html"
MULU = "/home/robertsong/workspace/claude/daizhige-daodu/mulu.html"
NUM = 288

def norm(s):
    return "".join(c for c in s if "一" <= c <= "鿿")

src = norm(open(SRC, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
errs = []
oks = set()

# ---------- 1. 正扫：q 与「」引文须在库内 ----------
body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)

quotes = re.findall(r"<q[^>]*>(.*?)</q>", body, flags=re.S)
qb = re.search(r'<div[^>]*id="qbank".*?</div>', body, flags=re.S)
if qb:
    quotes += re.findall(r"<li>(.*?)</li>", qb.group(0), flags=re.S)
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
scrub = re.sub(r"<q[^>]*>.*?</q>", "〓", scrub, flags=re.S)
scrub = re.sub(r'<div[^>]*id="qbank".*?</div>', "〓", scrub, flags=re.S)
scrub = re.sub(r"「[^」]*」", "〓", scrub)
scrub = re.sub(r"<title>.*?</title>", "〓", scrub, flags=re.S)
for cls in ["qsrc", "mono", "cplate", "axnode", "tnote", "hmeta", "chint", "kicker", "fnote", "who", "sno", "lbl", "lab", "zz", "lsrc", "day", "corr", "src", "fin"]:
    scrub = re.sub(r'<(\w+)[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>.*?</\1>' % cls, "〓", scrub, flags=re.S)
scrub = re.sub(r"<h1>.*?</h1>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<h2>.*?</h2>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<[^>]+>", "", scrub)
runs = re.findall(r"[一-鿿]+", scrub)
WIN = 8
hits = 0
for r in runs:
    for i in range(len(r) - WIN + 1):
        w = r[i:i+WIN]
        if w in src:
            hits += 1
            errs.append("反扫撞库 窗口=%s 上下文=%s" % (w, r[max(0,i-6):i+WIN+6]))
if hits == 0:
    print("== 反扫 0 撞库（%d 个汉字段）" % len(runs))

# ---------- 3. 排版红线 ----------
if "—" in html or "–" in html:
    errs.append("出现长划线")
for i, ln in enumerate(html.splitlines(), 1):
    if ln.count("·") > 1:
        errs.append("第%d行·超1个: %s" % (i, ln.strip()[:50]))
bad = sorted({c for c in html if ord(c) > 0xFFFF or (0xE000 <= ord(c) <= 0xF8FF) or (0x20000 <= ord(c) <= 0x3FFFF)})
if bad:
    errs.append("PUA/扩展区字符: %s" % [hex(ord(c)) for c in bad])
ext = re.findall(r'<(link|img|iframe|embed|object)\b|@import|src="http|href="http[^"]*\.(css|js|woff|ttf|png|jpg)', html)
if ext:
    errs.append("外部资源依赖: %s" % ext[:5])
else:
    print("== 零外部资源依赖 / 零长划线 / ·≤1 / 零PUA")

if "--page-only" in sys.argv:
    if errs:
        print("\nFAIL %d:" % len(errs))
        for e in errs: print("  ×", e)
        sys.exit(1)
    print("\nPAGE PASS ✔（引文 %d 处）" % pos)
    sys.exit(0)

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
if N != NUM:
    errs.append("mulu 最大号 %d != 本篇 %d（并行会话又出新号？）" % (N, NUM))
cn = "〇一二三四五六七八九"
def cnum(n):
    if n < 10: return cn[n]
    if n < 20: return "十" + (cn[n-10] if n % 10 else "")
    if n < 100: return cn[n // 10] + "十" + (cn[n % 10] if n % 10 else "")
    return None
want = "二百八十" + cnum(NUM - 280)
anchors = re.findall(r"(二百八十[一二三四五六七八九]*篇)(?=导读合订)", mulu) + \
          re.findall(r"(二百八十[一二三四五六七八九]*篇)(?=导读，)", mulu)
if len(anchors) < 2:
    errs.append("mulu 计数锚文本不足两处: %s" % anchors)
elif any(a != want + "篇" for a in anchors):
    errs.append("mulu 计数未更新至 %s: %s" % (want, anchors))
else:
    print("== mulu 计数锚两处均为 %s篇" % want)
if 'href="xuanguai-lu.html"' not in mulu:
    errs.append("mulu 未链接本页")
if ('<span class="no mono">%d</span>' % NUM) not in mulu:
    errs.append("mulu 缺 %d 号条目" % NUM)

if errs:
    print("\nFAIL %d:" % len(errs))
    for e in errs: print("  ×", e)
    sys.exit(1)
print("\nALL PASS ✔")
