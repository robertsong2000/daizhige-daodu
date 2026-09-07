#!/usr/bin/env python3
"""核验 xianbo-zhishi.html 引文、点将录、逆案数据与库内《先拨志始》逐字一致（去标点+异体归一，双向）。"""
import json, re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/先拨志始.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/xianbo-zhishi.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
text = norm(raw)
html = open(PAGE, encoding="utf-8").read()
fail = 0

def check(q, tag):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), f"[{tag}]", q[:28])
    if not ok:
        fail += 1

# ---------- 手工引文清单 ----------
QUOTES = [
    ("余年来屏居深山，先世遗书一散不可复返。日长如年，追忆家庭见闻，辄录片纸，投入甓中，至今春而甓且满矣。", "叙"),
    ("首纪国本，著门户之所由始也；终以逆案，著贞佞之所由判也。", "叙"),
    ("是贵辨之于早也。", "叙"),
    ("胎兆于娄东，派岐于四明，衅开于淮抚，而究以国本为归宿", "叙"),
    ("惨戮多贤，珰党煽虐之际", "叙"),
    ("凡逆贤所摧折者必东林人也，否则必不求异于东林者也。", "叙"),
    ("仍枭首于人烟凑集之所", "附妖书 圣旨"),
    ("昨梦观音大士说妖书系生光造的。", "妖言十大说"),
    ("哥儿，你莫恐！不干你事！但去读书写字，早些关门，晏些开门。", "妖书 谕太子"),
    ("似疯魔而又非疯魔者。", "梃击"),
    ("汝若不招，再加刑法。实招，与饭吃。不招，饿死。", "梃击"),
    ("我迷了", "梃击"),
    ("有马三舅、李外父，叫我跟不知姓名老公公，说“事成与几亩田地种，够你受用。”", "梃击"),
    ("你先撞一遭去。撞着二个，打杀一个，打杀了，我有力量救得你", "梃击"),
    ("打上宫去，撞一个打杀一个，打杀了小爷，吃也有你的，穿也有你的。", "梃击"),
    ("小爷洪福大了", "梃击"),
    ("每日章奏文书先奏选侍，方与朕览", "移宫"),
    ("侍从手抱八公主，徒步以行，凡簪珥衾裯之属俱为群阉所掠夺", "移宫"),
    ("伶仃之皇八妹入井谁怜？孀寡之未亡人雉经莫诉", "移宫"),
    ("雉经入井等语，有何凭据？", "移宫"),
    ("移宫自移宫，隆礼自隆礼，必两者相济而后二祖列宗之大宝始安，先帝在天之灵始安。", "移宫"),
    ("选侍又使李进忠牵朕衣。卿等亲见当日景象，安乎？危乎？当避宫乎？不当避宫乎？", "移宫"),
    ("逆贤辈不足责，熹庙中夜扪心，何以自解？", "移宫按"),
    ("当圣躬疾笃，正中外危疑之日，李可灼敢以无方无制之药，驾言金丹，夕进御而朝宾天。即不能深文以伸公讨，亦当治以庸医杀人之罪。", "红丸"),
    ("不要饿了他，也休要多了", "梃击"),
    ("革其已进仪注之贵妃，困其无端罗织之老父，伶仃之皇八妹入井谁怜？孀寡之未亡人雉经莫诉", "移宫"),
    ("遂致一激而为孙宗伯之弑逆，再激而为魏忠贤之爰书，党祸不已，国运随之。", "红丸按"),
    ("龙驭上宾矣。盖九月乙亥朔也。", "红丸"),
    ("若如此，不是明心堂，是昧心堂矣。", "六君子"),
    ("忠贤所恨，惟杨、左耳。杨、左死，四人犹或可生", "六君子"),
    ("庶有见天之日", "六君子"),
    ("追赃不允，仍着北司严限五日一比", "六君子"),
    ("各坐赃数万，俱拷掠无完肤。", "六君子"),
    ("每一公死，显纯即剔喉骨，用小盒封固送逆贤示信。", "六君子"),
    ("此福堂也，不死何待？", "六君子"),
    ("遂自尽刑部狱中。", "六君子"),
    ("天启四年甲子冬归安韩敬造。", "点将录"),
    ("惟天罡星少一人，地煞星多一人", "点将录按"),
    ("归安韩敬", "点将录"),
    ("魏忠贤，凶残祸国，僭肆逼尊，罪恶贯盈，神人共愤。逆形已著，寸磔允宜。", "逆案"),
    ("逆祠坊额碑文，人言多其缮写，已达天听，岂是风闻？", "逆案"),
]
print("== 手工引文清单 -> 库内文件 ==")
for q, tag in QUOTES:
    check(q, tag)

# ---------- 页面全部引文块双向覆盖 ----------
print("\n== 页面引文块（blockquote.bq + span.q） -> 库内文件 ==")
blocks = []
for m in re.finditer(r'<blockquote class="bq[^"]*">(.*?)</blockquote>', html, re.S):
    body = re.sub(r'<span class="from">.*?</span>', "", m.group(1), flags=re.S)
    blocks.append(re.sub(r"<[^>]+>", "", body))
blocks.extend(re.sub(r"<[^>]+>", "", q) for q in re.findall(r'<span class="q">(.*?)</span>', html, re.S))
for b in blocks:
    b = b.strip()
    if len(norm(b)) < 4:
        continue
    ok = norm(b) in text
    print(("PASS" if ok else "FAIL"), b[:26])
    fail += 0 if ok else 1

# ---------- 点将录数据 ----------
print("\n== 点将录 109 员 -> 库内文件 ==")
m = re.search(r"const ROSTER=(\[.*?\]);", html, re.S)
roster = json.loads(m.group(1))
if len(roster) != 109:
    print("FAIL 点将录人数", len(roster))
    fail += 1
for r in roster:
    s = r["star"] + r["nick"] + r["office"] + r["name"]
    ok = norm(s) in text
    if not ok:
        print("FAIL", s)
        fail += 1
tian = sum(1 for r in roster if r["star"].startswith("天"))
di = sum(1 for r in roster if r["star"].startswith("地"))
print("PASS" if (tian, di) == (35, 73) else "FAIL", f"点数 天罡{tian} 地煞{di}（须与按语'天罡少一人地煞多一人'相合）")
if (tian, di) != (35, 73):
    fail += 1

# ---------- 逆案数据 ----------
print("\n== 逆案七等 -> 库内文件 ==")
m = re.search(r"const NIAN=(\[.*?\]);", html, re.S)
nian = json.loads(m.group(1))
lines = [l.strip().replace(" ", "").replace("　", "") for l in raw.splitlines()]
# 从库内独立重算各级人数
i0 = next(i for i, l in enumerate(lines) if l.startswith("○钦定逆案"))
body = "\n".join(lines[i0:])
parts = re.split(r"［一］", body)[1:]
recount = {}
for p in parts:
    g = p.split("：", 1)[0]
    seg = p.split("：", 1)[1].split("［一］")[0]
    sl = [x for x in seg.split("\n") if x]
    if g == "逆孽军犯":
        nl = next(x for x in sl if "、" in x)
        recount[g] = len(nl.strip("。").split("、"))
    else:
        recount[g] = len([x for x in sl if re.match(r"^[一-鿿]{2,4}，", x)])
for g in nian:
    check_items = all(norm(it) in text for it in g["items"])
    print(("PASS" if check_items else "FAIL"), f"[{g['g']}] 样例条目")
    if not check_items:
        fail += 1
    ok = recount.get(g["g"]) == g["n"]
    print(("PASS" if ok else "FAIL"), f"[{g['g']}] 人数 {g['n']}（库内重算 {recount.get(g['g'])}）")
    if not ok:
        fail += 1
total = sum(g["n"] for g in nian)
print("PASS" if total == 289 else "FAIL", f"逆案合计 {total}（页面声明二百八十九）")
if total != 289:
    fail += 1
if "二百八十九人" not in html:
    print("FAIL 页面缺合计声明")
    fail += 1

# ---------- 排版规则 ----------
print("\n== 排版规则 ==")
for i, line in enumerate(html.split("\n"), 1):
    if "—" in line or "–" in line:
        print("FAIL 排版：长划线，行", i, line.strip()[:40])
        fail += 1
    if line.count("·") > 1:
        print("FAIL 排版：一行多个·，行", i, line.strip()[:40])
        fail += 1

# ---------- 硬性视觉 ----------
checks = [
    ("#191917" in html, "墨底 #191917"),
    ("#e8e4dc" in html, "纸白 #e8e4dc"),
    ("#c9963f" in html, "赭金 #c9963f"),
    ("Songti SC" in html, "宋体族"),
    ("@import" not in html and "<link" not in html and "url(http" not in html, "无外部字体样式"),
    ("<script src=" not in html and "<img" not in html and 'src="http' not in html, "无外部脚本图片"),
]
print("\n== 视觉 ==")
for ok, name in checks:
    print(("PASS" if ok else "FAIL"), name)
    fail += 0 if ok else 1

print("\n结果：", "全部通过" if fail == 0 else f"{fail} 处失败")
sys.exit(1 if fail else 0)
