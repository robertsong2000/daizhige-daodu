#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_dayi.py — 《大义觉迷录》导读页核验
1) 页面全部 .q 引文逐字对库（去标点+去空白后子串比对）
2) 页内机数断言（字数/问条/词频）
3) 排版红线（禁 — –，每行·≤1，PUA 不入引文）
"""
import re, sys
from html.parser import HTMLParser

PAGE = 'dayi-juemilu.html'
LIB = '../daizhige-simplified/史藏/诏令奏议/大义觉迷录.txt'

lib = open(LIB, encoding='utf-8').read()
page = open(PAGE, encoding='utf-8').read()

def norm(s):
    out = []
    for ch in s:
        if ch.isspace():
            continue
        cat = __import__('unicodedata').category(ch)
        if cat.startswith('P') or cat.startswith('S'):
            continue
        out.append(ch)
    return ''.join(out)

# ---------- 1. 引文收集（class 恰含 q，q 不嵌套） ----------
class QC(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bufs = []
        self.open_q = None
    def handle_starttag(self, tag, attrs):
        if 'q' in ((dict(attrs).get('class') or '').split()):
            self.bufs.append([])
            self.open_q = len(self.bufs) - 1
    def handle_endtag(self, tag):
        if self.open_q is not None:
            self.open_q = None
    def handle_data(self, d):
        if self.open_q is not None:
            self.bufs[self.open_q].append(d)

qc = QC(); qc.feed(page)
quotes = [''.join(x) for x in qc.bufs]
print(f'共收集 .q 引文 {len(quotes)} 段')

libn = norm(lib)
fails = []
for i, q in enumerate(quotes, 1):
    qn = norm(q)
    if not qn:
        fails.append((i, q, '空'))
        continue
    for c in q:
        if 0xE000 <= ord(c) <= 0xF8FF or 0x20000 <= ord(c) <= 0x3FFFF:
            fails.append((i, q, f'引文含生僻/PUA U+{ord(c):X}'))
    if qn not in libn:
        fails.append((i, q, '库内未命中'))

if fails:
    for i, q, why in fails:
        print(f'  FAIL #{i} [{why}] {q[:50]}')
    sys.exit(f'{len(fails)} 段引文未过')
print(f'  引文 {len(quotes)}/{len(quotes)} 全部逐字命中（去标点+去空白）')

# ---------- 2. 机数断言 ----------
lib_ns = ''.join(lib.split())
han = len(re.findall(r'[㐀-鿿\U00020000-\U0003ffff]', lib))
checks = [
    ('全帙字符', len(lib), 87743),
    ('去空白', len(lib_ns), 87332),
    ('汉字', han, 75409),
    ('问条(编辑标题)', sum(1 for l in lib.split(chr(10))
        if re.match(r'^[一二三四五六七八九十]+[、　 ]', l.strip()) and len(l.strip()) < 60), 55),
    ('弥天重犯', lib.count('弥天重犯'), 246),
    ('曾静', lib.count('曾静'), 261),
    ('吕留良', lib.count('吕留良'), 86),
    ('岳钟琪', lib.count('岳钟琪'), 50),
    ('张熙', lib.count('张熙'), 27),
    ('阿其那', lib.count('阿其那'), 66),
    ('塞思黑', lib.count('塞思黑'), 46),
    ('禽兽', lib.count('禽兽'), 56),
    ('上谕：', lib.count('上谕：'), 9),
    ('特谕', lib.count('特谕'), 4),
    ('奉上谕', lib.count('奉上谕'), 5),
    ('允缇缇(叠字讹在库)', lib.count('允缇缇'), 1),
]
bad = 0
for name, got, want in checks:
    ok = got == want
    print(f'  {"OK " if ok else "FAIL"} {name}: {got} (期望 {want})')
    bad += 0 if ok else 1
if bad: sys.exit(f'{bad} 项机数不符')

# ---------- 3. 页面结构断言 ----------
pc = [
    ('title 之九十九', '之九十九' in page),
    ('卷五十五 觉迷', '卷五十五　觉迷' in page),
    ('罪名签 11 枚', page.count('class="crime-chip"') == 11),
    ('学宫格 12 格', page.count('class="shelf full"') == 12),
    ('书命六站', len(re.findall(r'class="fate-stop[" ]', page)) == 6),
    ('流言笺 4 枚', page.count('class="r-name"') == 4),
    ('缺字框 1 处', page.count('class="lost"') == 1),
    ('页脚核验声明', '引文已经脚本对库逐字核验' in page),
    ('页脚时代局限', '时代产物' in page),
    ('页脚来源', '殆知阁简体库' in page),
    ('网络通道申报', '搜索配额冻结' in page),
]
bad = 0
for name, ok in pc:
    print(f'  {"OK " if ok else "FAIL"} {name}')
    bad += 0 if ok else 1
if bad: sys.exit(f'{bad} 项结构断言不符')

# ---------- 4. 排版红线 ----------
if '—' in page or '–' in page:
    sys.exit('红线：出现长划线')
viol = [(n+1, l) for n, l in enumerate(page.split(chr(10))) if l.count('·') > 1]
if viol:
    sys.exit(f'红线：单行·超限 {viol[:3]}')
print('  OK 排版红线（无长划线，每行·≤1）')
print('verify_dayi.py 全部通过')
