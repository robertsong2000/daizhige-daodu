#!/usr/bin/env python3
# 核验 haiwai-tongku-ji.html（海外恸哭记）：引文双侧逐字 + 机数 + 排版红线
import re, sys, collections
from html.parser import HTMLParser

PAGE = 'haiwai-tongku-ji.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/海外恸哭记.txt'

fails = []
def chk(cond, msg):
    if cond: print('  ok', msg)
    else: fails.append(msg); print('  FAIL', msg)

# ---------- norm：只留 CJK（含扩展区），去空白去标点去占位符 ----------
def norm(s):
    return ''.join(c for c in s if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)

lib_raw = open(LIB, encoding='utf-8').read()
lib_ns  = ''.join(lib_raw.split())
lib_n   = norm(lib_raw)
page_raw = open(PAGE, encoding='utf-8').read()

# ---------- .q 块收集 ----------
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
            self.qdepth = len(self.stack); self.buf = []
    def handle_endtag(self, tag):
        if tag in VOID: return
        if self.stack and self.stack[-1] == tag: self.stack.pop()
        if self.qdepth and len(self.stack) < self.qdepth:
            self.qdepth = 0
            self.blocks.append(''.join(self.buf)); self.buf = []
    def handle_data(self, data):
        if self.qdepth: self.buf.append(data)

class TC(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0; self.parts = []
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

# ---------- 引文清单 ----------
QUOTES = [
 '诸臣之诗，即起杜甫为之，亦未有以相过也。岂天下扰扰多杜甫哉？甫所遇之时、所历之境，未有诸臣万分之一。',
 '宗庙亡矣，亡日尚矣，归于何党矣。',
 '因次一时流离愁苦之事，为海外恸哭记；以待上之收京反国，即创业起居注之因也。舟山以后，■〈〈氵咸〉上木下〉所未详。行朝之臣，必有同志者。',
 '监国鲁元年（丙戌）夏六月丙子朔，浙江兵溃。上发绍兴。',
 '御舟碇蛟门。',
 '以海水为金汤、以舟楫为宫殿。',
 '公每日系河艍于驾舟之次，票拟章奏，即于其中接见宾客',
 '九月，北师破其城',
 '将军慨然，约明年四月发兵三万，一切战舰军资器械，自取其国之余资，足以供大兵中华数年之用。',
 '大司马余煌书来，曰此吴三桂之续也。',
 '京第即于舟中，朝服拜哭不已。',
 '孝卿乐之，忘其为乞师而来者，见轻于其国。其国发师之意益荒矣。',
 '十二日，见山，舵工惊曰：此高丽界也。转帆而南。',
 '日本不杀大唐僧，有犯法者止于逐；再往，则戮及同舟。',
 '故老不见兵革之事，本国且忘备，岂能渡海为人复仇乎？',
 '今日之事，何与之相类耶？',
 '当事诘夏之同谋者，夏慷慨而对曰：此事更有何人。无已，则太祖高皇帝、崇祯先帝耳。',
 '追之海水，数日之间，溺死者无算。遂空其地。',
 '以此形胜之地，仅仅以田横岛结局，悲夫！',
 '黄泉之路，请以兆人为道。',
 '吾守妇道三十年，垂绝而死男子之手乎？',
 '吾兵南下以来，所不易拔者，江阴、泾县合舟山而三耳。',
 '凡作■■■，即先生姓名',
 '公闻之，叹曰：主上仗我，我不忍去；今方寸乱矣。',
 '余屈身养母，戋戋自附于晋之处士，未知后之人其许我否也？',
 '父死不能葬、国亡不能救，死有余罪；今日之事，速死而已。',
 '我年适五九，复逢九月七，大厦已不支，成仁万事毕。',
 '公丙戌航海、甲辰就执，三度闽关、四入长江，两遭覆没，首尾十有九年。',
 '中原方逐鹿，何暇问虹梁？',
 '成败在此一举。天若祚国，从枕席上过师；否则，以余身为虀粉，亦始愿之所及也。',
]

print('== 引文双侧核验 ==', len(QUOTES), '条')
qn_list = [norm(q) for q in QUOTES]
for q, qn in zip(QUOTES, qn_list):
    chk(qn in lib_n,                        '库本含：' + q[:22])
    chk(any(qn in norm(b) for b in qs),     '页面.q含：' + q[:22])

# ---------- 反扫：页面所有「」/『』须是库本子串 ----------
print('== 反扫 ==')
bad = []
for m in re.finditer(r'「([^「」]*)」|『([^『』]*)』', ptext):
    span = m.group(1) if m.group(1) is not None else m.group(2)
    sn = norm(span)
    if sn and sn not in lib_n:
        bad.append(span)
chk(not bad, '所有引号内文字均库本子串' + ('' if not bad else ' 违例:' + repr(bad[:8])))

# ---------- 机数 ----------
print('== 机数 ==')
han = sum(1 for c in lib_ns if 0x3400 <= ord(c) <= 0x9FFF or 0x20000 <= ord(c) <= 0x3FFFF)
pua = [c for c in lib_raw if 0xE000 <= ord(c) <= 0xF8FF]
ext = collections.Counter(c for c in lib_raw if 0x20000 <= ord(c) <= 0x3FFFF)
chk(len(lib_ns) == 108548, '库本去空白 108,548（实 ' + format(len(lib_ns), ',') + '）')
chk(han == 91318,          '汉字 91,318（实 ' + str(han) + '）')
chk(len(pua) == 0,         'PUA 0 见')
chk(lib_raw.count('■') == 75,      '■ 75 见（实 ' + str(lib_raw.count('■')) + '）')
chk(len(ext) == 10 and sum(ext.values()) == 16,
    '扩展区 10 种 16 见（实 %d 种 %d 见）' % (len(ext), sum(ext.values())))
chk(lib_ns.count('周崔芝') == 3 and lib_ns.count('周鹤芝') == 14,
    '周崔芝 3 / 周鹤芝 14（实 %d / %d）' % (lib_ns.count('周崔芝'), lib_ns.count('周鹤芝')))
for w, n in [('监国鲁',7),('行朝',42),('舟山',81),('乞师',24),('日本',46),('恸哭',16),('苍水',9),('太冲',15),('黄宗羲',9)]:
    chk(lib_ns.count(w) == n, '词频 %s＝%d（实 %d）' % (w, n, lib_ns.count(w)))
for sig in ['日本乞师纪（行朝录之六）','舟山兴废（行朝录之五）','四明山寨纪（行朝录之七）',
            '沙定洲之乱（行朝录之九）','赣州失事纪（行朝录之二）','绍武争立纪（行朝录之三）',
            '兵部左侍郎苍水张公墓志铭','上元甲寅季春月，山阴吴隐石灊跋']:
    chk(sig in lib_ns, '结构标志在库：' + sig)

# ---------- 页面结构 ----------
print('== 页面结构 ==')
for s in ['108','548','七十五','十种十六见','十四见','三见','田横岛','雪交亭','洪武钱','蛟门','金狮子尊者']:
    chk(s in ptext, '页面数字与关目在：' + s)

# ---------- 排版红线 ----------
print('== 红线 ==')
chk('—' not in page_raw and '–' not in page_raw, '无长划线')
badmd = [i for i, l in enumerate(page_raw.split('\n'), 1) if l.count('·') > 1]
chk(not badmd, '每行 · ≤1（违例行 ' + str(badmd[:5]) + '）')
eng = re.sub(r'github\.com/robertsong2000/daizhigev20|mulu\.html|haiwai-tongku-ji', '', ptext)
eng = re.findall(r'[A-Za-z]+', eng)
chk(not eng, '正文无英文残留' + ('' if not eng else ' ' + repr(eng[:8])))

print()
if fails:
    print('FAIL ×', len(fails)); sys.exit(1)
print('ALL PASS')
