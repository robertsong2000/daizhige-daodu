#!/usr/bin/env python3
"""核验 beishan-jiujing.html 所有引文与库内原文逐字一致(去标点+NFKC+归一)"""
import re, sys, unicodedata

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/艺藏/饮馔/北山酒经.txt"
HTML = "/home/robertsong/workspace/claude/daizhige-daodu/beishan-jiujing.html"

VARIANT = {"巻": "卷", "幷": "并", "郞": "郎", "覩": "睹", "峯": "峰"}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VARIANT.get(c, c) for c in s)
    return re.sub(r"[^一-鿿㐀-䶿\U00020000-\U0003ffff]", "", s)

lib = norm(open(LIB, encoding="utf-8").read())
raw = open(HTML, encoding="utf-8").read()

fail = 0

# ── 1. 所有「」引语反扫 ──
brackets = re.findall(r'「([^」]+)」', raw)

# ── 2. 未加引号的原文元素(曲诀加粗句/瓮阵引文/曲饼引言) ──
plain = []
for m in re.finditer(r'<b style="color:var\(--zhi\)">([^<]+)</b>', raw):
    plain.append(m.group(1))
for m in re.finditer(r'<em>([^<]+)</em>', raw):
    plain.append(m.group(1))
for m in re.finditer(r'<span class="yan">([^<]+)</span>', raw):
    plain.append(m.group(1))

checks = [(t, "「」反扫") for t in brackets] + [(t, "素文") for t in plain]

seen = set()
for text, kind in checks:
    t = norm(text)
    if not t or t in seen:
        continue
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

print(f"\n共 {len(seen)} 项去重核验, 失败 {fail}")
sys.exit(1 if fail else 0)
