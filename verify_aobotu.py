# -*- coding: utf-8 -*-
"""核验《熬波图》导读：
1) quotes_aobotu.py 显示串 与 库本切片（去标点+异体归一后）逐字相等；
2) 页面 aobo-tu.html 抽出的全部引文块、散文内嵌片段均能在库本中找到；
3) 排版红线：禁长划线、每行·至多1个、无外部依赖、系列配色。"""
import re, sys
from quotes_aobotu import QUOTES, PROSE

SRC = "../daizhige-simplified/史藏/政书/熬波图.txt"
PAGE = "aobo-tu.html"
SLICES = "quotes_aobotu_slices.txt"

# 库本异体/讹写归一表（实测归纳）
VAR = {
    "圗": "图", "圖": "图",
    "塲": "场", "場": "场",
    "湏": "须", "濵": "滨", "濱": "滨",
    "氷": "冰", "醎": "咸", "毎": "每",
    "収": "收", "囬": "回", "旹": "时",
    "邉": "边", "邊": "边", "廵": "巡",
    "闗": "关", "髙": "高", "柈": "盘",
    "茆": "茅", "鼈": "鳖", "畧": "略",
    "纎": "纤", "樸": "朴",
    # 库本 PUA 字符归一（实测归纳，均有文意互证）
    "": "卤",  # 皆斥卤之地
    "": "场",  # 下砂场盐司 / 盐场提干 / 开辟摊场图
    "": "团",  # 各团灶座 / 建团立盘 / 三灶合一团（提要互证）
    "": "传",  # 诗礼传家 / 已经传摹
    "": "舠",  # 书中自注：舠音貂，吴船也
    "": "灰",  # 又作还魂灰
    "": "候",  # 候干 / 守候潮来
    "": "骨",  # 大牛骨箆
}
PUNCT = re.compile(r"[\s　。，、；：！？「」『』（）《》〈〉·．,.;:!?()\[\]【】\"'“”‘’…\-—―～※]")

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

# 2) 页面引文块（.q 去出处、.shi、.pos 去注）逐条命中库本
blocks = []
blocks += re.findall(r'<div class="q">(.*?)<span class="qs">', page, re.S)
blocks += re.findall(r'<div class="shi">(.*?)</div>', page, re.S)
blocks += re.findall(r'<div class="pos">(.*?)<span class="src">', page, re.S)
for b in blocks:
    t = norm(re.sub(r"<[^>]+>", "", b))
    if t and t not in book:
        fails.append(f"[页面引文未命中] {t[:30]}…")

# 散文内嵌片段
for frag in PROSE:
    if norm(frag) not in book:
        fails.append(f"[散文片段未命中] {frag}")

# 3) 排版红线
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

# 报告
nq = len(QUOTES) + len(blocks) + len(PROSE)
if fails:
    print("\n".join(fails))
    print(f"\n未通过：{len(fails)} 项（引文块{len(blocks)}，清单{len(QUOTES)}，散文片段{len(PROSE)}）")
    sys.exit(1)
print(f"全部核验通过：引文块{len(blocks)} + 清单{len(QUOTES)} + 散文片段{len(PROSE)}，共{nq}项命中库本")
print("排版红线通过：无长划线、每行·至多1个、零外部依赖、配色合规")
