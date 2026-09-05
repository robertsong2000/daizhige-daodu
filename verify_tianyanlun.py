# -*- coding: utf-8 -*-
"""核验《天演论》导读：
1) quotes_tianyanlun.py 显示串 与 库本切片（去标点+归一后）逐字相等；
2) 页面全部 .qt 引文块、散文内嵌片段、篇目 35 句首句均命中库本；
3) 词频数字（天行72 物竞61 人治52 天择25）与库本实测一致；
4) 排版红线：禁长划线、每行·至多1个、无外部依赖、系列配色。"""
import re, sys, json
from quotes_tianyanlun import QUOTES, PROSE

SRC = "../daizhige-simplified/子藏/笔记/天演论.txt"
PAGE = "tianyan-lun.html"
SLICES = "quotes_tianyanlun_slices.txt"

# 库本异体/讹写归一表（实测归纳；本书引文区内未见 PUA 字）
VAR = {
    "圗": "图", "圖": "图",
}

PUNCT = re.compile(r"[\s　。，、；：！？「」『』（）《》〈〉【】［］〔〕·．,.;:!?()\[\]{}\"'“”‘’…\-—―～※①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]")

def norm(s: str) -> str:
    for k, v in VAR.items():
        s = s.replace(k, v)
    return PUNCT.sub("", s)

book = norm(open(SRC, encoding="utf-8").read())
page = open(PAGE, encoding="utf-8").read()
fails = []

# 1) 显示串 == 库本切片
slices = {}
for line in open(SLICES, encoding="utf-8"):
    qid, s = line.rstrip("\n").split("\t", 1)
    slices[qid] = s
for qid, disp in QUOTES.items():
    if qid not in slices:
        fails.append(f"[缺切片] {qid}")
        continue
    if norm(disp) != norm(slices[qid]):
        fails.append(f"[异文] {qid}: 显示串与库本切片不一致")
    if norm(disp) not in book:
        fails.append(f"[未命中] {qid}")

# 2) 页面 .qt 引文块（去出处）与 .sheet 声部纸引文，逐条命中库本
blocks = re.findall(r'<div class="qt[^>]*>(.*?)<span class="qs">', page, re.S)
blocks += re.findall(r'<span class="tag">.*?</span>\s*<p>(.*?)</p>', page, re.S)
for b in blocks:
    t = norm(re.sub(r"<[^>]+>", "", b))
    if t and t not in book:
        fails.append(f"[页面引文未命中] {t[:30]}…")

# 散文内嵌片段
for frag in PROSE:
    if norm(frag) not in book:
        fails.append(f"[散文片段未命中] {frag}")

# 3) 篇目 35 句首句：与切片一致且命中库本
m = re.search(r'<script id="panes" type="application/json">(.*?)</script>', page, re.S)
if not m:
    fails.append("[篇目] 未找到 panes JSON")
else:
    panes = json.loads(m.group(1))
    if len(panes) != 35:
        fails.append(f"[篇目] 条数 {len(panes)} ≠ 35")
    for i, d in enumerate(panes, 1):
        pid = f"p{i:02d}"
        if pid not in slices:
            fails.append(f"[篇目缺切片] {pid}")
            continue
        if norm(d["t"]) != norm(slices[pid]):
            fails.append(f"[篇目异文] {pid} {d['n']}")
        if norm(d["t"]) not in book:
            fails.append(f"[篇目未命中] {pid} {d['n']}")

# 4) 词频数字
raw = open(SRC, encoding="utf-8").read()
for w, n in [("天行", 72), ("物竞", 61), ("人治", 52), ("天择", 25)]:
    if raw.count(w) != n:
        fails.append(f"[词频] {w} 库本 {raw.count(w)} ≠ 页面 {n}")

# 5) 排版红线
for i, ln in enumerate(page.split("\n"), 1):
    if ln.count("·") > 1:
        fails.append(f"[·超限] 第{i}行 {ln.count('·')}个")
for ch, name in [("—", "长划线—"), ("–", "en-dash–")]:
    if ch in page:
        fails.append(f"[禁字符] {name}")
if re.search(r'(src\s*=|<link|@import|url\(|https?://)', page):
    fails.append("[外部依赖] 页面含外链资源")
if "--bg:#191917" not in page.replace(" ", "") or "--paper:#e8e4dc" not in page.replace(" ", ""):
    fails.append("[配色] 系列底色/纸色缺失")
if "--c:#5f9270" not in page.replace(" ", ""):
    fails.append("[配色] 竹青点缀色缺失")

# 报告
nq = len(QUOTES) + len(blocks) + len(PROSE)
if fails:
    print("\n".join(fails))
    print(f"\n未通过：{len(fails)} 项（引文块{len(blocks)}，清单{len(QUOTES)}，散文片段{len(PROSE)}）")
    sys.exit(1)
print(f"全部核验通过：引文块{len(blocks)} + 清单{len(QUOTES)} + 散文片段{len(PROSE)} + 篇目35句，共{nq + 35}项命中库本")
print("词频通过：天行72 物竞61 人治52 天择25 与库本实测一致")
print("排版红线通过：无长划线、每行·至多1个、零外部依赖、配色合规")
