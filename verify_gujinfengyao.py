#!/usr/bin/env python3
# 引文核验+排版红线+mulu 连续性：古今风谣
import re, sys

SRC = "daizhige-simplified/诗藏/诗集/古今风谣.txt"
PAGE = "daizhige-daodu/gujin-fengyao.html"
MULU = "daizhige-daodu/mulu.html"

def norm(s):
    return "".join(c for c in s if "一" <= c <= "鿿")

src = norm(open(SRC, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
errs = []
oks = []

# ---------- 1. 正扫：q、qbank li 与「」引文须在库内 ----------
body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)

quotes = re.findall(r"<q[^>]*>(.*?)</q>", body, flags=re.S)
qb = re.search(r'<div id="qbank".*?</div>', body, flags=re.S)
if not qb:
    errs.append("缺 qbank")
else:
    quotes += re.findall(r"<li[^>]*>(.*?)</li>", qb.group(0), flags=re.S)
quotes += re.findall(r"「([^」]*)」", body)
pos = 0
seen = set()
for q in quotes:
    n = norm(re.sub(r"<[^>]+>", "", q))
    if not n:
        continue
    pos += 1
    if n in src:
        seen.add(n)
    else:
        errs.append("引文核验失败: %r" % n[:40])
print("== 正扫引文 %d 处（去重 %d 条）全须库内" % (pos, len(seen)))

# ---------- 2. 反扫：非引文文本不得与库本长段重合 ----------
scrub = body
scrub = re.sub(r"<q[^>]*>.*?</q>", "〓", scrub, flags=re.S)
scrub = re.sub(r'<div id="qbank".*?</div>', "〓", scrub, flags=re.S)
scrub = re.sub(r"「[^」]*」", "〓", scrub)
scrub = re.sub(r"<title>.*?</title>", "〓", scrub, flags=re.S)
for cls in ["qsrc", "mono", "lab", "kicker", "hmeta", "skytip", "rd-era", "rd-lib",
            "yr", "zt", "tag", "fin", "gbtn", "cb-note", "slip", "chip"]:
    scrub = re.sub(r'<(\w+)[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>.*?</\1>' % cls, "〓", scrub, flags=re.S)
scrub = re.sub(r"<h1>.*?</h1>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<h2>.*?</h2>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<h3>.*?</h3>", "〓", scrub, flags=re.S)
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

# ---------- 4. mulu 连续性与本页条目 ----------
mulu = open(MULU, encoding="utf-8").read()
nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
uniq = sorted(set(nos))
N = max(uniq)
dup = [x for x in set(nos) if nos.count(x) > 1]
if dup:
    errs.append("mulu 编号重复: %s" % dup)
if uniq != list(range(1, N + 1)):
    missing = sorted(set(range(1, N + 1)) - set(uniq))
    errs.append("mulu 编号断号: 缺 %s" % missing[:10])
else:
    print("== mulu 编号 1..%d 连续无重复（共 %d 条）" % (N, len(nos)))
if N < 261:
    errs.append("mulu 尚无 261 号（压号失败，需顺延）")
elif nos.count(261) != 1:
    errs.append("261 号出现 %d 次" % nos.count(261))
m = re.findall(r"(二百五十[七八九]|二百六[〇十]?)篇", mulu)
c259 = mulu.count("二百六十一篇")
if c259 < 2:
    errs.append("mulu 计数锚 二百六十一篇 不足两处（现 %d）" % c259)
else:
    print("== mulu 计数锚两处均已更新")
if 'href="gujin-fengyao.html"' not in mulu:
    errs.append("mulu 未链接本页")

# ---------- 5. 本页计数锚 ----------
if mulu.count("二百五十九篇") >= 2 and html.count("二百五十九") < 1:
    errs.append("页面缺 计数锚")

if errs:
    print("\nFAIL %d:" % len(errs))
    for e in errs:
        print("  ×", e)
    sys.exit(1)
print("\nALL PASS ✔")
