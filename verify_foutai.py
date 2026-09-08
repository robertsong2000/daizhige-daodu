#!/usr/bin/env python3
"""否泰录 引文核验：页面全部 .q 元素与库本去非汉字归一后子串双向比对。"""
import re, sys, html as H

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/否泰录.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/fou-tai-lu.html"

def norm(s):
    return "".join(ch for ch in s if "一" <= ch <= "鿿")

lib = norm(open(LIB, encoding="utf-8").read())
page = open(PAGE, encoding="utf-8").read()
page = re.sub(r"<script[\s\S]*?</script>", "", page)

qs = []
for m in re.finditer(r'class="q"[^>]*>([\s\S]*?)</(blockquote|span|td|p)>', page):
    txt = H.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
    if norm(txt):
        qs.append((m.start(), norm(txt), txt.strip()[:40]))

ok = bad = 0
for pos, n, raw in qs:
    if n in lib:
        ok += 1
    else:
        bad += 1
        print("FAIL @%d: %s" % (pos, raw))
print("q elements: %d, pass: %d, fail: %d" % (len(qs), ok, bad))

for ch in ("—", "–", "─", "──"):
    if ch in page:
        print("FORBIDDEN DASH:", ch)
sys.exit(1 if bad else 0)
