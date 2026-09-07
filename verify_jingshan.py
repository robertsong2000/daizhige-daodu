#!/usr/bin/env python3
"""核验 jingshan-riji.html 引文与库内《景善日记》逐字一致（去标点+仅留汉字，双向）+ 反扫 + 红线 + 机数。"""
import re, sys
from html.parser import HTMLParser

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/景善日记.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/jingshan-riji.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

lib_raw = open(SRC, encoding="utf-8").read()
lib = norm(lib_raw)
html = open(PAGE, encoding="utf-8").read()
fail = 0

def check_in(q, where, tag):
    global fail
    ok = norm(q) in (lib if where is lib else norm(html))
    print(("PASS" if ok else "FAIL"), f"[{tag}]", norm(q)[:24])
    if not ok:
        fail += 1

# ---------- 手工引文清单（须同时见于库内与页面） ----------
QUOTES = [
    ("《景善曰记》", "书名行"),
    ("今上之立，国人颇有责言，谓不合于继嗣之正。", "废立"),
    ("可封为昏德公。昔金封宋帝，曾用此号。", "废立"),
    ("这是我们一家人会议，兼召汉大臣，不过是为体面。", "废立"),
    ("澜公言观皇帝神情，如在梦中。", "废立"),
    ("大儿恩珠（译音）向予索银五十两买银鼠外褂。此子性情悖逆，甚为不孝。", "索银"),
    ("予今年七十八岁，诸子欺予耳聋，无所不为，皆不肯向上学好，予家风堕矣。", "家风"),
    ("今年有闰八月，人人皆谓不祥之兆。", "家风"),
    ("初不甚信，后有人以枪击之，连放数次，拳民毫无所伤。", "试法"),
    ("言天降义和团，以灭洋人。", "试法"),
    ("这回一定把洋人赶走了，一点也不用疑虑。", "试法"),
    ("几百个洋鬼子，怕他什么。", "试法"),
    ("东汉末年，黄巾作乱，其首领张角，奉五斗米道亦有法术", "试法"),
    ("惟女子与小人为难养也。近之则不逊，远之则怨。", "试法"),
    ("言京中外国使馆，五曰之内，即可攻毁净尽，但荣禄从中为梗，乃朝廷之奸臣", "殿上"),
    ("帝亦不言", "殿上"),
    ("帝亦无言", "废立"),
    ("示予所拟上谕一道，乃与各国开战者，彼预拟以待太后盖玺", "起坛"),
    ("有小孩五六人，约十三四岁，状若昏迷，口中喷沫，起而奋跳，执近前之物，乱跳乱舞，口出怪声，如疯狂然。", "起坛"),
    ("言若攻外国使馆，实与公法不合。", "独对"),
    ("荣禄奏对时，无一人在侧，退出后，直回其家，亦未与同僚一言。", "独对"),
    ("一夜火光四起，殊为奇观。", "火光"),
    ("其中教民数百，无论男妇老幼，均被焚死，臭味难闻，二人为之掩鼻。", "火光"),
    ("老佛爷在南海西小山上望见火光，看烧顺治门法国教堂，甚为清楚。", "火光"),
    ("予老矣，今曰得亲逢此盛事，真幸福也。", "火光"),
    ("火炎昆冈，玉石俱焚。", "玉石"),
    ("义和团本是好人，但其中亦有坏人搀杂于内，希图趁火抢劫。", "玉石"),
    ("请太后归政，以大权让与皇帝，废大阿哥，并许洋兵一万入京（此乃假造之文也）。", "假照会"),
    ("他们怎么敢干涉我的大权？此能忍，孰不能忍！", "假照会"),
    ("拚死一战，强于受他们的欺侮！", "假照会"),
    ("中国与各国开战，非由我启衅，乃各国自取。但围攻使馆之事，决不可行。若如端王等所主张，则宗庙社稷，实为危险。", "宣战"),
    ("你要是除这话之外，再没有别的好主意，可即退出，不必在此多话。", "宣战"),
    ("启秀遂由靴中取出所拟宣战之谕，进呈御览。", "宣战"),
    ("皇帝面色灰白，入座之时，战栗不已。", "宣战"),
    ("臣在总理衙门当差二年，见外国人皆和平讲礼，不信有请太后归政之照会。", "宣战"),
    ("肯听此汉奸之言吗？", "宣战"),
    ("酒乃最好之物。我平常每次可饮四五斤，但那天实未饮一杯。你怕我要倚酒希图减罪吗？", "安海"),
    ("安海真一忠勇之人，侃侃不惧，观者皆为动容，觉中国军中尚有英雄也。", "安海"),
    ("次曰即交于德人，在克林德被杀之地杀之。", "安海"),
    ("安海为国而死，当邀皇太后、皇上之悯惜，加以荣典，谨此具奏。", "安海"),
    ("心中甚乐。汝等即杀予以偿命可也。", "勘注阙文"),
    ("性情悖逆，甚为不孝", "井（回调）"),
    ("索银五十两买银鼠外褂", "井（回调）"),
    ("五月二十四曰", "同日重出"),
]

for q, tag in QUOTES:
    check_in(q, lib, "库内")
    check_in(q, html, "页面")

# ---------- 页面引文节点收集 ----------
EXEMPT = {"kc","dnum","dtag","rl","gh","stamp","verse","perf","leafcard"}
SKIP = {"style","script"}

class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack=[]   # (kind, exempt)  kind in SKIP,Q,KQ,P
        self.qnodes=[]
        self.kqnodes=[]
        self.bracket=[]
        self.nodes=[]   # (text, exempt)
    def handle_starttag(self,tag,attrs):
        if tag in SKIP: self.stack.append(("SKIP",True)); return
        d=dict(attrs); cls=d.get("class","") or ""
        cs=set(cls.split())
        if tag=="i" or tag=="small": self.stack.append(("I",True))
        elif tag=="span" and "q" in cs: self.stack.append(("Q",True))
        elif "kq" in cs: self.stack.append(("KQ",True))
        else: self.stack.append(("P", bool(cs & EXEMPT)))
    def handle_endtag(self,tag):
        if self.stack: self.stack.pop()
    def handle_data(self,data):
        kinds=[k for k,_ in self.stack]
        exempt=any(e for _,e in self.stack)
        for m in re.finditer(r"「([^」]{2,})」",data):
            self.bracket.append(m.group(1))
        if "SKIP" in kinds or "I" in kinds: return
        if "Q" in kinds: self.qnodes.append(data)
        elif "KQ" in kinds: self.kqnodes.append(data)
        else: self.nodes.append((data,exempt))

c=Collector(); c.feed(html)
onpage_q=[re.sub(r"<[^>]+>","",q) for q in c.qnodes]
print(f"页面 .q 节点 {len(onpage_q)} 个")
for q in onpage_q:
    check_in(q, lib, "q→库")
bad=0
print(f"行内「」引文 {len(c.bracket)} 段")
for q in c.bracket:
    if norm(q) not in lib:
        print("FAIL","[「」→库]",q); bad+=1
fail+=bad

# ---------- 反扫：未豁免文本节点，剥「」后 6 字连串不得撞库本 ----------
UI_OK=["光绪二十六年"]
hits=0
for txt,exempt in c.nodes:
    if exempt: continue
    s2=re.sub(r"「[^」]*」","",txt)
    for i in range(len(s2)-5):
        w=s2[i:i+6]
        if re.match(r"^[一-鿿]{6}$",w) and w in lib:
            if any(u in s2[max(0,i-8):i+10] for u in UI_OK): continue
            print("FAIL","[反扫]",w,"…",s2[max(0,i-10):i+14].replace("\n"," "))
            hits+=1
print(f"反扫命中 {hits} 处")
fail+=hits

# ---------- 红线 ----------
assert "—" not in html and "–" not in html, "长划线"
for ln in html.splitlines():
    assert ln.count("·") <= 1, f"一行多·: {ln[:40]}"
ext = [m for m in re.findall(r'(?:src|href)="([^"]+)"', html)
       if not (m.startswith("#") or m.endswith(".html") or "github.com/robertsong2000" in m)]
assert not ext, f"外部依赖: {ext}"
pua = [ch for ch in html if 0xE000 <= ord(ch) <= 0xF8FF or 0x20000 <= ord(ch) <= 0x3FFFF]
assert not pua, f"PUA/ExtB {len(pua)}"
print("红线：长划线/·/外部依赖/PUA 全过；「」闭合计数", html.count("「"), html.count("」"))

# ---------- 机数 ----------
flat = re.sub(r"\s", "", lib_raw)
assert len(flat) == 6277, len(flat)
assert flat.count("（译音）") == 2
assert flat.count("五月二十四曰") == 2
total_yue = flat.count("曰")
assert total_yue == 72, total_yue
assert len(c.kqnodes) >= 1, "库外引文块应至少 1 处（恽毓鼎段）"
assert "第二百三十四篇" in html and "二百三十四" in html
print(f"机数：库本去空白 {len(flat)} 字；十一叶（重出一见）；（译音）二见；曰 {total_yue} = 讹55 + 真17；.q 节点 {len(onpage_q)}；行内「」 {len(c.bracket)}")
print(f"共 {len(QUOTES)} 条手工引文")
sys.exit(1 if fail else 0)
