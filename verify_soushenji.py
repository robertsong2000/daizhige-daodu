#!/usr/bin/env python3
"""核验 soushenji.html 中的引文是否与殆知阁库内《搜神记》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/搜神记.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/soushenji.html"

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
    ("虽考先志于载籍，收遗逸于当时，盖非一耳一目之所亲闻睹也，又安敢谓无失实者哉。", "序 阶梯"),
    ("今之所集，设有承于前载者，则非余之罪也。若使采访近世之事，苟有虚错，愿与先贤前儒，分其讥谤。", "序 免责"),
    ("及其著述，亦足以发明神道之不诬也。", "序 主张"),
    ("晋 散骑常侍新蔡干宝令升撰", "书头题名"),
    ("女出门，谓永曰：“我，天之织女也。缘君至孝，天帝令我助君偿债耳。”语毕，凌空而去而去，不知所在。", "董永"),
    ("王梦见一儿，眉间广尺，言欲报雠。王即购之千金。", "三王墓 梦"),
    ("客以剑拟王，王头随堕汤中；客亦自拟己头，头复堕汤中。三首俱烂，不可识别。乃分其汤肉葬之。故通名三王墓。", "三王墓 结局"),
    ("其雨淫淫，河大水深，日出当心。", "韩凭 密书"),
    ("宿昔之间，便有大梓木，生于二冢之端，旬日而大盈抱，屈体相就，根交于下，枝错于上。", "韩凭 树"),
    ("宋人哀之，遂号其木曰“相思树。”“相思”之名，起于此也。", "韩凭 相思"),
    ("鬼问：“汝复谁？”定伯诳之，言：“我亦鬼。”", "定伯 相认"),
    ("鬼言：“卿太重，将非鬼也。”定伯言：“我新鬼，故身重耳。”", "定伯 称重"),
    ("惟不喜人唾", "定伯 忌讳"),
    ("当时石崇有言：“定伯卖鬼，得钱千五。”", "定伯 结案"),
    ("蛇便出。头大如囷，目如二尺镜，闻瓷香气，先啖食之。", "李寄 蛇"),
    ("寄入视穴，得其九女髑髅，悉举出，咤言曰：“汝曹怯弱，为蛇所食，甚可哀愍。”于是寄女缓步而归。", "李寄 归"),
    ("今在汝南北宜春县界", "三王墓 地望"),
    ("凌空而去而去", "讹字 叠字"),
    ("刘有雌雄", "讹字 刘"),
    ("何哭之甚悲耶：", "讹字 句读"),
    ("用蜜(麦少)灌之", "讹字 拆字"),
    ("左右莫解其意", "韩凭 按语用词"),
]
for q, where in MANUAL:
    check(q, where)

# 反向抽查：页面所有 .pull 块（剥掉 .from 编辑注）
html = open(PAGE, encoding="utf-8").read()
html = re.sub(r"<span class=\"from\">.*?</span>", "", html, flags=re.S)
pulls = re.findall(r'<div class="pull">(.*?)</div>', html, flags=re.S)
print(f"\n页面 .pull {len(pulls)} 个：")
for b in pulls:
    b = re.sub(r"<[^>]+>", "", b).strip()
    if len(norm(b)) < 4:
        continue
    check(b, "页面块")

for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
