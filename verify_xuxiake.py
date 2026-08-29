#!/usr/bin/env python3
"""核验 xuxiake-youji.html：引文逐字比对库内文件 + 排版红线。"""
import re, sys, html

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/xuxiake-youji.html"
BOOK = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/徐霞客游记.txt"

VARIANT = str.maketrans({"乆": "久", "寕": "宁"})
PUNCT = re.compile(r"[，。；：、！？（）「」『』《》〈〉【】\[\]…·\.\,\;\:\?\!\-　\s\r\n　""'']+")

def norm(s: str) -> str:
    return PUNCT.sub("", html.unescape(s)).translate(VARIANT)

book = norm(open(BOOK).read())
page_src = open(PAGE).read()

fails = []

# 1. 引文核验：所有 class=t 的引文正文须为库内文件子串
blocks = re.findall(r'<span class="t">(.*?)</span>', page_src, re.S)
if not blocks:
    fails.append("未找到任何 .t 引文块")
for i, raw in enumerate(blocks, 1):
    txt = norm(re.sub(r"<[^>]+>", "", raw))
    if not txt:
        fails.append(f"引文#{i}: 空内容")
        continue
    if txt not in book:
        # 找最长可匹配前缀，帮助定位断点
        lo, hi = 0, len(txt)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if txt[:mid] in book:
                lo = mid
            else:
                hi = mid - 1
        fails.append(f"引文#{i} 不在库内文件中: [{txt[:lo]}]<<<断>>>{txt[lo:lo+14]}")

# 2. 引文数量下限
n_quotes = len(blocks)
if n_quotes < 10:
    fails.append(f"引文块仅 {n_quotes} 个，少于预期 8")

# 3. 排版红线：禁长划线
for ch, name in [("—", "—(em dash)"), ("–", "–(en dash)"), ("‒", "―")]:
    if ch in page_src:
        fails.append(f"页面含 {name}")

# 4. 每行 · 最多 1 个（按源码行）
for ln, line in enumerate(page_src.splitlines(), 1):
    if line.count("·") > 1:
        fails.append(f"第{ln}行含 {line.count('·')} 个 ·")

# 5. 外部依赖检查
if re.search(r'(src|href)\s*=\s*["\']https?://', page_src):
    fails.append("含外部资源引用")

# 6. 库内文件体量
raw = open(BOOK).read()
print(f"库内文件字符数: {len(raw)}")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"PASS: {n_quotes} 条引文全部逐字命中，排版红线通过")
