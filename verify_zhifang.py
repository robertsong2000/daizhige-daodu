# -*- coding: utf-8 -*-
"""核验《职方外纪》导读：
1) quotes_zhifang.py 的 QUOTES 全部命中库本，且全部出现在页面（静态或 QT 引文库）；
2) 页面全部 .qt 引文块、.inline-q 内嵌引文、JS QT 引文库逐条命中库本；
3) PROSE 散文片段既命中库本也出现在页面；
4) 字数（库本去空白 30079）与页面所记一致；
5) 排版红线：禁长划线—–、每行·至多1个、无外部依赖、系列配色（墨底/纸白/竹青）。"""
import re, sys
from quotes_zhifang import QUOTES, PROSE

SRC = "../daizhige-simplified/史藏/地理/职方外纪.txt"
PAGE = "zhifang-waiji.html"
SLICES = "quotes_zhifang_slices.txt"

VAR = {"畧": "略", "逺": "远", "徳": "德", "氷": "冰", "眀": "明", "黙": "默", "葢": "盖", "髙": "高", "噉": "啖", "圜": "圆", "囬": "回"}
PUNCT = re.compile(r"[\s　。，、；：！？「」『』（）《》〈〉【】［］〔〕·．,.;:!?()\[\]{}\"'“”‘’…\-—―～※→←]")

def norm(s: str) -> str:
    for k, v in VAR.items():
        s = s.replace(k, v)
    return PUNCT.sub("", s)

book = norm(open(SRC, encoding="utf-8").read())
raw = open(SRC, encoding="utf-8").read()
page = open(PAGE, encoding="utf-8").read()
pagen = norm(page)
fails = []

# 1) QUOTES 命中库本 + 出现在页面
for qid, disp in QUOTES.items():
    if norm(disp) not in book:
        fails.append(f"[未命中库本] {qid}")
    if norm(disp) not in pagen:
        fails.append(f"[未上页] {qid}")

# 2) 页面静态 .qt / .inline-q 逐条命中库本（剔除 script 区，动态引文由 QT 检查覆盖）
page_noscript = re.sub(r"<script>.*?</script>", "", page, flags=re.S)
qblocks = re.findall(r'<div class="qt[^"]*">(.*?)<span class="qs">', page_noscript, re.S)
for frag in re.findall(r'<span class="inline-q">(.*?)</span>', page_noscript, re.S):
    qblocks.append(frag)
for b in qblocks:
    t = norm(re.sub(r"<[^>]+>", "", b))
    if t and t not in book:
        fails.append(f"[页面引文未命中] {t[:26]}…")

# JS QT 引文库
qt_src = re.search(r"var QT = \{(.*?)\n  \};", page, re.S)
if not qt_src:
    fails.append("[QT] 未找到引文库")
else:
    qt_items = re.findall(r'(\w+): "([^"]+)"', qt_src.group(1))
    if len(qt_items) < 30:
        fails.append(f"[QT] 条目过少 {len(qt_items)}")
    for k, v in qt_items:
        if norm(v) not in book:
            fails.append(f"[QT未命中] {k}")
        if (norm(v) not in pagen) and (f"'{k}'" not in page) and (f'"{k}"' not in page):
            fails.append(f"[QT未使用] {k}")

# 3) PROSE 命中库本 + 出现在页面
for frag in PROSE:
    if norm(frag) not in book:
        fails.append(f"[散文未命中库本] {frag}")
    if norm(frag) not in pagen:
        fails.append(f"[散文未上页] {frag}")

# 4) 切片文件一致性
for line in open(SLICES, encoding="utf-8"):
    qid, s = line.rstrip("\n").split("\t", 1)
    if qid in QUOTES and norm(QUOTES[qid]) != norm(s):
        fails.append(f"[切片不一致] {qid}")

# 5) 字数与卷次
nchars = len(re.sub(r"\s", "", raw))
if nchars != 30079:
    fails.append(f"[字数] 实测 {nchars} ≠ 30079")
if "库本去空白三万零七十九字" not in page:
    fails.append("[字数] 页面未标注去空白字数")
for v in ["职方外纪卷一", "职方外纪卷二", "职方外纪卷三", "职方外纪卷四", "职方外纪卷五"]:
    if v not in raw:
        fails.append(f"[卷次] 库本缺 {v}")

# 6) 排版红线
for i, ln in enumerate(page.split("\n"), 1):
    if ln.count("·") > 1:
        fails.append(f"[·超限] 第{i}行 {ln.count('·')}个")
for ch, name in [("—", "长划线—"), ("–", "en-dash–")]:
    if ch in page:
        fails.append(f"[禁字符] {name}")
if re.search(r'(src\s*=|<link|@import|url\(|https?://)', page):
    fails.append("[外部依赖] 页面含外链资源")
if "#191917" not in page or "#e8e4dc" not in page:
    fails.append("[配色] 墨底/纸白缺失")
if "#5f9270" not in page:
    fails.append("[配色] 竹青点缀色缺失")

# 报告
if fails:
    print("\n".join(fails))
    print(f"\n未通过：{len(fails)} 项（引文块 {len(qblocks)}，清单 {len(QUOTES)}，散文 {len(PROSE)}）")
    sys.exit(1)
print(f"全部核验通过：引文块 {len(qblocks)} + 清单 {len(QUOTES)} + 散文 {len(PROSE)} + QT 引文库，共命中库本 {len(qblocks) + len(QUOTES) + len(PROSE)}+ 项")
print("字数通过：库本去空白 30079 字，与页面所记一致；五卷卷次齐全")
print("排版红线通过：无长划线、每行·至多1个、零外部依赖、墨底纸白竹青合规")
