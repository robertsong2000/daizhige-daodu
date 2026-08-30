# -*- coding: utf-8 -*-
"""verify_zheyu.py — 折狱龟鉴导读页核验：引文逐字 + 排版红线 + 机器计数"""
import re, sys, os

PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/zheyu-guijian.html"
LIB  = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/法家/折狱龟鉴.txt"

html = open(PAGE, encoding="utf-8").read()
lib  = open(LIB, encoding="utf-8").read()

fails = []
def chk(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

def norm(s):
    return "".join(c for c in s if c.isalnum())

# ---------- QUOTES: 16 处 .q ----------
QUOTES = [
 "吴太子孙登，尝乘马出，有弹圆过。左右求之，适见一人，操弹佩圆，咸以为是。辞对不服。从者欲捶之，登不听。使求过圆，比之非类，乃见释。",
 "道显面有悲色。察狱以色，其此之谓乎！",
 "盖察狱之术有三：曰色，曰辞，曰情。",
 "盖宁可淹系以求其实，毋或滥刑以陷于冤",
 "马左而湿，湿，水也。左水右马，冯字也。两日，昌字也。其冯昌杀之乎？",
 "昌具首服，曰：“本与其妻谋杀董丰，期以新沐、枕枕为验，是以误中妇人。”",
 "举乃取猪二口，一杀之，一活之，而积薪烧之。活者口中有灰，杀者口中无灰。因验尸口，果无灰也。鞫之，服罪。",
 "有两人争鸡，琰问：“鸡早何食？”一云粟，一云豆。乃杀鸡破嗉，而有粟焉，遂罚言豆者。",
 "孝妇不当死，前太守强断之，咎傥在是乎？",
 "太守竟论杀孝妇。郡中枯旱三年。",
 "太守杀牛自祭孝妇家，因表其墓，天立大雨，岁孰。",
 "有民犯法，罪当杖脊。吏受赇，与之约曰：“今见尹，必付我责状。汝第号呼自辨，我与汝分罪。汝决杖，我亦决杖。”",
 "吏大声诃之曰：“但受脊杖出去，何用多言！”拯谓其招权，捽吏于庭，杖之十七。",
 "不知乃为所卖，卒如素约。",
 "怅束身自归，而法外加罪。懈怠失牛，事或可恕；加之木石，理有自诬。宜附罪疑从轻之例。",
 "如龟决疑，如鉴烛物，是亦惟良折狱之一助云。",
]
# 页面在 .q 之外逐字使用的库内句子
PLAIN_CHECKS = [
 "人之负冤，多因疑似，听者不能审谨，忿然作威，遂至枉滥",
 "临淄寡妇若不遇曹摅，则与东海、上虞无以异矣",
 "慝未显者，以物证之，则不可讳也",
 "占梦辞烦，删取其要",
 "矫枉过正，遂宽囚重，为彼窥测",
 "防其招权，不防其见卖",
 "善察奸者，可不鉴于此哉",
]

# ---------- 抓取页面 .q（无嵌套，直接非贪婪） ----------
qs = re.findall(r'<span class="q(?: inl)?">(.*?)</span>', html, re.S)
chk(len(qs) == 16, "页面 .q 引文数量 = 16（实得 %d）" % len(qs))

page_q_norm = norm(re.sub(r"<[^>]+>", "", " ".join(qs)))
for i, q in enumerate(QUOTES, 1):
    nq = norm(q)
    chk(nq in norm(lib),   "引文%02d 在库内逐字命中" % i)
    chk(nq in page_q_norm, "引文%02d 在页面 .q 中命中" % i)

page_all_norm = norm(re.sub(r"<[^>]+>", "", html))
for i, p in enumerate(PLAIN_CHECKS, 1):
    chk(norm(p) in norm(lib),  "白句%02d 在库内逐字命中" % i)
    chk(norm(p) in page_all_norm, "白句%02d 在页面命中" % i)

# ---------- 排版红线 ----------
chk("—" not in html and "–" not in html, "全文无 — 与 –")
strip_nl = re.sub(r"<[^>]+>", "", html)
bad = [l for l in strip_nl.split("\n") if l.count("·") > 1]
chk(not bad, "去标签后每行 · ≤ 1（违例 %d 行）" % len(bad))

# ---------- 页脚必备 ----------
for s in ["殆知阁简体库", "逐字比对通过", "时代局限", "github.com/robertsong2000/daizhige-daodu"]:
    chk(s in html, "页脚含「%s」" % s)

# ---------- 序号：title + kicker 同号 63 ----------
chk("导读之六十四" in html, "<title> 自标序号 63")
chk("之六十四" in html and "之六十三" not in html, "kicker 序号 64")
chk('href="doue-yuan.html"' in html and os.path.exists(
    os.path.join(os.path.dirname(PAGE), "doue-yuan.html")), "跨页链接 doue-yuan.html 存在")

# ---------- 库本机器计数 ----------
chk(len(lib) == 73476, "库本全帙 len = 73,476")
chk(sum(1 for c in lib if not c.isspace()) == 71503, "库本去空白 = 71,503")
chk(lib.count("按：") == 243, "库本按语 243 处")
chk(len(re.findall(r"折狱龟鉴译注卷[一二三四五六七八]", lib)) == 8, "译注卷次 8 卷")

MEN = ['释冤上','释冤下','辨诬','鞫情','议罪','宥过','惩恶','察奸','核奸','擿奸',
       '察慝','证慝','钩慝','察盗','迹盗','谲盗','察贼','迹贼','谲贼','严明','矜谨']
EXPECT = {'释冤上':17,'释冤下':20,'辨诬':20,'鞫情':8,'议罪':26,'宥过':7,'惩恶':14,
          '察奸':18,'核奸':17,'擿奸':4,'察慝':4,'证慝':13,'钩慝':4,'察盗':11,
          '迹盗':5,'谲盗':3,'察贼':6,'迹贼':4,'谲贼':4,'严明':18,'矜谨':20}
pos = [(m, re.search(r"^　+%s\s*$" % m, lib, re.M).start()) for m in MEN]
pos.append(("END", len(lib)))
seg_ok, total = True, 0
for i, m in enumerate(MEN):
    n = lib[pos[i][1]:pos[i+1][1]].count("按：")
    total += n
    if n != EXPECT[m]:
        seg_ok = False; print("  库内 %s 按=%d 预期=%d" % (m, n, EXPECT[m]))
chk(seg_ok and total == 243, "各门按语分布与库内逐段机算一致（合计 %d）" % total)

# 页面账册 21 格与数字一致
cells = re.findall(r'<div class="m(?: hot)?"><div class="mn">([^<]+)</div><div class="mc">按 (\d+)</div></div>', html)
chk(len(cells) == 21, "账册 21 门格（实得 %d）" % len(cells))
ledger = {m: int(n) for m, n in cells}
chk(ledger == EXPECT, "账册数字 = 库内分段机算")
nums = re.findall(r'class="mn">([^<]+)</div>', html)
chk(nums == MEN, "账册门名顺序 = 库本目录顺序")

# 页面声明数字与库内一致
for s in ["二百四十三处", "73,476", "二十一门", "八卷"]:
    chk(s in html, "页面声明含「%s」" % s)

print("\n%d 项断言，%d 项失败" % (
    3 + 2*len(QUOTES) + 2*len(PLAIN_CHECKS) + 3 + 4 + 2 + 1 + 1 + 4 + 1 + 1 + 1 + 1 + 1 + 4,
    len(fails)))
if fails:
    print("FAILED:"); [print(" -", f) for f in fails]; sys.exit(1)
print("ALL PASS")
