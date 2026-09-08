# -*- coding: utf-8 -*-
"""宣和画谱导读页核验：正扫(q↔库)+反扫(非引文不得撞库)+红线+mulu联检。
脚本名避让 verify_xuanhe.py（宣和遗事），按系列规矩用全拼。"""
import re, sys, os
from html.parser import HTMLParser

PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/xuanhe-huapu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/绘画/宣和画谱.txt'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'

VAR = {'徳':'德','歴':'历','曆':'历','熈':'熙','浄':'净','墖':'塔','闗':'关','廏':'厩','廐':'厩',
       '蔵':'藏','畆':'亩','胷':'胸','滳':'滴','籹':'妆','掲':'揭','穪':'称','鴈':'雁','纎':'纤',
       '寛':'宽','懐':'怀','巻':'卷','靑':'青','疎':'疏','歎':'叹','荅':'答','郷':'乡',
       '碁':'棋','槩':'概','畧':'略'}

def norm(s):
    out = []
    for ch in s:
        ch = VAR.get(ch, ch)
        if ord(ch) >= 0x3400:
            out.append(ch)
    return ''.join(out)

libraw = open(LIB, encoding='utf-8').read()
libnorm = norm(libraw)
page = open(PAGE, encoding='utf-8').read()

EXEMPT = {'qsrc','fm','att','use','ig','song'}
quotes = []
scrub = []

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.in_skip = 0
    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get('class') or '')
        toks = set(cls.split())
        if tag in ('script','style'):
            self.in_skip += 1
        self.stack.append((tag, toks))
        if tag == 'q':
            quotes.append([''])
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.in_skip:
            self.in_skip -= 1
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
    def handle_data(self, d):
        if self.in_skip:
            return
        qtoks = set()
        for tag, toks in self.stack:
            qtoks |= toks
        if self.stack and self.stack[-1][0] == 'q':
            quotes[-1][0] += d
            return
        if qtoks & EXEMPT:
            return
        scrub.append((d, qtoks))

p = P(); p.feed(page)

fails = []

# 1) 正扫：每个 <q> 归一后必须是库本子串
good = []
for text, in quotes:
    n = norm(text)
    if not n:
        fails.append('空 q 元素')
        continue
    if n in libnorm:
        good.append(n)
    else:
        fails.append('正扫未命中: ' + text[:30])
if fails:
    print('正扫失败'); [print(' ', f) for f in fails]; sys.exit(1)
uniq = sorted(set(good))
print(f'正扫 {len(good)} 处（去重 {len(uniq)} 条）全部命中库本')

# 2) 反扫：非引文可见文本 8 字窗不得撞库
hits = []
for d, toks in scrub:
    n = norm(d)
    for i in range(len(n) - 7):
        w = n[i:i+8]
        if w in libnorm:
            hits.append((w, d[:40]))
hits = sorted(set(hits))
if hits:
    print('反扫撞库', len(hits), '处')
    for w, ctx in hits[:20]:
        print('  窗口', w, '…', ctx)
    sys.exit(1)
print('反扫 8 字窗 0 撞库（非引文区', len(scrub), '段已扫）')

# 3) 红线
for ch, name in (('—','长划线—'), ('–','短划线–')):
    if ch in page:
        print('红线失败：页面含', name); sys.exit(1)
for ln, line in enumerate(page.split('\n'), 1):
    if line.count('·') > 1:
        print(f'红线失败：第{ln}行 · 超过1个'); sys.exit(1)
puas = {}
for ch in page:
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or 0x20000 <= o <= 0x3FFFF:
        puas[hex(o)] = puas.get(hex(o), 0) + 1
allowed = {'0x22b0d'}
bad = {k: v for k, v in puas.items() if k not in allowed}
if bad:
    print('红线失败：出现计划外扩展区字', bad); sys.exit(1)
if 'TODO' in page or '@@' in page:
    print('红线失败：占位符残留'); sys.exit(1)
print('红线通过（无长划线；每行·≤1；扩展区字仅', list(puas.keys()), '；无占位残留）')

# 4) mulu 联检：编号连续；未入目则报告 max，已入目则校验篇号与页脚 fin 一致
m = open(MULU, encoding='utf-8').read()
nos = sorted(int(x) for x in re.findall(r'<span class="no mono">(\d+)</span>', m))
if nos != list(range(1, len(nos)+1)):
    print('mulu 编号不连续！max=', nos[-1]); sys.exit(1)
f = os.path.basename(PAGE)
if f in m:
    blk = re.search(r'<a class="entry" href="' + f + r'">.*?<span class="no mono">(\d+)</span>', m, re.S)
    if not blk:
        print('mulu 中找到文件但无篇号'); sys.exit(1)
    finm = re.search(r'导读　之([一二三四五六七八九十百零]+)<', page)
    cn = {'零':0,'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
    u = {'十':10,'百':100,'千':1000}
    def c2i(s):
        t=0;c=0
        for ch in s:
            if ch in cn: c=cn[ch]
            elif ch in u:
                if c==0: c=1
                t+=c*u[ch];c=0
        return t+c
    no, fin = int(blk.group(1)), c2i(finm.group(1))
    if no != fin:
        print(f'篇号不一致 mulu={no} fin={fin}'); sys.exit(1)
    print(f'mulu 编号 1..{nos[-1]} 连续，本页已入目篇号 {no}，与页脚一致')
else:
    print(f'mulu 编号 1..{nos[-1]} 连续，本页未入目')

# 5) 结构自检
for tag in ('</html>','</body>','id="dgrid"','id="bars"','id="axcount"'):
    if tag not in page:
        print('结构缺失:', tag); sys.exit(1)
print(f'ALL PASS · 引文 {len(good)} 处 / 去重 {len(uniq)} 条 · 反扫 0 · 红线过 · mulu max={nos[-1]}')
