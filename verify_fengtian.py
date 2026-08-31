#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_fengtian.py — 奉天靖难记导读页核验：引文双侧逐字、反扫、红线、机数、结构"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/fengtian-jingnan-ji.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/奉天靖难记.txt'
NO = 135

html = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

def norm(s):
    return ''.join(c for c in s if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0002ffff')

libn = norm(lib)

fails, warns = [], []

# ---------- 收集 .q ----------
class QC(HTMLParser):
    VOID = {'br','img','meta','link','hr','input','source'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.qdepth = None; self.buf = []; self.qs = []; self.drop = 0
    def handle_starttag(self, tag, attrs):
        if tag in self.VOID: return
        cls = dict(attrs).get('class') or ''
        if 'lost' in cls.split(): self.drop += 1; self.stack.append((tag,'lost')); return
        if self.qdepth is None and 'q' in cls.split():
            self.qdepth = len(self.stack) + 1
        self.stack.append((tag,'q' if 'q' in cls.split() else ''))
    def handle_endtag(self, tag):
        if tag in self.VOID: return
        if self.stack:
            t, _ = self.stack.pop()
            if self.qdepth is not None and len(self.stack) < self.qdepth:
                self.qs.append(''.join(self.buf)); self.buf = []; self.qdepth = None
    def handle_data(self, d):
        if self.qdepth is not None and self.drop == 0:
            self.buf.append(d)

probe = re.sub(r'<span class="lost"[^>]*>.*?</span>', '', html, flags=re.S)
qc = QC(); qc.feed(probe)
if qc.stack: fails.append(f'标签未配平: {qc.stack}')
pageqs = [''.join(q.split()) for q in qc.qs]
pageqs = [norm(q) for q in pageqs if norm(q)]
print(f'[q] 收集 .q 块 {len(qc.qs)} 个')

# ---------- 期望引文（全部先对库、再对页） ----------
QUOTES = [
 "今上皇帝，太祖高皇帝第四子也。母孝慈高皇后，生五子，长懿文皇太子，次秦王，次晋王，次今上皇帝，次周王也。",
 "今上皇帝初生，云气满室，光彩五色，照映宫闼，连日不散。",
 "太祖常曰：「异日安国家，必燕王也。」",
 "学士刘三吾曰：「立燕王，置秦、晋二王于何地？且皇孙年已长，可立以继承。」",
 "至是病革，问左右曰：「第四子来未？」无敢应者，凡三问，言不及他，逾时遂崩。",
 "梓宫发引，与弟允熥各仗剑立宫门，指斥梓宫曰：「今复能言否？复能督责我否？」言讫皆笑，略无戚容。",
 "嬖幸者任其所需，谓羊不肥美，辄杀数羊以厌一妇之欲。",
 "祖训云：『朝无正臣，内有奸恶，必训兵讨之，以清君侧之恶。』",
 "待奸恶伏辜，吾行周公之事，以辅孺子，此吾之志。",
 "上见宫中烟起，急遣中使往救，至已死矣。出其尸于火中，上叹曰：「小子无知，乃至此乎？」",
 "上指烟焰处谓方孝孺曰：「今日使幼君自焚者，皆汝辈所为也，汝死有余辜。」",
 "莫逐燕，逐燕日高飞，高飞上帝畿。",
 "东方云开，露青天，仅尺许，有光烛地，洞彻上下，将士皆喜，以为上诚心感格也。",
 "天若助吾，河冰即合。",
 "有神爵五色飞驻旗竿之首，祭毕，由西北而去。",
 "上所御素红绒袍忽见白花如雪状，凝为龙纹，鳞鬣皆具，美如刺绣。",
 "忽东北风大起，尘埃涨天，沙砾击面，贼军眯目，咫尺不见。",
 "忽大风起，飞屋拔树，贼众力不能支。",
 "矢下如雨，箭集上旗，有若猬毛。",
 "臣自幼从军，多历战阵，今老矣，未尝见此战也。",
 "烧贼粮船数万余艘、粮数百万石、军资器械不可胜计，河水尽热，鱼鳖皆浮死",
 "尸填于河与桥平，人马皆乘尸而走",
 "我军三震炮，贼众误为己炮，急趋门走，门塞不得出",
 "众闻歌惨凄，皆堕泪，有怀乡之思，已无固守之志",
 "据王崇武奉天靖难记注底本明天一阁抄本改",
]
for i, q in enumerate(QUOTES):
    qn = norm(q)
    if qn not in libn:
        fails.append(f'Q{i:02d} 不在库本: {q[:30]}')
    if not any(qn in pq for pq in pageqs):
        fails.append(f'Q{i:02d} 不在页面: {q[:30]}')
print(f'[quotes] 期望 {len(QUOTES)} 条，全在库本与页面两侧断言')

# 反向：每个页面 .q 必须命中某条期望
for j, pq in enumerate(pageqs):
    if not any(norm(q) in pq or pq in norm(q) for q in QUOTES):
        fails.append(f'页面 .q#{j} 无期望来源: {pq[:36]}')

# ---------- 「」反扫 ----------
body = re.sub(r'<style>.*?</style>', '', html, flags=re.S)
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)
def strip_tags(s): return re.sub(r'<[^>]+>', '', s)
prose = strip_tags(body)
opens = [m.start() for m in re.finditer('「', prose)]
closes = [m.start() for m in re.finditer('」', prose)]
if len(opens) != len(closes): fails.append(f'「」不配对: {len(opens)}/{len(closes)}')
for a, b in zip(opens, closes):
    frag = norm(prose[a+1:b])
    if frag and frag not in libn:
        fails.append(f'「」反扫不通过: {prose[a:b+1]}')
print(f'[rev] 「」反扫 {len(opens)} 对')

# ---------- 红线 ----------
if '—' in prose or '–' in prose:
    fails.append('红线: 出现长划线 — 或 –')
for li, line in enumerate(prose.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'红线: 第{li}行有 {line.count("·")} 枚 ·')
print('[red] 长划线/· 红线')

# ---------- 机数（库本侧） ----------
def cnt(pat): return len(re.findall(pat, lib))
checks = [
    (len(lib), 54955, '全帙字符'), (len(''.join(lib.split())), 54005, '去空白'),
    (sum(1 for c in lib if '㐀' <= c <= '鿿'), 43981, '汉字'),
    (cnt('天一阁'), 78, '天一阁'), (cnt('明天一阁抄本改'), 44, '校记改'),
    (cnt('国朝典故本'), 32, '国朝典故本'), (cnt('王崇武'), 1, '王崇武'),
    (cnt('●奉天靖难记'), 4, '卷次标记'), (cnt('清君侧'), 3, '清君侧'),
    (cnt('自焚'), 4, '自焚'), (cnt('孝慈高皇后'), 9, '孝慈高皇后'),
    (cnt('金川门'), 2, '金川门'), (cnt('莫逐燕'), 1, '莫逐燕'),
    (cnt('必燕王也'), 1, '必燕王也'), (cnt('第四子来未'), 1, '第四子来未'),
    (cnt('周公之事'), 1, '周公之事'), (cnt('神爵'), 1, '神爵'),
    (cnt('允炆'), 46, '允炆'), (cnt('割股'), 1, '割股'),
    (sum(1 for c in lib if 0xE000 <= ord(c) <= 0xF8FF), 1, 'PUA'),
    (cnt('■'), 35, '■'), (cnt('□'), 0, '□'), (cnt('囗'), 0, '囗'),
]
ann = re.findall(r'（[^（）]*）', lib)
checks.append((len(ann), 112, '校记条数'))
checks.append((sum(len(a) for a in ann), 3529, '校记字符'))
checks.append((sum('改' in a for a in ann), 62, '校记改条'))
checks.append((sum('补' in a for a in ann), 48, '校记补条'))
checks.append((sum('删' in a for a in ann), 4, '校记删条'))
for got, want, label in checks:
    if got != want:
        fails.append(f'机数 {label}: 页外断言 {got} != {want}')
print(f'[num] 机数断言 {len(checks)} 项')

# ---------- 页面结构 ----------
for anchor, label in [
    ('殆知阁导读　之一百三十五　卷四鼎革', 'kicker'),
    ('<title>奉天靖难记 · 殆知阁导读之一百三十五</title>', 'title'),
    ('github.com/robertsong2000/daizhigev20', '来源'),
    ('全帙 54,955 字', '字数'),
    ('class="lost"', '缺字虚框'),
    ('class="q"', '引文块'),
    ('fubi-lu.html', '复辟录互链'),
    ('zuiwei-lu.html', '罪惟录互链'),
    ('mulu.html', '总目互链'),
    ('殆知阁古代文献简体库', '来源行'),
    ('引文均经与库本逐字核验', '核验声明'),
    ('批判眼光', '时代局限提醒'),
]:
    if anchor not in html: fails.append(f'结构缺: {label}')
if html.count('之一百三十五') < 3: fails.append('页内序号出现不足 3 处')

# ---------- 输出 ----------
print()
if fails:
    print('FAIL'); [print(' -', f) for f in fails]; sys.exit(1)
print(f'PASS — 奉天靖难记 · 导读之{NO}')
