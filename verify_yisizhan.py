#!/usr/bin/env python3
"""核验 yisi-zhan.html 引文与殆知阁库内《乙巳占》逐字一致，并查排版规则。"""
import re, unicodedata, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/易藏/术数/乙巳占.txt"
SRC2 = "/home/robertsong/workspace/claude/daizhige-simplified/易藏/术数/开元占经.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yisi-zhan.html"

VAR = {"掲": "揭", "頺": "颓", "頽": "颓", "髙": "高", "竒": "奇", "渉": "涉",
       "箒": "帚", "彚": "汇", "鬛": "鬣", "偹": "备", "恠": "怪", "麄": "粗",
       "冩": "写", "浄": "净", "礲": "砻", "崄": "险", "児": "儿", "巻": "卷"}
PUNCT = re.compile(r"[\s，。、；：？！「」『』（）()《》〈〉·…—–\-,.:;?!'\"“”‘’【】●■　]")

def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = "".join(VAR.get(c, c) for c in s)
    return PUNCT.sub("", s)

raw = open(SRC, encoding="utf-8").read()
body = norm(raw)
body2 = norm(open(SRC2, encoding="utf-8").read())
html = open(PAGE, encoding="utf-8").read()
fail = 0

def check(q, where):
    global fail
    frags = [f for f in re.split(r"……|\.\.\.", q) if norm(f)]
    bad = [f for f in frags if norm(f) not in body and norm(f) not in body2]
    ok = not bad
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    for b in bad:
        print("   不匹配片段：", b[:50])
    fail += 0 if ok else 1

# 页面所有「」引文（先剥内嵌标签）
quotes = re.findall(r"「([^」]*)」", html)
print(f"页面「」引文 {len(quotes)} 个：")
for i, q in enumerate(quotes, 1):
    check(re.sub(r"<[^>]+>", "", q), f"引文{i}")

# 「」之外散置的原文片段（八家牌、卦辞、器械说、风级、流水账）
MANUAL = [
    # 卷一天象 · 八家
    ("论天体象者，凡有八家：一曰浑天，即今所载张衡《灵宪》是也；二曰宣夜，绝无师学；三曰盖天，《周髀》所载；四曰轩天，姚信所说；五曰穹天，虞耸所拟；六曰安天，虞喜所述；七曰方天，王充所论；八曰四天，祅胡寓言。", "八家 全文"),
    ("凡此八家，浑天最亲，今独取之，以载于此。", "八家 断语"),
    ("绝无师学", "宣夜 牌"),
    ("祅胡寓言", "四天 牌"),
    ("姚信所说", "轩天 牌"),
    ("虞耸所拟", "穹天 牌"),
    ("虞喜所述", "安天 牌"),
    ("王充所论", "方天 牌"),
    # 卷一 嫦娥卦辞
    ("羿请不死之药于西王母，姮娥窃之以奔月，将往，求筮于有黄，有黄占之曰：吉，翩翩归妹，独将西行，逢天晦芒，无恐无惊，后且大昌。姮娥遂托身于月，是为蟾蜍。", "灵宪 姮娥"),
    # 卷三 史司 补充
    ("君恶直谏，臣矜谄谀", "史司 汉魏之后"),
    # 卷十 候风法 木乌
    ("亦可于竿首作盘，盘上作木乌三足", "候风法 木乌"),
    # 卷十 占风远近法 八级
    ("凡风动叶十里，鸣条百里，摇枝二百里，堕叶三百里，折小枝四百里，折大枝五百里。一云：折木飞砂石千里。或云：伐木施千里，又云：折木千里，拔木树及根五千里。", "占风远近 八级"),
    ("凡大风非常，三日三夜者，天下尽风也；二日二夜者，天下半风也；一日一夜者，万里风也。", "占风远近 时长"),
    # 卷十 候诏书
    ("诸阳宫之日，风从阳征上来，为诏书到也。", "候诏书"),
    # 卷第二 天数 自夸
    ("余近造乙巳元历术，实为绝妙之极，日夜法度诸法，皆同一母，以通众术。", "天数 历术"),
]
print("\n散置片段：")
for q, where in MANUAL:
    check(q, where)

# 库内字符数
n = len(raw)
print(f"\n库内总字符数：{n:,}")
ok = f"{n:,}" in html
print(("PASS" if ok else "FAIL"), "页面声称字符数与实测一致")
fail += 0 if ok else 1

# 排版规则：长划线；每行·至多一个
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

# 页脚要素
for k in ["殆知阁", "daizhigev20", "核验", "时代局限", "mulu.html", "kaiyuan-zhanjing.html"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
