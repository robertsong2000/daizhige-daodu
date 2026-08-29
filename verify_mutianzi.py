#!/usr/bin/env python3
# 核验 mutianzi-zhuan.html：引文逐字（去标点+空白归一，保留□●■）、机器计数、排版红线
import re, sys, unicodedata

PAGE = "mutianzi-zhuan.html"
SRC = {
    "mtz":    "../daizhige-simplified/史藏/志存记录/穆天子传.txt",
    "jinshu": "../daizhige-simplified/史藏/正史/晋书.txt",
    "shiji":  "../daizhige-simplified/史藏/正史/史记集解三家注索隐正义.txt",
    "suoyin": "../daizhige-simplified/史藏/正史/史记索隐.txt",
}
KEEP = set("□●■")  # 缺字符号参与比对，不归一

def norm(s):
    out = []
    for ch in s:
        if KEEP & set(ch):
            out.append(ch)
        elif ch.isspace():
            continue
        elif unicodedata.category(ch).startswith("P"):
            continue
        elif unicodedata.category(ch).startswith("S"):
            continue
        else:
            out.append(ch)
    return "".join(out)

def strip_tags(html):
    html = re.sub(r"<br\s*/?>", "", html)
    html = re.sub(r"<[^>]+>", "", html)
    return html

src_text = {k: open(v).read() for k, v in SRC.items()}
src_norm = {k: norm(v) for k, v in src_text.items()}
page = open(PAGE).read()
page_text = strip_tags(page)
page_norm = norm(page_text)

fails = []
nq = 0

# 1) .q 引文按 data-src 逐条比对
for m in re.finditer(r'<span class="q" data-src="(\w+)">(.*?)</span>', page, re.S):
    key, frag = m.group(1), strip_tags(m.group(2))
    nq += 1
    if norm(frag) not in src_norm[key]:
        fails.append(f"Q[{key}] 不匹配: {frag[:50]}")

# 2) 历日签 / 里程带标签 / 八骏名牌 / qnote 内引文，逐条对穆传库本
EXTRA = [
    # 历日签 .ev
    "天子北征，乃绝漳水", "至于□觞", "雨雪，天子猎于并山之西阿", "北征于犬戎",
    "北风雨雪", "西征", "饮于河水之阿", "鹜行至于阳纡之山",
    # 八骏名牌
    "赤骥", "盗骊", "白义", "逾轮", "山子", "渠黄", "华骝", "绿耳",
    # 里程带 .li
    "三千有四百里", "二千又五百里", "千又五百里", "七百里", "三百里", "三千里", "千有九百里",
    # 里程带 .to
    "宗周", "河宗之邦", "西夏氏", "河首襄山", "昆仑之丘", "赤乌氏舂山",
    "群玉之山", "西王毋之邦", "旷原之野",
    # 干支
    "戊寅", "庚辰", "癸未", "乙酉", "庚寅", "甲午", "丙午",
    # qnote 内成段引文
    "戊寅，天子北征，乃绝漳水", "癸未，雨雪，天子猎于并山之西阿",
    "庚寅，北风雨雪。天子以寒之故，命王属休",
    "膜拜而受", "取玉三乘", "载玉万只", "六师之人翔畈于旷原，得获无强，鸟兽绝群",
    "载羽百车",
]
ne = 0
for frag in EXTRA:
    ne += 1
    if norm(frag) not in src_norm["mtz"]:
        fails.append(f"EXTRA 不匹配: {frag[:50]}")
if norm("谯周不信此事") not in src_norm["suoyin"]:
    fails.append("EXTRA[suoyin] 不匹配: 谯周不信此事")

# 3) 机器计数复核
t = src_text["mtz"]
total = len(t)
sq = t.count("□"); sk = t.count("●"); sh = t.count("■")
burnt = sq + sk + sh
checks = [
    (f"8,342 字", total == 8342 and "8,342" in page),
    (f"□230", sq == 230 and "□ 230" in page),
    (f"●85", sk == 85 and "● 85" in page),
    (f"■23", sh == 23 and "■ 23" in page),
    (f"338 处", burnt == 338 and "338" in page),
    ("红点 4/100", page.count('class="burnt"') == 4),
]
for name, ok in checks:
    if not ok:
        fails.append(f"计数不符: {name}")

# 4) 排版红线：禁 — –；每行 · ≤1；无外部依赖
if "—" in page or "–" in page:
    fails.append("排版: 出现长划线")
for i, line in enumerate(page.split("\n"), 1):
    if line.count("·") > 1:
        fails.append(f"排版: 第{i}行 · 超过1个")
if re.search(r'<script[^>]+src=|<link[^>]+href=|url\(', page):
    fails.append("排版: 出现外部依赖")

# 5) 页内自标篇号与 mulu 同号制（45 期，commit 前最后核对）
if "之四七" not in page:
    fails.append("篇号: 页内未标之四七")

print(f"引文 .q: {nq} 段, 扩展片段: {ne} 条")
if fails:
    print("FAIL", len(fails))
    for f in fails: print(" -", f)
    sys.exit(1)
print("ALL PASS")
