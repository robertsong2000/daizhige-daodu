#!/usr/bin/env python3
"""从库内《先拨志始》解析东林点将录与钦定逆案数据，注入页面模板，生成 xianbo-zhishi.html。"""
import json, re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/先拨志始.txt"
OUT = "/home/robertsong/workspace/claude/daizhige-daodu/xianbo-zhishi.html"

lines = open(SRC, encoding="utf-8").read().splitlines()

# ---------- 点将录 ----------
i0 = next(i for i, l in enumerate(lines) if l.strip().startswith("○东林点将录"))
i1 = next(i for i, l in enumerate(lines) if i > i0 and "韩敬造" in l)
seg = [l.strip().replace("　", "") for l in lines[i0 + 1 : i1]]
seg = [l for l in seg if l]

LEX = [
    "操江右佥都御史", "南京广东道御史", "南京吏部郎中", "南京江西道御史", "南京山西道御史",
    "南京四川道御史", "南京工科给事中", "礼部员外即", "左春坊左谕德", "吏科都给事中",
    "兵部左侍郎", "兵部右侍郎", "户部左侍郎", "户部右侍郎", "礼部右侍郎", "吏部左侍郎",
    "左副都御史", "左佥都御史", "右佥都御史", "翰林院修撰", "翰林院简讨", "翰林院检讨",
    "翰林院庶吉士", "吏部员外郎", "吏部郎中", "大理寺少卿", "太常寺少卿", "太仆寺少卿",
    "光禄寺少卿", "光禄寺寺丞", "尚宝司少卿", "尚宝司丞", "尚宝司卿", "广西道御史",
    "浙江道御史", "福建道御史", "陕西道御史", "山东道御史", "河南道御史", "湖广道御史",
    "江西道御史", "山西道御史", "云南道御史", "贵州道御史", "四川道御史", "湖南道御史",
    "兵科给事中", "户科给事中", "吏科给事中", "工科给事中", "刑科给事中", "左通政使",
    "左通政", "南京户部尚书", "大学士", "吏部尚书", "户部尚书", "礼部尚书", "兵部尚书",
    "刑部尚书", "工部尚书", "左都御史", "右都御史", "刑部侍郎", "内阁中书", "礼部主事",
    "左谕德", "御史",
]

roster, group, fail = [], "", []
for ln in seg:
    ln = ln.rstrip("。")
    if ln.startswith("开山元帅"):
        roster.append({"g": "开山元帅", "star": "", "nick": "托塔天王", "office": "南京户部尚书", "name": "李三才"})
        continue
    if "协同参赞军务头领一员" in ln:
        body = ln.split("协同参赞军务头领一员")[0]
        m = re.match(r"^([天地][^星]{0,5}星(?:（[^）]*）)?)(.+)$", body)
        star, rest = m.group(1), m.group(2)
        roster.append({"g": group, "star": star, "nick": rest[: rest.index("左都御史")],
                       "office": "左都御史", "name": rest.replace(rest[: rest.index("左都御史")], "").replace("左都御史", "")})
        group = "协同参赞军务头领一员"
        continue
    if ln.endswith("：") and ln.count("星") == 0:
        group = ln[:-1]
        continue
    m = re.match(r"^([天地][^星]{0,5}星(?:（[^）]*）)?)(.+)$", ln)
    if not m:
        fail.append(ln)
        continue
    star, rest = m.group(1), m.group(2)
    best, bend = "", -1
    for off in LEX:
        p = rest.rfind(off)
        if p >= 0 and (p + len(off) > bend or (p + len(off) == bend and len(off) > len(best))):
            best, bend = off, p + len(off)
    if not best:
        fail.append(ln)
        continue
    nick, name = rest[: bend - len(best)], rest[bend:]
    if not re.fullmatch(r"[一-鿿]{2,3}", name) or not nick:
        fail.append(ln)
        continue
    roster.append({"g": group, "star": star, "nick": nick, "office": best, "name": name})

if fail:
    print("点将录解析失败：", fail)
    sys.exit(1)
tian = sum(1 for r in roster if r["star"].startswith("天"))
di = sum(1 for r in roster if r["star"].startswith("地"))
print(f"点将录：共 {len(roster)} 员，天罡 {tian}，地煞 {di}")

# ---------- 钦定逆案 ----------
t = "\n".join(lines).replace(" ", "").replace("　", "")
i0 = t.index("○钦定逆案")
body = t[i0:]
parts = re.split(r"［一］", body)[1:]
nian = []
for p in parts:
    gname = p.split("：", 1)[0]
    segbody = p.split("：", 1)[1].split("［一］")[0]
    seglines = [x for x in segbody.split("\n") if x]
    if gname == "逆孽军犯":
        nameline = next(x for x in seglines if "、" in x)
        names = nameline.strip("。").split("、")
        note = next((x for x in seglines if x.startswith("（按")), "")
        nian.append({"g": gname, "n": len(names), "items": [nameline], "note": note})
    else:
        ents = [x for x in seglines if re.match(r"^[一-鿿]{2,4}，", x)]
        note = next((x for x in seglines if x.startswith("（按") or x.startswith("以上")), "")
        nian.append({"g": gname, "n": len(ents), "items": ents[:3], "note": note})
total = sum(x["n"] for x in nian)
for x in nian:
    print(f"逆案 {x['g']}：{x['n']} 人")
print(f"逆案合计：{total} 人")

# ---------- 模板 ----------
TEMPLATE = open("/home/robertsong/workspace/claude/daizhige-daodu/xianbo.tpl.html", encoding="utf-8").read()
html = TEMPLATE.replace("__ROSTER__", json.dumps(roster, ensure_ascii=False)) \
               .replace("__NIAN__", json.dumps(nian, ensure_ascii=False))
open(OUT, "w", encoding="utf-8").write(html)
print("已生成", OUT, len(html), "字节")
