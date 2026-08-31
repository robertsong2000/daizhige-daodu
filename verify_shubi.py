#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_shubi.py — 蜀碧导读页核验：引文双侧逐字、反扫、红线、机数、结构"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/shubi.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/蜀碧.txt'
NO = 129

html = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

def norm(s):
    return ''.join(c for c in s if '\u3400' <= c <= '\u9fff' or '\U00020000' <= c <= '\U0002ffff')

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
 "「蜀碧」四卷，国朝彭遵泗撰。遵泗字磬泉，丹棱人，乾隆丁巳进士，官翰林院编修。",
 "其曰蜀碧者，取苌弘之血三年化碧意也。起明崇祯元年戊辰，至我朝康熙二年癸卯；末有附记及杨展、刘道贞、铁脚板、余飞等传。",
 "是书纪蜀乱始末及一时死节士女",
 "蜀碧者，哭蜀也。",
 "故曰哭蜀者，所以着杨嗣昌之罪而悯邵捷春之愚也",
 "故曰哭蜀者，所以吊忠魂烈魄于地下也",
 "呜呼！蜀非有深怨积怒于贼也，而残忍若此，天实为之耶？抑人事使然耶？",
 "起戊辰、止癸未",
 "起甲申、止本年十二月",
 "起乙酉、止丁亥",
 "起顺治戊子、止仁皇帝康熙二年癸卯",
 "天以万物与人，人无一物与天，鬼神明明，自思自量。",
 "命右相严锡命作批注发明之，刻诸石。",
 "割手足谓之匏奴，分夹脊谓之边地，鎗其背于空中谓之雪鳅，以火城围炙小儿谓之贯剧",
 "匏奴死、雪鳅死、贯戏死、刳腹死、边地死：",
 "士尽矣，及匠佣",
 "男尽矣，及妇女",
 "民尽矣、及僧道",
 "人尽矣，及犬牛",
 "物尽矣，及兵卒",
 "是日也，惨然操觚，悲风四起，余壹不知心之所极",
 "参将杨展大破贼于江口，焚其舟，贼奔还。",
 "献闻展兵势甚盛，大惧，率兵十数万，装金宝数千艘，顺流东下，与展决战。且欲乘势走楚，变姓名，作巨商也。",
 "展闻逆于彭山之江口，纵火大战，烧沈其舟，贼奔北，士卒辎重丧亡几尽。复走还成都。展取所遗金宝，以益军储，自是富强甲诸将（至今居民时于江底获大鞘，其金银镌有各州邑名号）。",
 "将所余蜀府金银铸鉼，及瑶宝等物，用法移锦江，锢其流，穿穴数仞实之，因尽杀凿工，下土石掩盖，然后决堤放流，使后来者不得发。名曰锢金。",
 "丙戌顺治三年（是岁十二月，献忠伏诛）。",
 "进忠指善射者章京雅布兰射之，一矢中其喉，拔矢视之，曰：果然大兵也。",
 "王乃拔佩刀仰而祝天曰：献忠罪恶滔天，毒流万姓，子受天子命奉行天诛，谨敢为百姓复仇。",
 "咱生在燕子岭，死在凤凰山",
 "修塔余一龙，拆塔张献忠。岁逢甲乙丙，此地血流红。妖运终川北，毒气播川东。吹箫不用竹，一箭贯当胸。炎兴元年诸葛孔明记。",
 "至肃王督师攻献于西充射杀之，乃知吹箫不用竹，盖肃字也。",
 "至今居民时于江底获大鞘，其金银镌有各州邑名号。",
 "贼钱肉色光润精致，不类常铜。至今得者，作妇女簪花，不减赤金。",
 "王珂你回来，饶了夹江那个龟知县罢（伪诏，资阳有人藏之，今存）。",
 "至今所书雨洗风凌，墨痕不灭。",
 "蜀中古迹尽毁于贼，惟李卫公筹边楼在保县城中，贼未至，故至今犹存。",
 "康熙四十年，其人尚在。",
 "至康熙六十年尚存，颈上刀痕宛然。",
 "临死厉声曰：宁多剐我一刀，少杀一百姓。",
 "宁作明朝武生，岂为逆贼元老？",
 "将及城门，大呼曰：贼至矣。贼杀之。",
 "贼至，命之渡，不应，问船所在，亦不应。贼胁以刃，忿怒拳击贼，贼杀之。",
 "我辈受国家养士恩三百年矣，恨不能噬贼肉以报国，尚欲腼颜求活乎？丈夫死即死耳。乞怜何益？",
 "老僧为百万生灵，忍惜如来一戒乎？遂尝数脔，贼因免之。",
 "邵公不知兵，吾一妇人，受国恩，应死，所恨与邵同死耳。",
 "吾不惧献忠，岂惧他人耶？",
 "嘉陵、峨眉间，二三遗民，不与献忠之难者，杨将军力也。且背施忘好，而取人杯酒之间，天下其谓我何？",
 "吾忍以一科累桑梓哉？",
 "洗颈待死，与抗贼杀死等死。奈何袖手待尽耶？",
 "大书于上曰：敢与残忍流贼张献忠为敌者，从我",
 "贼来生乎？死乎？曰：死。顺贼荣乎？辱乎？曰：辱。逃可免乎？曰：不敢知。曰：如是，飞策决矣。",
 "寇来则战，去则耕。",
 "先大父五吾公，讳万昆，时谋拒贼，伪持牛酒侦贼营，门军止焉，缚见酋，以计免，且绐贼旗持归，聚壮勇守险阨，贼入乡者辄杀之。一日，有打粮贼三百人突至，设伏擒获，诛之于三溪口。贼不敢近，一乡获全。",
 "夹江生员王志道缚草为笔，以大缸贮墨，渖濡三日，提出直书，不爽毫发。",
 "献熟视曰：尔有才如此，他日图我者必尔也。立用祭旗。",
 "死时，年二十七，余外曾祖也。",
 "外王父遯庵先生云：往时避寇山中，经过一茅屋，突烟腾起，疑为居人，直入，见釜中所煮皆入手掌腿足等物，骇愕失声。",
 "家老仆云：宅外里许，有饿死于道者，某某谋夜定剥之，至则止存一头，先为人所攫矣。",
 "余儿时见亲故中，老叟数人，目黄如蜡，询之，皆啖人肝所致者。",
 "王父耳授公子策，贻骏马遣之，而身诣贼酋，告以故。",
 "其食人之法，亦有如下。羹羊、饶把、火和、骨烂等名目，鸡肋篇所载云云也。",
 "杨展追贼于汉州，不及，封遗骨而还。",
 "怜尔白骨之惨，用加黄壤之封",
 "备书死难者姓名，以雪斯耻",
 "体例冗杂",
 "太涉神怪也",
]
dupwarn = 0
for i, q in enumerate(QUOTES):
    qn = norm(q)
    if qn not in libn:
        fails.append(f'Q{i:02d} 不在库本: {q[:30]}')
    if not any(qn in pq for pq in pageqs):
        fails.append(f'Q{i:02d} 不在页面: {q[:30]}')
used = {i for i,q in enumerate(QUOTES) if norm(q) in pageqs}
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
if '—' in strip_tags(re.sub(r'<style>.*?</style>','',html,flags=re.S)) or '–' in strip_tags(re.sub(r'<style>.*?</style>','',html,flags=re.S)):
    fails.append('红线: 出现长划线 — 或 –')
for li, line in enumerate(strip_tags(re.sub(r'<style>.*?</style>','',html,flags=re.S)).split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'红线: 第{li}行有 {line.count("·")} 枚 ·')
print('[red] 长划线/· 红线')

# ---------- 机数（库本侧） ----------
def cnt(pat): return len(re.findall(pat, lib))
checks = [
    (len(lib), 41685, '全帙字符'), (len(''.join(lib.split())), 40576, '去空白'),
    (sum(1 for c in lib if '㐀' <= c <= '鿿'), 33754, '汉字'),
    (cnt('至今'), 7, '至今'), (cnt('今存'), 1, '今存'), (cnt('尚存'), 2, '尚存'),
    (cnt('尚在'), 1, '尚在'), (cnt('犹存'), 2, '犹存'), (cnt('哭蜀'), 5, '哭蜀'),
    (cnt('杀杀杀'), 0, '杀杀杀'), (cnt('七杀'), 0, '七杀'),
    (cnt('先大父五吾公'), 1, '先大父五吾公'), (cnt('外曾祖'), 1, '外曾祖'),
    (cnt('外王父'), 1, '外王父'), (cnt('家老仆'), 1, '家老仆'), (cnt('余儿时'), 1, '余儿时'),
    (cnt('贯戏'), 1, '贯戏'), (cnt('贯剧'), 1, '贯剧'),
    (sum(1 for c in lib if 0xE000 <= ord(c) <= 0xF8FF), 7, 'PUA'),
    (cnt('囗'), 23, '囗'), (cnt('□'), 1, '□'),
    (cnt(r'\.'), 161, '半角句点'),
    (cnt('铁脚板传'), 1, '铁脚板传'), (cnt('余飞传'), 1, '余飞传'),
    (cnt('书周鼎昌杀贼事'), 1, '周鼎昌'), (cnt('丙戌顺治三年'), 1, '丙戌顺治三年'),
    (cnt('一乡获全'), 1, '一乡获全'), (cnt('鸡肋篇所载'), 1, '鸡肋篇所载'),
    (cnt('五吾公'), 2, '五吾公'),
]
markers = cnt('至今')+cnt('今存')+cnt('尚存')+cnt('尚在')+cnt('犹存')
checks.append((markers, 13, '幸存标记合计'))
for got, want, label in checks:
    if got != want:
        fails.append(f'机数 {label}: 页外断言 {got} != {want}')
print(f'[num] 机数断言 {len(checks)+1} 项')

# ---------- 页面结构 ----------
for anchor, label in [
    ('殆知阁导读　之一百二十九　卷七十四碧血', 'kicker'),
    ('<title>蜀碧 · 殆知阁导读之一百二十九</title>', 'title'),
    ('殆知阁导读之一百二十九<br>', 'footer'),
    ('github.com/robertsong2000/daizhigev20', '来源'),
    ('哭蜀', 'seal'),
    ('class="lost"', '缺字虚框'),
    ('jile-bian.html', '鸡肋编互链'),
    ('全帙 41,685 字，去空白 40,576，汉字 33,754', '字数'),
]:
    if anchor not in html: fails.append(f'结构缺: {label}')
if html.count('之一百二十九') < 3: fails.append('页内序号出现不足 3 处')

# ---------- 输出 ----------
print()
if fails:
    print('FAIL'); [print(' -', f) for f in fails]; sys.exit(1)
print('ALL PASS')
