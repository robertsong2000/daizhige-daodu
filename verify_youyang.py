#!/usr/bin/env python3
"""核验 youyang-zazu.html 中的引文是否与殆知阁库内《酉阳杂俎》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/酉阳杂俎.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/youyang-zazu.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

text = norm(open(SRC, encoding="utf-8").read())
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    fail += 0 if ok else 1

MANUAL = [
    ("炙羞鳖，岂容下箸乎？", "序 内联"),
    ("号《酉阳杂俎》，凡三十篇，为二十卷", "自注引序"),
    ("月桂高五百丈，下有一人常斫之，树创随合。人姓吴名刚，西河人，学仙有过，谪令伐树。", "天咫 吴刚"),
    ("君知月乃七宝合成乎？月势如丸，其影，日烁其凸处也。常有八万二千户修之，予即一数。", "天咫 修月"),
    ("左膊曰『生不怕京兆尹』，右膊曰『死不畏阎罗王』。", "黥 甲"),
    ("凡刻三十余处，首体无完肤，陈至呼为『白舍人行诗图』也。", "黥 乙"),
    ("陀汗王意其洞人以非道得之，遂禁锢而栲掠之，竟不知所从来。……乃搜其室，得叶限，令履之而信。", "叶限 pull"),
    ("成式旧家人李士元听说。士元本邕州洞中人，多记得南中怪事。", "叶限出处"),
    ("成式以此事颇怪，然大传众口，不得不着之。", "天咫 按语"),
    ("韦视之，乃木札也。须臾，积札埋至膝。", "盗侠 标注"),
]
for q, where in MANUAL:
    segs = [s for s in re.split(r"……", q) if len(norm(s)) >= 4]
    for s in segs:
        check(s, where)

# 反向抽查：页面所有 <q> 与 .pull 块
html = open(PAGE, encoding="utf-8").read()
html = re.sub(r"<span class=\"src\">.*?</span>", "", html, flags=re.S)
qs = re.findall(r"<q[^>]*>(.*?)</q>", html, flags=re.S)
pulls = re.findall(r'<div class="pull">(.*?)</div>', html, flags=re.S)
print(f"\n页面 <q> {len(qs)} 个，.pull {len(pulls)} 个：")
for b in qs + pulls:
    b = re.sub(r"<[^>]+>", "", b).strip()
    if len(norm(b)) < 4:
        continue
    for s in [x for x in re.split(r"……", b) if len(norm(x)) >= 4]:
        check(s, "页面块")

for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
