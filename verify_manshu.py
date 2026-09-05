#!/usr/bin/env python3
"""核验 manshu.html 所有引文与库内原文逐字一致(去标点+归一)"""
import re, sys, unicodedata

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/蛮书.txt"
HTML = "/home/robertsong/workspace/claude/daizhige-daodu/manshu.html"

VARIANT = {"巻": "卷", "幷": "并", "郞": "郎", "覩": "睹"}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VARIANT.get(c, c) for c in s)
    return re.sub(r"[^一-鿿㐀-䶿\U00020000-\U0003ffff]", "", s)

lib = norm(open(LIB, encoding="utf-8").read())
raw = open(HTML, encoding="utf-8").read()

fail = 0

# ── 1. 引文块:取 .who 之后到 .src 之前的文本 ──
quotes = re.findall(r'<span class="who">[^<]*</span>\s*(.*?)\s*<span class="src">', raw, re.S)

# ── 2. 短语与谣辞 ──
snippets = [
    "冬时欲归来，高黎共上雪。秋夏欲归来，无那穹赕热。春时欲归来，平中络赂绝。",
    "此条原在巻八蛮夷风俗篇末。",
    "原本作龙口城。",
    "原缺",
    "玷苍山顶立旗，先上到旗下为一次上。",
    "抚我则后，虐我则雠。",
    "咸通五年六月，左授夔州都督府长史。",
    "河赕贾客在寻传覊离未还者，为之谣曰",
    "贞元十年，三使悉至阙下",
]

# ── 3. 页面所有「」引语反扫 ──
brackets = re.findall(r'「([^」]+)」', raw)

checks = [(q, "quote块") for q in quotes] + [(s, "短语") for s in snippets] + [(b, "「」反扫") for b in brackets]

seen = set()
for text, kind in checks:
    t = norm(text)
    if not t or t in seen:
        continue
    seen.add(t)
    if t in lib:
        print(f"PASS {kind}: {text[:18]}... ({len(t)}字)")
    else:
        lo, hi = 0, len(t)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if t[:mid] in lib:
                lo = mid
            else:
                hi = mid - 1
        print(f"FAIL {kind}: {text[:34]}...")
        print(f"      连续匹配至第{lo}字: ...{t[max(0,lo-8):lo]}【{t[lo:lo+10]}】...")
        fail += 1

# ── 4. 禁用长划线 ──
for i, line in enumerate(raw.splitlines(), 1):
    if "—" in line or "–" in line:
        print(f"FAIL 禁用符: 第{i}行含长划线: {line.strip()[:40]}")
        fail += 1

# ── 5. 每行·最多1个 ──
for i, line in enumerate(raw.splitlines(), 1):
    n = line.count("·")
    if n > 1:
        print(f"FAIL 间隔号: 第{i}行含{n}个·: {line.strip()[:50]}")
        fail += 1

print(f"\n共 {len(seen)} 项去重核验, 失败 {fail}")
sys.exit(1 if fail else 0)
