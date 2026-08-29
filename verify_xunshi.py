#!/usr/bin/env python3
"""核验 xunshi-pinghua.html 中的引文是否与殆知阁库内《训世评话》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/集藏/话本/训世评话.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/xunshi-pinghua.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

QUOTES = [
    # hero / 体例
    ("母冻吾之子，我冻母之子。", "hero 文"),
    ("母亲冻我的儿子，因此我冻娘的儿子。", "hero 白"),
    ("虞舜父顽母嚣象傲，常欲杀舜。克谐以孝，不格奸。", "第一课文"),
    ("古时虞舜，他的父亲瞽叟心里无有德行，后娘也口里无些儿好言语。", "第一课白"),
    ("这个是天下的大孝。", "第一课白末"),
    # 壹 学话的人
    ("语音不通，乃设承文院司译院", "跋"),
    ("使习汉训，日讲月试，课其能否。或赏或罚", "跋"),
    ("一齐众楚，鲜能成就", "跋"),
    ("太宗大王十七年丁酉中第", "跋"),
    ("庸童少女亦尝习知其语。日用使唤，应对如流", "跋"),
    ("国语音与中朝不同，使事交际之间，不无扞格不通之患。", "自序"),
    ("乃捃抚为善阴骘之事，及平昔所尝闻者，编辑为书。译以汉音，名曰训世评话，缮写以进", "跋"),
    ("欲令后学者易于研穷", "跋"),
    # 叁 选读
    ("我天之织女，感君之至孝，天使我为君偿债，君事了，不得久停。", "董永文"),
    ("我是天上织女，上帝感动你孝心，教我下来织布还你少债。", "董永白"),
    ("感君之至孝", "董永评"),
    ("感动你孝心", "董永评"),
    ("天使我为君偿债", "董永评"),
    ("教我下来织布还你少债", "董永评"),
    ("昔苏东坡为徐州太守时，州有一妓容色可爱，人皆悦之，车马日盈其门。", "叶保儿文"),
    ("忽有娠，弥月生一子曾一见妓者皆以为己子，诉于太守。", "叶保儿文"),
    ("太守笑曰：此叶字二十人做头，又三十人伽腰，又十八人做足。争子者皆有惭色。", "叶保儿文"),
    ("恁众人仔细听我说。我如今为这小厮立起姓氏，叫做叶保儿。", "叶保儿白"),
    ("挺身突出，声色俱厉，抛以瓦石，蹴倒书案。", "葡萄架文"),
    ("汝夫妻姑退，县衙葡萄架子亦为风倒。一县士女闻之皆笑。", "葡萄架文"),
    ("待要决杖时，知县的娘子听这断罪的话，猛可里拿将石头瓦子抛打那知县，高声大骂。", "葡萄架白"),
    ("你两口儿且退去，我这屋里的葡萄架子也倒了。", "葡萄架白"),
    ("当县住的大小每都听得这话，笑的无尽。", "葡萄架白"),
    ("千年红顶鹤，从天而下；万年绿毛龟自海而来；老鼠生驴，不数日始马大。", "兔熊文"),
    ("这两日我家里有祥瑞的东西。", "兔熊白"),
    ("千年朱顶鹤儿从天上下来了", "兔熊白"),
    ("万年绿毛龟海里出来了", "兔熊白"),
    ("老鼠下一个公驴子，不到七日，马一般大了。", "兔熊白"),
    ("此乃借米不均之患也。", "兔熊评"),
    ("其皮内皆是蚕儿，蚕儿之种自此始。", "兔熊评"),
    # 肆 词汇表
    ("军人每都江水里渰死了", "词汇·每"),
    ("恁众臣宰每圆梦吉凶如何", "词汇·恁"),
    ("他的儿子祖娘根前无礼", "词汇·根前"),
    ("有一日晨早，见一小妮子", "词汇·妮子"),
    ("老妳妳上无礼，妳妳恼他这般做来", "词汇·妳妳"),
    ("每日店里打双六下象棋", "词汇·双六"),
    ("到晌午里，也进问，到晚夕又进问", "词汇·晌午"),
    # 伍 来历
    ("以渔钓为业，养母无懈色", "昔脱解"),
    ("过哀不食而死，年才二十", "金淑女"),
    # 陸 下落
    ("命用铸字，印出若平卷，颁赐朝臣", "跋"),
    ("不但为学汉音者之指南", "跋"),
    ("历岁既久，散逸殆尽。", "跋"),
]

text = norm(open(SRC, encoding="utf-8").read())
fail = 0
for q, where in QUOTES:
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:20] + ("…" if len(q) > 20 else ""))
    fail += 0 if ok else 1

# 反向抽查：页面所有引文块（blockquote.yw 与 .reg .rtxt）。
# 课卡原文若包了 .q 则逐段核验（中间隔着舞台备注的原文不被当成一句）；
# 未包 .q 的块整体作为一段核验。
html = open(PAGE, encoding="utf-8").read()
html = re.sub(r'<span class="stg">.*?</span>', "", html, flags=re.S)
blocks = []
for m in re.finditer(r'<blockquote class="yw">(.*?)</blockquote>', html, re.S):
    body = re.sub(r'<span class="from">.*?</span>', "", m.group(1), flags=re.S)
    blocks.append(re.sub(r"<[^>]+>", "", body))
for m in re.finditer(r'<div class="rtxt">(.*?)</div>', html, re.S):
    inner = m.group(1)
    qs = re.findall(r'<span class="q">(.*?)</span>', inner, re.S)
    if qs:
        blocks.extend(re.sub(r"<[^>]+>", "", q) for q in qs)
    else:
        blocks.append(re.sub(r"<[^>]+>", "", inner))
print(f"\n页面引文块 {len(blocks)} 个（blockquote + 课卡文白原文段）：")
for b in blocks:
    b = b.strip()
    if len(norm(b)) < 4:
        continue
    ok = norm(b) in text
    print(("PASS" if ok else "FAIL"), b[:26])
    fail += 0 if ok else 1

# 排版规则：禁止长划线；每行 · 至多 1 个
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：出现长划线，行", i)
        fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40])
        fail += 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
