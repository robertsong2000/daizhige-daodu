#!/usr/bin/env python3
# 引文核验+排版红线+mulu 连续性：大金吊伐录
import re, sys, unicodedata

SRC = "daizhige-simplified/史藏/志存记录/大金吊伐录.txt"
PAGE = "daizhige-daodu/dajin-diaofa-lu.html"
MULU = "daizhige-daodu/mulu.html"

def norm(s):
    return "".join(c for c in s if "一" <= c <= "鿿")

src = norm(open(SRC, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
errs = []
oks = []

# ---------- 1. 正扫：q 与「」引文须在库内 ----------
body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)
WHITELIST = {"靖康之变", "靖康之耻", "海上之盟"}  # 页脚库外申报用语

quotes = re.findall(r"<q>(.*?)</q>", body, flags=re.S)
quotes += re.findall(r"「([^」]*)」", body)
pos_total = 0
for q in quotes:
    n = norm(q)
    if not n:
        oks.append("空引文（全角占位）跳过: %r" % q[:12])
        continue
    if n in WHITELIST:
        oks.append("白名单（库外申报语）: " + n)
        continue
    pos_total += 1
    if n in src:
        oks.append("OK[%d字] %s…" % (len(n), n[:18]))
    else:
        errs.append("引文核验失败: %r" % n[:40])
print("== 正扫引文 %d 处（另白名单 %d，空 %d）" % (pos_total, len(WHITELIST), len(quotes) - pos_total - sum(1 for q in quotes if not norm(q))))

# ---------- 2. 反扫：非引文文本不得与库本长段重合 ----------
scrub = body
scrub = re.sub(r"<q>.*?</q>", "〓", scrub, flags=re.S)
scrub = re.sub(r"「[^」]*」", "〓", scrub)
scrub = re.sub(r"<title>.*?</title>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<script.*?</script>", "〓", scrub, flags=re.S)
# 版面铬件（标签/出处/角签/题元）整块剔除
for cls in ["qsrc", "doctype", "k", "ann", "cap", "mono", "dt", "head"]:
    scrub = re.sub(r'<(\w+)[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>.*?</\1>' % cls, "〓", scrub, flags=re.S)
scrub = re.sub(r"<caption>.*?</caption>", "〓", scrub, flags=re.S)
scrub = re.sub(r"<h1>.*?</h1>", "〓", scrub, flags=re.S)
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
cnt = "二百五十四"
anchors = re.findall(r"二百五十[三四]篇", mulu)
if len(anchors) < 2:
    errs.append("mulu 计数锚文本不足两处: %s" % anchors)
elif any("二百五十三" in a for a in anchors):
    errs.append("mulu 计数未更新: %s" % anchors)
else:
    print("== mulu 计数锚两处均为 %s" % cnt)
if 'href="%s"' % "dajin-diaofa-lu.html" not in mulu:
    errs.append("mulu 未链接本页")
if '<span class="no mono">254</span>' not in mulu:
    errs.append("mulu 缺 254 号条目")

print("== 正扫引文 %d 处全过" % pos_total if not errs else "", )
if errs:
    print("\nFAIL %d:" % len(errs))
    for e in errs: print("  ×", e)
    sys.exit(1)
print("\nALL PASS ✔")
