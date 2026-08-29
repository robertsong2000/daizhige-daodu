#!/usr/bin/env python3
"""核验 zhouhou-beijifang.html 中的引文是否与殆知阁库内《肘后备急方》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/医藏/肘后备急方.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/zhouhou-beijifang.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
text = norm(raw)
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:20] + ("…" if len(q) > 20 else ""))
    fail += 0 if ok else 1

MANUAL = [
    ("余今采其要约以为《肘后救卒》三卷，率多易得之药，其不获已须买之者，亦皆贱价，草石所在皆有，兼之以灸，灸但言其分寸，不名孔穴。凡人览之，可了其所用，或不出乎垣篱之内，顾眄可具。", "自序"),
    ("夫生人所为大患，莫急于疾，疾而不治，犹救火而不以水也。", "陶弘景序（行文提及）"),
    ("郭之妇翁得诸汴之掖庭，变乱之际，与身存亡，未尝轻以示人，迨今而出焉，天也", "段成巳序"),
    ("又方 青蒿一握。以水二升渍，绞取汁。尽服之。", "疟 青蒿"),
    ("比岁有病时行。仍发疮头面及身，须臾周匝，状如火疮，皆戴白浆，随决随生，不即治，剧者多死。治得瘥后，疮瘢紫黑，弥岁方减，此恶毒之气。", "虏疮 主文"),
    ("以建武中于南阳击虏所得，仍呼为虏疮", "虏疮 名源"),
    ("又方，仍杀所咬犬，取脑敷之，后不复发。", "犬咬 取脑"),
    ("山水间多有沙虱，甚细略不可见，人入水浴，及以水澡浴。此虫在水中，着人身，及阴天雨行草中，亦着人。便钻入皮里", "沙虱 传播"),
    ("初得之皮上正赤，如小豆黍米粟粒，以手摩赤上，痛如刺。", "沙虱 诊法"),
    ("已深者，针挑取虫子，正如疥虫，着爪上映光方见行动也。若挑得，便就上灸三四壮，则虫死病除。", "沙虱 治法"),
    ("一方 取葱黄心刺其鼻，男左、女右，入七八寸。若使目中血出，佳。扁鹊法同。", "卒死 葱刺鼻"),
    ("书舌上作风字，又画纸上作两蜈蚣相交，吞之", "卒死 巫方（行文提及）"),
    ("治牛马六畜水谷疫疠诸病方第七十三", "末篇 篇名"),
    ("救卒中恶死方第一", "第一篇 篇名"),
    ("治寒热诸疟方第十六", "篇名 出处"),
    ("治伤寒时气温病方第十三", "篇名 出处"),
    ("治卒为犬所咬毒方第五十四", "篇名 出处"),
    ("治卒中沙虱毒方第六十六", "篇名 出处"),
]
for q, where in MANUAL:
    check(q, where)

# 数字核对：库内实测字符数（含标点空白）
nchars = len(raw)
nhz = len(text)
print(f"\n库内总字符数：{nchars}，其中汉字 {nhz}")
ok = nchars == 115102
print(("PASS" if ok else "FAIL"), "页面声称实测字符数 115102")
fail += 0 if ok else 1

# 反向抽查：页面所有 blockquote.sq 内的引文
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r"<blockquote class=\"sq\">(.*?)</blockquote>", html, flags=re.S)
# 第一处 sq 是陶弘景序引文页面上未放（只在行文提及），此处全部应当命中
print(f"\n页面引文块 {len(blocks)} 个（blockquote.sq）：")
for b in blocks:
    body = re.sub(r"<span.*?</span>", "", b, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body).strip()
    check(body, "页面块")

# 排版规则
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i, line.strip()[:40]); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

for k in ["殆知阁", "核验", "局限", "mulu.html"]:
    if k not in html:
        print("FAIL 页面缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
