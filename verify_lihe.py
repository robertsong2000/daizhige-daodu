#!/usr/bin/env python3
"""核验 lihe-geshi.html 引文与库内《笺注评点李长吉歌诗》逐字一致（去标点+仅留汉字，双向）+ 反扫 + 红线 + 机数。"""
import re, sys
from html.parser import HTMLParser

SRC = "/home/robertsong/workspace/claude/daizhige-simplified/集藏/四库别集/笺注评点李长吉歌诗.txt"
PAGE = "/home/robertsong/workspace/claude/daizhige-daodu/lihe-geshi.html"

def norm(s):
    return re.sub(r"[^一-鿿]", "", s)

lib_raw = open(SRC, encoding="utf-8").read()
lib = norm(lib_raw)
html = open(PAGE, encoding="utf-8").read()
html_page = norm(re.sub(r'(?:data-t|title|style)="[^"]*"', "", html))
fail = 0

def check_in(q, where, tag):
    global fail
    ok = norm(q) in (lib if where is lib else html_page)
    print(("PASS" if ok else "FAIL"), f"[{tag}]", norm(q)[:24])
    if not ok:
        fail += 1

QUOTES = [
    ("笺注评防李长吉歌诗", "书名行"),
    ("正子则不知何许人。", "提要"),
    ("以正子是注为最古。", "提要"),
    ("王琦解塞土胭脂凝夜紫，不用紫塞之说，而改塞土为塞北。", "提要"),
    ("大和五年十月中，半夜时，舍外有疾呼传缄书者。", "半夜来书"),
    ("我亡友李贺，元和中，义爱甚厚，日夕相与起居饮食。", "沈子明书"),
    ("贺且死，尝授我平生所着歌诗，离为四编，凡二百三十三首。", "临终托编"),
    ("唐皇诸孙，贺字长吉。", "身世"),
    ("世皆曰：使贺且未死，少加以理，奴仆命骚可也。", "判词"),
    ("贺生二十七年死矣。", "早夭"),
    ("贺死后凡十有五年，京兆杜牧为其序。", "落款"),
    ("云烟聨绵不足为其态也", "九不足一"),
    ("水之迢迢不足为其情也", "九不足二"),
    ("春之盎盎不足为其和也", "九不足三"),
    ("秋之明洁不足为其格也", "九不足四"),
    ("风樯阵马不足为其勇也", "九不足五"),
    ("瓦棺篆鼎不足为其古也", "九不足六"),
    ("时花美女不足为其色也", "九不足七"),
    ("荒国陊殿梗莽邱陇不足为其恨怨悲愁也", "九不足八"),
    ("鲸呿鼇掷牛蛇神不足为其虚荒诞幻也", "九不足九（缺鬼位）"),
    ("黑云压城城欲摧　甲光向月金鳞开", "雁门一"),
    ("角声满天秋色里", "雁门二"),
    ("塞土燕脂凝夜紫", "雁门三"),
    ("半卷红旗临易水", "雁门四"),
    ("霜重鼔寒声不起", "雁门五"),
    ("报君黄金台上意　提擕玉龙为君死", "雁门六"),
    ("幽闲鼓吹云贺以歌诗谒韩公，时公送客归，极困，解带读之，首篇乃鴈门太守行，即束带见之。", "韩愈束带"),
    ("秦筑长城土皆紫色，故曰紫塞", "紫塞注"),
    ("有此一语方畅", "辰翁评"),
    ("此等景不可无", "辰翁评"),
    ("颇似败后之作", "辰翁评"),
    ("桐风惊心壮士苦　衰灯络纬啼寒素", "秋来一"),
    ("谁防青简一编书　不遣花虫粉空蠧", "秋来二"),
    ("思牵今夜肠应直　雨冷香魂吊书客", "秋来三"),
    ("秋坟唱鲍家诗　恨血千年土中碧", "秋来四（缺鬼位）"),
    ("非长吉自挽耶", "辰翁评"),
    ("宫官既拆盘，仙人临载，乃澘然泪下。唐诸王孙李长吉，遂作金铜仙人辞汉歌。", "金铜序"),
    ("茂陵刘郎秋风客　夜闻马嘶晓无迹", "金铜一"),
    ("画栏桂树悬秋香　三十六宫土花碧", "金铜二"),
    ("魏官牵车指千里　东闗酸风射眸子", "金铜三"),
    ("空将汉月出宫门", "金铜四"),
    ("衰兰送客咸阳道　天若有情天亦老", "金铜五"),
    ("擕盘独出月荒凉　渭城已逺波声小", "金铜六"),
    ("古今无此神妙", "辰翁评"),
    ("神凝意黯不觉铜仙能言", "辰翁评"),
    ("幽兰露　如啼眼", "苏小小一"),
    ("无物结同心　烟花不堪剪", "苏小小二"),
    ("草如茵　松如盖　风为裳　水为佩　油壁车　夕相待", "苏小小三"),
    ("冷翠烛　劳光彩　西陵下　风吹雨", "苏小小四"),
    ("便是墓中语", "辰翁评"),
    ("妙极自然", "辰翁评"),
    ("古今鬼语无此惨澹尽情", "辰翁评"),
    ("温公云石曼卿尝对长吉天若有情天亦老之句云月如无恨月长圆时人号为勍敌", "对句典"),
    ("鬼灯如漆防松花", "幸存鬼"),
    ("南山何其悲鬼雨洒空草", "幸存鬼"),
    ("至教神妪忽入鬼语", "幸存鬼"),
    ("鬼语之浅浅者", "幸存鬼"),
    ("始知牧亦未尝读也即读亦未知也", "总评"),
    ("千年长吉，犹无知已也。", "总评"),
    ("千年长吉，余甫知之耳。", "总评"),
    ("诗之难读如此，而作者常呕心何也。", "总评"),
    ("贺复无家室子弟，得以给养防问。", "序冷语"),
    ("尝闻薛常州士龙言，长吉诗蜀本、防稽姚氏本皆二百一十九篇，宣城本二百四十二篇。", "外集账"),
    ("然观此巻所作，名是后人模仿之为，词意往往儇浅，真长吉笔者无防。", "外集断"),
    ("余不敢尽削，姑去其重出者一篇。", "外集宽"),
    ("公于诗为深妙竒博", "行内"),
    ("然终甚惭", "行内"),
    ("不足为其", "行内"),
    ("名是后人模仿之为", "行内"),
]

for q, tag in QUOTES:
    check_in(q, lib, "库内")
    check_in(q, html, "页面")

EXEMPT = {"ui"}
SKIP = {"style", "script"}

class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.qnodes = []
        self.kqnodes = []
        self.bracket = []
        self.nodes = []
    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.stack.append(("SKIP", True)); return
        d = dict(attrs); cls = d.get("class", "") or ""
        cs = set(cls.split())
        if tag == "i" or tag == "small":
            self.stack.append(("I", True))
        elif tag == "span" and "q" in cs:
            self.stack.append(("Q", True))
        elif "kq" in cs:
            self.stack.append(("KQ", True))
        else:
            self.stack.append(("P", bool(cs & EXEMPT)))
    def handle_endtag(self, tag):
        if self.stack: self.stack.pop()
    def handle_data(self, data):
        kinds = [k for k, _ in self.stack]
        exempt = any(e for _, e in self.stack)
        for m in re.finditer(r"「([^」]{2,})」", data):
            self.bracket.append(m.group(1))
        if "SKIP" in kinds or "I" in kinds: return
        if "Q" in kinds: self.qnodes.append(data)
        elif "KQ" in kinds: self.kqnodes.append(data)
        else: self.nodes.append((data, exempt))

c = Collector(); c.feed(html)
print(f"页面 .q 节点 {len(c.qnodes)} 个")
for q in c.qnodes:
    n = norm(q)
    if not n: continue
    check_in(q, lib, "q→库")
bad = 0
print(f"行内「」引文 {len(c.bracket)} 段")
for q in c.bracket:
    if norm(q) not in lib:
        print("FAIL", "[「」→库]", q); bad += 1
fail += bad
assert len(c.kqnodes) >= 1, "库外申报块缺失"

hits = 0
for txt, exempt in c.nodes:
    if exempt: continue
    s2 = re.sub(r"「[^」]*」", "", txt)
    for i in range(len(s2) - 5):
        w = s2[i:i + 6]
        if re.match(r"^[一-鿿]{6}$", w) and w in lib:
            print("FAIL", "[反扫]", w, "…", s2[max(0, i - 10):i + 14].replace("\n", " "))
            hits += 1
print(f"反扫命中 {hits} 处")
fail += hits

assert "—" not in html and "–" not in html, "长划线"
for ln in html.splitlines():
    assert ln.count("·") <= 1, f"一行多·: {ln[:40]}"
ext = [m for m in re.findall(r'(?:src|href)="([^"]+)"', html)
       if not (m.startswith("#") or m.endswith(".html") or "github.com/robertsong2000" in m)]
assert not ext, f"外部依赖: {ext}"
pua = [ch for ch in html if 0xE000 <= ord(ch) <= 0xF8FF or 0x20000 <= ord(ch) <= 0x3FFFF]
assert not pua, f"PUA/ExtB {len(pua)}"
print("红线：长划线/·/外部依赖/PUA 全过；「」闭合计数", html.count("「"), html.count("」"))

flat = re.sub(r"\s", "", lib_raw)
assert len(flat) == 51325, len(flat)
assert flat.count("防") == 227, flat.count("防")
assert flat.count("点") == 0, flat.count("点")
assert flat.count("鬼") == 13, flat.count("鬼")
assert flat.count(chr(0xEF5B)) == 22, flat.count(chr(0xEF5B))
assert flat.count("长吉") == 92, flat.count("长吉")
assert flat.count("评防") == 14, flat.count("评防")
assert flat.count("巻") == 38, flat.count("巻")
assert "第二百三十八" in html
print(f"机数：去空白 {len(flat)} 字；防227/点0；鬼明写13+隐身22(U+EF5B)；长吉92；评防14；巻38；.q 节点 {len(c.qnodes)}；「」{len(c.bracket)}")
print(f"共 {len(QUOTES)} 条手工引文")
sys.exit(1 if fail else 0)
