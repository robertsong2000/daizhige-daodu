# -*- coding: utf-8 -*-
"""核验 刘宾客嘉话录 导读页：引文双侧逐字 + 「」反扫 + BARE 裸引 + 排版红线 + 机数断言"""
import re, sys
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/liubinke-jiahualu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/刘宾客嘉话录.txt'

html = open(PAGE, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if ch.isspace():
            continue
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x2FFFF:
            out.append(ch)
    return ''.join(out)

LIBN = norm(lib)

FAILS = []
def check(name, ok, detail=''):
    tag = 'PASS' if ok else 'FAIL'
    print(f'[{tag}] {name}' + (f'　{detail}' if detail and not ok else ''))
    if not ok:
        FAILS.append(name)

# ---------- 1. QCollector（html.parser 栈配平，VOID 不入栈） ----------
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class QCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.qdepth = None
        self.buf = []
        self.chunks = []
        self.in_skip = 0
    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get('class', '') or ''
        isq = 'q' in cls.split()
        if tag in ('style', 'script'):
            self.in_skip += 1
            return
        if isq and self.in_skip == 0:
            self.buf = []
        if tag not in VOID:
            self.stack.append(tag)
        if isq and self.in_skip == 0:
            self.qdepth = len(self.stack)
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.in_skip = max(0, self.in_skip - 1)
            return
        if tag in VOID:
            return
        if self.stack and tag == self.stack[-1]:
            self.stack.pop()
        else:
            while self.stack and tag in self.stack:
                self.stack.pop()
        if self.qdepth is not None and len(self.stack) < self.qdepth:
            txt = ''.join(self.buf)
            if txt.strip():
                self.chunks.append(txt)
            self.qdepth = None
            self.buf = []
    def handle_data(self, data):
        if self.in_skip:
            return
        if self.qdepth is not None:
            self.buf.append(data)

qc = QCollector()
qc.feed(html)
qs = [norm(c) for c in qc.chunks]
print(f'收集 .q 块：{len(qs)}')

EXPECTED = [
    '自襄阳负笈至江陵，挐叶舟，升巫峡，抵白帝城，投谒故赠兵部尚书宾客中山刘公二十八丈，求在左右学问。',
    '是岁长庆元年春，蒙丈人许措足侍立，解衣推食，晨昏与诸子起居',
    '即席听之，退而默记，或染翰竹简，或簪笔书绅，其不暇记，因而遗忘者，不知其数，在掌中梵夹者，百存一焉',
    '或因宴命坐，与语论，大抵根于教诱，而解释经史之暇，偶及国朝文人剧谈，卿相新语，异常梦话，若谐谑卜祝，童谣佳句。',
    '绚少陆机入洛之三岁，多重耳在外之二年',
    '今悉依当时日夕所话而录之，不复编次，号曰《刘公嘉话录》，传之好事，以为谈柄也。时大中十年二月，朝散大夫江陵少尹上柱国京兆韦绚序。',
    '五夜者，甲、乙、丙、丁、戊，更相送之，今惟言乙夜与子夜何也？',
    '未详。',
    '岂非颇棱国将来，而语讹为菠棱耶。',
    '菜之菠棱者，本西国中，有僧自彼将其子来，如苜蓿、蒲陶，因张骞而至也。',
    '诸葛所止，令兵士独种蔓菁者何？',
    '莫不是取其才出甲者可生啖，一也；叶舒可煮食，二也；久居则随以滋长，三也；弃去不惜，四也；回则易寻而采之，五也',
    '比诸蔬属，其利不亦博乎？',
    '信矣。',
    '为诗用僻事，须有来处。',
    '吾缘明日是重阳，欲押一“餻”字，续寻思六经竟未见有“餻”字，不敢为之。',
    '后辈业诗，即须有据，不可率尔道也。',
    '『左飧右粥』，何如我《平淮西雅》之云：『仰父俯子』。',
    '美宪宗俯下之道尽矣。',
    '韩碑柳雅',
    '城中晨鸡喔喔鸣，城头鼓角声和平',
    '美李尚书愬之入蔡城也，须臾之间，贼都不觉。',
    '始知元和十二载，四海重见升平时',
    '早过户，未尝不闻讴歌而当垆',
    '本流既大，心计转粗，不暇唱《渭城》矣。',
    '吾思官徒亦然。',
    '美不可言，美不可言。',
    '某四道节度使女，十八年宰相妻，今日相公犯罪，死即甘心；使妾为舂婢，不如死也。',
    '身为宰相，夜醮何求？',
    '知则不知，死则合死。',
    '元载于万年县佛堂子中谒主者，乞一快死也。',
    '相公今日受些子污泥，不怪也。',
    '德宗降三日，玄宗立于高阶上，肃宗次之，代宗又次之，保母襁抱德宗来呈',
    '真我儿也。',
    '汝不及他。',
    '汝亦不及他，仿佛似我。',
    '崽郎亦一遍到此来里。',
    '其母将诞之夕，梦人与秤，曰：“持之秤量天下文士。”',
    '秤量天下，岂是汝耶？',
    '宇文融合为宰相。',
    '宇文融岂堪作宰相？',
    '天符已下，数日多少即由判官。',
    '既拜，果百日而罢。',
    '官不前定，何名真宰？',
    '两角女子绿衣裳，却背太行邀君王，一止之月必消亡。',
    '安',
    '禄',
    '一止',
    '卿书与我书孰优？',
    '陛下书帝王第一，臣书人臣第一。',
    '尝以撅笔书，恐帝所忌故也。',
    '好事者乃为假面以写其状，呼为“踏摇娘”，今谓之“谈娘”。',
    '年年岁岁花相似，岁岁年年人不同。',
    '其舅宋之问苦爱此两句，知其未示人，恳乞，许而不与。之问怒，以土袋压杀之。宋生不得其死，天报之也。',
    '臣被围四十七日，凡一千二百余阵。',
    '主辱臣死，当臣致命之时；恶稔罪盈，是贼灭亡之日。',
    '向若救至身存，不过是一张仆射耳。则张巡、许远之名，焉得以光扬于万古哉！',
    '今谓进士登第为迁莺者久矣',
    '伐木丁丁，鸟鸣嘤嘤，出自幽谷，迁于乔木。',
    '名下定无虚士。',
    '坐卧观之，留宿其下，十日不能去。',
    '驻马观之，良久而去。数百步复还，下马伫立，疲倦则布毯坐观。因宿其下，三日而去。',
    # 绚字文明／诸史艺文志两条在 verdict 内以「」呈现，由反扫覆盖
    '盖《学海类编》所收诸书，大抵窜改旧本，以示新异。',
    '皆全与李绰《尚书故实》相同，间改窜一二句，其文必拙陋不通。',
    '幸所搀入者尚有踪迹可寻，今悉刊除，以存其旧。',
    '开成末，韦绚自左补阙为起居舍人。',
    '绚即置笔札于玉阶栏槛之石，遽然趋而致词拜舞焉。',
    '至武宗即位，随仗而退，无复簪笔之任矣。',
]
for i, qn in enumerate(EXPECTED):
    q = norm(qn)
    check(f'引文{i+1:02d} 页面载有', any(q in pq for pq in qs), qn[:30])
    check(f'引文{i+1:02d} 库本有据', q in LIBN, qn[:30])

# ---------- 2. BARE 裸引（页面叙述中直接放库内原文、不在 .q 或「」内） ----------
BARE = [
    '在掌中梵夹者，百存一焉',          # hero 竖排
    '传之好事，以为谈柄也',            # coda 大字
    '百存一焉',                        # coda 正文
    '今悉刊除',                        # 书命链
    '措足侍立',                        # 讲席 lead 用「许措足侍立」？改查整体
]
for b in BARE:
    nb = norm(b)
    inpage = nb in norm(re.sub(r'<[^>]+>', '', html))
    inlib = nb in LIBN
    check(f'BARE {b[:14]}', inpage and inlib)

# ---------- 3. 「」反扫：页面所有「」内容必须库本有据 ----------
body_no_style = re.sub(r'<style>.*?</style>', '', html, flags=re.S)
body_no_style = re.sub(r'<script>.*?</script>', '', body_no_style, flags=re.S)
plain = re.sub(r'<[^>]+>', '', body_no_style)
quotes = re.findall(r'「([^「」]+)」', plain)
check('「」反扫数量', len(quotes) > 0, str(len(quotes)))
for t in quotes:
    nt = norm(t)
    check(f'「」库内 {t[:16]}', nt in LIBN)

# ---------- 4. 排版红线 ----------
check('禁长划线—', '—' not in html)
check('禁短划线–', '–' not in html)
bad_dot = []
for ln in plain.splitlines():
    if ln.count('·') > 1:
        bad_dot.append(ln.strip()[:40])
check('每行·≤1', not bad_dot, str(bad_dot))

# ---------- 5. 机数断言（对库本复算） ----------
ns = ''.join(lib.split())
han = sum(1 for c in lib if '㐀' <= c <= '鿿' or '\U00020000' <= c <= '\U0002ffff')
lines = lib.splitlines()
body_idx = [i for i in range(14, 240) if lines[i].strip() and lines[i].strip() != '　　 ']
pua = sum(1 for c in lib if 0xE000 <= ord(c) <= 0xF8FF)
extb_list = [c for c in lib if 0x20000 <= ord(c) <= 0x2FFFF]

check('总字数 22,836', len(lib) == 22836, str(len(lib)))
check('去空白 21,357', len(ns) == 21357, str(len(ns)))
check('汉字 17,039', han == 17039, str(han))
check('正文 113 段', len(body_idx) == 113, str(len(body_idx)))
check('绚曰 7', lib.count('绚曰') == 7)
check('公曰 12', lib.count('公曰') == 12)
check('禹锡曰 20', lib.count('禹锡曰') == 20)
check('刘禹锡曰 15', lib.count('刘禹锡曰') == 15)
check('公答未详仅一见', len(re.findall(r'公曰：“未详', lib)) == 1)
check('提要「一条」41', lines[3].count('一条') == 41, str(lines[3].count('一条')))
check('唐语林 44', lib.count('唐语林') == 44)
check('太平广记 28', lib.count('太平广记') == 28)
check('长庆元年 2', lib.count('长庆元年') == 2)
check('大中十年 2', lib.count('大中十年') == 2)
check('干道癸巳 1', lib.count('干道癸巳') == 1)
check('PUA 0', pua == 0)
check('ExtB 3 种 6 见', len(set(extb_list)) == 3 and len(extb_list) == 6)
check('缺字□ 11', lib.count('□') == 11)
check('拆字｛ 4', lib.count('｛') == 4)
check('856-821=35', 856 - 821 == 35)

# 提要点名抽查 34 条名目正文俱在
body = lib[lib.find('刘宾客嘉话录正文'):lib.find('刘宾客嘉话录补遗')]
named = ['昭明太子胫骨','人腊','蜀王尝造千面琴','百衲琴','碧落碑','狸骨','张嘉佑','刺猬','汲冢书','牡丹花','王僧虔','蜀道易','受禅碑','书断','九井','虎头骨','五星','紫芝殿','王次仲','商胡','项斯','石经','借船帖','飞白书','寒具','金根车','迁莺','千字文','尧女冢','圣善寺银佛','谢真人']
found = [n for n in set(named) if n in body]
check('点名抽查 31 条俱在正文', len(found) == 31, f'{len(found)}/{len(set(named))}')

# ---------- 6. 页面结构断言 ----------
check('grid100 存在', 'grid100' in html)
check('grid100 lit 1 枚', 'i === 54' in html)
check('cutcells 41 格', 'j < 41' in html)
check('title 篇号', '第140篇' in html)
check('页脚来源', '子藏/笔记/刘宾客嘉话录.txt' in html)
check('页脚核验声明', '逐字核验' in html)
check('页脚时代局限', '阅读时须加分辨' in html)
check('返回总目', 'href="mulu.html"' in html)

print()
print(f'共 {len(FAILS)} 项 FAIL')
if FAILS:
    for f in FAILS:
        print('  FAIL:', f)
    sys.exit(1)
print('ALL PASS')
