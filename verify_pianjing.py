#!/usr/bin/env python3
# verify_pianjing.py — 骗经 页面核验：引文双侧逐字 + 「」反扫 + 红线 + 机数
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/pianjing.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/骗经.txt'

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(ch)
    return ''.join(out)

lib = open(LIB, encoding='utf-8').read()
LIBN = norm(lib)
html = open(PAGE, encoding='utf-8').read()

VOID = {'br','img','meta','link','hr','input','source'}

class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.blocks = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'):
            self.skip += 1
            return
        if tag in VOID:
            return
        if self.skip:
            return
        isq = False
        for k, v in attrs:
            if k == 'class' and v and 'q' in v.split():
                isq = True
        self.stack.append([tag, isq, []])
    def handle_endtag(self, tag):
        if tag in ('script','style'):
            self.skip -= 1
            return
        if tag in VOID or self.skip:
            return
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                popped = self.stack[i:]
                del self.stack[i:]
                for entry in popped:
                    if entry[1]:
                        self.blocks.append(''.join(entry[2]))
                break
    def handle_data(self, data):
        if self.skip:
            return
        for entry in reversed(self.stack):
            if entry[1]:
                entry[2].append(data)
                break

qc = QC()
qc.feed(html)
blocks = qc.blocks
BLOCKN = [norm(b) for b in blocks]

QUOTES = [
 "言买马，非买马，实欲假马作罨，为脱缎之术。",
 "忽有一棍，擎好伞，穿色衣，翩然而来，伫立瞻顾，不忍舍去。",
 "我买，但要归家作契对银。",
 "代看住，待我买缎几匹，少顷与你同归。",
 "将缎拿过手，出门便逃去。缎客见马与伙尚在，心中安然。",
 "你伙拿吾缎去，你将焉往？",
 "先以色服章身，令人信其为真豪富",
 "既而伫立相马，令人信其为真作家",
 "迨入缎铺，诳言有马与伙，令人信其为真实言",
 "以他人之马，赚你之缎，是假道灭虢术也。此你自遭骗，何可罪庆？",
 "不敢相瞒，我实是一小偷，爱得对门店下一只鹅吃，只大街面难下手。我有一小术，只要一个人赞成。",
 "凭你拿去。",
 "我真拿去？",
 "说定了，任你拿去。",
 "两旁店人皆闻其问答之语，小偷遂负其柜上一捆青布而去",
 "看鹅尚在，自己柜头反失一捆青布。",
 "欲去人之鹅，而反自失其布，是自贻祸也，将谁怨哉？",
 "子月念二日夜将半，梦一飞熊，手擎红春花，行红日之中，上有金字‘大魁’二字，看甚分明。",
 "醒而忆之，日者，建阳也；熊者，君姓也；春花者，君治《春秋》经也。",
 "熊举人之家阅之大喜，赏使银三两。",
 "请益，复与二两",
 "人赏之者，皆三五金以上。",
 "真是好一场春梦也！",
 "虽赏他几两银，亦博得举家人肚中欢喜四个月。",
 "余于壬子秋，在书坊检得一小本仔，辨说银之真假，甚是明白。",
 "松纹，与细丝一样，其皆足色也。",
 "水丝，又名曰干丝，自七成、八成、九成、九五止，通名曰水丝。",
 "泻出而无丝，以铁锥画丝于其上，曰画丝。",
 "银一入，口含吹筒即吹之以成丝也，曰吹丝。",
 "以湿纸盖其上，中取一孔，以银从孔泻下，吸以成其丝也，曰吸丝。",
 "鼎银，即汞银也，又曰水银。",
 "以纹银九钱，入铅一钱，入炉中锅内不用一毫之硝",
 "故造假银，俗曰“神仙”。",
 "虽以凿凿开，必不能辨。",
 "车壳即灌铅。",
 "预将假元宝二个重一百两，埋藏其处",
 "至今被人骗者，俗语曰“勿说他”。",
 "其妻有智，即以其元宝凿来与他，知是锡。",
 "世道人心，一变至此极乎！偶因前事，遂备述之，以为出途者警。",
 "人受此色身，哪能断绝食色？假托辟谷者，不过暗藏干粮，以哄惑愚民耳。",
 "唯持二十四个弥陀珠",
 "止十九枚在手耳",
 "将四个调与众百姓看",
 "后十五枚发与医生治补损",
 "众看此辟谷僧，在褚爷前辟三日谷，即饿死矣。",
 "故客路不在虚得人之有，而在密藏己之有也，斯无所失矣。",
 "故责在贲生矜夸炫耀，是自招其脱也。噫！",
 "其言太甘，其中必毒。",
 "小人之计甚诡，君子之防宜密。庶棍术虽多，亦不能愚弄我也。",
 "谨密勿泄",
]

fails = []
# 1) 引文双侧：在库本 + 在页面某个 .q 块
for i, q in enumerate(QUOTES, 1):
    qn = norm(q)
    if qn not in LIBN:
        fails.append(f"[库本MISS] #{i} {q[:24]}")
    if not any(qn in bn for bn in BLOCKN if bn):
        fails.append(f"[页面MISS] #{i} {q[:24]}")

# 2) 「」反扫（页面全文不应出现）
if '「' in html or '」' in html:
    fails.append("[反扫] 页面出现「」")

# 3) 红线：长划线、间隔号
if '—' in html:
    fails.append("[红线] 出现 —")
if '–' in html:
    fails.append("[红线] 出现 –")
for li, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f"[红线] 第{li}行 · 超一枚")

# 4) 英文残词（剥标签后仅白名单）
body = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
body = re.sub(r'<[^>]+>', '', body)
ALLOW = {'github','com','robertsong','daizhigev','daodu','txt','daizhige'}
words = set(re.findall(r'[A-Za-z]{2,}', body))
bad = words - ALLOW
if bad:
    fails.append(f"[英文残留] {bad}")

# 5) CSS content 不得夹中文
if re.search(r'content\s*:\s*"[^"]*[㐀-鿿]', html):
    fails.append("[红线] CSS content 夹中文")

# 6) 机数：库本侧重算
raw_n   = len(lib)
ns_n    = len(re.sub(r'\s', '', lib))
han_n   = len(norm(lib))
kw      = {w: lib.count(w) for w in ['棍','银','僧','骗','光棍','局']}
an_yu   = lib.count('按：')
lines   = [l.strip().replace('　',' ') for l in lib.split('\n')]
cats, cases = [], []
cat = None
for s in lines:
    if not s:
        continue
    m = re.match(r'^([一二三四五六七八九十]{1,3})类\s+(.+)$', s)
    if m:
        cat = m.group(1) + '类' + m.group(2)
        cats.append(cat)
        continue
    if s.startswith('骗经') or s.startswith('按'):
        continue
    if len(s) <= 12 and '。' not in s and '，' not in s:
        cases.append((cat, s))
assert len(cats) == 24, len(cats)
assert len(cases) == 83, len(cases)
assert an_yu == 76, an_yu

mach = [
    ('83,948', raw_n == 83948), ('81,906', ns_n == 81906), ('67,084', han_n == 67084),
]
for token in ['83,948','81,906','67,084']:
    if token not in html:
        fails.append(f"[页面缺机数] {token}")
if f"{kw['棍']} 见" not in html: fails.append("[页面缺机数] 棍")
if f"{kw['银']} 见" not in html: fails.append("[页面缺机数] 银")
if f"{kw['僧']} 见" not in html: fails.append("[页面缺机数] 僧")
if f"{kw['骗']} 见" not in html: fails.append("[页面缺机数] 骗")
if f"{kw['光棍']} 见" not in html: fails.append("[页面缺机数] 光棍")
if f"{kw['局']} 见" not in html: fails.append("[页面缺机数] 局")
if '八万三千九百四十八' not in html: fails.append("[页面缺机数] 全帙字数中文")
if '二十四类' not in html or '八十三案' not in html:
    fails.append("[页面缺机数] 类案数")
if '按语七十六' not in html: fails.append("[页面缺机数] 按语数")

# 7) 珠账：24 粒、5 空、4+15=19
mbeads = re.search(r'<div class="beads">(.*?)</div>', html, re.S)
dots = re.findall(r'<i( class="u")?></i>', mbeads.group(1))
used = mbeads.group(1).count('class="u"')
if len(dots) != 24 or used != 5:
    fails.append(f"[珠账] 总{len(dots)} 空{used} 应 24/5")
assert 4 + 15 == 19

# 8) 类墙：24 chips、计数和 83
chips = re.findall(r'<span class="chip[^"]*"><b>[^<]+</b><i>(\d+)</i></span>', html)
if len(chips) != 24 or sum(map(int, chips)) != 83:
    fails.append(f"[类墙] chips={len(chips)} sum={sum(map(int,chips))} 应 24/83")

# 9) 自标号
if '之一百三十三' not in html:
    fails.append("[自标号] 缺 之一百三十三")
if '<title>骗经 · 殆知阁导读之一百三十三</title>' not in html:
    fails.append("[自标号] title 不符")
if '殁知阁' in html:
    fails.append("[自标号] 殆误作殁")

# 10) .q 块总数（神仙条在抽屉与高亮带复现一次，refrain 1）
REFRAIN = 1
if len(blocks) != len(QUOTES) + REFRAIN:
    fails.append(f"[块数] .q 块 {len(blocks)} ≠ 清单 {len(QUOTES)}+refrain{REFRAIN}")

print(f"库本：全帙 {raw_n:,} / 去空白 {ns_n:,} / 汉字 {han_n:,}")
print(f"机数：类{len(cats)} 案{len(cases)} 按{an_yu} " +
      " ".join(f"{k}{v}" for k, v in kw.items()))
print(f".q 块：{len(blocks)}　清单：{len(QUOTES)}")
if fails:
    print("FAIL")
    for f in fails:
        print(" ", f)
    sys.exit(1)
print("ALL PASS")
