#!/usr/bin/env python3
# 核验 doue-yuan.html：引文逐字（去标点+空白归一）、曲牌/字数实测、排版红线
import re, sys, unicodedata

PAGE = "doue-yuan.html"
SRC = {"doue": "../daizhige-simplified/诗藏/剧曲/窦娥冤.txt"}

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        if unicodedata.category(ch).startswith(("P", "S")):
            continue
        out.append(ch)
    return "".join(out)

def strip_tags(html):
    html = re.sub(r"<br\s*/?>", "", html)
    html = re.sub(r"<[^>]+>", "", html)
    return html

src_raw = open(SRC["doue"]).read()
src_norm = {"doue": norm(src_raw)}
page = open(PAGE).read()
page_text = strip_tags(page)

fails = []
nq = 0

# 1) 全部 data-src 引文逐条比对：扫描器处理嵌套标签与 div/span 两种容器
def find_q_blocks(html):
    blocks = []
    for m in re.finditer(r'data-src="(\w+)"[^>]*>', html):
        key, pos, depth, end_close = m.group(1), m.end(), 1, None
        while depth > 0:
            nxt = re.search(r'<(/?)(span|div)\b[^>]*>', html[pos:])
            if not nxt:
                end_close = None
                break
            depth += -1 if nxt.group(1) else 1
            if depth == 0:
                end_close = pos + nxt.start()
            pos += nxt.end()
        if end_close is None:
            fails.append(f"Q[{key}] 标签未闭合")
            continue
        blocks.append((key, html[m.end():end_close]))
    return blocks

for key, frag in find_q_blocks(page):
    nq += 1
    frag = re.sub(r'<span class="who">.*?</span>', "", frag, flags=re.S)
    if key not in SRC:
        fails.append(f"Q 未知来源: {key}")
    elif norm(strip_tags(frag)) not in src_norm[key]:
        fails.append(f"Q[{key}] 不匹配: {strip_tags(frag)[:50]}")

# 2) 机器计数：总字数（去空白含标点）、分折字数、曲牌数
def hanzi_ws(s):
    return len(re.sub(r"\s", "", s))

total = hanzi_ws(src_raw)
acts = re.split(r"《[^》]+》", src_raw)[1:]
act_chars = [hanzi_ws(a) for a in acts]
act_paiban = [len(re.findall(r"【[^】]+】", a)) for a in acts]
checks = [
    ("总字数 15,207", total == 15207 and "15,207" in page),
    ("五折齐全", len(acts) == 5),
    ("分折字数", act_chars == [1148, 2828, 3884, 1912, 5402]),
    ("曲牌总数 41", sum(act_paiban) == 41),
    ("分折曲牌数与页面对应", act_paiban == [1, 9, 11, 10, 10]
        and all(f"{n} 支曲牌" in page for n in act_paiban)),
]
for name, ok in checks:
    if not ok:
        fails.append(f"计数不符: {name} (acts={act_chars}, paiban={act_paiban})")

# 3) 排版红线：禁 — –；每行 · ≤1；无外部依赖；篇号 之六十
if "—" in page or "–" in page:
    fails.append("排版: 出现长划线")
for i, line in enumerate(page.split("\n"), 1):
    if line.count("·") > 1:
        fails.append(f"排版: 第{i}行 · 超过1个")
if re.search(r'<script[^>]+src=|<link[^>]+href=|url\(', page):
    fails.append("排版: 出现外部依赖")
if "之六十一" not in page:
    fails.append("篇号: 页内未标之六十一")
for need in ["daizhigev20", "逐字核验", "以文献视之"]:
    if need not in page:
        fails.append(f"页脚缺失: {need}")

print(f"引文 data-src: {nq} 段, 源 {total} 字, 曲牌 {act_paiban}")
if fails:
    print("FAIL", len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("ALL PASS")
