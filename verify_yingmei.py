#!/usr/bin/env python3
"""核验 yingmei-an-yiyu.html 引文与殆知阁库内《影梅庵忆语》逐字一致，并查排版规则。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/影梅庵忆语.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/yingmei-an-yiyu.html"

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

# 首查：写稿时逐字取材的引文底稿
MANUAL = [
    ("余一生清福，九年占尽，九年折尽矣。", "开场竖排"),
    ("爱生于昵，昵则无所不饰。缘饰著爱，天下鲜有真可爱者矣。", "卷一 论饰"),
    ("此亦闺秀之奇冤，而啖名之恶习已。", "卷一 奇冤"),
    ("亡妾董氏，原名白，字小宛，复字青莲。籍秦淮，徙吴门。", "卷一 小宛"),
    ("今忽死，余不知姬死而余死也！", "卷一 终句"),
    ("面晕浅春，缬眼流视，香姿五色，神韵天然，懒慢不交一语。余惊爱之，惜其倦，遂别归，此良晤之始也。时姬年十六。", "卷一 初见"),
    ("委此身如江水东下，断不复返吴门", "卷一 金山誓江"),
    ("越二十七日，凡二十七辞，姬惟坚以身从。", "卷一 二十七辞"),
    ("越十月，愿始毕，然后往返葛藤，则万斛心血所灌注而成也。", "卷一 落籍"),
    ("归来与姬遍搜诸书，续成之，名曰《奁艳》。", "卷二 奁艳"),
    ("午夜衾枕间，犹拥数十家《唐书》而卧。", "卷二 唐诗"),
    ("死能弥留，元旦次日，求见老母，始瞑目。", "卷二 弥留"),
    ("始以身入，人在菊中，菊与人俱在影中。", "卷三 菊影"),
    ("菊之意态足矣，其如人瘦何？", "卷三 菊语"),
    ("途行需碎金，无从办。", "卷三 碎金问"),
    ("姬出一布囊，自分许至钱许，每十两可数百小块，皆小书轻重于其上，以便仓卒随手取用。", "卷三 碎金布囊"),
    ("我有年友，信义多才，以子托之，此后如复相见，当结平生欢，否则听子自裁，毋以我为念。", "卷三 冒襄诀别"),
    ("君言善。举室皆倚君为命，复命不自君出，君堂上膝下，有百倍重于我者，乃以我牵君之臆。非徒无益，而又害之。", "卷三 姬诀别"),
    ("前与君纵观大海，狂澜万顷，是否葬身处也！", "卷三 姬诀别二"),
    ("自此百日，皆展转深林僻路、茅屋渔艇。或一月徙，或一日徙，或一日数徙，饥寒风雨，苦不具述", "卷三 百日流离"),
    ("此百五十日，姬仅卷一破席，横陈榻边，寒则拥抱，热则被拂，痛则抚摩。或枕其身，或卫其足，或欠伸起伏，为之左右翼，凡病骨之所适，皆以身就之。", "卷四 病榻"),
    ("余病失常性，时发暴怒，诡谇三至，色不少忤，越五月如一日。", "卷四 暴怒"),
    ("竭我心力，以殉夫子。夫子生而余死犹生也；脱夫子不测，余留此身于兵燹间，将安寄托？", "卷四 姬曰殉"),
    ("余五年危疾者三，而所逢者皆死疾", "卷四 三疾"),
    ("余有生之年，皆长相忆之年也。", "卷四 忆字签"),
    ("姬临终时，自顶至踵，不用一金珠纨绮，独留跳脱不去手", "卷四 临终镯"),
    ("岂死耶？", "卷四 梦中语"),
    ("讵知梦真而诗谶咸来先告哉？", "卷四 梦谶"),
]
for q, where in MANUAL:
    check(q, where)

# 复查：页面所有 blockquote.q 逐块回验
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'<blockquote class="q[^"]*">(.*?)</blockquote>', html, flags=re.S)
print(f"\n页面引文块 {len(blocks)} 个（blockquote.q）：")
for b in blocks:
    body = re.sub(r"<span.*?</span>", "", b, flags=re.S)
    body = re.sub(r"<em>(.*?)</em>", r"\1", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body).strip()
    check(body, "页面块")

# 数字核对：库内实测字符数（含标点空白）
nchars = len(raw)
print(f"\n库内总字符数：{nchars}，其中汉字 {len(text)}")
ok = nchars == 12827
print(("PASS" if ok else "FAIL"), "页面声称实测字符数 12,827")
fail += 0 if ok else 1

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
