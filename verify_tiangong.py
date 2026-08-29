#!/usr/bin/env python3
"""核验 tiangong-kaiwu.html 中的引文是否与殆知阁库内《天工开物》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/农家/天工开物.txt"

def norm(s):
    s = re.sub(r"[^一-鿿]", "", s)  # 去标点/空白/字母数字
    return s

# (页面引文, 库内出处行号提示)
QUOTES = [
    ("生人不能久生而五谷生之，五谷不能自生而生人生之。", "乃粒"),
    ("纨裤之子，以赭衣视笠蓑；经生之家，以农夫为诟詈。晨炊晚饷，知其味而忘其源者众矣！", "乃粒"),
    ("火药机械之窍，其先凿自西番与南裔，而后乃及于中国。", "佳兵"),
    ("岂中国辉山、媚水者，萃在人身，而天地菁华止有此数哉？", "珠玉"),
    ("祟在种内，反怨鬼神。", "乃粒·稻灾"),
    ("古碎器日本国极珍重，真者不惜千金。", "陶埏"),
    ("水火既济而土合。", "陶埏"),
    ("陶成雅器，有素肌玉骨之象焉。", "陶埏"),
    ("今时妄想进身博官者，人人张目而道，著书以献，未必尽由试验。", "佳兵"),
]

text = norm(open(SRC).read())
fail = 0
for q, where in QUOTES:
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    fail += 0 if ok else 1

# 反向抽查：HTML 里所有「」引文块也必须能对上（防止写页时手滑改字）
import os
path = "/home/robertsong/workspace/claude/daizhige-daodu/tiangong-kaiwu.html"
if not os.path.exists(path):
    print("\n（页面尚未生成，跳过 HTML 抽查）")
    sys.exit(1 if fail else 0)
html = open(path).read()
html_quotes = re.findall(r"[「『]([^「」『』]{6,})[」』]", html)
for m in re.finditer(r"<blockquote>\s*<p>(.*?)</p>", html, re.S):
    html_quotes.append(re.sub(r"<[^>]+>", "", m.group(1)))
print(f"\nHTML 内引文块 {len(html_quotes)} 个：")
for q in html_quotes:
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), q[:24])
    fail += 0 if ok else 1

sys.exit(1 if fail else 0)
