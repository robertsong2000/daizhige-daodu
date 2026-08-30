#!/usr/bin/env python3
"""核验 jingchu-suishiji.html 中的引文是否与殆知阁库内《荆楚岁时记》逐字一致。"""
import re, sys

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/荆楚岁时记.txt"
SRC_TG = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/编年/资治通鉴.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/jingchu-suishiji.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

QUOTES = [
    # hero 轮心
    ("腊鼓鸣", "轮心谚"),
    ("春草生", "轮心谚"),
    # 壹 骨架（无引文）
    # 贰 江陵来的人（辅证引文，对库内《资治通鉴》核验）
    ("文武之道，今夜尽矣", "burnline 辅证 资治通鉴卷一六五"),
    # 叁 节日卡
    ("正月一日。是三元之日也。谓之端月", "元日 三元"),
    ("于是长幼悉正衣冠。以次拜贺。进椒柏酒。饮桃汤。进屠苏酒。胶牙饧。下五辛盘。进敷于散。服却鬼丸。各进一鸡子。凡饮酒次第。从小起", "元日 拜贺"),
    ("饮必自幼。云少者得岁。故先饮。老者失岁。故后饮", "元日 按屠苏"),
    ("先于庭前爆竹。以辟山臊恶鬼", "爆竹"),
    ("西方山中有人焉。其长尺余。一足。性不畏人。犯之则令人寒热。名曰山臊", "山臊按"),
    ("帖画鸡。或斲镂五采及土鸡于户上。造桃板着户。谓之仙木。绘二神。贴户左右。左神荼。右郁垒。俗谓之门神", "门神"),
    ("正月七日。为人日。以七种菜为羹。翦彩为人。或镂金箔为人。以贴屏风。亦戴之以头鬓。亦造华胜以相遗。登高赋诗", "人日"),
    ("正月一日为鸡。二日为狗。三日为羊。四日为猪。五日为牛。六日为马。七日为人", "六畜日按"),
    ("正月十五日。作豆糜。加油膏其上。以祠门户", "上元 豆糜"),
    ("其夕迎紫姑。以卜将来蚕桑。并占众事", "上元 紫姑"),
    ("紫姑本人家妾。为大妇所妒。正月十五日感激而死。故世人作其形迎之", "紫姑按"),
    ("去冬节一百五日。即有疾风甚雨。谓之寒食。禁火三日。造饧大麦粥", "寒食"),
    ("三月三日。四民并出江渚池沼间。临清流。为流杯曲水之饮", "上巳"),
    ("五月俗称恶月。多禁忌曝床荐席。及忌盖屋", "恶月"),
    ("五月五日。谓之浴兰节。四民并蹋百草之戏。采艾以为人。悬门户上。以禳毒气。以菖蒲或镂或屑以泛酒", "浴兰节"),
    ("是日竞渡。采杂药", "竞渡"),
    ("七月七日。为牵牛织女聚会之夜", "七夕"),
    ("是夕。人家妇女结彩缕。穿七孔针。或以金银石为针。陈几筵酒脯瓜果于庭中。以乞巧。有喜子网于瓜上。则以为符应", "乞巧"),
    ("旧说天河与海通。近世有人居海渚者。每年八月。有浮槎去来不失期", "浮槎（白话转述所本）"),
    ("七月十五日。僧尼道俗。悉营盆供诸仙", "中元"),
    ("目连见其亡母生饿鬼中。即以钵盛饭。往饷其母。食未入口。化成火炭。遂不得食", "目连按"),
    ("九月九日。四民并籍野饮宴", "重九"),
    ("急令家人缝囊。盛茱萸系臂上。登山饮菊花酒。此祸可消", "桓景按"),
    ("举家登山。夕还。见鸡犬牛羊一时暴死", "桓景按续"),
    ("十二月八日为腊日。史记陈胜传。有腊日之言。是谓此也。谚言。腊鼓鸣。春草生。村人并系细腰鼓。戴胡公头。及作金刚力士。以逐疫。沐浴转除罪障", "腊日"),
    ("其日。并以豚酒祭灶神", "祭灶"),
    ("姓苏名吉利。妇姓王名搏颊", "灶神名按"),
    ("岁暮。家家具肴蔌一作核。诣宿岁之位。以迎新年。相聚酣饮", "守岁"),
    ("三百六旬之尽。七十二候之穷", "年穷极辑佚"),
    # 肆 注者的声音
    ("据左传及史记。并无介推被焚之事", "注 寒食"),
    ("然则禁火。周之旧制也", "注 寒食续"),
    ("俗为屈原投汨罗日。伤其死所。故并命舟楫以拯之", "注 竞渡屈原说"),
    ("斯又东吴之俗。事在子胥。不关屈平也", "注 竞渡子胥说"),
    ("越地传云。起于越王勾践。不可详矣", "注 竞渡勾践说"),
    ("俗人月讳。何代无之。但当矫之。归于正耳", "注 恶月"),
    # 伍 散叶
    ("正月夜。多鬼鸟度。家家槌床打户。捩狗耳。灭灯烛。以禳之", "佚文 鬼车鸟"),
    ("凡有桥处。相率以过。名走百病", "佚文 走百病"),
    ("江南风俗。谓正月三十日为补天日。以红丝缕系煎饼。置屋上。谓之补天穿", "佚文 补天穿"),
]

text = norm(open(SRC, encoding="utf-8").read())
text_tg = norm(open(SRC_TG, encoding="utf-8").read())
fail = 0
for q, where in QUOTES:
    pool = text_tg if "资治通鉴" in where else text
    ok = norm(q) in pool
    print(("PASS" if ok else "FAIL"), where, q[:18] + ("…" if len(q) > 18 else ""))
    fail += 0 if ok else 1

# 页面所有引文块（blockquote.q 与 div.zhu）整体复核
html = open(PAGE, encoding="utf-8").read()
blocks = []
for m in re.finditer(r'<blockquote class="q">(.*?)</blockquote>', html, re.S):
    body = re.sub(r'<span class="from">.*?</span>', "", m.group(1), flags=re.S)
    blocks.append(re.sub(r"<[^>]+>", "", body))
for m in re.finditer(r'<div class="zhu">(.*?)</div>', html, re.S):
    body = re.sub(r'<span class="from">.*?</span>', "", m.group(1), flags=re.S)
    body = re.sub(r"<b>按</b>", "", body)
    blocks.append(re.sub(r"<[^>]+>", "", body))

print(f"\n页面引文块 {len(blocks)} 个（blockquote.q + 注卡）：")
for b in blocks:
    b = b.strip().replace("「", "").replace("」", "")
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
