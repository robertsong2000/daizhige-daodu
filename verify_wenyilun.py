#!/usr/bin/env python3
"""核验 wenyilun.html 引文与库内《温疫论》逐字一致（去标点+归一，双向），另含整页反扫与排版红线。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/医藏/温疫论.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/wenyilun.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
lib = norm(raw)
html = open(PAGE, encoding="utf-8").read()
fail = 0

def check(q, tag):
    global fail
    ok = norm(q) in lib
    print(("PASS" if ok else "FAIL"), f"[{tag}]", q[:30])
    if not ok:
        fail += 1

# ---------- 机数断言 ----------
n_char = len(re.sub(r"\s", "", raw))
if n_char != 40174:
    print("FAIL 去空白字数", n_char)
    fail += 1
else:
    print("PASS", "库本去空白 40174 字")
ln = [l.strip() for l in raw.splitlines()]
titles = [(ln[i], ln[i + 2]) for i, l in enumerate(ln) if l in ("上卷", "下卷") and i + 2 < len(ln) and ln[i + 2]]
if len(titles) != 86 or sum(1 for v, _ in titles if v == "上卷") != 50:
    print("FAIL 条目数", len(titles))
    fail += 1
else:
    print("PASS", "凡八十六条（上50 下36 机数）")

# ---------- 手工引文清单（页面申报，双向） ----------
QUOTES = [
    ("夫温疫之为病，非风、非寒、非暑、非湿，乃天地间别有一种异气所感。", "自叙"),
    ("崇祯辛巳，疫气流行，山东、浙省、南北两直，感者尤多，至五六月益甚，或至阖门传染。", "自叙"),
    ("病愈急，投药愈乱，不死于病，乃死于医，不死于医，乃死于圣经之遗亡也。", "自叙"),
    ("余虽固陋，静心穷理，格其所感之气，所入之门，所受之处，及其传变之体，平日所用历验方法，详述于下，以俟高明者正之。", "自叙"),
    ("时崇祯壬午仲秋姑苏洞庭吴有性书于淡淡斋", "自叙落款"),
    ("温疫论 明 吴又可", "卷首题行"),
    ("疫者感天地之疠气，在岁有多寡；在方隅有浓薄；在四时有盛衰。此气之来，无论老少强弱，触之者即病。", "原病"),
    ("邪自口鼻而入", "原病"),
    ("舍于伏脊之内，去表不远，附近于胃", "原病"),
    ("是为半表半里", "原病"),
    ("昔有三人，冒雾早行，空腹者死，饮酒者病，饱食者不病。", "原病"),
    ("有先表而后里者，有先里而后表者，有但表而不里者，有但里而不表者，有表里偏胜者，有表里分传者，有表而再表者，有里而再里者。有表里分传而又分传者。", "原病九传"),
    ("温疫初起，先憎寒而后发热，日后但热而无憎寒也。", "温疫初起"),
    ("初得之二三日，其脉不浮不沉而数，昼夜发热，日晡益甚，头疼身痛", "温疫初起"),
    ("上用水二钟，煎八分，午后温服。", "达原饮用法"),
    ("槟榔能消能磨，除伏邪，为疏利之药，又除岭南瘴气", "达原饮按"),
    ("破戾气所结", "达原饮按"),
    ("辛烈气雄，除伏邪盘踞", "达原饮按"),
    ("热伤津液，加知母以滋阴", "达原饮按"),
    ("热伤营血，加白芍以和血", "达原饮按"),
    ("清燥热之余", "达原饮按"),
    ("为和中之用", "达原饮按"),
    ("三味协力，直达其巢穴，使邪气溃败，速离膜原，是以为达原也。", "达原饮按"),
    ("以后四味，不过调和之剂，如渴与饮，非拔病之药也。", "达原饮按"),
    ("此一日之间，而有三变，数日之法，一日行之。因其毒甚，传变亦速，用药不得不紧。", "急证急攻"),
    ("此邪不在经，汗之徒伤表气，热亦不减", "温疫初起"),
    ("此邪不在里，下之徒伤胃气，其渴愈甚", "温疫初起"),
    ("医者不知九传之法，不知邪之所在，如盲者之不任杖，聋者之听宫商，无音可求，无路可适", "统论疫有九传治法"),
    ("表证多而里证少，当治其表，里证兼之", "统论疫有九传治法"),
    ("但治其里，表证自愈", "统论疫有九传治法"),
    ("大约病偏于一方，延门阖户，众人相同，皆时行之气，即杂气为病也。", "杂气论"),
    ("至于瓜瓤瘟、疙瘩瘟，缓者朝发夕死，急者顷刻而亡，此在诸疫之最重者。", "杂气论"),
    ("或时众人头面浮肿，俗名为大头瘟是也", "杂气论"),
    ("或时众人咽痛，或时音哑", "杂气论"),
    ("或时众人呕血暴下，俗名为瓜瓤瘟，探头瘟是也", "杂气论"),
    ("实不知杂气为病，更多于六气为病者百倍，不知六气有限，现下可测，杂气无穷，茫然不可测也。", "杂气论"),
    ("夫物者气之化也，气者物之变也，气即是物，物即是气，知气可以知物，则知物之可以制气矣。", "论气所伤不同"),
    ("牛病而羊不病，鸡病而鸭不病，人病而禽兽不病，究其所伤不同，因其气各异也。", "论气所伤不同"),
    ("能知以物制气，一病只有一药之到病已，不烦君臣佐使品味加减之劳矣。", "论气所伤不同"),
    ("邪之着人，如饮酒然。", "知一"),
    ("有醉后妄言妄动，醒后全然不知者；有虽沉醉而神思终不乱者；醉后应面赤而反刮白者；应痿弱而反刚强者", "知一"),
    ("至论醉酒一也，及醒一时诸态如失。", "知一"),
    ("若纯用破气之品，津液愈耗，热结愈固", "妄投破气药论"),
    ("譬若河道阻塞，前舟既行，余舟连尾而下矣。", "妄投破气药论"),
    ("今投补剂，邪气益固，正气日郁，转郁转热，转热转瘦，转瘦转补，转补转郁，循环不已，乃至骨立而毙", "妄投补剂论"),
    ("病家止误一人，医者终身不悟，不知杀人无算。", "妄投补剂论"),
    ("若概用寒凉，何异扬汤止沸", "妄投寒凉药论"),
    ("三春旱草，得雨滋荣；残腊枯枝，虽灌弗泽。", "老少异治"),
    ("所以老年慎泻，少年慎补，何况误用耶！", "老少异治"),
    ("如鸟栖巢，如兽藏穴，营卫所不关，药石所不及", "行邪伏邪之别"),
    ("邪伏于膜原", "行邪伏邪之别"),
    ("温疫初起，先憎寒而后发热，日后但热而无憎寒也。初得之二三日，其脉不浮不沉而数，昼夜发热，日晡益甚，头疼身痛。", "温疫初起（方笺）"),
    ("邪不在经，汗之徒伤表气，热亦不减", "膜原图注"),
    ("邪不在里，下之徒伤胃气，其渴愈甚", "膜原图注"),
    ("能消能磨，除伏邪，为疏利之药，又除岭南瘴气", "方笺药注"),
    ("邪毒最重复瘀到胃，急投大承气汤", "一日三变"),
    ("万有年高禀浓，年少赋薄者，又当从权", "老少异治"),
    ("至夜半热退，次早鼻黑苔刺如失", "急证急攻"),
    ("受无形杂气为病，莫知何物之能制", "论气所伤不同"),
]
print("== 手工引文清单 -> 库内文件 ==")
for q, tag in QUOTES:
    check(q, tag)

# ---------- 页面引文块（blockquote p / q） -> 库内文件 ----------
print("\n== 页面引文块 -> 库内文件 ==")
body = html.split("</head>", 1)[1]
plain = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", body, flags=re.S)
blocks = []
for m in re.finditer(r"<blockquote[^>]*>(.*?)</blockquote>", html, re.S):
    b = re.sub(r"<span class=\"src\">.*?</span>", "", m.group(1), flags=re.S)
    blocks.append(re.sub(r"<[^>]+>", "", b))
blocks.extend(re.sub(r"<[^>]+>", "", q) for q in re.findall(r"<q[^>]*>(.*?)</q>", html, re.S))
for b in blocks:
    b = b.strip()
    if len(norm(b)) < 4:
        continue
    ok = norm(b) in lib
    print(("PASS" if ok else "FAIL"), b[:28])
    fail += 0 if ok else 1

# ---------- 整页反扫：12 字阈值，页面里任何 12 字库本成句必须落在已申报引文内 ----------
print("\n== 整页反扫（阈值 12 字） ==")
plain = re.sub(r"<[^>]+>", "", plain)
page = norm(plain)
decl = [norm(q) for q, _ in QUOTES]
mask = [False] * len(page)
for qn in decl:
    start = 0
    while True:
        i = page.find(qn, start)
        if i < 0:
            break
        for k in range(i, i + len(qn)):
            mask[k] = True
        start = i + 1
lib12 = {lib[i:i + 12] for i in range(len(lib) - 11)}
bad = []
i = 0
while i <= len(page) - 12:
    w = page[i:i + 12]
    if not any(mask[i:i + 12]) and w in lib12:
        j = i
        while j < len(page) and not mask[j]:
            j += 1
        bad.append((i, page[i:j]))
        i = j
    else:
        i += 1
if bad:
    for i, s in bad[:12]:
        print("FAIL 反扫命中", f"@{i}", s[:60])
    fail += len(bad)
else:
    print("PASS 整页反扫无未申报库本成句")

# ---------- 排版规则 ----------
print("\n== 排版规则 ==")
for n, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：长划线，行", n, line.strip()[:40])
        fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", n, line.strip()[:40])
        fail += 1

# ---------- 硬性视觉 ----------
checks = [
    ("#191917" in html, "墨底 #191917"),
    ("#e8e4dc" in html, "纸白 #e8e4dc"),
    ("#5f9270" in html, "竹青 #5f9270"),
    ("Songti SC" in html, "宋体族"),
    ("@import" not in html and "<link" not in html and "url(http" not in html, "无外部字体样式"),
    ("<script src=" not in html and "<img" not in html and 'src="http' not in html, "无外部脚本图片"),
    ("殆知阁简体库" in html and "github.com/robertsong2000/daizhigev20" in html, "页脚来源与仓库"),
    ("逐字核验" in html and "现代医学" in html, "页脚核验声明与时代局限提醒"),
]
print("\n== 视觉 ==")
for ok, name in checks:
    print(("PASS" if ok else "FAIL"), name)
    fail += 0 if ok else 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
