#!/usr/bin/env python3
"""核验 kaiyuan-tianbao-yishi.html 所有引文与库内原文逐字一致(去标点+NFKC+归一)"""
import re, sys, unicodedata

LIB = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/开元天宝遗事.txt"
HTML = "/home/robertsong/workspace/claude/daizhige-daodu/kaiyuan-tianbao-yishi.html"

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[^一-鿿㐀-䶿\U00020000-\U0003ffff]", "", s)

lib = norm(open(LIB, encoding="utf-8").read())
raw = open(HTML, encoding="utf-8").read()

fail = 0

# ── 1. 所有「」引语反扫 ──
checks = [(t, "「」反扫") for t in re.findall(r'「([^」]+)」', raw)]

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

# ── 2. 禁用长划线 ──
for i, line in enumerate(raw.splitlines(), 1):
    if "—" in line or "–" in line:
        print(f"FAIL 禁用符: 第{i}行含长划线: {line.strip()[:40]}")
        fail += 1

# ── 3. 每行·最多1个 ──
for i, line in enumerate(raw.splitlines(), 1):
    n = line.count("·")
    if n > 1:
        print(f"FAIL 间隔号: 第{i}行含{n}个·: {line.strip()[:50]}")
        fail += 1

# ── 4. 结构断言 ──
asserts = [
    ("编号", "殆知阁导读之一百五十五" in raw),
    ("页脚来源", "殆知阁简体库（github.com/robertsong2000/daizhigev20）" in raw),
    ("页脚核验", "引文均与库内文件逐字核对" in raw),
    ("页脚提醒", "请以史料之眼读之" in raw),
    ("锚点齐全", all(f'id="s{i}"' in raw for i in range(1, 7))),
    ("无外链script", "<script" not in raw and "src=" not in raw),
    ("无href外跳", "href=" not in raw),
]
for name, ok in asserts:
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        fail += 1

print(f"\n共 {len(seen)} 项引文去重核验 + {len(asserts)} 项结构断言, 失败 {fail}")
sys.exit(1 if fail else 0)
