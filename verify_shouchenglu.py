#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""守城录 导读页核验：引文双侧逐字（两抄本各归其本）+ 「」反扫 + 排版红线 + 机数断言"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/shoucheng-lu.html'
LIB_S = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/守城录.txt'
LIB_Z = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/兵家/守城录.txt'

page = open(PAGE, encoding='utf-8').read()
libs = {
    's': open(LIB_S, encoding='utf-8', errors='replace').read(),
    'z': open(LIB_Z, encoding='utf-8', errors='replace').read(),
}
FAIL = []

VAR = {'徳': '德', '熈': '熙', '寳': '宝', '髙': '高', '濠': '壕', '甎': '砖', '塼': '砖',
       '冦': '寇', '乆': '久', '噐': '器', '寜': '宁', '靣': '面', '鎗': '枪', '歴': '历'}

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        ch = VAR.get(ch, ch)
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

# ---------- 1. 收集页面 .q ----------
VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'source', 'wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []; self.qs = []; self.cur = None; self.qdepth = 0
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        a = dict(attrs)
        cls = a.get('class', '') or ''
        isq = 'q' in cls.split()
        if isq:
            self.qdepth = len(self.stack)
            self.cur = []
        self.stack.append((tag, isq))
    def handle_endtag(self, tag):
        if tag in VOID: return
        if not self.stack: return
        t, isq = self.stack.pop()
        if isq:
            self.qs.append(''.join(self.cur or []))
            self.cur = None
    def handle_data(self, d):
        if self.cur is not None:
            self.cur.append(d)

collect = QC(); collect.feed(page)
qtexts = [q for q in collect.qs if q.strip()]

class TC(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.buf = []
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('style', 'script'): self.skip = max(0, self.skip - 1)
    def handle_data(self, d):
        if not self.skip: self.buf.append(d)
tc = TC(); tc.feed(page)
ALLTEXT = ''.join(tc.buf)

def q_in_page(qn):
    nq = norm(qn)
    for q in qtexts:
        if nq and nq in norm(q):
            return True
    return False

# ---------- 2. QUOTES：双侧断言（s=史藏本 z=四库本） ----------
QUOTES = [
 ('s', '京城已为金破。'),
 ('s', '乃知京城果为敌陷，徒深痛切，但不知城破之所以然尔！'),
 ('s', '又恨当时不得身在围城中，陪守御之士，以效绵薄。'),
 ('s', '殆不足信'),
 ('s', '痛心疾首，不觉涕零'),
 ('s', '非也'),
 ('s', '攻城者有生有死，善守者有生无死'),
 ('s', '规以为城愈大而守愈易，分段数作限隔则易守'),
 ('s', '有善守者，假使更资炮数百座，亦必无害，在于御炮之术善不善也'),
 ('s', '金人攻城，大炮对楼，势岂可当？'),
 ('s', '贵显言之，则怏然而不敢辩；众人言之，则亦不敢痛折'),
 ('s', '每对楼上载兵八十人，一对楼得城，则引众兵上'),
 ('s', '楼广不过二丈，当面立得几人？与守城人接战者，不过十数人而已'),
 ('s', '强弱之势，自古无定，惟在用兵之人何如耳'),
 ('s', '绍兴十年五月日陈规序'),
 ('z', '出知顺昌与刘锜同却金兵'),
 ('s', '金人以儿戏之具攻城，守御者一时失计，遂致城拔。'),
 ('s', '此钓桥有害无益明矣'),
 ('s', '兵已出复拽起桥板，则缓急难于退却，苟为敌所逼逐，往往溺于壕中'),
 ('s', '城门贵多不贵少，贵开不贵闭'),
 ('s', '城不必太高，太高则积雨摧塌'),
 ('s', '羊马墙比大城虽甚低薄，其捍御坚守之效，不在大城之下也'),
 ('s', '每个干重五斤，轻重一般，则打物有准'),
 ('s', '不为敌人复放入城'),
 ('s', '单梢炮上等远至二百七十步，中等二百六十步，下等二百五十步'),
 ('s', '勿谓小炮不能害物，中人四肢，则四肢必折；中腰以上，则人必死'),
 ('s', '攻守利器，皆莫如炮。攻者得用炮之术，则城无不拔；守者得用炮之术，则可以制敌。'),
 ('z', '汤璹字君寳潭州浏阳人淳熈十四年进士授徳安府教授'),
 ('s', '王在、党忠寇德安二十日引去'),
 ('s', '夺到旗六十三面、鼓四十面、钲五面、枪刀二十三条、牌十五面、甲七连、弓三张、弩二枝、牛五十二头、马九十匹、骡五头、驴十二头'),
 ('s', '张世、李孝义寇德安四日引去'),
 ('s', '杨进寇德安一十六日引去'),
 ('s', '有众一百五十万马三万五千余匹'),
 ('s', '本府视贼寨约有十余万人，马三千余匹'),
 ('s', '孔彦舟三次寇德安皆不克引去'),
 ('s', '剃头辫发，作金人装束'),
 ('s', '董平寇德安三万人即日败去'),
 ('s', '赵寿寇德安三日引去'),
 ('s', '曹成、李宏寇德安自六月至二月引去'),
 ('s', '桑仲、夏、邢、尚、孙群贼寇德安三月引去'),
 ('s', '李横寇德安六十五日引去'),
 ('s', '于贼退之后，其未远止在城外侧近围绕之中，寅夜偷工开壕筑城'),
 ('s', '城壁长八百八十二丈，高二丈五尺'),
 ('s', '城上以《千字文》为号，每步一字，每字一人，以五人为一甲，十甲为一队'),
 ('s', '其天桥底盘上复系大竹索两条，各长二十余丈，每条百余人牵拽'),
 ('s', '贼所立炮七座，不住施放一十四昼夜'),
 ('s', '并不曾正打著城上城内一人'),
 ('s', '又以火炮药造下长竹竿火枪二十余条'),
 ('z', '城内人饥饿杂草木皮叶食之'),
 ('z', '规坐城楼炮折足指容色不变'),
 ('z', '愿得粟二百斛而去'),
 ('z', '与之则遁有日矣'),
 ('z', '杀牛代食敌闻之围猝未解矣'),
 ('z', '城围七十日矣以一妇人活一城之众不亦可乎'),
 ('z', '使横即退是我以妇人求和况未必退乎其再来当斩妓首以遗之'),
 ('z', '县有粟百斛路绝不通规命乘风雨呵殿而来贼军疑其有神不敢睥睨'),
 ('s', '便是朝廷差我做镇抚使，教我去那里吃著甚底？我也不能做得他镇抚使，我待打城破后相度。'),
 ('z', '使横更七日不解曲蘖亦尽矣'),
 ('z', '乾道八年诏刻规徳安守城录颁天下为诸守将法'),
 ('z', '乾道中追封忠利智敏侯立庙徳安'),
 ('z', '规字元则宻州安邱人中明法科'),
 ('z', '编为建炎德安守御录'),
 ('z', '绍熈四年除太学录乃表上之'),
 ('z', '三书本各自为帙不知何人始并为一编观书末识语则寜宗以后人所辑矣'),
 ('z', '然至元师南下直破临安为东京之续率未闻有一人登陴以抗敌者'),
 ('z', '小县傍州或可赖通都大邑转难行'),
 ('z', '用于仓猝无备之中九攻九拒应敌无穷十万百万靡不退却'),
]
seen = []
for q in QUOTES:
    if q in seen: continue
    seen.append(q)
for src, q in seen:
    inlib = norm(q) in norm(libs[src])
    inpage = q_in_page(q)
    if not inlib: FAIL.append(f'库本{src}无: {q[:24]}')
    if not inpage: FAIL.append(f'页面.q无: {q[:24]}')
print(f'[1] 引文双侧 {len(seen)} 条（史藏 {sum(1 for s,_ in seen if s=="s")} / 四库 {sum(1 for s,_ in seen if s=="z")}）：{"PASS" if not FAIL else "FAIL"}')

# ---------- 3. 「」反扫：页面所有「」必须库内有 ----------
liball = norm(libs['s'] + libs['z'])
bad = []
for m in re.finditer(r'「([^「」]{2,60})」', ALLTEXT):
    s = m.group(1)
    if re.search(r'[a-zA-Z0-9]', s):
        continue
    if norm(s) and norm(s) not in liball:
        bad.append(s)
if bad:
    FAIL.append(f'「」反扫失败 {len(bad)} 条: ' + ' ／ '.join(bad[:6]))
print(f'[2] 「」反扫：{"PASS" if not bad else "FAIL"}')

# ---------- 4. 排版红线 ----------
red = []
page_nostyle = re.sub(r'<style[\s\S]*?</style>', '', page)
page_nostyle = re.sub(r'<script[\s\S]*?</script>', '', page_nostyle)
if '—' in page_nostyle: red.append('长划线—')
if '–' in page_nostyle: red.append('短划线–')
for i, line in enumerate(page_nostyle.split('\n'), 1):
    if line.count('·') > 1:
        red.append(f'行{i} · 超限')
bad_w = re.findall(r'[a-zA-Z]{4,}', re.sub(r'<[^>]*>', '', page_nostyle))
allow = {'Songti', 'Noto', 'Serif', 'SimSun', 'serif', 'Menlo', 'Consolas', 'PingFang',
         'github', 'robertsong', 'daizhigev'}
stray = [w for w in bad_w if w not in allow]
if stray: red.append(f'英文残留: {stray[:6]}')
if page.count('<div') != page.count('</div>'):
    red.append(f'div 不配平: 开{page.count("<div")} 闭{page.count("</div>")}')
if red: FAIL.extend(red)
print(f'[3] 排版红线+div配平：{"PASS" if not red else "FAIL"}')

# ---------- 5. 机数断言（库本侧） ----------
S, Z = libs['s'], libs['z']
def han(x): return len([c for c in x if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0002ffff'])
checks = [
    (len(S), 38837, '史藏全帙字符'), (han(S), 32432, '史藏汉字'),
    (len(Z), 18729, '四库全帙字符'), (han(Z), 18355, '四库汉字'),
    (S.count('靖康朝野佥言后序'), 2, '史藏后序标题(附录重收)'),
    (S.count('附录'), 1, '附录标记'),
    (Z.count('守城机要'), 3, '四库机要(提要+卷头+诗注)'),
    (S.count('长竹竿火枪'), 2, '史藏火枪'), (Z.count('长竹竿火枪'), 0, '四库无此目'),
    (S.count('千字文'), 2, '史藏千字文'), (Z.count('千字文'), 1, '四库千字文'),
    (S.count('羊马墙'), 52, '史藏羊马墙'), (Z.count('羊马墙'), 24, '四库羊马墙'),
    (S.count('对楼'), 58, '史藏对楼'),
    (S.count('泥圆'), 6, '史藏泥圆'), (S.count('泥团'), 4, '史藏泥团'),
    (S.count('儿戏之具'), 2, '史藏儿戏之具'),
    (S.count('立大炮七座'), 4, '史藏对轰七炮(重收x2)'),
    (Z.count('曲糵'), 1, '四库曲糵'), (Z.count('曲蘖'), 1, '四库曲蘖'),
    (Z.count('炮折足指'), 1, '四库炮折足指'), (Z.count('妓首'), 1, '四库妓首'),
    (Z.count('九攻九拒'), 1, '四库九攻九拒'), (Z.count('忠利智敏侯'), 1, '四库侯号'),
    (Z.count('乾道八年'), 1, '四库乾道八年'),
    (S.count('顺昌'), 2, '史藏顺昌'), (Z.count('顺昌'), 4, '四库顺昌'),
    (S.count('迄及一纪有余'), 2, '史藏一纪有余(重收x2)'),
]
for got, exp, lab in checks:
    if got != exp:
        FAIL.append(f'计数 {lab}: {got} ≠ {exp}')
print(f'[4] 机数断言 {len(checks)} 项：{"PASS" if not any("计数" in f for f in FAIL) else "FAIL"}')

# ---------- 6. 九标题各命中两次（附录重收所致） ----------
heads = ['王在、党忠寇德安二十日引去', '张世、李孝义寇德安四日引去', '杨进寇德安一十六日引去',
         '孔彦舟三次寇德安皆不克引去', '董平寇德安三万人即日败去', '赵寿寇德安三日引去',
         '曹成、李宏寇德安自六月至二月引去', '桑仲、夏、邢、尚、孙群贼寇德安三月引去',
         '李横寇德安六十五日引去']
hb = [h for h in heads if S.count(h) != 2]
if hb: FAIL.append(f'九标题异常: {hb}')
print(f'[5] 九次围城标题 9 条各 2 见：{"PASS" if not hb else "FAIL"}')

# ---------- 7. 算术 ----------
if 80 * 5 != 400: FAIL.append('对楼算术')
if 1140 - 1126 != 14 or 14 <= 12: FAIL.append('一纪有余算术')
if 1172 - 1126 != 46: FAIL.append('乾道八年四十六年')
if 1193 - 1126 != 67: FAIL.append('绍熙四年六十七年')
print('[6] 页面算术 4 项：' + ('PASS' if not any('算术' in f for f in FAIL) else 'FAIL'))

# ---------- 8. 页面要素 ----------
for s in ['之一百四十二', '卷七兵略', 'github.com/robertsong2000/daizhigev20',
          '时代局限提醒', '逐字核验', '殆知阁导读']:
    if s not in page: FAIL.append(f'页面缺: {s}')
print(f'[7] 页面要素：{"PASS" if not any("页面缺" in f for f in FAIL) else "FAIL"}')

print('=' * 46)
if FAIL:
    print('FAIL', len(FAIL), '项')
    for f in FAIL: print(' ✗', f)
    sys.exit(1)
print('ALL PASS')
