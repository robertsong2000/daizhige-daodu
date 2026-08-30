# -*- coding: utf-8 -*-
"""verify_yuefu.py — 乐府杂录导读页核验：引文逐字 + 排版红线 + 机器计数"""
import re, sys, os

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yuefu-zalu.html"
LIB  = "/home/robertsong/workspace/claude/daizhige-simplified/艺藏/音乐/乐府杂录.txt"

html = open(PAGE, encoding="utf-8").read()
lib  = open(LIB, encoding="utf-8").read()

fails = []
def chk(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

def norm(s):
    return "".join(c for c in s if c.isalnum())

lib_clean = re.sub(r'（[^（）]*）', '', lib)   # 去案语括注后的正文
lib_raw_n = norm(lib)
lib_clean_n = norm(lib_clean)

# ---------- 抓取页面 .q（.q 内嵌 .qa，按 span 深度配对） ----------
def extract_q(html):
    out, i = [], 0
    while True:
        m = re.search(r'<span class="q(?: inl)?">', html[i:])
        if not m: break
        start = i + m.end()
        depth, j = 1, start
        while depth > 0:
            nxt = re.search(r'<span\b|</span>', html[j:])
            if not nxt: raise RuntimeError("unbalanced span")
            depth += -1 if nxt.group(0) == "</span>" else 1
            j += nxt.end()
        inner = re.sub(r'<[^>]+>', ' ', html[start:j - len("</span>")])
        out.append(inner)
        i = j
    return out

qs = extract_q(html)
chk(len(qs) == 21, "页面 .q 引文数量 = 21（实得 %d）" % len(qs))
page_q_norm = norm(" ".join(qs))

# ---------- QUOTES：21 处 .q（corpus: clean=去案语正文 / raw=含案语全文） ----------
QUOTES = [
 ("安节以幼少即好音律，故得粗晓宫商，亦以闻见数多，稍能记忆。", "clean"),
 ("洎从离乱，礼寺隳颓，簨簴既移，警鼓莫辨。梨园弟子，半已奔亡；乐府歌章，咸皆丧坠。", "clean"),
 ("宫悬四面，天子乐也。", "clean"),
 ("口作“傩”、“傩”之声以除逐也。", "clean"),
 ("丝不如竹，竹不如肉", "clean"),
 ("遇高秋朗月，台殿清虚，喉啭一声，响传九陌。", "clean"),
 ("永新乃撩鬓举袂，直奏曼声，至是广场寂寂，若无一人；喜者闻之气勇，愁者闻之肠绝。", "clean"),
 ("及卒，谓其母曰：“阿母钱树子倒矣！”", "clean"),
 ("即令隔屏风歌之，一声不失。", "clean"),
 ("妾本风尘丐者，一旦老父死有所归，致身入内，皆自韦青，妾不忍忘其恩。”乃一恸而绝。", "clean"),
 ("我亦弹此曲，兼移在枫香调中。”及下拨，声如雷，其妙入神。", "clean"),
 ("本领何杂？兼带邪声。", "clean"),
 ("且遣昆仑不近乐器十余年，使忘其本领，然后可教。", "clean"),
 ("曹纲有右手，兴奴有左手。", "clean"),
 ("是内弟子郑中丞也。昨以忤旨，命内官缢杀，投于河中", "clean"),
 ("曰：“此郑中丞琵琶声也。”", "clean"),
 ("此曲宫声往而不返，大驾东巡，必不回矣。汝可托疾勿去也。", "clean"),
 ("其徵音有其声，无其调。", "clean"),
 ("唐季钟簴频移，乐纪废坠，无复贞观十部之盛。段氏就其闻见，撰为此录", "clean"),
 ("然唐时乐制，绝无传者，存此尚足略见一斑", "clean"),
 ("‘莫是宫中胡二子否？’妓熟视曰：‘君岂梨园骆供奉耶？’相对泣下。", "raw"),
]
for i, (q, corpus) in enumerate(QUOTES, 1):
    hay = lib_raw_n if corpus == "raw" else lib_clean_n
    chk(norm(q) in hay,         "引文%02d 在库内逐字命中（%s）" % (i, corpus))
    chk(norm(q) in page_q_norm, "引文%02d 在页面 .q 中命中" % i)

# ---------- 页面在 .q 之外逐字使用的库内句子 ----------
PLAIN_CHECKS = [
 "朝议大夫守国子司业上柱国赐紫金鱼袋段安节撰",
 "红红乃以小豆数合，记其节拍。",
 "洎渔阳之乱，六宫星散。",
 "号大、小忽雷",
 "乃僧也",
 "乃一片方响",
 "盖蕤宾铁也",
 "朕得杨氏，如得至宝也",
 "笙者，女娲造也",
 "筝者，蒙恬所造也",
 "芜驳不伦",
 "语不可解",
 "造木偶人，运机关",
 "发正秃，善优笑",
 "皆称绝音",
 "颇谓壮观也",
]
RAW_PLAIN = {"皆称绝音"}   # 案语补文，仅存于原文括注内
page_all_norm = norm(re.sub(r"<[^>]+>", "", html))
for i, p in enumerate(PLAIN_CHECKS, 1):
    hay = lib_raw_n if p in RAW_PLAIN else lib_clean_n
    chk(norm(p) in hay,           "白句%02d 在库内逐字命中" % i)
    chk(norm(p) in page_all_norm, "白句%02d 在页面命中" % i)

# ---------- 排版红线 ----------
chk("—" not in html and "–" not in html, "全文无 — 与 –")
strip_nl = re.sub(r"<[^>]+>", "", html)
bad = [l for l in strip_nl.split("\n") if l.count("·") > 1]
chk(not bad, "去标签后每行 · ≤ 1（违例 %d 行）" % len(bad))

# ---------- 页脚必备 ----------
for s in ["殆知阁简体库", "逐字比对通过", "时代局限", "github.com/robertsong2000/daizhige-daodu"]:
    chk(s in html, "页脚含「%s」" % s)

# ---------- 序号与跨页链接 ----------
chk("导读之六十七" in html, "<title> 自标序号 67")
chk("殆知阁导读 · 六十七" in html, "kicker 序号 67")
chk("导读之六十四" not in html, "不误标 64")
chk('href="youyang-zazu.html"' in html and os.path.exists(
    os.path.join(os.path.dirname(PAGE), "youyang-zazu.html")), "跨页链接 youyang-zazu.html 存在")

# ---------- 库本机器计数 ----------
chk(len(lib) == 14548, "库本全帙 len = 14,548")
chk(sum(1 for c in lib if not c.isspace()) == 13994, "库本去空白 = 13,994")
chk(lib.count("（案") == 135, "库本案语 135 处")
chk(len(re.findall(r"第[一二三四五六七]运", lib)) == 28, "第X运 28 处")
chk("钱熙祚识" in lib and "乐府杂录跋" in lib, "库本含钱熙祚跋")

BU = ['雅乐部','云韶部','清乐部','鼓吹部','驱傩','熊罴部','鼓架部','龟兹部','胡部']
MU = ['歌','舞工','俳优','琵琶','筝','箜篌','笙','笛','觱篥','五弦','方响','击瓯','琴','阮咸','羯鼓','鼓','拍板']
QU = ['安公子','黄骢叠','离别难','夜半乐','雨霖铃','还京乐','康老子','得宝子','文叙子','望江南','杨柳枝','新倾杯乐','道调子']
lines = [l.strip() for l in lib.split("\n")]
chk(all(("　"+b) in lib or b in lines for b in BU) and len(BU) == 9, "乐部 9 部俱在")
chk(all(m in lines for m in MU), "乐器技艺条目 17 目俱在（库内独立行）")
chk(all(q in [l[:12] for l in lines] or any(l.startswith(q) for l in lines) for q in QU), "曲目 13 条俱在（库内行首）")

# 页面结构数
chk(len(re.findall(r'<div class="bu">', html)) == 9, "页面九部 9 行")
chk(len(re.findall(r'<article class="story">', html)) == 4, "声中人 4 篇")
chk(len(re.findall(r'<div class="plaque(?: feature)?">', html)) == 13, "曲牌 13 面")

# ---------- 二十八调：页面方阵 = 库本四节逐名比对 ----------
ROWS = ['平声羽七调','上声角七调','去声宫七调','入声商七调']
segs = []
for i, r in enumerate(ROWS):
    a = lib.find(r)
    b = lib.find(ROWS[i+1]) if i+1 < len(ROWS) else lib.find("上平声调")
    chk(a != -1 and b != -1 and a < b, "库本节「%s」定位" % r)
    segs.append(lib[a:b])
EXPECT = [
 ['中吕调','正平调','高平调','仙吕调','黄钟调','般涉调','高般涉调'],
 ['越角调','大石角调','高大石角调','双角调','小石角调','歇指角调','林钟角调'],
 ['正宫调','高宫调','中吕宫','道调宫','南吕宫','仙吕宫','黄钟宫'],
 ['越调','大石调','高大石调','双调','小石调','歇指调','林钟商调'],
]
for r, seg, names in zip(ROWS, segs, EXPECT):
    pos, ok = -1, True
    for n in names:
        idx = seg.find(n, pos+1)
        if idx == -1: ok = False; break
        pos = idx
    chk(ok, "库本「%s」七运名次序逐字可查" % r)
cells = re.findall(r'<div class="mc2(?: row-start)?">([^<]+)</div>', html)
chk(len(cells) == 28, "页面调格 = 28（实得 %d）" % len(cells))
chk(cells == sum(EXPECT, []), "页面二十八调名与次序 = 库本四节")

# 页面声明数字与库内一致
for s in ["一百三十五处", "13,994", "九个部，十七个条目，十三支曲，二十八调"]:
    chk(s in html, "页面声明含「%s」" % s)

print("\n%d 项断言，%d 项失败" % (
    1 + 2*len(QUOTES) + 2*len(PLAIN_CHECKS) + 3 + 4 + 2 + 1 + 1 + 1 + 1 + 3
    + 1 + 4 + 4 + 2 + 1 + 1 + 1 + 3,
    len(fails)))
if fails:
    print("FAILED:"); [print(" -", f) for f in fails]; sys.exit(1)
print("ALL PASS")
