# -*- coding: utf-8 -*-
"""勿庵历算书记 导读页构建：解析88条签 + 生成静态页面"""
import re, json, html

SRC = "daizhige-simplified/子藏/算法/勿庵历算书记.txt"
OUT = "daizhige-daodu/wuan-lisuan-shuji.html"

lines = open(SRC).read().split("\n")

# ---- 解析条目 ----
# 手工帙分组（行号 -> 帙名）
LI_GROUP = {
 21:"发轫",54:"发轫",56:"发轫",58:"发轫",164:"发轫",134:"发轫",
 23:"通考",25:"通考",32:"通考",48:"通考",62:"通考",64:"通考",66:"通考",70:"通考",113:"通考",168:"通考",
 34:"史志",36:"史志",38:"史志",40:"史志",42:"史志",45:"史志",51:"史志",
 76:"交食",78:"交食",82:"交食",88:"交食",94:"交食",98:"交食",
 101:"行度",102:"行度",104:"行度",106:"行度",108:"行度",68:"行度",72:"行度",74:"行度",115:"行度",
 117:"通考",
 111:"测器",120:"测器",122:"测器",124:"测器",126:"测器",128:"测器",130:"测器",132:"测器",
 136:"测器",138:"测器",140:"测器",142:"测器",144:"测器",146:"测器",148:"测器",150:"测器",152:"测器",154:"测器",60:"测器",
 156:"参商",158:"参商",162:"参商",166:"参商",
}
SU_GROUP = {
 172:"通算",174:"通算",176:"通算",178:"通算",181:"通算",206:"通算",238:"通算",
 188:"几何",195:"几何",197:"几何",208:"几何",210:"几何",216:"几何",218:"几何",220:"几何",224:"几何",226:"几何",230:"几何",232:"几何",
 193:"古算",200:"古算",204:"古算",236:"古算",
 212:"器用",214:"器用",234:"器用",
}
ATTACH = {90:"并入交食蒙求订补",93:"并入交食蒙求订补",228:"附入用句股解几何之根"}

def parse_entry(ln):
    s = lines[ln-1].strip()
    body = s[1:]  # 去掉「一」
    m = re.match(r"^(.*?卷)", body)
    if m and "【原自为" not in body[:6]:
        title = m.group(1)
        rest = body[m.end():]
    else:
        # 无卷数标题：到行末或【】组结束
        title = body; rest = ""
    # 标题拆：名 + 【状态】
    st = ""
    mm = re.search(r"【([^】]*)】\s*$", title)
    if mm:
        st = mm.group(1); title = title[:mm.start()]
    title = title.strip()
    return title, st, rest.strip()

# 解题行拼接：从标题行下一行到下一标题行前
def sol_text(ln, nxt):
    segs = []
    if ln+1 < nxt:
        segs.append(lines[ln].strip())
    for k in range(ln+1, nxt-0):
        if k+1 < nxt and not re.match(r"^　　一", lines[k]):
            segs.append(lines[k].strip())
        else:
            break
    return "".join(segs)

entries = []
allmarks = sorted(list(LI_GROUP)+list(SU_GROUP)+list(ATTACH))
for idx, ln in enumerate(allmarks):
    nxt = allmarks[idx+1] if idx+1 < len(allmarks) else len(lines)+1
    title, st, rest = parse_entry(ln)
    sol = rest + sol_text(ln, nxt)
    kind = "li" if ln in LI_GROUP else ("su" if ln in SU_GROUP else "at")
    grp = LI_GROUP.get(ln) or SU_GROUP.get(ln) or ""
    entries.append({"ln":ln,"kind":kind,"grp":grp,"title":title,"st":st,"sol":sol})

main = [e for e in entries if e["kind"]!="at"]
att  = [e for e in entries if e["kind"]=="at"]
print("main:", len(main), "attach:", len(att), "total:", len(entries))
for e in main[:3]+main[-3:]: print(e["ln"], e["grp"], e["title"], "|", e["st"][:16])
json.dump(entries, open("daizhige-daodu/.wuan_entries.json","w"), ensure_ascii=False, indent=1)
