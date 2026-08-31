#!/usr/bin/env python3
# 核验 zhuangzi.html（庄子）：引文双侧逐字 + 伤口账 + 机数 + 排版红线
import re, sys
from html.parser import HTMLParser

PAGE = 'zhuangzi.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/道藏/藏外/庄子.txt'

fails, warns = [], []
def chk(cond, msg):
    if cond: print('  ok', msg)
    else: fails.append(msg); print('  FAIL', msg)

# ---------- norm：只留 CJK（含扩展区），去空白去标点 ----------
def norm(s):
    out = []
    for c in s:
        o = ord(c)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(c)
    return ''.join(out)

lib_raw = open(LIB, encoding='utf-8').read()
lib_ns  = ''.join(lib_raw.split())          # 去空白，保留标点
lib_n   = norm(lib_raw)
page_raw = open(PAGE, encoding='utf-8').read()

# ---------- QCollector：class.split() 恰含 q ----------
VOID = {'br','img','meta','link','hr','input','area','base','col','embed','source','track','wbr'}
class QC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.buf, self.blocks, self.qdepth = [], [], [], 0
    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        self.stack.append(tag)
        cls = dict(attrs).get('class','') or ''
        if 'q' in cls.split():
            self.qdepth = len(self.stack)
            self.buf = []
    def handle_startendtag(self, tag, attrs):
        if tag in VOID: return
        cls = dict(attrs).get('class','') or ''
        if 'q' in cls.split():
            self.buf = []
            self.blocks.append(''.join(self.buf))
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag: self.stack.pop()
                if self.stack: self.stack.pop()
        if self.qdepth and len(self.stack) < self.qdepth:
            self.qdepth = 0
            self.blocks.append(''.join(self.buf))
            self.buf = []
    def handle_data(self, data):
        if self.qdepth: self.buf.append(data)

# 全文正文文本（剥 style/script/标签），用于反扫、裸引、英文检查
class TC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('style','script'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('style','script'): self.skip = max(0, self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

qc = QC(); qc.feed(page_raw)
qs = [b for b in (blk.strip() for blk in qc.blocks) if b]
tc = TC(); tc.feed(page_raw)
ptext = ''.join(tc.parts)
pn = norm(ptext)

print('== 收集 ==')
print('  .q 块数', len(qs))

# ---------- 引文清单：双侧（库本 + 页面某 .q 块） ----------
QUOTES = [
 '北冥有鱼，其名为鲲。鲲之大，不知其几千里也。',
 '怒而飞，其翼若垂天之云。',
 '化而为鸟，其名为鹏。',
 '蜩与学鸠笑之',
 '我决起而飞，枪榆枋而止，时则不至而控于地而已矣。',
 '鹏之徙于南冥也，水击三千里，抟扶摇而上者九万里，去以六月息者也。',
 '小知不及大知，小年不及大年。',
 '鹪鹩巢于深林，不过一枝；偃鼠饮河，不过满腹。',
 '藐姑射山，有神人居焉，肌肤若冰雪，淖约若处子。不食五谷，吸风饮露。',
 '彷徨乎无为其侧，逍遥乎寝卧其下。',
 '无何有之乡，广莫之野',
 '至人无己，神人无功，圣人无名。',
 '吾生也有涯，而知也无涯。以有涯随无涯，殆已！',
 '岁更刀，割也',
 '月更刀，折也',
 '今臣之刀十九年矣，所解数千牛矣，而刀刃若新发于硎。',
 '臣之所好者，道也，进乎技矣。',
 '以无厚入有间，恢恢乎其于游刃必有余地矣。',
 '提刀而立，为之四顾，为之踌躇满志，善刀而藏之。',
 '吾闻庖丁之言，得养生焉。',
 '泽雉十步一啄，百步一饮，不蕲畜乎樊中。神虽王，不善也。',
 '昔者庄周梦为胡蝶，栩栩然胡蝶也。自喻适志与！不知周也。俄然觉，则蘧蘧然周也。不知周之梦为胡蝶与，胡蝶之梦为周与？周与胡蝶，则必有分矣。此之谓物化。',
 '栩栩然胡蝶也。自喻适志与！',
 '俄然觉，则蘧蘧然周也。',
 '泉涸，鱼相与处于陆，相呴以湿，相濡以沫，不如相忘于江湖。',
 '何不虑以为大樽而浮乎江湖。',
 '安时而处顺，哀乐不能入也。',
 '日出而作，日入而息，逍遥天地间而心意自得。',
 '南海之帝为倏，北海之帝为忽，中央之帝为浑沌。',
 '日凿一窍，七日而浑沌死。',
 '庄周家贫，故往贷粟于监河侯。',
 '周顾视车辙中，有鲋鱼焉。',
 '曾不如早索我于枯鱼之肆！',
 '夫处穷闾阨巷，困窘织屦，槁项黄馘者，商所短也；一悟万乘之主而从车百乘者，商之所长也。',
 '破痈溃痤者得车一乘，舐痔者得车五乘，所治愈下，得车愈多。',
 '何得车之多也？子行矣！',
 '惠子谓庄子曰',
 '鲦鱼出游从容，是鱼之乐也。',
 '惠子曰︰「子鱼，安知鱼之乐？」',
 '子非我，安知我不知鱼之乐？',
 '子曰「我非子，固不知子矣；子固非鱼也，子之不知鱼之乐，全矣！」',
 '请循其本。子曰汝安知鱼乐』云者，既已知吾知之而问我。我知之濠上也。',
 '庄子送葬，过惠子之墓',
 '郢人垩慢其鼻端若蝇翼',
 '匠石运斤成风，听而斲之，尽垩而鼻不伤。',
 '郢人立不失容。',
 '臣则尝能斲之。虽然，臣之质死久矣。',
 '自夫之死也，吾无以为质矣，吾无与言之矣！',
 '昔赵文王喜剑，剑士夹门而客三千余人，日夜相击于前，死伤者岁百人，好之不厌。',
 '庄子当能。',
 '十步一人，不留行。',
 '芴漠无形，变化无常，死与？生与？天地并与，神明往与﹗',
 '独与天地精神往来，不敖倪于万物，不谴是非，以与世俗处。',
 '庄子（南华经）',
]

print('== 引文双侧核验 ==', len(QUOTES), '条')
qn_list = [norm(q) for q in QUOTES]
for q, qn in zip(QUOTES, qn_list):
    chk(qn in lib_n,                        '库本含：' + q[:22])
    chk(any(qn in norm(b) for b in qs),     '页面.q含：' + q[:22])

# ---------- 伤口账（库本应有 / 通行应无 / 页面照录） ----------
WOUNDS = [
 ('枪榆枋而止','抢榆枋而止'),
 ('奚以这九万里','奚以之九万里'),
 ('而后乃今掊风','而后乃今培风'),
 ('此年也。而彭祖','此小年也。而彭祖'),
 ('乘云气，御龙，','乘云气，御飞龙，'),
 ('殆而矣','殆而已矣'),
 ('可以养亲，可以尽','可以养亲，可以尽年'),
 ('斧铖之诛','斧钺之诛'),
 ('夫子贪失理','夫子贪生失理'),
 ('时相遇于浑地','时相与遇于浑沌之地'),
 ('逍遥天地间而心意自得','逍遥于天地之间而心意自得'),
 ('子鱼，安知鱼之乐','子非鱼，安知鱼之乐'),
 ('子曰「我非子','庄子曰「我非子'),
 ('商所短也','商之所短也'),
 ('子岂治其邪','子岂治其痔邪'),
 ('使匠之。匠石运斤成风','使匠石斲之。匠石运斤成风'),
 ('自夫之死也','自夫子之死也'),
 ('十步一人，不留行','十步一人，千里不留行'),
]
print('== 伤口账 ==', len(WOUNDS), '处')
for has, nots in WOUNDS:
    hn = norm(has)
    chk(norm(lib_raw).find(hn) >= 0,        '库本有：' + has)
    chk(norm(nots) not in lib_n,            '库本无通行：' + nots)
    chk(hn in pn,                           '页面照录：' + has)
chk(lib_ns.count('此小年也') == 1, '「此小年也」库内恰 1 见（对照伤口）')
chk('子曰汝安知鱼乐』云者' in lib_ns and '子曰『汝安知鱼乐' not in lib_ns, '缺前引号（括号口径）')
chk(sum(1 for b in qs if '』' in b and '『' not in b) == 1, '孤』.q 块恰 1（照录库本缺符号）')

# ---------- 反扫：页面所有「」/『』须是库本子串 ----------
print('== 反扫 ==')
bad = []
for m in re.finditer(r'「([^「」]*)」|『([^『』]*)』', ptext):
    span = m.group(1) if m.group(1) is not None else m.group(2)
    sn = norm(span)
    if sn and sn not in lib_n:
        bad.append(span)
chk(not bad, '所有引号内文字均库本子串' + ('' if not bad else ' 违例:' + repr(bad[:5])))
chk(True, '孤』检查移至伤口段')

# ---------- 机数 ----------
print('== 机数 ==')
ns = lib_ns
han = sum(1 for c in ns if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)
pua = [c for c in lib_raw if 0xE000 <= ord(c) <= 0xF8FF]
ext = [c for c in lib_raw if 0x20000 <= ord(c) <= 0x3FFFF]
import collections
extk = collections.Counter(ext)
chk(len(ns) == 78563,  '库本去空白 78,563（实 ' + format(len(ns),',' ) + '）')
chk(han == 63670,      '汉字 63,670（实 ' + str(han) + '）')
chk(len(pua) == 0,     'PUA 0 见')
chk(len(extk) == 14 and sum(extk.values()) == 25, '扩展区 14 种 25 见（实 %d 种 %d 见）' % (len(extk), sum(extk.values())))
chk(ns.count('﹗') == 27 and ns.count('︰') == 12, '竖排标点 ﹗27 / ︰12')
lines = [l.strip() for l in lib_raw.split('\n') if l.strip()]
chk(sum(1 for l in lines if l.startswith('卷')) == 26, '卷头 26')
chk(lines.count('杂篇') == 1 and lines.count('内篇') == 0 and lines.count('外篇') == 0, '分部标记仅存杂篇')
for w, n in [('江湖',7),('逍遥',7),('游',109),('忘',83),('梦',30),('蝶',7),('笑',30),('鱼',42),('物化',9),('惠子',22),('孔子',80),('庄子',76)]:
    chk(ns.count(w) == n, '词频 %s＝%d（实 %d）' % (w, n, ns.count(w)))
for name in ['逍遥游','齐物论','养生主','人间世','德充符','大宗师','应帝王','骈拇','马蹄','胠箧','在宥','天地','天道','天运','刻意','缮性','秋水','至乐','达生','山木','田子方','知北游','庚桑楚','徐无鬼','则阳','外物','寓言','让王','盗跖','说剑','渔父','列御寇','天下']:
    chk(name in lib_ns, '篇名在库：' + name)
for sig in ['刻意尚行','田子方侍坐','知北游于玄水','徐无鬼因女商','盗跖从卒九千人','有渔父者','列御寇之齐']:
    chk(sig in lib_ns, '脱头七篇正文俱在：' + sig)
chk('卷一上第一' in lib_ns and '卷三下第七' in lib_ns and '卷十下第三十三' in lib_ns, '卷头编号样例在')

# ---------- 页面结构 ----------
print('== 页面结构 ==')
chk(page_raw.count('class="piece"') + page_raw.count('class="piece void"') == 33, '篇墙 33 格')
chk(page_raw.count('class="piece void"') == 7, '虚格 7')
for s in ['78,563','63,670','二十六','二十五见','二十七见','十二见','七见','二十二回']:
    chk(s in ptext, '页面数字在：' + s)

# ---------- 排版红线 ----------
print('== 红线 ==')
chk('—' not in page_raw and '–' not in page_raw, '无长划线')
badmd = [i for i, l in enumerate(page_raw.split('\n'), 1) if l.count('·') > 1]
chk(not badmd, '每行 · ≤1（违例行 ' + str(badmd[:5]) + '）')
ALLOW = {'github.com/robertsong2000/daizhigev20','mulu.html'}
eng = re.sub(r'github\.com/robertsong2000/daizhigev20|mulu\.html|庄子\.txt', '', ptext)
eng = re.findall(r'[A-Za-z]+', eng)
chk(not eng, '正文无英文残留' + ('' if not eng else ' ' + repr(eng[:8])))

print()
print('共 %d 条引文 / %d 处伤口 / %d 段机数与红线' % (len(QUOTES), len(WOUNDS), len(fails) and 0 or 1))
if fails:
    print('FAIL ×', len(fails)); sys.exit(1)
print('ALL PASS')
