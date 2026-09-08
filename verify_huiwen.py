#!/usr/bin/env python3
# 引文核验+排版红线：囘文类聚
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/集藏/文总集/囘文类聚.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/huiwen-leiju.html"
MULU = "/home/robertsong/workspace/claude/daizhige-daodu/mulu.html"

def norm(s):
    return "".join(c for c in s if "一" <= c <= "鿿")

src = norm(open(SRC, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
errs = []
oks = set()

# ---------- 1. 正扫 ----------
body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
body = re.sub(r"<style.*?</style>", "", body, flags=re.S)
body = re.sub(r"<title>.*?</title>", "", body, flags=re.S)

quotes = re.findall(r"<q\b[^>]*>(.*?)</q>", body, flags=re.S)
quotes += re.findall(r"<li>(.*?)</li>", re.search(r'<div id="qbank".*?</div>', body, flags=re.S).group(0), flags=re.S)
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

# ---------- 1b. JS 里的引文（knots/tags/chips 的 q 字段） ----------
script = "".join(re.findall(r"<script>(.*?)</script>", html, flags=re.S))
jsq = re.findall(r"q:'([^']+)'", script)
qbank_set = set(norm(x) for x in re.findall(r"<li>(.*?)</li>", html, flags=re.S))
for q in jsq:
    n = norm(q)
    if not n:
        continue
    if n not in src:
        errs.append("JS引文不在库内: %r" % n[:40])
    if n not in qbank_set:
        errs.append("JS引文缺入qbank: %r" % n[:30])
print("== JS q 字段 %d 条：库内 + qbank 双查" % len(jsq))

# ---------- 2. 回读断言：rvtext 必须 = fw 逐字倒排 ----------
for i in (1, 2, 3):
    fw = norm(re.search(r'<div class="fwt" id="fw%d"><q[^>]*>(.*?)</q>' % i, body, flags=re.S).group(1))
    rv = norm(re.search(r'<span class="rvtext">(.*?)</span>', body, flags=re.S).group(1)) if i == 1 else None
    # 逐个取各自 rvtext
    boxes = re.findall(r'<span class="rvtext">(.*?)</span>', body, flags=re.S)
    rv = norm(boxes[i-1])
    if rv != fw[::-1]:
        errs.append("回读断言失败 fw%d: fw=%s rv=%s" % (i, fw[:12], rv[:12]))
print("== 回读断言 3 组：rvtext == 顺读逐字倒排")

# ---------- 3. 反扫 ----------
scrub = body
scrub = re.sub(r"<q\b[^>]*>.*?</q>", "〓", scrub, flags=re.S)
scrub = re.sub(r'<div id="qbank".*?</div>', "〓", scrub, flags=re.S)
scrub = re.sub(r"「[^」]*」", "〓", scrub)
for cls in ["qsrc", "mono", "colnote", "tnote", "kicker", "fnote", "lbl", "song", "att", "use", "ig",
            "rvbox", "bigcap", "edict", "fv", "fs", "ktit", "rvtag", "njarr", "who"]:
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

# ---------- 4. 排版红线 ----------
if "—" in html or "–" in html:
    errs.append("出现长划线")
for i, ln in enumerate(html.splitlines(), 1):
    if ln.count("·") > 1:
        errs.append("第%d行·超1个: %s" % (i, ln.strip()[:50]))
bad = sorted({c for c in html if 0xE000 <= ord(c) <= 0xF8FF or 0x20000 <= ord(c) <= 0x3FFFF})
if bad:
    errs.append("PUA/扩展区字符: %s" % [hex(ord(c)) for c in bad])
ext = re.findall(r'<(link|img|iframe|embed|object)\b|@import|src="http|href="http[^"]*\.(css|js|woff|ttf|png|jpg)', html)
if ext:
    errs.append("外部资源依赖: %s" % ext[:5])
else:
    print("== 零外部资源依赖 / 零长划线 / ·≤1 / 零PUA")

# ---------- 5. div/q 配平 + 页脚 ----------
if body.count("<div") != body.count("</div>"):
    errs.append("div 不配平: %d/%d" % (body.count("<div"), body.count("</div>")))
for kw in ["文本来源", "引文", "时代局限提醒", "daizhigev20"]:
    if kw not in html:
        errs.append("页脚缺: %s" % kw)

# ---------- 6. mulu 联检（提交前 mulu 可能未更新，此处只检已有连续性） ----------
mulu = open(MULU, encoding="utf-8").read()
nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
if sorted(set(nos)) == list(range(1, len(nos) + 1)) and len(nos) == len(set(nos)):
    print("== mulu 编号 1..%d 连续无重" % max(nos))
else:
    from collections import Counter
    dup = [k for k, v in Counter(nos).items() if v > 1]
    errs.append("mulu 编号异常: max=%d 重复=%s 缺号=%s" % (max(nos), dup[:5], [x for x in range(1, max(nos)+1) if x not in set(nos)][:5]))

if errs:
    print("\nFAIL %d:" % len(errs))
    for e in errs[:40]:
        print("  ×", e)
    sys.exit(1)
print("\nALL PASS ✔")
