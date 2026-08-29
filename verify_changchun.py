#!/usr/bin/env python3
"""核验 changchun-xiyouji.html 中的引文是否与殆知阁库内《长春真人西游记》逐字一致。

底本：道藏/藏外/长春真人西游记.txt（丛书集成初编本）。
归一规则：去标点等非汉字字符；库本「日」系统性讹作「曰」，两侧统一映射 曰→日 后比对；
「县虎头金牌」之「县」通「悬」，两侧均照录不映射。
"""
import re

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/道藏/藏外/长春真人西游记.txt"
SRC2 = "/home/robertsong/workspace/claude/daizhige-simplified/道藏/正统道藏正一部/长春真人西游记.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/changchun-xiyouji.html"

def norm(s):
    s = s.replace("曰", "日")
    return re.sub(r"[^一-鿿]", "", s)

raw = open(SRC, encoding="utf-8").read()
text = norm(raw)
raw2 = open(SRC2, encoding="utf-8").read()
fail = 0

def check(q, where):
    global fail
    ok = norm(q) in text
    print(("PASS" if ok else "FAIL"), where, q[:22] + ("…" if len(q) > 22 else ""))
    fail += 0 if ok else 1

# 页面 blockquote.sq 全部引文（显示端已将讹「曰」径改「日」）
SQ = [
    ("成吉思皇帝遣侍臣刘仲禄县虎头金牌，其文曰：如朕亲行，便宜行事。", "金牌"),
    ("我之行止，天也。非若辈所及知，当有留不住时，去也。", "行止"),
    ("无使真人饥且劳，可扶持缓缓来。", "敕刘仲禄"),
    ("齐人献女乐，孔子去鲁。余虽山野，岂与处女同行哉？", "辞女乐"),
    ("北度野狐岭，登高南望，俯视太行诸山，晴岚可爱，北顾但寒沙衰草，中原之风，自此隔绝矣。", "野狐岭"),
    ("妇人冠以桦皮，高二尺许，往往以皂褐笼之，富者以红绡，其末如鹅鸭，名曰故故，大忌人触", "故故"),
    ("又行十日，夏至，量日影三尺六七寸", "夏至影"),
    ("正如以扇翳灯，扇影所及，无复光明。其旁渐远，则灯光渐多矣。", "扇翳灯喻"),
    ("我来时当八九月，半山已上皆为雪。山前草木暖如春，山后衣衾冷如铁。", "金山诗结句"),
    ("邪精妖鬼，逢正人远避，书传所载，其孰不知？道人家何忧此事？", "白骨甸"),
    ("忽有大池，方圆几二百里，雪峰环之，倒影池中，师名之曰天池。", "天池"),
    ("桃花石诸事皆巧。桃花石，谓汉人也。", "桃花石"),
    ("方算端氏之未败也，城中常十万余户。国破而来，存者四之一", "邪米思干"),
    ("上劳之曰：他国征聘皆不应，今远逾万里而来，朕甚嘉焉。对曰：山野奉诏而赴者，天也。上悦，赐坐，食次，问真人远来，有何长生之药以资朕乎？师曰：有卫生之道，而无长生之药。上嘉其诚实", "初见"),
    ("上曰：自今以往，可呼神仙。", "神仙号"),
    ("我之帝所临河上，欲罢干戈致太平。", "中秋诗"),
    ("神仙三说养生之道，我甚入心，使勿泄于外。", "三说"),
    ("据丘神仙底应系出家门人等随处院舍，都教免了差发赋税者", "免税圣旨"),
    ("四大假躯，终为朽物。一灵真性，自在无拘。", "赵九古墓前"),
    ("虽救之不得，犹愈于坐视其死也。", "招谕"),
    ("朕常念神仙，神仙无忘朕。", "贾昌传旨"),
    ("三载归，三载归。", "归期"),
    ("初，师之西行也，众请还期。师曰：三载归，三载归。至是，果如其言。", "三载应验"),
    ("丘神仙，你春月行程别来至夏日，路上炎热艰难来，沿路好底铺马得骑来么？路里饮食广多不少来么？你到宣德州等处，官员好觑你来么？下头百姓得来么？我这里常思量着神仙你，我不曾忘了你，你休忘了我者。", "圣旨其四"),
    ("山摧池枯，吾将与之俱乎？", "池枯"),
    ("我九日上堂去也。", "九日上堂"),
]
for q, where in SQ:
    check(q, where)

# 页面行文中的内联引文（非 blockquote）
INLINE = [
    ("白刃临头，犹不畏惧。况盗贼未至，复预忧乎", "行内 盗贼"),
    ("道人不以死生动心，不以苦乐介怀", "行内 师训"),
    ("黑车白帐，随水草放牧", "行内 白帐"),
    ("有上古之遗风焉", "行内 遗风"),
    ("凡疲兵至此，十无一还", "行内 白骨甸注"),
    ("刊木为四十八桥，桥可并车", "行内 四十八桥"),
    ("以农桑为务", "行内 大石林牙"),
    ("传国几百年", "行内 大石林牙"),
    ("翕然归慕", "行内 燕京归慕"),
    ("道家事一仰神仙处置", "行内 金虎牌"),
    ("百姓佥曰：神仙雨也", "行内 神仙雨"),
    ("非尔所知也", "行内 祈雨答"),
    ("三太子修金山，二太子修阴山", "行内 开路注"),
    ("二千之罪，莫大于不孝", "行内 震雷问"),
    ("朕已深省，神仙劝我良是", "行内 谏猎"),
    ("如朕亲行，便宜行事", "行内 路引"),
    ("路里饮食广多不少来么", "行内 圣旨其四小注"),
]
for q, where in INLINE:
    check(q, where)

# 数字核对：库内实测字符数（含标点空白）
n1, n2 = len(raw), len(raw2)
print(f"\n藏外本字符数：{n1}，道藏本字符数：{n2}，藏外本汉字数：{len(text)}")
for val, name in ((24472, "藏外本 24472"), (25157, "道藏本 25157")):
    src = raw if "藏外" in name else raw2
    print(("PASS" if len(src) == val else "FAIL"), f"页面声称{name}")
    fail += 0 if len(src) == val else 1

# 反向抽查：页面所有 blockquote.sq 内容必须命中
html = open(PAGE, encoding="utf-8").read()
blocks = re.findall(r"<blockquote class=\"sq\">(.*?)</blockquote>", html, flags=re.S)
print(f"\n页面引文块 {len(blocks)} 个（blockquote.sq）：")
for b in blocks:
    body = re.sub(r"<span.*?</span>", "", b, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body).strip()
    check(body, "页面块")

# 排版规则：禁止长划线；每行 · 最多 1 个
for i, line in enumerate(html.splitlines(), 1):
    if "—" in line or "–" in line:
        print("FAIL", f"长划线 行{i}"); fail += 1
    if line.count("·") > 1:
        print("FAIL", f"多点 行{i}"); fail += 1
print("排版检查：长划线与行内多点 已扫描")

print(("\nALL PASS" if fail == 0 else f"\nFAILED {fail}"))
raise SystemExit(0 if fail == 0 else 1)
