#!/usr/bin/env python3
"""核验 mengxi-bitan.html 中的引文是否与殆知阁库内《梦溪笔谈》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/梦溪笔谈.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/mengxi-bitan.html"

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
    ("庆历中，有布衣毕升，又为活版。其法用胶泥刻字，薄如钱唇，每字为一印，火烧令坚。", "技艺 活版"),
    ("若止印三、二本，未为简易；若印数十百千本，则极为神速。", "技艺 活版"),
    ("升死，其印为余群从所得，至今保藏。", "技艺 活版"),
    ("鄜、延境内有石油，旧说「高奴县出脂水」，即此也。", "杂志一 石油"),
    ("此物后必大行于世，自余始为之。盖石油至多，生于地中无穷，不若松木有时而竭。", "杂志一 石油"),
    ("二郎山下雪纷纷，旋卓穹庐学塞人。化尽素衣冬未老，石烟多似洛阳尘。", "杂志一 延州诗"),
    ("方家以磁石磨针锋，则能指南，然常微偏东，不全南也。", "杂志一 磁针"),
    ("磁石之指南，犹柏之指西，莫可原其理。", "杂志一 磁针"),
    ("治平元年，常州日禺时，天有大声如雷，乃一大星，几如月，见于东南。", "神奇 坠星"),
    ("又久之，发其窍，深三尺余，乃得一圆石，犹热，其大如拳，一头微锐，色如铁，重亦如之。", "神奇 坠星"),
    ("州守郑伸得之，送润州金山寺，至今匣藏，游人到则发视。", "神奇 坠星"),
    ("余观雁荡诸峰，皆峭拔崯怪，上耸千尺，穷崖巨谷，不类他山。", "杂志一 雁荡"),
    ("原其理，当是为谷中大水冲激，沙土尽去，唯巨石岿然挺立耳。", "杂志一 雁荡"),
    ("予退处林下，深居绝过从。思平日与客言者，时纪一事于笔，则若有所晤言，萧然移日，所与谈者，唯笔砚而已，谓之《笔谈》。", "序"),
    ("然自古图牒，未尝有言者", "杂志一 雁荡 内联"),
    ("色如铁，重亦如之", "账本 内联"),
    ("所与谈者，唯笔砚而已", "尾声 内联"),
]
for q, where in MANUAL:
    check(q, where)

# 反向抽查：页面所有 .slip .txt 内的 <i> 与 <q>
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r'<div class="txt"><i>(.*?)</i></div>', html, flags=re.S)
blocks += re.findall(r"<q>(.*?)</q>", html, flags=re.S)
print(f"\n页面引文块 {len(blocks)} 个（slip + q）：")
for b in blocks:
    check(re.sub(r"<[^>]+>", "", b).strip(), "页面块")

for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i); fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40]); fail += 1

for k in ["殆知阁", "核验", "局限"]:
    if k not in html:
        print("FAIL 页脚缺少：", k); fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
