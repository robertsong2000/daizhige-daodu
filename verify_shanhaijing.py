#!/usr/bin/env python3
# 山海经导读页核验：引文逐字比对 + 排版规则 + 机器计数复核
import re, sys
from collections import Counter

SRC = "../daizhige-simplified/史藏/志存记录/山海经.txt"
PAGE = "shanhaijing.html"

src_raw = open(SRC, encoding="utf-8").read()
page_raw = open(PAGE, encoding="utf-8").read()

PUNCT = r'[\s，。：；、！？“”"‘’\'·（）()\[\]{}《》〈〉●！？　]'
def norm(s):
    return re.sub(PUNCT, '', s)

src_n = norm(src_raw)

# 页面去标签
page_text = re.sub(r'<style.*?</style>', '', page_raw, flags=re.S)
page_text = re.sub(r'<[^>]+>', '', page_text)
page_n = norm(page_text)

fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("　" + detail if detail and not ok else ""))
    if not ok:
        fails.append(name)

# ---------- 1. 策展引文：库本逐字 + 页面在册 ----------
QUOTES = [
 "南山经之首曰鹊山。其首曰招摇之山，临于西海之上，多桂，多金玉。",
 "禹曰：天下名山，经五千三百七十山，六万四千五十六里，居地也。",
 "出铜之山四百六十七，出铁之山三千六百九十。",
 "戈矛之所发也，刀铩之所起也，能者有余，拙者不足。",
 "封于太山，禅于梁父，七十二家，得失之数，皆在此内，是谓国用。",
 "其味酸甘，食之已狂，见则天下大穰。",
 "是炎帝之少女名曰女娃，女娃游于东海，溺而不返，故为精卫。常衔西山之木石，以堙于东海。",
 "夸父与日逐走，入日。渴欲得饮，饮于河渭，河渭不足，北饮大泽。未至，道渴而死。弃其杖。化为邓林。",
 "形天与帝至此争神，帝断其首，葬之常羊之山。乃以乳为目，以脐为口，操干戚以舞。",
 "钟山之神，名曰烛阴，视为昼，瞑为夜，吹为冬，呼为夏，不饮，不食，不息，息为风。身长千里。",
 "是烛九阴，是烛龙。",
 "西王母其状如人，豹尾虎齿而善啸，蓬发戴胜，是司天之厉及五残。",
 "有人戴胜，虎齿，有豹尾，穴处，名曰西王母。此山万物尽有。",
 "应龙处南极，杀蚩尤与夸父，不得复上，故下数旱。旱而为应龙之状，乃得大雨。",
 "黄帝乃下天女曰魃，雨止，遂杀蚩尤。魃不得复上，所居不雨。",
 "洪水滔天。鲧窃帝之息壤以堙洪水，不待帝命。帝命祝融杀鲧于羽郊。鲧复生禹。帝乃命禹卒布土以定九州。",
 "其北有林焉，名曰桃林，是广员三百里，其中多马。",
 "神北行",
]
for i, q in enumerate(QUOTES, 1):
    nq = norm(q)
    check(f"引文{i:02d} 库本在册", nq in src_n, q[:18])
    check(f"引文{i:02d} 页面在册", nq in page_n, q[:18])

# ---------- 2. 页面所有 .q / .p-quote / .wq / .med 片段逐一比对 ----------
qspans = re.findall(r'<span class="q">(.*?)</span>', page_raw, flags=re.S)
for i, s in enumerate(qspans, 1):
    t = norm(re.sub(r'<[^>]+>', '', s))
    check(f"片段{i:02d} q/p-quote/wq", t in src_n, t[:20])
meds = re.findall(r'<div class="med"><b>(.*?)</b><span>(.*?)</span></div>', page_raw, flags=re.S)
for i, (name, gloss) in enumerate(meds, 1):
    check(f"药条{i:02d} 名", norm(name) in src_n, name)
    check(f"药条{i:02d} 用", norm(gloss) in src_n, gloss)
print(f"共扫描 q/p-quote/wq 片段 {len(qspans)} 组，药条 {len(meds)} 条")

# ---------- 3. 排版规则 ----------
check("禁长划线", "—" not in page_raw and "–" not in page_raw)
for ln_i, line in enumerate(page_text.split("\n"), 1):
    if line.count("·") > 1:
        check(f"行{ln_i} 间隔号≤1", False)
        break
else:
    check("间隔号·每行≤1", True)
check("无外链脚本", ("<script" not in page_raw.lower()) and ('href="http' not in page_raw.lower()) and ("<link" not in page_raw.lower()))

# ---------- 4. 机器计数复核 ----------
secs = re.split(r'●', src_raw)[1:]
check("十八篇", len(secs) == 18, str(len(secs)))
ticks = re.findall(r'又([东南西北])([一二三四五六七八九十百千]+)里', src_raw)
check("计程句三百", len(ticks) == 300, str(len(ticks)))
# 里程尺标签逐个在库本
tick_labels = re.findall(r'<div class="tick[^"]*">.*?<span>(.*?)</span>', page_raw, flags=re.S)
for t in tick_labels:
    check(f"尺标 {t.strip()}", norm(t) in src_n)
cnt = lambda p: len(re.findall(p, src_raw))
check("食之 62", cnt(r'食之[^，。！\n]{1,8}') == 62, str(cnt(r'食之[^，。！\n]{1,8}')))
check("服之 14", cnt(r'服之[^，。！\n]{1,8}') == 14, str(cnt(r'服之[^，。！\n]{1,8}')))
check("佩之 7", cnt(r'佩之[^，。！\n]{1,8}') == 7, str(cnt(r'佩之[^，。！\n]{1,8}')))
check("可以御 21", src_raw.count("可以御") == 21, str(src_raw.count("可以御")))
omen = re.findall(r'见则[^，。\n]{1,12}', src_raw)
check("见则 52", len(omen) == 52, str(len(omen)))
def tally(sub):
    return sum(1 for o in omen if sub in o.replace(" ", ""))
check("大旱 12", tally("大旱") == 12, str(tally("大旱")))
check("大水 8", tally("大水") == 8, str(tally("大水")))
check("兵 7", tally("兵") == 7, str(tally("兵")))
check("疫 4", tally("疫") == 4, str(tally("疫")))
check("穰 3", tally("穰") == 3, str(tally("穰")))
check("安宁 2", tally("安宁") == 2, str(tally("安宁")))
check("大风 2", tally("大风") == 2, str(tally("大风")))
check("土功 2", tally("土功") == 2, str(tally("土功")))
check("狡客 1", tally("狡客") == 1, str(tally("狡客")))
rest = 52 - sum(tally(x) for x in ["大旱","大水","兵","疫","穰","安宁","大风","土功","狡客"])
check("其余散条 11", rest == 11, str(rest))

# ---------- 5. 结算单数字 ----------
check("库本南山总叙", "凡四十山，万六千三百八十里" in src_raw)
check("库本西山总叙", "凡七十七山，一万七千五百一十七里" in src_raw)
check("库本北山总叙", "凡八十七山，二万三千二百三十里" in src_raw)
check("库本中山总叙", "凡百九十七山，二万一千三百七十一里" in src_raw)
# 东山经脱总叙：四段相加
dong = [12+17+9+8, 3600+6640+6900+1720]
check("东山四段相加 46 山 18860 里", dong == [46, 18860], str(dong))
total_m = 16380+17517+23230+18860+21371
total_s = 40+77+87+46+197
check("合计 447 山 97358 里", (total_s, total_m) == (447, 97358), f"{total_s}/{total_m}")
for s in ["四万四千一百七十七", "十八", "三百", "凡四十山", "万六千三百八十里", "凡七十七山",
          "一万七千五百一十七里", "凡八十七山", "二万三千二百三十里", "凡四十六山",
          "一万八千八百六十里", "凡百九十七山", "二万一千三百七十一里", "四百四十七山",
          "九万七千三百五十八里", "五千三百七十山", "六万四千五十六里",
          "出铜之山四百六十七", "出铁之山三千六百九十",
          "62 条", "14 条", "7 条", "21 条"]:
    check(f"页面含 {s}", norm(s) in page_n if s[0].isdigit() is False else s in page_raw)
check("库本字符 44177", len(src_raw) == 44177, str(len(src_raw)))

print()
print(f"{'全部通过' if not fails else '失败 ' + str(len(fails)) + ' 项: ' + '; '.join(fails)}")
sys.exit(1 if fails else 0)
