#!/usr/bin/env python3
"""核验 taoyuan-wenlu-waibian.html 引文与库内《弢园文录外编》逐字一致（去标点+归一，双向），另含整页反扫与排版红线。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/弢园文录外编.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/taoyuan-wenlu-waibian.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
lib = norm(raw)
html = open(PAGE, encoding="utf-8").read()
fail = 0

def check(q, tag):
    global fail
    ok = norm(q) in lib
    print(("PASS" if ok else "FAIL"), f"[{tag}]", q[:30])
    if not ok:
        fail += 1

# ---------- 机数断言 ----------
n_char = len(re.sub(r"\s", "", raw))
if n_char != 221935:
    print("FAIL 去空白字数", n_char)
    fail += 1
else:
    print("PASS", "库本去空白 221935 字")

lines = [l.strip() for l in raw.splitlines()]
toc_idx = (5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27)
toc = [[t for t in lines[i].split("　") if t] for i in toc_idx]
per = [len(x) for x in toc]
if per != [13, 13, 15, 14, 17, 10, 15, 15, 20, 19, 18, 18] or sum(per) != 187:
    print("FAIL 目次篇目数", per)
    fail += 1
else:
    print("PASS", "目次十二卷一百八十七篇（13/13/15/14/17/10/15/15/20/19/18/18，皆机数）")
juan = [l for l in lines if re.fullmatch(r"卷[一二三四五六七八九十]+", l)]
if len(juan) != 24:
    print("FAIL 卷行数", len(juan))
    fail += 1
else:
    print("PASS", "卷字二十四见（目次正文各十二，机数）")
miss = [t for grp in toc for t in grp if norm(t) not in lib]
if miss:
    print("FAIL 目次正文缺", miss)
    fail += 1
else:
    print("PASS", "目次一百八十七篇正文皆有")

# ---------- 手工引文清单（页面申报，双向） ----------
QUOTES = [
    ("今春忽患风痹，几于手足拘挛，杜门却扫，习静养疴，因取历年来存稿稍加厘次，授诸手民。", "自序"),
    ("曰“外编”者，因其中多言洋务，不欲入于集中也。", "自序"),
    ("自中外通商以来，天下之事繁变极矣。", "自序"),
    ("知文章所贵在乎纪事述情，自抒胸臆", "自序"),
    ("言之者谆谆而听之者藐藐", "自序"),
    ("光绪九年夏四月浴佛前二日", "自序落款日期"),
    ("此皆余二十七八年前之所言也，时在咸丰初元，国家方讳言洋务", "洋务上"),
    ("中西同有舟，而彼则以轮船；中西同有车，而彼则以火车；中西同有驿递，而彼则以电音", "变法中"),
    ("西人凡于政事，无论巨细，悉载日报", "洋务上"),
    ("老民姓王氏，素居苏州城外长洲之甫里村，即唐陆天随所隐处也。", "自传·初名"),
    ("十八岁，以第一入县学，督学使者为秦中张筱坡侍郎，称老民文有奇气。", "自传·旋易名瀚"),
    ("遭难后避粤，乃更名韬，字仲弢，一字子潜，自号天南遁叟，五十后又曰弢园老民。", "自传·更名之由"),
    ("然用其言而仍弃其人，并欲从而中伤之，此老民之所以扼腕太息痛哭流涕长往而不顾者也。", "自传·遁叟之遁"),
    ("老民急还沪上，犹思面为折辨，顾久之，事卒不解，不得已航海至粤，旅居香海。", "自传·五十后自号"),
    ("游屐所至，殊足娱情适", "自传·中断处"),
    ("如英国之《泰晤士》，人仰之几如泰山北斗，国家有大事，皆视其所言以为准则，盖主笔之所持衡，人心之所趋向也。", "论日报"),
    ("而我局之《循环日报》行之亦已二年。", "论日报"),
    ("今日云蒸霞蔚，持论蜂起，无一不为庶人之清议，其立论一秉公平，其居心务期诚正。", "论日报"),
    ("不知此乃其富强之末而非其富强之本也。英国之所恃者，在上下之情通，君民之分亲", "纪英国政治"),
    ("国家有大事则集议于上下议院，必众论佥同，然后举行。", "纪英国政治"),
    ("西人动讥儒者墨守孔子之道而不变，不知孔子而处于今日，亦不得不一变。", "变法上"),
    ("今观中国之所长者无他，曰因循也，苟且也，蒙蔽也，粉饰也，贪罔也，虚骄也，喜贡谀而恶直言，好货财而彼此交征利。", "变法中"),
    ("同一舟也，帆船与轮舶，迟速异焉矣；同一车也，驾马与鼓轮，远近殊焉矣", "变法上"),
    ("故我曰取士之法不变，则人才终不出。", "变法中"),
    ("故时文不废，天下不治。", "原士"),
    ("故我曰，兵法不变则兵不能强。", "变法中"),
    ("是谓以不教民战，无殊驱之就死地也。", "变法中"),
    ("是朝廷有养士之名，而无养士之实也。", "变法中"),
    ("是朝廷有行法之名，而无奉法之实也。", "变法中"),
    ("吾知中国不及百年，必且尽用泰西之法而驾乎其上。", "变法上"),
    ("是则导我以不容不变者，天心也；迫我以不得不变者，人事也。", "变法上"),
    ("上下三千年，纵横九万里，每当酒酣耳热之际，往往举杯问天，拔剑斫地", "易言跋"),
    ("若舍西法一途，天下无足与图治者。", "易言跋"),
    ("用夏变夷则有之矣，未闻变于夷者也。", "易言跋"),
    ("而今则创三千年来未有之局", "易言跋"),
    ("夫形而上者道也，形而下者器也，杞忧生之所欲变者器也，而非道也。", "易言跋"),
    ("余妇兄杨醒逋明经，曾于冷摊上购得《浮生六记》残本，为吴门处士沈三白所作，而轶其名。", "浮生六记跋"),
    ("今仅存四卷，而阙末后两卷。", "浮生六记跋"),
    ("以活字版排印，特邮寄此跋，附于卷末，志所始也。", "浮生六记跋"),
    ("天下之道，一而已矣", "原道"),
    ("其始也由同而异，其终也由异而同。", "原道"),
    ("东方有圣人焉，此心同此理同也", "原道"),
    ("西方有圣人焉，此心同此理同也", "原道"),
    ("道不能即通，则先假器以通之，火轮舟车皆所以载道而行者也。", "原道"),
    ("泰西诸国今日所挟以凌侮我中国者，皆后世圣人有作，所取以混同万国之法物也。", "原道"),
]
print("== 手工引文清单 -> 库内文件 ==")
for q, tag in QUOTES:
    check(q, tag)

# ---------- 页面引文块（blockquote p / q） -> 库内文件 ----------
print("\n== 页面引文块 -> 库内文件 ==")
body = html.split("</head>", 1)[1]
plain = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
blocks = []
for m in re.finditer(r"<blockquote[^>]*>(.*?)</blockquote>", html, re.S):
    b = re.sub(r"<span class=\"src\">.*?</span>", "", m.group(1), flags=re.S)
    blocks.append(re.sub(r"<[^>]+>", "", b))
for q in re.findall(r"<q[^>]*>(.*?)</q>", html, re.S):
    blocks.append(re.sub(r"<[^>]+>", "", q))
for b in blocks:
    b = b.strip()
    if len(norm(b)) < 4:
        continue
    ok = norm(b) in lib
    print(("PASS" if ok else "FAIL"), b[:28])
    fail += 0 if ok else 1

# ---------- 整页反扫：12 字阈值 ----------
print("\n== 整页反扫（阈值 12 字） ==")
plain = re.sub(r"<[^>]+>", "", plain)
page = norm(plain)
decl = [norm(q) for q, _ in QUOTES]
mask = [False] * len(page)
for qn in decl:
    start = 0
    while True:
        i = page.find(qn, start)
        if i < 0:
            break
        for k in range(i, i + len(qn)):
            mask[k] = True
        start = i + 1
lib12 = {lib[i:i + 12] for i in range(len(lib) - 11)}
bad = []
i = 0
while i <= len(page) - 12:
    w = page[i:i + 12]
    if not any(mask[i:i + 12]) and w in lib12:
        j = i
        while j < len(page) and not mask[j]:
            j += 1
        bad.append((i, page[i:j]))
        i = j
    else:
        i += 1
if bad:
    for i, s in bad[:12]:
        print("FAIL 反扫命中", f"@{i}", s[:60])
    fail += len(bad)
else:
    print("PASS 整页反扫无未申报库本成句")

# ---------- 排版规则 ----------
print("\n== 排版规则 ==")
for n, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：长划线，行", n, line.strip()[:40])
        fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", n, line.strip()[:40])
        fail += 1

# ---------- 硬性视觉 ----------
checks = [
    ("#191917" in html, "墨底 #191917"),
    ("#e8e4dc" in html, "纸白 #e8e4dc"),
    ("#c9963f" in html, "赭金 #c9963f"),
    ("Songti SC" in html, "宋体族"),
    ("@import" not in html and "<link" not in html and "url(http" not in html, "无外部字体样式"),
    ("<script src=" not in html and "<img" not in html and 'src="http' not in html, "无外部脚本图片"),
    ("殆知阁简体库" in html and "github.com/robertsong2000/daizhigev20" in html, "页脚来源与仓库"),
    ("逐字比对" in html and "时代局限" in html, "页脚核验声明与时代局限提醒"),
]
print("\n== 视觉 ==")
for ok, name in checks:
    print(("PASS" if ok else "FAIL"), name)
    fail += 0 if ok else 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
