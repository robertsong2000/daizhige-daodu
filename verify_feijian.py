#!/usr/bin/env python3
# 核验 feijian-ji.html：引文双侧逐字 + 反扫 + 红线 + 机数
import re, sys
from html.parser import HTMLParser

PAGE = 'feijian-ji.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/'
NO = 124  # mulu 同号制，撞号顺延时与页面 sed 同改

LIBS = {
    'novel': LIB + '集藏/小说/锲唐代吕纯阳得道飞剑记.txt',
    'miao':  LIB + '道藏/正统道藏洞真部/记传类/纯阳帝君神化妙通纪.txt',
    'tidao': LIB + '道藏/正统道藏洞真部/记传类/历世真仙体道通鉴.txt',
}

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(ch)
    return ''.join(out)

raw = {}
NORM = {}
for k, p in LIBS.items():
    raw[k] = open(p, encoding='utf-8').read()
    NORM[k] = norm(raw[k])

html = open(PAGE, encoding='utf-8').read()
errors, warns = [], []

# ---------------- 收集器：html.parser 栈配平，VOID 不入栈 ----------------
VOID = {'br', 'img', 'meta', 'link', 'hr', 'input', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}

class QC(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []          # (tag, is_q_start)
        self.qstarts = []        # (stack_depth, buf_pos)
        self.buf = []
        self.blocks = []         # (text, is_q)
        self.alltext = []        # 含非 q 文本（剥 script/style）
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        if tag in ('script', 'style'):
            self.skip += 1
            self.stack.append((tag, False))
            return
        cls = (dict(attrs).get('class') or '').split()
        isq = 'q' in cls
        if isq:
            self.qstarts.append((len(self.stack), len(self.buf)))
        self.stack.append((tag, isq))
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                if tag in ('script', 'style'):
                    self.skip -= 1
                closed = self.stack[i:]
                del self.stack[i:]
                while self.qstarts and self.qstarts[-1][0] >= i:
                    _, b0 = self.qstarts.pop()
                    txt = ''.join(self.buf[b0:])
                    del self.buf[b0:]
                    self.blocks.append(txt)
                break
    def handle_data(self, data):
        if self.skip == 0:
            self.alltext.append(data)
        if self.skip == 0:
            self.buf.append(data)
        elif self.skip > 0:
            return

p = QC()
p.feed(html)
qblocks = [b.strip() for b in p.blocks if b.strip()]
vis = ''.join(p.alltext)
print(f'收集 .q 块：{len(qblocks)}；可见文本 {len(vis)} 字符')

UNION = NORM['novel'] + '' + NORM['miao'] + '' + NORM['tidao']

# ---------------- 期望引文清单（双侧：库内 + 页面） ----------------
QUOTES = [
    ('novel', '一断烦恼，二断色欲，三断贪嗔'),
    ('novel', '此剑用昆仑山所产之铜，女娲炼石之炭，老君却魔之扇，祝融烧天之火，煅炼而成。禀阴阳之纯粹，凛雪霜之寒铓。'),
    ('novel', '俗语道得好：红粉赠与佳人，宝剑付之烈士。'),
    ('novel', '此二剑一属雄，一属雌，君以此自卫则可，以此斩邪则可，若以此杀人，则不可也。'),
    ('novel', '有道剑有法剑，道剑则出入无形，法剑则以术治之者，此俗眼所共见，第能除妖去祟耳。'),
    ('novel', '削平浮世不平事，与尔相将上九霄'),
    ('novel', '黄粱犹未熟，一梦到华胥。'),
    ('novel', '升沉万态，荣瘁多端，五十年间一顷耳。'),
    ('novel', '吾七度试子，皆能坚忍，得道必矣。'),
    ('novel', '孽畜，不得无礼！'),
    ('novel', '小仙们是钟离云房徒弟，适间不揣，飞二剑戏侮，望慈悲见恕。'),
    ('novel', '我也肯慈悲你，你却不肯慈悲别人。'),
    ('novel', '你当日行凶，剑插于腰股之间，分为左右，今日这口剑却要你佩在背脊之上。要斩他人，拔出鞘来，先从你项下经过，斩妖诛邪，听你所用，如要伤人，先伤你自己。'),
    ('novel', '故此叫做个洞宾背剑。'),
    ('novel', '我闻得火龙真人以雌雄二剑付汝，一断色欲，二断贪嗔，三断烦恼，且嘱咐你除妖则可，杀人则不可。'),
    ('novel', '纯阳子将那口宝剑飞起径，奔禅师身上，那禅师喝道：孽畜，不得无礼！用手一指，那剑遂插在左边地上。'),
    ('novel', '此正是一旦泄之有余，千日修之不足。'),
    ('novel', '干者阳也，系屯纯字也，分明是吕纯阳下世。'),
    ('novel', '世人欲见吾甚切，既见吾，又不能识，亦命也。'),
    ('novel', '道在目前，蓬莱跬步；抚机不发，当面蹉过。'),
    ('novel', '鲸吸鳌吞数百杯，玉山谁起复谁颓。醒时两袂天风吟，一朵红云海上来。'),
    ('novel', '仙籍班班有姓名，蓬莱倦客吕先生。凡夫肉眼知多少，不及城南老树精。'),
    ('novel', '独自行来独自坐，独自吟来独自坐。惟有城南柳树精，分明知我神仙过。'),
    ('novel', '朝游北海暮苍梧，袖里青蛇胆气粗。三醉岳阳人不识，朗然飞过洞庭湖。'),
    ('novel', '斋供倒好，只是吕洞宾在那里，打不得些儿乱搅。'),
    ('novel', '眼前不是成仙客，成仙只是姓何人。'),
    ('novel', '嵓之志异于先生，必须度尽众生方上升未晚也。'),
    ('novel', '人心奸险，未易度化，止度有何氏女一人而已。'),
    ('novel', '就封吕嵓为演正警化真人之职，封何惠娘为太玄演化仙姑之职，各赐金书玉旨，擢入仙班。'),
    ('novel', '白云归洞口，红日架山腰。'),
    ('miao',  '似此问答不一，以帝君飞剑斩黄龙，蠢哉。'),
    ('miao',  '故朱文公云：君子仁慈犹克己，神仙安肯取人头。'),
    ('tidao', '吾不愿学，恐误五百年后人。'),
]

print(f'期望引文：{len(QUOTES)} 条')
for src, q in QUOTES:
    qn = norm(q)
    if qn not in NORM[src]:
        errors.append(f'库内缺失[{src}]: {q[:24]}')
    hit = any(qn in norm(b) for b in qblocks)
    if not hit:
        errors.append(f'页面 .q 未载: {q[:24]}')

# ---------------- .q 全量反查（每块必须是某库连续原文） ----------------
bad = 0
for b in qblocks:
    bn = norm(b)
    if bn and bn not in UNION:
        bad += 1
        errors.append(f'.q 块与库不连续: {b[:30]}')
print(f'.q 全量反查：{len(qblocks)} 块，不连续 {bad}')

# ---------------- 「」反扫（剥标签后可见文本中的引号串） ----------------
vis1 = re.sub(r'\s+', '', vis)
brs = re.findall(r'「([^」]*)」', vis)
print(f'「」串：{len(brs)} 枚')
if vis.count('「') != vis.count('」'):
    errors.append(f'引号不配对 「={vis.count("「")} 」={vis.count("」")}')
for s in brs:
    sn = norm(s)
    if sn and sn not in UNION:
        errors.append(f'「」内容非库内原文: {s[:30]}')

# ---------------- 红线 ----------------
if '—' in html or '–' in html:
    errors.append('出现长划线/短划线')
dotlines = [ln for ln in vis.split('\n') if ln.count('·') > 1]
if dotlines:
    errors.append(f'一行多·: {dotlines[:2]}')
eng = set(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z0-9]*', vis))
ALLOW = {'github', 'com', 'robertsong2000', 'daizhigev20', 'mulu', 'html', 'cjk', 'a'}
stray = eng - ALLOW
if stray:
    errors.append(f'英文残留: {stray}')

# ---------------- 机数（库本重算） ----------------
t = raw['novel']
nows = len(re.sub(r'\s', '', t))
han = sum(1 for c in t if 0x3400 <= ord(c) <= 0x9FFF)
pua = sum(1 for c in t if 0xE000 <= ord(c) <= 0xF8FF)
extb = sum(1 for c in t if 0x20000 <= ord(c) <= 0x2A6DF)
huimu = len(re.findall(r'第[一二三四五六七八九十]+回', t))
M = {
    '去空白': (nows, 43084), '汉字': (han, 36007),
    '回目': (huimu, 13),
    '诗曰': (t.count('诗曰'), 17), '正是': (t.count('正是'), 23),
    '钟离子': (t.count('钟离子'), 31), '云房子': (t.count('云房子'), 37), '钟高子': (t.count('钟高子'), 4),
    '火龙真人': (t.count('火龙真人'), 23), '火尤真人': (t.count('火尤真人'), 1),
    '干系屯': (t.count('干系屯'), 28), '□': (t.count('□'), 9),
    '五试': (t.count('五试'), 1), '试他七次': (t.count('试他七次'), 1), '七度': (t.count('七度'), 1),
    'PUA': (pua, 0), 'ExtB': (extb, 1),
    '黄粱': (t.count('黄粱'), 1), '度尽众生': (t.count('度尽众生'), 1),
}
for k, (got, exp) in M.items():
    tag = 'OK ' if got == exp else 'FAIL'
    print(f'{tag} 机数 {k}: 库本 {got} vs 页载 {exp}')
    if got != exp:
        errors.append(f'机数不合 {k}: 库本 {got} 页载 {exp}')

# 页面数字出现
for s in ['43,084', '36,007', '28', '31／37／4', '23／1']:
    if s not in html:
        errors.append(f'页面缺计数 {s}')

# ---------------- 结构 ----------------
if len(re.findall(r'class="chapgrid"', html)) != 1:
    errors.append('chapgrid 缺失')
ch = re.search(r'<div class="chapgrid">(.*?)</section>', html, re.S).group(1)
n_chap = len(re.findall(r'<span class="no mono">', ch))
if n_chap != 13:
    errors.append(f'剑格回目数 {n_chap} ≠ 13')
n_rail = len(re.findall(r'<a href="#(?:zhu|jie|shi|zhe|mo|gu|gui)"( class="on")?><span class="rb">', html))
if n_rail != 7:
    errors.append(f'鞘轨结数 {n_rail} ≠ 7')
n_row = len(re.findall(r'<div class="lrow', html))
n_hit = len(re.findall(r'<div class="lrow hit"', html))
if (n_row, n_hit) != (7, 1):
    errors.append(f'度人账 {n_row} 行 / 命中 {n_hit} ≠ (7,1)')
for kn in ['壹', '贰', '叁', '肆', '伍', '陆', '柒']:
    if f'<span class="knum">{kn}</span>' not in html:
        errors.append(f'缺节号 {kn}')
if f'之一百二十{chr(0x4e8c) if False else "三"}' not in html or f'之一百二十三' not in html:
    errors.append('页内序号非之一百二十三')
if f'<span class="no mono">{NO}</span>' not in open('mulu.html', encoding='utf-8').read():
    print(f'提醒：mulu.html 尚无 {NO} 号条目（定号前正常）')

# ---------------- 汇总 ----------------
print()
if errors:
    print(f'FAIL：{len(errors)} 项')
    for e in errors:
        print('  ×', e)
    sys.exit(1)
print(f'ALL PASS：{len(QUOTES)} 条引文双侧逐字 + {len(qblocks)} 块全量反查 + 红线 + 机数 {len(M)} 项 + 结构')
