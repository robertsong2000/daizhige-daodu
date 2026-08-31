#!/usr/bin/env python3
"""verify wanli-yehuobian.html quotes against daizhige source + layout redlines."""
import re, sys, unicodedata

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/wanli-yehuobian.html"
SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/万历野获编.txt"

VAR = {"惥": "恿", "俛": "俯", "峯": "峰", "畧": "略"}
PUNC = re.compile(r"[\s，。、；：？！「」『』《》〈〉（）()“”‘’\"'`【】\[\].,;:?!…·{}※]")

def norm(s: str) -> str:
    for k, v in VAR.items():
        s = s.replace(k, v)
    return PUNC.sub("", s)

html = open(HTML, encoding="utf-8").read()
src = open(SRC, encoding="utf-8").read()

fails = []

# 1) banned dashes
if "—" in html or "–" in html:
    fails.append("banned em/en dash present")

# 2) interpunct per rendered line
text = re.sub(r"<script[\s\S]*?</script>", "", html)
text = re.sub(r"<style[\s\S]*?</style>", "", text)
plain = re.sub(r"<[^>]+>", "\n", text)
for i, line in enumerate(plain.splitlines()):
    if line.count("·") > 1:
        fails.append(f"line {i} has >1 interpunct: {line[:60]}")

# 3) every quote block (.qt whole blockquote) and inline span (.q) verified against source
qt_blocks = [re.sub(r"<[^>]+>", "", b) for b in re.findall(r'<div class="qt">([\s\S]*?)</div>', html)]
q_spans = [re.sub(r"<[^>]+>", "", b) for b in re.findall(r'<(?:span|em)[^>]*class="[^"]*\bq\b[^"]*"[^>]*>([\s\S]*?)</(?:span|em)>', html)]
nsrc = norm(src)
seen = set()
checked = 0
for q in qt_blocks + q_spans:
    nq = norm(q)
    if not nq or nq in seen:
        continue
    seen.add(nq)
    checked += 1
    if nq not in nsrc:
        fails.append(f"quote NOT in source: {q[:70]}")
    if "—" in q or "–" in q:
        fails.append(f"quote contains banned dash: {q[:40]}")
if checked < 23:
    fails.append(f"only {checked} distinct quotes verified, expected >=23")

# 4) footer essentials
for key in ["殆知阁古代文献简体库", "逐字核验", "时代局限" if "时代局限" in html else "阅读时须加分辨"]:
    if key not in html:
        fails.append(f"footer missing: {key}")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"OK: {checked} distinct quotes verified against source; no banned dashes; interpunct rule pass; footer ok")
