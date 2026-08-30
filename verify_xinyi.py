#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_xinyi.py — 新仪象法要 导读页核验
1) QUOTES: 页面 .q/.qzhu 引文 ← 库本逐字比对（去标点+去空白+异体归一）
2) 排版红线: 禁 — – 、每行·≤1
3) 机算: 字数口径 / 图数 17+18+25 / 星账 283名1464数 / 齿轮 600牙 / 木人 24+96+25 / 枢轮36壶
"""
import re, sys, html
from pathlib import Path

BASE = Path(__file__).parent
LIB = Path('/home/robertsong/workspace/claude/daizhige-simplified/子藏/算法/新仪象法要.txt')
PAGE = BASE / 'xinyi-xiangfayao.html'

STOP = '，。、；：？！「」『』（）《》〈〉【】·…—–,.;:?!()"\'‘’“”　 \t\n\r'

def norm(s, strip_gloss=False):
    if strip_gloss:
        s = re.sub(r'【[^【】]*】', '', s)
    out = []
    for ch in s:
        if ch.isspace() or ch in STOP:
            continue
        out.append(ch)
    return ''.join(out)

lib_raw = LIB.read_text(encoding='utf-8')
lib_nomark = re.sub(r'<子部[^>]*>', '', lib_raw)
LIBN = norm(lib_nomark)
LIBN_nogloss = norm(re.sub(r'【[^【】]*】', '', lib_nomark))  # 双方剥【】注，供带注引文比对

FAIL = []
def fail(msg):
    FAIL.append(msg)
    print('FAIL', msg)

# ---------------- 1. 引文清单（页面将逐字使用） ----------------
QUOTES = [
 # (id, 引文, 源标注, 是否剥【】注)
 ('进状-水运之理', '葢天者运行不息水者注之不竭以不竭逐不息之运茍注挹均调则参校旋转之势无有差舛也', '进仪象状', False),
 ('进状-水运之理-短', '水者注之不竭以不竭逐不息之运', '进仪象状（hero 摘句）', False),
 ('进状-水银代水', '至冬水凝运行迟涩则以水银代之故无差舛', '进仪象状', False),
 ('进状-一台', '今则兼采诸家之说备存仪象之器共置一台中台有二隔浑仪置于上浑象置于下枢机轮轴隐于中钟鼔时刻司辰运于轮上木阁五层蔽于前司辰击鼓揺铃执牌出没于阁内以水激轮轮转而仪象皆动', '进仪象状', False),
 ('进状-五色珠', '又以五色珠为日月五星贯以丝绳两末以钩环挂于南北轴依七曜盈缩迟疾留逆移徙令常在见行躔次之内昼夜随天而旋', '进仪象状', False),
 ('进状-省得失', '观璇玑者不独视天时而布政令抑欲察灾祥而省得失', '进仪象状', False),
 ('进状-木様', '遂具奏陈乞先创木様进呈差官试验', '进仪象状', False),
 ('进状-置局', '二年八月十六日诏如臣所请置局差官', '进仪象状', False),
 ('进状-主簿', '遂奏差郑州原武县主簿充夀州州学教授', '进仪象状', False),
 ('提要-苏颂', '宋苏颂撰颂字子容南安人徙居丹徒庆厯二年进士官至右仆射兼中书门下侍郎', '四库提要', False),
 ('提要-三层台', '以吏部令史韩公亷有巧思奏用之授以古法为台三层上设浑仪中设浑象下设司辰贯以一机激水转轮不假人力', '四库提要引宋史本传', False),
 ('进状-时至刻临', '时至刻临则司辰出告', '四库提要引宋史本传', False),
 ('提要-流传', '南宋以后流传甚稀此本为明钱曽所藏后有乾道壬辰九月九日呉兴施元之刻本于三衢坐啸斋', '四库提要', False),
 ('提要-钱曾', '图様界昼不爽毫髪凡数月而后成楮墨精妙绝伦', '四库提要引读书敏求记', False),
 ('提要-无足轻重', '我朝仪器精宻敻绝千古颂所创造固无足轻重', '四库提要', False),
 ('提要-不传', '其学畧授冬官正袁惟几今其法苏氏子孙亦不传', '四库提要引石林燕语', False),
 ('天经-北极', '于地浑面自北扶天而上三十有五度少弱则北极出地之度也', '卷上·天经双环', False),
 ('赤道-差三度', '其四正日躔之宿旧据厯法推步今以新仪考测知日躔与今天道差违凡三度', '卷上·赤道单环', False),
 ('赤道-四正', '葢元丰甲子岁冬之日至在赤道斗三度夏之日至在井九度少弱春分日在奎初度强秋分日在轸七度太弱', '卷上·赤道单环', False),
 ('浑象-星账', '中外官星其名二百四十六其数一千二百八十一紫微垣在浑象北上规星其名三十七其数一百八十三二项总名二百八十三星数一千四百六十四', '卷中·浑象', False),
 ('浑象-体径', '浑象体正圆如毬径四尺五寸六分半', '卷中·浑象', False),
 ('浑象-赤道牙', '就赤道为牙距四百七十八牙以衔天轮随机轮之地毂以运动', '卷中·浑象', False),
 ('木阁-总', '右木阁五层在机轮前第一层时初木人左揺铃刻至中击鼓时正右扣钟第二层木人出报时初又时正第三层木人出报十二时中百刻第四层夜漏击金钲第五层分布木人出报夜漏箭', '卷下·木阁', False),
 ('木阁一层-三色', '每时初即服绯司辰于左门内揺铃刻至即服绿司晨中门内击鼓时正即服紫司辰右门内扣钟', '卷下·木阁第一层', False),
 ('司辰24', '昼夜时初正司辰轮在木阁第二层内直径七尺三寸上置二十四司辰十二人报时初十二人报时正', '卷下·时初正司辰轮', False),
 ('司辰96', '报刻司辰轮在木阁第三层内直径七尺二寸上布十二时之百刻分布报刻司辰除时初外以刻言之其司辰九十六人', '卷下·报刻司辰轮', False),
 ('六十一箭', '凡冬夏夜有长短不可以一法测之故一岁设六十一箭箭亦有长短故随节气更换则四时之昼夜各无差舛', '卷下·夜漏箭轮', False),
 ('齿轮-元丰法', '每中轮动机轮六牙距为一刻五十牙距为一时其六百牙为十二时者元丰法也', '卷下·拨牙机轮', False),
 ('天轮六百牙', '右天轮直径三尺八寸上安六百牙距', '卷下·天轮', False),
 ('水法-河车起', '先实水于升水下壶壶满则拨河车八距', '卷下·仪象运水法', False),
 ('河车-戽斗', '河车外出十六拨牙以拨升水下轮十六距对拨牙北安手把八以运河车二轮辋外斜安戽斗二十四上轮十六下轮八', '卷下·河车天河', False),
 ('渇乌', '天池水南出渇乌注入平水壶由渇乌西注入枢轮受水壶', '卷下·仪象运水法', False),
 ('平水壶-凖水箭', '平水壶上有凖水箭自河车发水入天河以注天池壶', '卷下·天池平水壶', False),
 ('平水壶', '天池壶受水有多少紧慢不均故以平水壶节之即注枢轮受水壶昼夜停匀时刻自正', '卷下·天池平水壶', False),
 ('周而复始', '每受水一壶过水落入退水壶由下窍北流入升水下壶再动河车运水入上水壶周而复始', '卷下·仪象运水法', False),
 ('擒纵', '壶虚即为格义所格所以能受水水实即格义不能胜壶故格义落格义落即壶侧铁拨击开天衡闗舌掣动天条天条动则天衡起发动天衡闗左天鏁开即放枢轮一辐过', '卷下·仪象运水法', False),
 ('检栝二', '枢轮所检栝者二一以运浑仪二以动机轮', '卷下·仪象运水法', False),
 ('检栝四', '机轮所以检栝者四一以天轮运浑象二以动钟鼓轮三以动时初正司辰轮四以动报刻司辰轮', '卷下·仪象运水法', False),
 ('枢轮36壶', '枢轮直径一丈一尺以七十二辐【七十二一本云九十六】双植于一毂为三十六【三十六一本云四十八】洪束以三辋每洪夹持受水壶一总三十六壶', '卷下·枢轮', True),
 ('圭表', '其制于浑仪下安圭座面与水趺中心相结各为水沟通流以定平凖圭长一丈三尺为日行晷之南北', '卷下·浑仪圭表', False),
]

# 库内侧断言
for qid, q, src, sg in QUOTES:
    nq = norm(q, strip_gloss=sg)
    if nq not in (LIBN_nogloss if sg else LIBN):
        for cut in range(len(nq), 2, -4):
            if nq[:cut] in LIBN:
                print(f'  前缀至{cut}字可中: …{q[:cut]}|||{q[cut:cut+12]}…')
                break
        else:
            print('  开头即不中')
        fail(f'引文[{qid}]({src})不在库本')

# ---------------- 2. 页面抓取 ----------------
from html.parser import HTMLParser

class QCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []      # (tag, capture)
        self.qs = []         # 抓到的 .q 文本
        self.texts = []      # 全文
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        toks = cls.split()
        cap = any(t == 'q' for t in toks)
        self.stack.append((tag, cap))
        if tag in ('br', 'img', 'meta', 'link', 'hr', 'input'):
            self.stack.pop()
    def handle_endtag(self, tag):
        while self.stack and self.stack[-1][0] != tag:
            self.stack.pop()
        if self.stack:
            self.stack.pop()
    def handle_data(self, data):
        self.texts.append(data)
        if any(cap for _, cap in self.stack):
            self.qs.append(data)

page = (BASE / 'xinyi-xiangfayao.html').read_text(encoding='utf-8')
p = QCollector()
p.feed(page)
pagetext = ''.join(p.texts)
spans = [norm(s, strip_gloss=True) for s in p.qs if s.strip()]
spans_raw = [s for s in p.qs if s.strip()]

print(f'页面 .q 段数: {len(spans)}　QUOTES: {len(QUOTES)}')
for qid, q, src, sg in QUOTES:
    nq = norm(q, strip_gloss=sg)
    if not any(nq in sp or nq == sp for sp in spans):
        fail(f'页面上找不到引文[{qid}]')
# 页面每段 .q 都要能在库本里找到（剥【】注后比对）
for i, sp in enumerate(spans):
    if sp not in LIBN_nogloss:
        fail(f'页面第{i+1}段 .q 不在库本: {sp[:28]}…')

# ---------------- 3. 排版红线 ----------------
if '—' in pagetext or '–' in pagetext:
    fail('排版红线：出现长划线')
for ln in page.split('\n'):
    if ln.count('·') > 1:
        fail(f'排版红线：单行超过1个· → {ln[:40]}')

# ---------------- 4. 机算断言 ----------------
def need(*frag):
    for f in frag:
        if f not in pagetext:
            fail(f'页面缺关键表述: {f}')

# 字数口径：全帙=len；白文去空白含标点=去标记后剥一切空白（不去标点）
n_all = len(lib_raw)
n_nospace = len(re.sub(r'\s', '', lib_raw))
n_plain = len(re.sub(r'\s', '', re.sub(r'<子部[^>]*>', '', lib_raw)))
n_nopunct = len(norm(lib_raw))
print(f'库本字数: 全帙{n_all} 去空白含标点{n_nospace} 白文去空白含标点{n_plain} 全文去标点{n_nopunct}')
if (n_all, n_plain) != (15340, 13833):
    fail('库本字数与页面口径不符')
need('一万五千三百四十', '一万三千八百三十三')

# 图目 17/18/25
FIGS = {
 '卷上': ['浑仪','六合仪','三辰仪','四游仪','天经双环','阴纬单环','天常单环','三辰仪双环','赤道单环','黄道双环','四象单环','天运单环','四游仪双环','望筒直距','龙柱','鳌云','水趺'],
 '卷中': ['浑象','浑象六合仪','浑象地柜','浑象赤道牙','紫微垣星图','东北方中外官星图','西南方中外官星图','北极星图','南极星图','四时昏晓加临中星图','春分昏中星图','春分晓中星图','夏至昏中星图','夏至晓中星图','秋分昏中星图','秋分晓中星图','冬至昏中星图','冬至晓中星图'],
 '卷下': ['水运仪象台','运动仪象制度','木阁昼夜机轮','机轮轴','天轮','拨牙机轮','木阁第一层','昼时钟鼓轮','木阁第二层','昼夜时初正司辰轮','木阁第三层','报刻司辰轮','木阁第四层五层','夜漏金钲轮','夜漏司晨轮','枢轮退水壶','铁枢轴','天柱','天毂','天池平水壶','天衡','升水上下轮','河车天河','仪象运水法','浑仪圭表'],
}
assert [len(FIGS[k]) for k in ('卷上','卷中','卷下')] == [17, 18, 25], '图目清单本身数目错误'
assert 17 + 18 + 25 == 60
for k, lst in FIGS.items():
    for name in lst:
        if norm(name) not in LIBN:
            fail(f'图目[{name}]不在库本')
        if name not in pagetext:
            fail(f'图目[{name}]未上页面')
need('十七图', '十八图', '二十五图')

# 星账：246名+37名=283名；1281数+183数=1464数
assert 246 + 37 == 283 and 1281 + 183 == 1464
need('二百八十三', '一千四百六十四')

# 齿轮：600牙 = 12时 × 50牙/时；一时100/12刻=8⅓刻；50牙=6牙×8⅓
assert 600 == 12 * 50
assert abs(50 / 6 - 100 / 12) < 1e-9
need('六百', '五十', '四百七十八')

# 木人：24+96+25=145
assert 24 + 96 + 25 == 145
need('一百四十五', '二十四', '九十六', '二十有五')

# 枢轮 36 壶 / 别本 48
assert '总三十六壶' in norm(lib_nomark)
need('三十六', '四十八')

# PUA 缺字计数
pua = {'候': 0, '龟': 0, '宿': 0, '雨': 0, '拏': 0}
for c, k in [('','候'), ('','龟'), ('','宿'), ('','雨'), ('','拏')]:
    pua[k] = lib_raw.count(c)
camel = lib_raw.count('𫘞')
print('PUA:', pua, '𫘞:', camel)
if pua != {'候': 19, '龟': 2, '宿': 1, '雨': 1, '拏': 2} or camel != 1:
    fail(f'缺字计数与页面校记不符: {pua} 𫘞{camel}')
if sum(pua.values()) + camel != 26:
    fail('缺字总数口径错误（页面校记称二十五枚PUA+一枚Ext-B）')
need('候十九', '龟二', '宿一', '雨一', '拏二', '二十五枚')

# 引文段数与页脚声明一致
if f'引文 {len(QUOTES)} 段' not in pagetext:
    fail(f'页脚引文数与实际不符，应为 {len(QUOTES)}')

print()
print(f'== 引文 {len(QUOTES)} 条 / 页面 .q {len(spans)} 段, 失败 {len(FAIL)} ==')
sys.exit(1 if FAIL else 0)
