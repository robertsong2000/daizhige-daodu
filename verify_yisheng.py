#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_yisheng.py 翊圣保德传 页面核验"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yisheng-baode-zhuan.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/道藏/正统道藏正一部/翊圣保德传.txt'
LIB_CB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/编年/续资治通鉴长编.txt'
LIB_SS = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/正史/宋史.txt'
NO = 141

page = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()
cb   = open(LIB_CB, encoding='utf-8').read()
ss   = open(LIB_SS, encoding='utf-8').read()

def norm(s):
    out = []
    for c in s:
        o = ord(c)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(c)
    return ''.join(out)

VOID = {'br','img','meta','link','input','hr','source','wbr'}

class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.qdepths = []
        self.blocks = []
        self.in_skip = 0
        self.qdepth = None
    def handle_starttag(self, tag, attrs):
        if tag in ('style','script'):
            self.in_skip += 1
            return
        if tag in VOID:
            return
        a = dict(attrs)
        cls = a.get('class','') or ''
        isq = 'q' in cls.split()
        if isq and self.qdepth is None:
            self.qdepth = len(self.stack)
            self.buf = []
            self.cur_src = a.get('data-src','')
        self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in ('style','script'):
            self.in_skip = max(0, self.in_skip-1)
            return
        if tag in VOID or not self.stack:
            return
        self.stack.pop()
        if self.qdepth is not None and len(self.stack) <= self.qdepth:
            self.blocks.append((''.join(self.buf), self.cur_src))
            self.qdepth = None
    def handle_data(self, d):
        if self.in_skip:
            return
        if self.qdepth is not None:
            self.buf.append(d)

qc = QC(); qc.feed(page)
blocks = qc.blocks
for txt, src in blocks:
    assert src == '' or src in ('续资治通鉴长编','宋史'), f'未知 data-src: {src}'
assert len(blocks) >= 40, f'收集 .q 块过少: {len(blocks)}'

M = [
"吾受命降灵，汝何为顽梗如此，不听吾言。吾若不为宋朝大事，当已粉碎汝矣。",
"吾是高天大圣玉帝辅臣，授命卫时乘龙降世。",
"剑法有三，但以铜、铁、锻为利刃，吾目一视便可用也。",
"结坛之法有九，上三坛则为国家设之。",
"吾将来运值太平君，宋朝第二主，修上清太平宫，建十二座堂殿。",
"太祖召小黄门长啸于侧，谓守真日：神人之言，若此乎。",
"陛下傥谓臣妖妄，乞赐按验，戮臣于市，勿以斯言亵渎上圣。",
"今乃使小儿呼啸，以比吾言，斯为不可。",
"言天上宫阙已成玉铄开",
"晋王有仁心，凡百余言。",
"时开宝九年十月十九日之夕也。翌日，太祖升遐，太宗嗣位。",
"建隆元年奉帝言，乘龙下降卫人君。扫除妖孽犹闲事，纵横整顿立乾坤。",
"汝奉诏修宫，勤则至矣。然何为不开日月华门，不画八小殿壁，阶墀璧梵亦未严备，唯求速成以冀恩宠。然上天亦不掩尔功，亦不赦尔罪。",
"守节染疾而亡，龟从殁于兵刃。此乃不掩功、不赦罪之戒明矣。",
"上天已定胜负也。瑜旬，而王师告捷",
"汝当上问官家，所言翊圣者，翊于何圣。",
"玉皇辅臣，所辅翊者，上帝也。",
"承平之世将继有明君，吾已有期，却归天上，汝等不复闻吾言矣。",
"佛，即西方得道之圣人也。在三清之中，别有梵天居之。于上帝，则如世之九卿奉天子也。",
"天赋汝文性，不赋汝禄位。",
"顽闻之，不悦而退。后三载，果无成而卒。",
"搏之炼气养神，颇得其要。然及物之功未至，但有所主掌耳。",
"人问官职，守真不及汝，天上名位，汝不及守真也。",
"化形为菩萨之状，诱彼居民舍财为供",
"上帝以此故，授其符命，俾为邓州土地。",
"赵普扶持社稷，甚有功勋，上天所知，赐汝福寿。",
"以大妨小，幽府亦有冤对。",
"汝官职、寿数已有限矣。",
"每存忠信齐其天，文武班行自有贤。",
"擎天之柱着功勋，包罗大海佐明君。",
"其封神为斓圣将军",
"其所录成翊圣保德真君事迩三卷，谨随表上进以闻。",
"作序以冠篇首",
"赐名以纪芳羹",
"勉从勤请，良积腼数，嘉尚之怀，寤兴无舍。",
"显告于开宝之末，大庇下土，卫我家邦",
"凤翔府上清太平宫翊圣保德真君，可特加翊圣应感储庆保德真君。",
]
CB = [
"初，有神降于盩厔县民张守真家",
"号黑杀将军，玉帝之辅也",
"风肃然，声若婴儿，独守真能晓之，所言祸福多验",
"命内侍王继恩就建隆观设黄箓醮，令守真降神",
"天上宫阙已成，玉□开。晋王有仁心。",
"言讫不复降",
"太祖闻守真言以为妖，将加诛，会宴驾",
"恐不然也，今不取",
"但遥见烛影下晋王时或离席，若有所逊避之状",
"此据吴僧文莹所为湘山野录，正史、实录并无之",
"然文莹所言道士，不得姓名，岂即张守真耶",
"壬戌，诏封太平宫神为翊圣将军，从道士张守真之请也。",
"十一月癸未朔，加号翊圣将军曰翊圣保德真君。",
"己卯，王钦若表上翊圣保德真君传三卷，上制序。",
]
SS = [
"冬十月己卯，王钦若表上《翊圣保德真君传》",
"项有附疣，时人目为『瘿相』",
"钦若自以深达道教，多所建明，领校道书，凡增六百余卷",
"七元辅弼真君红绡衣、翊圣保德真君皂袍",
]

fails = []
def check_list(lst, srclib, tag):
    for q in lst:
        qn = norm(q)
        sn = norm(srclib)
        if qn not in sn:
            fails.append(f'[{tag}] 库内无: {q[:40]}')
            continue
        src = {'M':'','CB':'续资治通鉴长编','SS':'宋史'}[tag]
        hit = any(qn in norm(b) and src == s for b, s in blocks)
        if not hit:
            fails.append(f'[{tag}] 页面 .q 未载用(或 data-src 不符): {q[:40]}')

check_list(M, lib, 'M')
check_list(CB, cb, 'CB')
check_list(SS, ss, 'SS')

# 「」反扫：页面上每一个「」内容(去标签)必须 norm 后在某一库本中
def strip_tags(s):
    s = re.sub(r'<(style|script)[\s\S]*?</\1>', '', s)
    return re.sub(r'<[^>]+>', '', s)
ptext = strip_tags(page)
pua_removed = ptext
for m in re.finditer(r'「([^「」]*)」', ptext):
    qn = norm(m.group(1))
    if not qn:
        continue
    if not (qn in norm(lib) or qn in norm(cb) or qn in norm(ss)):
        fails.append(f'[「」反扫] 库内无: {m.group(1)[:40]}')

# 红线
for i, line in enumerate(page.split('\n'), 1):
    if '—' in line or '–' in line:
        fails.append(f'[红线] L{i} 长划线')
    if line.count('·') > 1:
        fails.append(f'[红线] L{i} · 多于一枚: {line.strip()[:50]}')

# 机数
cnt_total = len(lib)
cnt_nospc = len(''.join(lib.split()))
cnt_han = sum(1 for c in lib if '㐀' <= c <= '鿿')
exp = {
    '12,312': cnt_total, '12,191': cnt_nospc, '10,230': cnt_han,
    '降言 45 见': lib.count('降言'), '官家 8 见': lib.count('官家'),
    '守真 95 见': lib.count('守真'), '醮 23 见': lib.count('醮'),
    '坛 27 见': lib.count('坛'), '剑 20 见': lib.count('剑'),
    '翊圣 15 见': lib.count('翊圣'),
}
for s, real in exp.items():
    assert s in ptext, f'页面缺机数串: {s}'
for s, real in [('45', lib.count('降言')), ('8', lib.count('官家')), ('95', lib.count('守真')),
                ('23', lib.count('醮')), ('27', lib.count('坛')), ('20', lib.count('剑')),
                ('15', lib.count('翊圣'))]:
    pass
assert lib.count('降言') == 45 and lib.count('官家') == 8 and lib.count('守真') == 95
assert lib.count('醮') == 23 and lib.count('坛') == 27 and lib.count('剑') == 20
assert lib.count('翊圣') == 15
assert cnt_total == 12312 and cnt_nospc == 12191 and cnt_han == 10230
assert lib.count('曰') == 66 and lib.count('日') == 112
assert lib.count('真君曰') == 9 and lib.count('真君日') == 4
assert '曰 66 见' in ptext and '日 112 见' in ptext and '真君曰 9 见' in ptext and '真君日 4 见' in ptext
star = [3600,2400,1200,640,490,360,240,120,81]
assert sum(star) == 9131 and '9,131' in ptext
assert lib.count('晋王有仁心') == 1 and lib.count('晋王．有仁心') == 1
assert '晋王有仁心 2 见' in ptext
assert lib.count('#1') == 4, lib.count('#1')
assert '三卷' in lib

# 结构
assert f'之一百四十一' in ptext, '页内序号 NO 不符'
for k in ['翊圣将军','翊圣保德真君','进书制序','太平兴国六年','大中祥符七年十一月癸未朔','大中祥符九年十月己卯','崇宁三年四月十八日']:
    assert k in ptext, f'缺结构串: {k}'
assert 'github.com/robertsong2000/daizhigev20' in ptext
assert '殆知阁简体库' in ptext and '逐字核对' in ptext and '时代局限' in ptext
assert '北宋亡国，二十三年' in ptext and 1104 + 23 == 1127
assert lib.count('上清太平宫') >= 3
assert cb.count('王钦若表上翊圣保德真君传三卷') == 1
# 页内无英文残留（除代码与链接）
body = re.sub(r'<(style|script)[\s\S]*?</\1>', '', page)
body_txt = strip_tags(body)
latin = re.findall(r'[A-Za-z]{3,}', body_txt)
allow = {'github','com','robertsong','daizhigev'}
bad = [w for w in latin if w not in allow]
assert not bad, f'英文残留: {bad[:8]}'

print(f'blocks={len(blocks)}  M={len(M)} CB={len(CB)} SS={len(SS)}')
print(f'lib: {cnt_total}/{cnt_nospc}/{cnt_han}  降言45 官家8 守真95 醮23 坛27 剑20 翊圣15')
if fails:
    print('FAIL')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ALL PASS')
