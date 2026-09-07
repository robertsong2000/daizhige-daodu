#!/usr/bin/env python3
"""核验 jinlouzi.html 引文与库内《金楼子》逐字一致（去标点+仅留汉字，双向）+ 反扫 + 红线 + 机数。"""
import re, sys
from html.parser import HTMLParser

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/金楼子.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/jinlouzi.html"

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
    ("吾今年四十六岁，自聚书来四十年，得书八万卷，河间之侔汉室，颇谓过之矣。", "聚书结尾"),
    ("合二十帙，一百一十五卷，并是元嘉书，纸墨极精奇。", "元嘉帙"),
    ("初出□在西省，蒙敕旨赉五经正副本。", "账·赐"),
    ("为东州时，写得《史》、《汉》、《三国志》、《晋书》。", "账·写"),
    ("为丹阳时，启请先宫书。", "账·请"),
    ("又于长沙寺经藏，就京公写得四部。", "账·得甲"),
    ("又得招提琰法师众义疏，及众经序。又得头陀寺昙智法师阴阳、卜祝、冢宅等书。", "账·得乙"),
    ("又聚得细书《周易》、《尚书》、《周官》、《仪礼》、《礼记》、《毛诗》、《春秋》各一部。", "账·聚"),
    ("又使孔昂写得《前汉》、《后汉》、《史记》、《三国志》、《晋阳秋》、《庄子》、《老子》、《肘后方》、《离骚》等，合六百三十四卷，悉在一巾箱中，书极精细。", "账·巾箱"),
    ("人间之世飘忽几何如凿石见火，窥隙观电。", "自序开卷"),
    ("余六岁解为诗，奉敕为诗曰：池萍生已合，林花发稍稠。风入花枝动，日映水光浮。", "六岁诗"),
    ("自余年十四，苦眼疾沈痼，比来转暗，不复能自读书。三十六年来，恒令左右唱之，曾生所谓「诵诗读书，与古人居；读书诵诗，与古人期」，兹言是也。", "唱书"),
    ("吾小时，夏日夕中下绛纱蚊纟□中有银瓯一枚，贮山阴甜酒。卧读有时至晓，率以为常。", "甜酒"),
    ("频丧五男，衔悲恍惚，心地荼苦。", "五男"),
    ("明月之夜，可以远视，不可以近书；雾露之朝，可以近书，不通以远视。人才性亦如是，各有不同也。", "远视近书"),
    ("与人善言，暖于布帛；伤人以言，深于矛戟。", "善言"),
    ("夫耳目之外，无有怪者。余以为不然也，水至寒而有温泉之热，火至热而有萧丘之寒。", "志怪开篇"),
    ("有人以优师献周穆王，甚巧，能作木人，趋走俯仰如人。领其颐则可语，捧其手则可舞。", "木人"),
    ("乃废其肝，则目不能□寅；废其心，则口不能语；废其脾，则手不能运。", "废五脏"),
    ("此真君家果。", "捷对问"),
    ("未闻孔雀是夫子家禽。", "捷对答"),
    ("戒之哉，无多言，多言多败；无多事，多事多患。", "金人铭"),
    ("效伯高不得，犹为谨敕之士，所谓刻鹄不成尚类鹜者也。", "刻鹄"),
    ("效季良不得，所谓画虎不成反类狗者也。", "画虎"),
    ("尝为革囊盛血，仰而射之，命曰射天。", "射天"),
    ("造酒池可以运舟，一鼓而牛饮者三千人。", "酒池"),
    ("（此篇仅存三条，皆与《说蕃》篇同）", "断脊批注"),
    ("辗转付托，阅十有馀人。", "汪跋接力"),
    ("题缄之字，已磨灭殆尽，不可辨识，而缄封且半敝矣。启而读之，不惟双节赠言无恙也。", "汪跋启缄"),
    ("太史从《永乐大典》辑录《金楼子》六卷，命致鲍君以文者亦俨然在焉。", "汪跋辑本"),
    ("乾隆四十六年嘉平七日萧山汪辉祖跋", "汪跋落款"),
]

for q, tag in QUOTES:
    check_in(q, lib, "库内")
    check_in(q, html, "页面")

# ---------- 页面引文节点收集 ----------
EXEMPT = {"kc","dnum","dtag","rl","gh","stamp","verse","flabel","fi-src","kwai","ext-tag","yr"}
SKIP = {"style","script"}
# 已申报的库外引文（页脚库外申报一节声明出处者）
EXTERNAL_OK = {"文武之道，今夜尽矣"}

class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack=[]
        self.qnodes=[]
        self.kqnodes=[]
        self.bracket=[]
        self.nodes=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs); cls=d.get("class","") or ""
        cs=set(cls.split())
        if tag in SKIP: self.stack.append(("SKIP",True))
        elif tag=="i" or tag=="small": self.stack.append(("I",True))
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
    if norm(q) in lib: continue
    if q in EXTERNAL_OK:
        print("PASS","[「」→库外申报]",q); continue
    print("FAIL","[「」→库]",q); bad+=1
fail+=bad

# ---------- 反扫：未豁免文本节点，剥「」后 6 字连串不得撞库本 ----------
hits=0
for txt,exempt in c.nodes:
    if exempt: continue
    s2=re.sub(r"「[^」]*」","",txt)
    for i in range(len(s2)-5):
        w=s2[i:i+6]
        if re.match(r"^[一-鿿]{6}$",w) and w in lib:
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
assert len(flat) == 58962, len(flat)
ju = flat[flat.index("聚书篇六"):]
ju = ju[:ju.index("二南五霸篇七")]
assert len(ju) == 1004, len(ju)
assert ju.count("写得") == 14, ju.count("写得")
assert ju.count("又得") == 9, ju.count("又得")
assert ju.count("又写") == 6, ju.count("又写")
assert flat.count("八万卷") == 1
pua_n = sum(1 for ch in lib_raw if 0xE000 <= ord(ch) <= 0xF8FF)
assert pua_n == 173, pua_n
assert "（此篇仅存三条，皆与《说蕃》篇同）" in lib_raw
assert len(c.kqnodes) >= 1, "库外引文块应至少 1 处（文武之道）"
assert "第二百三十九篇" in html
spine=[7529,3799,2886,733,2271,1004,26,10809,12252,2722,1429,4023,6755,1423]
assert sum(spine) == 57661, sum(spine)
print(f"机数：库本去空白 {len(flat)} 字；十四篇合计 {sum(spine)}；聚书篇 {len(ju)} 字（写得14 又得9 又写6）；八万卷一见；库本私用区半字 {pua_n}；.q 节点 {len(onpage_q)}；行内「」 {len(c.bracket)}；库外引文块 {len(c.kqnodes)}")
print(f"共 {len(QUOTES)} 条手工引文")
sys.exit(1 if fail else 0)
