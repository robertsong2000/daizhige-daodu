#!/usr/bin/env python3
"""核验 qinglou-ji.html：全部「」引文逐字对库 + 6字反扫 + 排版红线 + 机数 + mulu 联检(传参 mulu 时)。"""
import re, sys
from html.parser import HTMLParser

PAGE = 'qinglou-ji.html'
LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/青楼集.txt'

raw = open(LIB, encoding='utf-8', errors='ignore').read()

def norm(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x3400 <= o <= 0x9FFF or 0x20000 <= o <= 0x3FFFF:
            out.append(ch)
    return ''.join(out)

LIB_N = norm(raw)

class QCollect(HTMLParser):
    """收集 body 全部文本节点（逐节点，不跨标签拼接）。"""
    def __init__(self):
        super().__init__()
        self.nodes = []
    def handle_data(self, data):
        if data.strip():
            self.nodes.append(data)

html = open(PAGE, encoding='utf-8').read()
body = html[html.index('<body'):]
qc = QCollect()
qc.feed(body)
nodes = qc.nodes
qtext = ''.join(nodes)

fails = []

# ---------- 1. 全部「」引文逐字对库 ----------
spans = re.findall(r'「([^」]*)」', qtext)
bad_quotes = []
for s in spans:
    sn = norm(s)
    if len(sn) == 0:
        continue
    if sn not in LIB_N:
        bad_quotes.append(s[:42])

# 申报清单：页面中不括引号的库本成句（则目、章节题），逐条对库
DECLARED = [
    '士失其业，志则郁矣',   # 第二节标题，序语
    '赵真真杨玉娥',         # 库本则目，名册卡题
    '秦玉莲秦小莲',         # 库本则目，名册卡题
    '龙楼景丹墀秀',         # 库本则目，名册卡题
]
for s in DECLARED:
    if norm(s) not in LIB_N:
        bad_quotes.append('[申报清单] ' + s[:42])

# ---------- 2. 反扫：每个文本节点剥引文后，不得残留 ≥6 字库本连续段 ----------
G = set(LIB_N[i:i + 6] for i in range(len(LIB_N) - 5))
uncovered = []
for nd in nodes:
    t = re.sub(r'「[^」]*」', '\x00', nd)
    tn = norm(t)
    for d in DECLARED:
        tn = tn.replace(norm(d), '\x00')
    i = 0
    while i < len(tn) - 5:
        if tn[i:i + 6] in G:
            j = i
            while j < len(tn) - 5 and tn[j:j + 6] in G:
                j += 1
            uncovered.append(tn[i:j + 5])
            i = j + 1
        else:
            i += 1

# ---------- 3. 排版红线 ----------
for ln, line in enumerate(html.splitlines(), 1):
    if '—' in line or '–' in line:
        fails.append(f'[长划线] 第{ln}行')
    if line.count('·') > 1:
        fails.append(f'[·密度] 第{ln}行 {line.strip()[:40]}')

# ---------- 4. 机数 ----------
full = raw
oheads = re.findall(r'(^|\n)\s*○', full)
items_67 = len([l for l in full.split('\n') if l.strip().startswith('○') and l.strip() != '○序'])
checks = [
    ('全帙去空白 6725', len(re.sub(r'\s', '', raw)) == 6725),
    ('○行目 68(含序)', items_67 + 1 == 68),
    ('附目喜春景 1', full.count('○喜春景') == 1),
    ('李定奴无目', '○李定奴' not in full and '李定奴' in full),
    ('花旦定义在库', '凡妓以墨点破其面者为花旦' in full),
    ('末跋至正丙午', '至正丙午' in full and '夏邦彦' in full and '风月楼' in full),
    ('title 含书名', '青楼集' in re.search(r'<title>(.*?)</title>', html).group(1)),
    ('篇号 213 两处', html.count('第213篇') == 2),
    ('墨底纸白石青', '#191917' in html and '#e8e4dc' in html and '#5e8fbb' in html),
    ('无外部脚本', '<script src' not in html and '<link' not in html),
    ('核验声明', '逐字核验' in html),
    ('来源链接', 'daizhigev20' in html),
    ('生平通行申报', '通行说法' in html),
    ('卷号 一百三十', '卷一百三十' in html),
    ('名册卡 70', body.count('class="nm"') == 70),
    ('对答 4 折', body.count('class="dlg"') == 4),
    ('曲签 8', body.count('class="qsign"') == 8),
    ('终局 9 站', body.count('class="stop"') == 9),
]
for name, ok in checks:
    if not ok:
        fails.append(f'[机数] {name}')

# ---------- 5. mulu 联检 ----------
if 'mulu' in sys.argv:
    mulu = open('mulu.html', encoding='utf-8').read()
    nums = sorted(int(n) for n in re.findall(r'class="no mono">(\d+)<', mulu))
    mchecks = [
        ('mulu 含新页', 'qinglou-ji.html' in mulu),
        ('编号连续 1..215', nums == list(range(1, 216))),
        ('kicker 二百一十五', '二百一十五篇导读合订' in mulu),
        ('footer 二百一十五', '二百一十五篇导读' in mulu),
        ('卷一百三十条目', '卷一百三十' in mulu),
    ]
    for name, ok in mchecks:
        if not ok:
            fails.append(f'[mulu] {name}')

# ---------- 汇总 ----------
if bad_quotes:
    fails = [f'[引文非库本] {q}' for q in bad_quotes] + fails
if uncovered:
    fails = [f'[反扫未申报≥6字] …{seg}…' for seg in uncovered[:12]] + fails

print(f'引文对库: {len(spans)} 条, 反扫未覆盖段: {len(uncovered)}, 机数: {len(checks)} 项')
if fails:
    print(f'\nFAIL ({len(fails)}):')
    for f in fails[:30]:
        print(' ', f)
    sys.exit(1)
print('PASS: 全部「」引文逐字对库通过；6字反扫通过；排版红线通过；机数全部通过。')
