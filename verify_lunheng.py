#!/usr/bin/env python3
# 论衡页核验：引文逐字对库 + 篇名归属定位 + 排版红线 + 机数复核
import re, sys

HTML = "/home/robertsong/workspace/claude/daizhige-daodu/lunheng.html"
LIB  = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/论衡.txt"
NUM  = "七十五"

def cjk(s):
    return "".join(ch for ch in s if "一" <= ch <= "鿿")

errs = []
def chk(cond, msg):
    if not cond:
        errs.append(msg)

lib = open(LIB, encoding="utf-8").read()
html = open(HTML, encoding="utf-8").read()
QUOTES = [
    "乃闭门潜思礼绝庆吊戸牖墙壁各置刀笔著论衡八十五篇二十余万言释物类同异",
    "中土未有传者蔡邕入吴防始得之常秘玩以为谈助",
    "或捜求其帐中隠处果得论衡抱数卷持去邕丁宁之曰",
    "邕丁宁之曰惟我与尔共之勿广也",
    "其后王郎来守防稽又得其书",
    "或曰不见异人当得异书",
    "问之果以论衡之益繇是遂见传焉",
    "改正涂注凡一万一千二百五十九字",
    "即募工刋印庶传不泯",
    "盛夏之时雷电迅疾击折树木坏败室屋时犯杀人",
    "世无愚智莫不谓然",
    "推人道以论之虚妄之言也",
    "何以验之雷者火也",
    "以人中雷而死即询其身中头则须髪烧燋中身则皮肤灼燌临其尸上闻火气一验也",
    "道术之家以为雷烧石色赤投于井中石燋井寒激声大鸣若雷之状二验也",
    "人伤于寒寒气入腹腹中素温温寒分争激气雷鸣三验也",
    "当雷之时电光时见大若火之耀四验也",
    "当雷之击时或燔人室屋及地草木五验也",
    "夫论雷之为火有五验言雷为天怒无一效",
    "然则雷为天怒虚妄之言",
    "难曰论语云迅雷风烈必变",
    "天之与人犹父子有父为之变子安能忽",
    "或颇有而增其语或无有而空生其言虚妄之俗好造怪竒",
    "世谓死人为鬼有知能害人",
    "试以物类验之死人不为鬼无知不能害人",
    "人物也物亦物也物死不为鬼人死何故独能为鬼",
    "凡天地之间有鬼非人死精神为之也皆人思念存想之所致也",
    "致之何由由于疾病人病则忧惧忧惧见鬼出",
    "畏惧则存想存想则目虚见",
    "伯乐学相马顾玩所见无非马者",
    "宋之庖丁学解牛三年不见生牛所见皆死牛也",
    "思念存想自见异物也",
    "皆存想虚致未必有其实也",
    "昼日则鬼见暮卧则梦",
    "儒者论圣人以为前知千岁后知万世",
    "事来则名不学自知不问自晓",
    "人才有髙下知物由学学之乃知不问不识",
    "所谓神者不学而知所谓圣者须学以圣",
    "天地之间含血之类无性知者",
    "世之治乱在时不在政国之安危在数不在教",
    "贤不贤之君明不明之政无能损益",
    "为善恶之行不在人质性在于岁之饥穰",
    "世儒学者好信师而是古以为贤圣所言皆无非",
    "夫贤圣下笔造文用意详审尚未可谓尽得实况仓卒吐言安能皆是",
    "何以验之以学于孔子不能极问也",
    "向偶翻阅诸书见有王充论衡喜其识博而言辩颇具出俗之识",
    "乃知其为背经离道好竒立异之人而欲以言传者也夫",
    "充则刺孟而且问孔矣此与明末李贽之邪说何异",
    "大抵订讹砭俗中理者多亦殊有禆于风教",
    "其书凡八十五篇而第四十四招致篇有录无书实八十四篇",
    "王充者防稽上虞人也字仲任",
    "论衡篇以十数亦一言也曰疾虚妄",
    "诗三百一言以蔽之曰思无邪",
    "如衡之平如鉴之开",
    "年渐七十时可悬舆",
    "世谓古人君贤则道德施行施行则功成治安",
    "其全书则未之览也",
]


# ---- 1. 每条库内原串唯一 ----
for r in QUOTES:
    chk(lib.count(r) == 1, "库内不唯一(%d): %s" % (lib.count(r), r[:20]))
chk(len(QUOTES) == 57, "引文清单应为 57 条，实 %d" % len(QUOTES))

chk("天之与人犹父子有父为之变子安能忽" in QUOTES, "扩引文未入清单")

# ---- 2. 页面 .q 收集（.q 内无嵌套 span，可能嵌 <b>，剥标签即可） ----
qs = re.findall(r'class="q"[^>]*>(.*?)</span>', html, re.S)
qnorms = [cjk(re.sub(r"<[^>]+>", "", q)) for q in qs]
chk(len(qnorms) == 57, "页面 .q 应 57 段，实 %d" % len(qnorms))

# ---- 3. .q 与库内原串一一配对（页面允许截去原串尾部，不许改动字序） ----
pool = [cjk(r) for r in QUOTES]
for i, qn in enumerate(qnorms):
    hit = [j for j, rn in enumerate(pool) if rn.startswith(qn)]
    chk(len(hit) == 1, "第%d段 .q 无法唯一配对: %s…" % (i + 1, qn[:16]))
    if len(hit) == 1:
        pool.pop(hit[0])
chk(not pool, "库内原串未被页面引用: %s" % [p[:16] for p in pool])
for qn in qnorms:
    chk(len(qn) >= 8, "过短引文: " + qn)

# ---- 4. 篇名归属定位（区间锚点） ----
def offset(kw, rev=False):
    return lib.rfind(kw) if rev else lib.find(kw)
pos = lambda s: lib.find(cjk(s))
blocks = [
    ("何以验之雷者火也", "雷虚篇", "道虚篇", False),
    ("世谓死人为鬼有知能害人", "论死篇", "死伪篇", True),
    ("凡天地之间有鬼非人死精神为之也", "订鬼篇", "言毒篇", True),
    ("人才有髙下知物由学学之乃知不问不识", "实知篇", "知实篇", False),
    ("所谓神者不学而知所谓圣者须学以圣", "实知篇", "知实篇", False),
    ("世之治乱在时不在政国之安危在数不在教", "治期篇", "齐世篇", True),
    ("世儒学者好信师而是古以为贤圣所言皆无非", "问孔篇", "非韩篇", False),
    ("论衡篇以十数亦一言也曰疾虚妄", "佚文篇", "论死篇", True),
    ("王充者防稽上虞人也字仲任", "自纪篇", "终末", True),
    ("如衡之平如鉴之开", "自纪篇", "终末", True),
    ("乃闭门潜思礼绝庆吊", "论衡后序", "终末", False),
]
anchor_pat = re.compile(r"\n　　([一-鿿]{1,5}篇)\n")
anchors = [(m.group(1), m.start()) for m in anchor_pat.finditer(lib)]
def nextpos(start_at, name):
    if name == "终末":
        return len(lib)
    for a, p in anchors:
        if p > start_at and a == name:
            return p
    return -1
for raw, a1, a2, rev in blocks:
    s = offset("\n　　" + a1 + "\n", rev)
    e = nextpos(s, a2)
    p = pos(raw)
    chk(s >= 0 and e > s, "锚点失效: %s→%s" % (a1, a2))
    chk(s < p < e, "归属失败: %s 不在 %s 区间" % (raw[:12], a1))
chk(lib.find("向偶翻阅诸书") < lib.find("钦定四库全书"), "御制批语应在卷首提要之前")

# ---- 5. 机数 ----
nchars = len(re.sub(r"\s", "", lib))
chk("213,814" in html and nchars == 213814, "字数口径不符: %d" % nchars)
for kw, disp in [("何以验之", 43), ("何以明之", 35), ("何以效之", 14), ("虚妄", 33)]:
    n = lib.count(kw)
    chk(n == disp, "%s 库内 %d 见, 页面申报 %d" % (kw, n, disp))
    chk('>%d</div>' % disp in html, "页面缺统计数 %d" % disp)
chk(lib.count("验也") == 54 and "五十四见" in html, "验也 54 见申报不符")
chk(43 + 35 + 14 == 92 and "九十二见" in html, "三连合计申报不符")
mu = lib[lib.find("论衡目录"):lib.find("论衡卷一", lib.find("论衡目录"))]
nmu = len(re.findall(r"[一-鿿]{1,6}第[一二三四五六七八九十百]{1,5}", mu))
chk(nmu == 85, "目录条目应 85, 实 %d" % nmu)
chk("招致第四十四" in mu, "目录缺招致条目")
nti = len(anchor_pat.findall(lib))
chk(nti == 84, "正文篇题应 84, 实 %d" % nti)
for cjkno in "一二三四五":
    chk('<span class="no mono">%s</span>' % cjkno in html, "五验缺第%s验" % cjkno)

# ---- 6. 排版红线 ----
chk("—" not in html, "出现长划线 —")
chk("–" not in html, "出现 – ")
for i, line in enumerate(html.split("\n"), 1):
    chk(line.count("·") <= 1, "第%d行 · 超限: %s" % (i, line.strip()[:40]))

# ---- 7. 页面自我申报 ----
chk("殆知阁导读 · 之%s" % NUM in html, "kicker 序号不符")
chk("<title>论衡 · 殆知阁导读之%s</title>" % NUM in html, "title 序号不符")
chk("github.com/robertsong2000/daizhigev20" in html, "页脚缺仓库链接")
chk("逐字核验" in html, "页脚缺核验声明")
chk("时代产物" in html, "页脚缺时代局限提醒")
chk(html.count("殆知阁古代文献简体库") == 1, "来源表述异常")

if errs:
    print("FAIL %d 项" % len(errs))
    for e in errs:
        print("  -", e)
    sys.exit(1)
print("PASS: 57 段 .q 逐字对库 + 篇名归属 11 区间 + 目录85/正文84 + 机数 + 红线 + 页面申报 全过")
