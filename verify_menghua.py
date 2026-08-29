#!/usr/bin/env python3
"""核验 dongjing-menghualu.html 中的引文是否与殆知阁库内《东京梦华录》逐字一致。"""
import re, sys, os

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/东京梦华录.txt"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)  # 去标点/空白/字母数字

text = norm(open(SRC).read())
print(f"库内文件字符数（归一后）: {len(text)}")

QUOTES = [
    # 序
    ("垂髫之童，但习鼓舞，班白之老，不识干戈", "序"),
    ("一旦兵火，靖康丙午之明年，出京南来，避地江左，情绪牢落，渐入桑榆。", "序"),
    ("暗想当年，节物风流，人情和美，但成怅恨。", "序"),
    ("古人有梦游华胥之国，其乐无涯者，仆今追念，回首怅然，岂非华胥之梦觉哉。", "序"),
    ("此录语言鄙俚，不以文饰者，盖欲上下通晓尔", "序"),
    ("绍兴丁卯岁除日，幽兰居士孟元老序", "序·落款"),
    # 城
    ("穿城河道有四。", "卷一·河道"),
    ("自西京洛口分水入京城，东去至泗州，入淮，运东南之粮，凡东南方物，自此入京城，公私仰给焉。", "卷一·河道"),
    ("南通一巷，谓之“界身”，并是金银彩帛交易之所，屋宇雄壮，门面广阔，望之森然，每一交易，动即千万，骇人闻见。", "卷二·东角楼街巷"),
    ("自州桥南去，当街水饭、爊肉、干脯。", "卷二·州桥夜市"),
    ("每个不过十五文", "卷二·州桥夜市"),
    ("直至龙津桥须脑子肉止，谓之杂嚼，直至三更。", "卷二·州桥夜市"),
    ("凡京师酒店，门首皆缚彩楼欢门", "卷二·酒楼"),
    ("后改为丰乐楼，宣和间，更修三层相高。五楼相向，各有飞桥栏槛，明暗相通，珠帘绣额，灯烛晃耀。", "卷二·酒楼"),
    ("在京正店七十二户，此外不能遍数，其余皆谓之“脚店”。", "卷二·酒楼"),
    # 夜
    ("每日交五更，诸寺院行者打铁牌子或木鱼循门报晓", "卷三·天晓诸人入市"),
    ("又于高处砖砌望火楼，楼上有人卓望。", "卷三·防火"),
    ("街南桑家瓦子，近北则中瓦，次里瓦。其中大小勾栏五十余座。", "卷二·东角楼街巷"),
    ("瓦中多有货药、卖卦、喝故衣、探搏、饮食、剃剪、纸画、令曲之类。", "卷二·东角楼街巷"),
    ("终日居此，不觉抵暮。", "卷二·东角楼街巷"),
    ("夜市直至三更尽，才五更又复开张。如要闹去处，通晓不绝。", "卷三·马行街铺席"),
    ("冬月虽大风雪阴雨，亦有夜市", "卷三·马行街铺席"),
    ("市井经纪之家，往往只于市店旋买饮食，不置家蔬。", "卷三·马行街铺席"),
    ("主张小唱：李师师、徐婆惜、封宜奴、孙三四等，诚其角者。", "卷五·京瓦伎艺"),
    ("霍四究，说《三分》。尹常卖，《五代史》。", "卷五·京瓦伎艺"),
    ("以至贫下人家，就店呼酒，亦用银器供送。有连夜饮者，次日取之。", "卷五·民俗"),
    ("其阔略大量，天下无之也。", "卷五·民俗"),
    # 年
    ("灯山上彩，金碧相射，锦绣交辉。", "卷六·元宵"),
    ("乐声嘈杂十余里", "卷六·元宵"),
    ("四野如市，往往就芳树之下，或园囿之间，罗列杯盘，互相劝酬。", "卷七·清明节"),
    ("大抵都城左近，皆是园圃，百里之内，并无闲地。", "卷六·收灯都人出城探春"),
    ("皆卖磨喝乐，乃小塑土偶耳。", "卷八·七夕"),
    ("市人争饮，至午未间，家家无酒，拽下望子。", "卷八·中秋"),
    ("中秋夜，贵家结饰台榭，民间争占酒楼玩月。", "卷八·中秋"),
    ("夜市骈阗，至于通晓。", "卷八·中秋"),
    ("土庶之家，围炉团坐，达旦不寐，谓之“守岁”。", "卷十·除夕"),
    ("观其所先拈者，以为征兆，谓之“试晬”。", "卷五·育子"),
]

fail = 0
for q, where in QUOTES:
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    fail += 0 if ok else 1
print(f"\n直接核对: {len(QUOTES)} 条, 失败 {fail}")

path = "/home/robertsong/workspace/claude/daizhige-daodu/dongjing-menghualu.html"
if not os.path.exists(path):
    print("（页面尚未生成，跳过 HTML 抽查）")
    sys.exit(1 if fail else 0)

html = open(path).read()
strip_tags = lambda s: re.sub(r"<[^>]+>", "", s)
cands = []
for m in re.finditer(r"<blockquote>(.*?)</blockquote>", html, re.S):
    body_only = re.sub(r'<span class="src">.*?</span>', "", m.group(1), flags=re.S)
    for seg in re.split(r"</?p[^>]*>", body_only):
        seg = strip_tags(seg).strip()
        if len(norm(seg)) >= 6:
            cands.append((seg, "blockquote"))
for m in re.finditer(r"<span class=\"qline\">(.*?)</span>", html, re.S):
    seg = strip_tags(m.group(1)).strip()
    if len(norm(seg)) >= 6:
        cands.append((seg, "qline"))

fail2 = 0
for seg, tag in cands:
    ok = norm(seg) in text
    print(("PASS" if ok else "FAIL"), f"[html:{tag}]", seg[:24])
    fail2 += 0 if ok else 1
print(f"\nHTML 引文块抽查: {len(cands)} 条, 失败 {fail2}")

# 夜市词条卡与竖排楼签
cards = re.findall(r'class="qcard[^"]*">([^<]+)<', html)
towers = re.findall(r'<span>([^<]+)</span>', re.search(r'<div class="towers">(.*?)</div>\s*<p class="note">', html, re.S).group(1)) if '<div class="towers">' in html else []
fail3 = 0
for w in cards + towers:
    ok = norm(w) in text
    if not ok:
        print("FAIL", "[词条]", w)
        fail3 += 1
print(f"夜市词条 {len(cards)} 个 + 楼签 {len(towers)} 个, 失败 {fail3}")

# 全页弯引号串：凡是 "…" 圈起的内容必须能在库内找到
body = strip_tags(html)
spans = re.findall(r"“([^”]{2,})”", body)
fail4 = 0
for s in spans:
    if len(norm(s)) >= 2 and norm(s) not in text:
        print("FAIL", "[引号串]", s[:30])
        fail4 += 1
print(f"弯引号串 {len(spans)} 处, 失败 {fail4}")
sys.exit(1 if (fail + fail2 + fail3 + fail4) else 0)
