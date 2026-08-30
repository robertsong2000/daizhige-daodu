#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_you-chengnan-ji.html — 引文逐字对库 + 排版红线 + 机数断言"""
import re, sys
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/地理/游城南记.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/you-chengnan-ji.html'

lib = open(LIB, encoding='utf-8').read().strip()
page = open(PAGE, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

LN = norm(lib)

fails, warns = [], []

# ---------- QCollector：栈配平，跳过 VOID ----------
VOID = {'br', 'meta', 'link', 'img', 'hr', 'input', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}

class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, is_q)
        self.quotes = []         # collected .q texts
        self.spans = []          # collected .stag texts
        self.cur_q = None
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        cls = None
        for k, v in attrs:
            if k == 'class': cls = v or ''
        is_q = cls is not None and 'q' in cls.split()
        is_stag = cls is not None and 'stag' in cls.split()
        self.stack.append((tag, is_q, is_stag))
        if is_q and self.cur_q is None:
            self.cur_q = []
        elif is_stag and self.cur_q is None:
            self.cur_stag = True
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in VOID: return
        # pop until matching tag (balanced scan)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                closing = self.stack[i:]
                del self.stack[i:]
                was_q = any(c[1] for c in closing)
                was_stag = any(c[2] for c in closing)
                if self.cur_q is not None and (was_q or self._in_q()):
                    txt = ''.join(self.cur_q); self.cur_q = None
                    if txt.strip(): self.quotes.append(txt)
                break
        if not self._in_q() and self.cur_q is not None:
            txt = ''.join(self.cur_q); self.cur_q = None
            if txt.strip(): self.quotes.append(txt)
    def _in_q(self):
        return any(c[1] for c in self.stack)
    def handle_data(self, data):
        if self._in_q():
            if self.cur_q is None: self.cur_q = []
            self.cur_q.append(data)
        elif any(c[2] for c in self.stack):
            self.spans.append(data)

qc = QC(); qc.feed(page)
pq = [norm(x) for x in qc.quotes]
pq = [x for x in pq if x]
print(f'页面 .q 收集：{len(pq)} 枚')

# ---------- 期望引文清单（双侧断言） ----------
QUOTES = [
"元祐改元，季春戊申，明微、茂中同出京兆之东南门。",
"肃宗以禄山国仇，恶闻其姓，京兆坊里有安字者，率易之。",
"二坊之地，今为京兆东西门外之草市，余为民田。",
"隋宇文恺，城大兴，以城中有六大冈，东西横亘象干之六爻。故于九二置宫室，以当帝王之居，九三置百司，以应君子之数，九五贵位，不欲常人居之，故置玄都观、大兴善寺以镇之。",
"非衣小儿坦其腹，天上有口被驱逐。",
"其寺文明元年立，谓之大献佛寺，天授元年改为荐福寺，景龙中，宫人率出钱，起塔十五层。",
"寺之浮图今正谓之荐福寺塔，尚存焉。",
"贞祐乙亥岁，塔之缠腰尚存，辛卯迁徙，废荡殆尽，惟砖塔在焉。",
"永徽三年，沙门玄奘起塔，初惟五层，砖表土心，效西域窣堵波",
"长安中摧倒，天后及王公施钱，重加营建，至十层。",
"塔自兵火之余，止存七层，长兴中，西京留守安重霸再修之，判官王仁裕为之记。",
"长安士庶，每岁春时，游者道路相属，熙宁中，富民康生遗火，经宵不灭，而游人自此衰矣。",
"塔既经焚，涂圬皆剥，而砖始露焉，唐人墨迹于是毕见，今孟郊、舒元舆之类尚存，至其它不闻于后世者，盖不可胜数也。",
"正大迁徙，寺宇废毁殆尽，惟一塔俨然。塔之东西两龛，唐褚遂良所书《圣教序》，及《唐人题名记》碑刻存焉。",
"倚塔下瞰曲江宫殿，乐游燕喜之地，皆为野草，不觉有黍离麦秀之感。",
"唐进士新及第者，往往泛舟游宴于此。",
"文宗时，曲江宫殿废十之九，帝因诵杜甫《哀江南》之诗，慨然有意复升平故事。",
"太和九年，发左右神策军三千人疏浚，修紫云楼、彩霞亭",
"江水虽涸，故道可因，若自甫张村引黄渠水，经鲍陂以注曲江，则江景可复其旧。",
"庄即唐宦官仇士良别业也。",
"其南为郭子仪墓，西南长孙无忌之墓，碑皆断仆。",
"殿宇总四千一百三十间，分四十八院",
"今此基不甚侈，且与《志》所载地里不同，岂四十八院之一耶？",
"香积寺，唐永隆二年建，中多石像，塔砖中裂，院中荒凉，人鲜游者。",
"世传杜固有王气，诸杜居之，衣冠世美，及正伦执政，建言凿杜固通水以利人，既凿，川流如血，阅十曰方止，自是南杜稍不显。",
"长安有此竹者，惟处士苏季明、张思道与中伯三家而已。",
"先是泓陟相德裕宅为玉碗，僧孺宅为金杯，且云金毁可作他器，玉毁不复用矣，其言果验。",
"至崇业坊，览玄都观之遗基，过冈，论唐昌观故事。",
"中有玉蕊花。元和中，有仙子来观，严休父，元稹辈俱有唱和。",
"东上朱坡，憩华岩寺，下瞰终南之胜，雾岩、玉案、圭峰、紫阁，粲在目前，不待足履而尽也。",
"疏钟摇雨脚，积雨浸云容",
"登山有道，徐行则不困，择平稳之地而置足则不跌，人莫不知之，鲜能慎。",
"院引北岩泉水，架竹落庭注石盆中，萦澈可挹，使人不觉顿忘俗意。",
"澄襟院，水久涸",
"庄则金兴定辛巳间，尚为元氏之居，迁徙后，遂无闻焉。",
"有闻其名而失其地者",
"有具其名得其地而不知其所以者",
"有见于近世而未著于前代者",
"至于名迹可据，而暴于人之耳目者，皆得以详书焉。",
"故皆略之，以俟再考。",
"杨氏苗裔，太和间尚盛，人呼为庙坡杨，辛卯迁移后，无闻焉。",
"起塔十五层","尚存焉","塔之缠腰尚存","惟砖塔在焉","初惟五层","至十层","止存七层","惟一塔俨然",
"塔砖中裂","人鲜游者","有三藏玄奘、慈恩、西明三塔","三藏塔奠中差大","在东阁法堂之北","壁间二石记，皆唐刻也",
"泉北有塔","小塔累累相比",
"既而北行数里，入含光门而归焉。实闰月十六也。",
]
# 页面裸引（非 .q 类，逐字核验）
BARE = [
"即横冈之第五爻也，今谓之草场坡，古场存焉。",
"自务本西门，入圣容院，观荐福寺塔",
"东南至慈恩寺，少迟登塔，观唐人留题",
"东南历仇家庄","由赵村访章敬寺基","西望香积寺塔","东次杜曲，前瞻杜固",
"子虚邀饮韦氏会景堂","过塔院，抵韦赵",
"瓦砾遍地","清谈终曰","谒龙堂","夜宿寺之南轩","观干湫","醉还申店几夜半",
"甲寅北归",
]

for q in QUOTES:
    qn = norm(q)
    if qn not in LN:
        fails.append(f'【库内无】{q[:36]}')
    if qn not in pq:
        fails.append(f'【页面无】{q[:36]}')
for b in BARE:
    bn = norm(b)
    if bn not in LN:
        fails.append(f'【裸引不在库】{b[:30]}')

# 页面 .q 全集逐条对库（含期望清单外者）
for x in pq:
    if x not in LN:
        fails.append(f'【页面引文不在库】{x[:40]}')

# 长引文页面查重（≥12 字 norm）
seen = {}
for x in pq:
    if len(x) >= 12:
        seen[x] = seen.get(x, 0) + 1
for x, c in seen.items():
    if c > 1: warns.append(f'【复现≥2】{x[:24]} × {c}')

# ---------- 红线 ----------
for i, line in enumerate(page.split('\n'), 1):
    if '—' in line: fails.append(f'【L{i} 禁 —】')
    if '–' in line: fails.append(f'【L{i} 禁 –】')
    if line.count('·') > 1: fails.append(f'【L{i} · >1】')

# 生僻扩展区/PUA 不得出现在页面
for ch in set(page):
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF: fails.append(f'【页面含 PUA {hex(o)}】')
    if 0x20000 <= o <= 0x2FA1F: fails.append(f'【页面含 Ext-B {hex(o)}】')

# ---------- 机数 ----------
nosp = re.sub(r'\s', '', lib)
segs = [s.strip() for s in re.split(r'\n\s*\n', lib) if s.strip()]
zt = [s for s in segs if s.startswith('张注曰')]
xz = [s for s in segs if s.startswith('续注曰')]
body = [s for s in segs if not s.startswith(('张注曰', '续注曰')) and s != '游城南记　　宋 张礼']
c = lambda ss: len(re.sub(r'\s', '', ss))
A = [
 ('段数 33/33/9', (len(body), len(zt), len(xz)) == (33, 33, 9)),
 ('去空白 8496', len(nosp) == 8496),
 ('总 8799', len(lib) == 8799),
 ('正文 1019', c(''.join(body)) == 1019),
 ('张注 6285', c(''.join(zt)) == 6285),
 ('续注 1185', c(''.join(xz)) == 1185),
 ('三层和 8489', c(''.join(body)) + c(''.join(zt)) + c(''.join(xz)) == 8489),
 ('塔 44', nosp.count('塔') == 44),
 ('寺 86', nosp.count('寺') == 86),
 ('观 30', nosp.count('观') == 30),
 ('迁徙 3', nosp.count('迁徙') == 3),
 ('迁移 1', nosp.count('迁移') == 1),
 ('无闻 2', nosp.count('无闻') == 2),
 ('惟 4', nosp.count('惟') == 4),
 ('俟再考 2', nosp.count('俟再考') == 2),
 ('玄都观 4', nosp.count('玄都观') == 4),
 ('唐昌观 2', nosp.count('唐昌观') == 2),
 ('黍离 1', nosp.count('黍离') == 1),
 ('曰代日 4', sum(nosp.count(k) for k in ('十曰', '终曰', '晦曰', '他曰')) == 4),
 ('Ext-B 2', len([ch for ch in set(lib) if 0x20000 <= ord(ch) <= 0x2FA1F]) == 2),
 ('PUA 0', len([ch for ch in set(lib) if 0xE000 <= ord(ch) <= 0xF8FF]) == 0),
 ('□ 3', lib.count('□') == 3),
]
# 迁徙/迁移全在续注
xtext = norm(''.join(xz))
for k in ('迁徙', '迁移'):
    pass
ok_all_x = all(norm(s) in norm(''.join(xz)) for s in
               ['辛卯迁徙，废荡殆尽', '正大迁徙', '迁徙后，遂无闻焉', '辛卯迁移后，无闻焉'])
A.append(('迁徙迁移 4 见全在续注', ok_all_x and nosp.count('迁徙') + nosp.count('迁移') == 4))
# 磨崖廿八
i = lib.find('登山有道'); s = lib[i:i + 80].split('。')[0]
A.append(('磨崖恰 28 字', len(norm(s)) == 28 and s.count('，') == 4))
# 七日干支连续
gz = ['戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑', '甲寅']
G = '甲乙丙丁戊己庚辛壬癸'; Z = '子丑寅卯辰巳午未申酉戌亥'
ix = [(G.index(g[0]), Z.index(g[1])) for g in gz]
A.append(('七日干支连续', all((ix[j+1][0]-ix[j][0]) % 10 == 1 and (ix[j+1][1]-ix[j][1]) % 12 == 1 for j in range(6))))
for g in gz:
    A.append((f'页面行程带含 {g}', g in page))
# 页面文案计数
A.append(('页面 8,799', '8,799' in page))
A.append(('页面 8,496', '8,496' in page))
A.append(('页面 之一百零八', '之一百零八' in page))
A.append(('页面 四十四次', '四十四次' in page))
A.append(('页面 二十八实数', '实数恰二十八' in page))
A.append(('页面 校记十曰', '十曰当作十日' in page))
A.append(('页面 校记哀江头', '哀江头' in page))
A.append(('页面 页脚链接', 'daizhigev20' in page))
A.append(('页面 局限提醒', '时代局限提醒' in page and '读者察之' in page))

for name, ok in A:
    print(('PASS  ' if ok else 'FAIL  ') + name)
    if not ok: fails.append('机数 ' + name)

print()
print(f'机数 {sum(1 for _, ok in A if ok)}/{len(A)}　引文期望 {len(QUOTES)} 条 + 裸引 {len(BARE)} 条')
if warns:
    print('WARN:')
    for w in warns: print('  ' + w)
if fails:
    print('FAILED:')
    for f in fails: print('  ' + f)
    sys.exit(1)
print('ALL PASS')
