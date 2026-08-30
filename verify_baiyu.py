# -*- coding: utf-8 -*-
"""verify_baiyu.py 〈百喻经〉导读页核验：57 段 .q 逐字对库（三库分源）+ 排版红线 + 机数复算"""
import re, sys
from html.parser import HTMLParser

PAGE = 'baiyu-jing.html'
SRC = {
    'main': '../daizhige-simplified/佛藏/乾隆藏/西土圣贤撰集/百喻经.txt',
    'ji':   '../daizhige-simplified/佛藏/大藏经/杂藏/目录部/出三藏记集.txt',
    'ky':   '../daizhige-simplified/佛藏/乾隆藏/此土著述/开元释教录.txt',
}

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

# ---------------- QUOTES：(引文, 源) ----------------
QUOTES = [
    # hero + 序分
    ('我不欲下二重之屋。先可为我作最上屋。', 'main'),
    ('闻如是。一时佛在王舍城。在鹊封竹园。', 'main'),
    ('佛言。汝等善听。今为汝广说众喻。', 'main'),
    ('心开意解求受五戒', 'main'),
    ('答曰。亦有亦无。', 'main'),
    ('答曰。人从谷而生。', 'main'),
    ('答曰。五谷从四大火风而生。', 'main'),
    ('答曰。四大火风从空而生。', 'main'),
    ('答曰。从无所有生。', 'main'),
    ('答曰。从自然生。', 'main'),
    ('答曰。从泥洹而生。', 'main'),
    # 憨人画廊八幅 + 双签
    ('所以美者缘有盐故。少有尚尔况复多也。愚人无智便空食盐。食已口爽返为其患。', 'main'),
    ('夫答之言。我妇久死。汝是阿谁妄言我妇。乃至二三犹故不信。', 'main'),
    ('我失釪时画水作记。本所画水与此无异。是故觅之。', 'main'),
    ('我今饱足由此半饼。然前六饼唐自捐弃。设知半饼能充足者应先食之。', 'main'),
    ('尔好守门并看驴索。', 'main'),
    ('大家先付门驴及索。自是以外非奴所知。', 'main'),
    ('比得药顷王要莫看。待与药已然后示王。', 'main'),
    ('实是良医。与我女药能令卒长。', 'main'),
    ('骆驼入头瓮中食谷又不得出。既不得出以为忧恼。', 'main'),
    ('汝当斩头自得出之。即用其语以刀斩头。既复杀驼而复破瓮。', 'main'),
    ('昔有雄雌二鸽共同一巢。秋果熟时取果满巢。', 'main'),
    ('即便以觜啄雌鸽杀。', 'main'),
    ('彼实不食。我妄杀他。即悲鸣命唤雌鸽汝何处去。', 'main'),
    ('与我无物必应有无物。', 'main'),
    ('医以酥涂。上下着板。用力痛压。不觉双目一时并出。', 'main'),
    # 鼓点 + 偈 + 落款
    ('凡夫之人亦复如是。', 'main'),
    ('戏笑如叶裹', 'main'),
    ('实义在其中', 'main'),
    ('智者取正义', 'main'),
    ('戏笑便应弃', 'main'),
    ('尊者僧伽斯那造作痴花鬘竟。', 'main'),
    # 点验单术语
    ('昔有', 'main'),
    ('譬如有人', 'main'),
    ('亦复如是', 'main'),
    ('毗舍阇鬼喻估客驼死喻', 'main'),
    ('毗舍阇鬼喻估客驼死喻', 'main'),   # 校记三复现一次
    # 校记引题
    ('以梨打破头喻', 'main'),
    ('以梨打头破喻', 'main'),
    ('妇诈语称死喻', 'main'),
    ('贼盗锦绣', 'main'),
    ('贫人能作鸳鸯鸣喻', 'main'),
    ('一鸽喻', 'main'),
    ('将来之世入于地狱喻双目出', 'main'),
    ('凡一百事', 'ji'),
    ('凡有百事', 'ji'),
    ('叠毛', 'main'),        # [叠　　毛] 去空白后
    ('谷禾牛', 'main'),      # [谷-禾+牛] 去符号后
    ('卄积', 'main'),        # [卄/积]
    ('麸夫戈', 'main'),      # [麸-夫+戈]
    ('人效王眼𥆧喻', 'main'),
    ('𥆧', 'main'),
    ('𫗪', 'main'),
    # 书命跨库辅证
    ('初僧伽斯于天竺国抄集修多罗藏十二部经中要切譬喻撰为一部。凡有百事。以教授新学。', 'ji'),
    ('以永明十年秋。译出为齐文凡十卷。即百句譬喻经也。', 'ji'),
    ('沙门求那毗地。齐言德进。中印度人。', 'ky'),
    ('祐等并云译成十卷此之四卷百事足矣', 'ky'),
]

# ---------------- QCollector：栈配平 ----------------
class QCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(tag, is_q)]
        self.collected = []      # [(text, src)]
    def handle_starttag(self, tag, attrs):
        cls = ''
        src = None
        for k, v in attrs:
            if k == 'class':
                cls = v or ''
            if k == 'data-src':
                src = v
        parent_q = self.stack[-1][1] if self.stack else False
        parent_src = self.stack[-1][2] if self.stack else None
        is_q = ('q' in cls.split()) or parent_q
        eff_src = src or parent_src or 'main'
        self.stack.append((tag, is_q, eff_src))
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return
    def handle_data(self, data):
        if self.stack:
            top = self.stack[-1]
            if top[1] and top[2] is not None:
                self.collected.append((data, top[2]))

fails = []
page = open(PAGE, encoding='utf-8').read()
p = QCollector()
p.feed(page)
qs = [(norm(t), s) for t, s in p.collected]
qs = [(t, s) for t, s in qs if t]

srcs = {k: open(v, encoding='utf-8').read() for k, v in SRC.items()}
srcn = {k: norm(v) for k, v in srcs.items()}
qn = norm(page)

print(f'页面 .q 收集：{len(qs)} 段　QUOTES 清单：{len(QUOTES)} 条')

# 1) 双向核对：清单每条在对应库内；页面每段 .q 在清单内
qnorms = [norm(q) for q, _ in QUOTES]
for i, (q, s) in enumerate(QUOTES):
    if norm(q) not in srcn[s]:
        fails.append(f'QUOTE[{i}] 不在库内[{s}]: {q[:28]}…')
for i, (t, s) in enumerate(qs):
    if t not in qnorms:
        fails.append(f'页面 .q[{i}] 不在核验清单: {t[:28]}…')
if len(qs) != len(QUOTES):
    fails.append(f'页面 .q 数 {len(qs)} ≠ 清单 {len(QUOTES)}')

# 2) 库本机数复算
m = srcs['main']
secs = re.findall(r'^（[一二三四五六七八九○]+）(\S+?喻)', m, re.M)
up = [x for x in re.search(r'愚人食盐喻　.*?医治脊偻喻。', m).group(0).replace('。', '').split('　') if x]
dn = [x for x in re.search(r'五人买婢共使作喻　.*?小儿得大龟喻。', m).group(0).replace('。', '').split('　') if x]
assert len(secs) == 98, len(secs)
assert len(up) == 49 and len(dn) == 48, (len(up), len(dn))
assert m.count('凡夫之人亦复如是') == 15, m.count('凡夫之人亦复如是')
assert m.count('亦复如是') == 79, m.count('亦复如是')
assert m.count('昔有') == 71, m.count('昔有')
assert m.count('譬如有人') == 4, m.count('譬如有人')
nonspace = len(re.sub(r'\s', '', m))
assert nonspace == 20866, nonspace
assert m.startswith('百喻经二卷')
print(f'库本机数：喻{len(secs)}　目录上{len(up)}/下{len(dn)}　凡夫 refrain {m.count("凡夫之人亦复如是")}　'
      f'亦复如是 {m.count("亦复如是")}　昔有 {m.count("昔有")}　去空白 {nonspace}')

# 3) 页面数字断言
for s in ['九十八', '卷上五十，卷下四十八', '四十九题', '七十一次', '七十九见', '十五见', '20,866', '之九十六']:
    if s not in page:
        fails.append(f'页面缺数字断言串: {s}')

# 4) 排版红线：长划线；每渲染行 · ≤1
if '—' in page or '–' in page:
    fails.append('页面含长划线 — 或 –')
plain_lines = [re.sub(r'<[^>]+>', '', ln) for ln in page.split('\n')]
for i, ln in enumerate(plain_lines, 1):
    if ln.count('·') > 1:
        fails.append(f'第{i}行 · 超 1 个: {ln.strip()[:36]}')

# 5) 页脚与标题
for s in ['殆知阁简体库', 'daizhigev20', '逐字核对', '时代产物', '出三藏记集', '开元释教录']:
    if s not in page:
        fails.append(f'页面缺页脚/来源串: {s}')

if fails:
    print('FAIL')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('PASS')
