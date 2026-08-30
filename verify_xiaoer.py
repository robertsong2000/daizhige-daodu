#!/usr/bin/env python3
# 小儿药证直诀页核验：引文逐字对库 + 库本断裂申报 + 排版红线 + 机数复核
import re, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/xiaoer-yaozheng-zhijue.html"
LIB  = "/home/robertsong/workspace/claude/daizhige-simplified/医藏/小儿药证直诀.txt"

def cjk(s):
    return "".join(ch for ch in s if "一" <= ch <= "鿿")

errs = []
def chk(cond, msg):
    if not cond:
        errs.append(msg)

lib = open(LIB, encoding="utf-8").read()
html = open(HTML, encoding="utf-8").read()

# ---- 0. 开场竖排大字（非 .q，单独核验） ----
m = re.search(r'class="vtxt">(.*?)</div>', html, re.S)
chk(m is not None, "开场 vtxt 缺失")
if m:
    big = cjk(re.sub(r"<[^>]+>", "", m.group(1)))
    chk(big == "医之为艺诚难矣而治小儿为尤难", "竖排大字异常: %s" % big)
chk(lib.count("医之为艺诚难矣，而治小儿为尤难。") == 1, "序首句库内不唯一")

QUOTES = [
    "自六岁以下，黄帝不载其说",
    "脉既难凭，必资外证。而其骨气未成，形声未正，悲啼喜笑，变态不常，其难三也。",
    "问而知之，医之工也。而小儿多未能言，言亦未足取信，其难四也。",
    "脏腑柔弱，易虚易实，易寒易热，又所用多犀、珠、龙、麝，医苟难辨，何以已疾？其难五也。",
    "目见庸医妄施方药而杀之者，十常四五，良可哀也！",
    "父颢，善针医，然嗜酒喜游。一旦匿姓名，东游海上，不复返。乙时三岁。母前亡，父同产姑，嫁医吕氏，哀其孤，收养为子。",
    "乙号泣，请返迹父。凡五六返，乃得所在。又积数岁，乃迎以归。是时乙年三十余。乡人惊叹，感慨为泣下，多赋诗咏其事。",
    "乙始以《颅囟方》着山东。元丰中，长公主女有疾，召使视之，有功，奏授翰林医学，赐绯。",
    "夫当诸臣搜采之日，天下藏书之家，莫不争献秘籍。卒未得是书真本，而今乃复见于世，岂非古人精气有不可磨灭者欤？",
    "左腮为肝，右腮为肺，额上为心，鼻为脾，颏为肾。赤者，热也，随证治之。",
    "故以生之日后，三十二日一变。",
    "脱齿者，如花之易苗。",
    "凡急慢惊，阴阳异证，切宜辨而治之，急惊合凉泻，慢惊合温补。世间俗方，多不分别，误小儿甚多。",
    "疳皆脾胃病，亡津液之所作也。",
    "且小儿病疳，皆愚医之所坏病。",
    "故小儿之脏腑柔弱，不可痛击，大下必亡津液而成疳。",
    "钱曰：此病必死，不可治也。",
    "今三泻肝而肝病不退，三补肺而肺证犹虚，此不久生，故言死也。",
    "果大喘而死。",
    "其白术散末煎一两，汁三升，使任其意取足服。",
    "朱生曰：饮多不作泻否？钱曰：无生水不能作泻，纵荡不足怪也，但不可下耳。",
    "至晚服尽。钱看之曰：更可服三升。",
    "钱曰：止渴治痰，退热清里，皆此药也。",
    "钱曰：凡吐泻，五月内，九分下而一分补；八月内，十分补而无一分下。",
    "治肾怯失音，囟开不合，神不足，目中白睛多，面色　白等方。",
    "熟地黄（八钱）　山萸肉　干山药（各四钱）　泽泻　牡丹皮　白茯苓（去皮各三钱）",
    "上为末，炼蜜丸，如梧子大，空心，温水化下三丸。",
    "余五六岁时，病惊疳癖瘕，屡至危殆，皆仲阳拯之良愈。是时仲阳年尚少，不肯轻传其书。余家所传者，才十余方耳！",
    "大观初，余筮仕汝海，而仲阳老矣。于亲旧间，始得说证数十条。后六年，又得杂方。",
    "其先后则次之，重复则削之，讹谬则正之，俚语则易之。上卷脉证治法，中卷记尝所治病，下卷诸方，而书以全。",
    "使幼者免横夭之苦，老者无哭子之悲，此余之志也。",
    "是书原刻阎名作「孝忠」，「真诀」作「直诀」，今未敢易也。",
]

# ---- 1. 每条库内原串唯一（地黄丸证行库本缺字为空格，比对口径含□） ----
for r in QUOTES:
    chk(lib.count(r) == 1, "库内不唯一(%d): %s" % (lib.count(r), r[:20]))
chk(len(QUOTES) == 32, "引文清单应为 32 条，实 %d" % len(QUOTES))

# ---- 2. 页面 .q 收集（span 或 p，可带 style；<i> 内为白话注，先剥去） ----
qs = re.findall(r'class="q"[^>]*>(.*?)</(?:span|p)>', html, re.S)
qnorms = [cjk(re.sub(r"<i>.*?</i>", "", q, flags=re.S)) for q in qs]
qnorms = [cjk(re.sub(r"<[^>]+>", "", q)) for q in qnorms]
chk(len(qnorms) == 32, "页面 .q 应 32 段，实 %d" % len(qnorms))

# ---- 3. .q 与库内原串一一配对（页面允许截取库串前缀，不许改动字序；□ 滤除等价库本空格） ----
pool = [cjk(r) for r in QUOTES]
for i, qn in enumerate(qnorms):
    hit = [j for j, rn in enumerate(pool) if rn.startswith(qn)]
    chk(len(hit) == 1, "第%d段 .q 无法唯一配对: %s…" % (i + 1, qn[:16]))
    if len(hit) == 1:
        pool.pop(hit[0])
chk(not pool, "库内原串未被页面引用: %s" % [p[:16] for p in pool])
for qn in qnorms:
    chk(len(qn) >= 5, "过短引文: " + qn)

# ---- 4. 库本断裂与脱文申报 ----
chk("明年，皇" in html, "断裂点未展示")
chk("跋语" in html and "混入" in html, "周学海跋混入未说明")
chk("脱了第一难" in html, "阎序脱第一难未说明")
chk("缺了一个字" in html and "□" in html, "地黄丸行缺字未标注")
chk(lib.find("夫当诸臣搜采之日") > lib.find("明年，皇"), "跋语混入位置与页面叙述不符")

# ---- 5. 机数 ----
nchars = len(re.sub(r"\s", "", lib))
chk("31,062" in html and nchars == 31062, "字数口径不符: %d" % nchars)
for kw, disp in [("钱曰", 28), ("学海案", 29), ("主之", 74), ("易虚易实", 4), ("地黄丸", 14), ("泻青丸", 13)]:
    n = lib.count(kw)
    chk(n == disp, "%s 库内 %d 见, 页面申报 %d" % (kw, n, disp))
chk("二十八见" in html, "页面缺钱曰 28 见申报")
chk("校语二十九处" in html, "页面缺学海案 29 处申报")
chk("记尝所治病二十三证" in lib, "卷中标题异常")
chk("二十三份病历" in html, "页面缺二十三证申报")

# ---- 6. 排版红线 ----
chk("—" not in html, "出现长划线 —")
chk("–" not in html, "出现 – ")
for i, line in enumerate(html.split("\n"), 1):
    chk(line.count("·") <= 1, "第%d行 · 超限: %s" % (i, line.strip()[:40]))

# ---- 7. 页面自我申报 ----
chk("殆知阁导读 · 之七十八" in html, "kicker 序号不符")
chk("<title>小儿药证直诀 · 殆知阁导读之七十八</title>" in html, "title 序号不符")
chk("github.com/robertsong2000/daizhigev20" in html, "页脚缺仓库链接")
chk("逐字核验" in html, "页脚缺核验声明")
chk("时代产物" in html, "页脚缺时代局限提醒")
chk(html.count("殆知阁古代文献简体库") == 1, "来源表述异常")
chk("医方卷" in html, "缺医方卷归属")

if errs:
    print("FAIL %d 项" % len(errs))
    for e in errs:
        print("  -", e)
    sys.exit(1)
print("PASS: 开场大字 + 32 段 .q 逐字对库 + 断裂申报 4 处 + 机数 + 红线 + 页面申报 全过")
