#!/usr/bin/env python3
# 云谣集杂曲子 导读页核验
import re, sys, unicodedata
from html.parser import HTMLParser

SRC = 'daizhige-simplified/诗藏/剧曲/云谣集杂曲子.txt'
PAGE = 'daizhige-daodu/yunyao-ji.html'

VAR = {'鴈': '雁', '髙': '高'}
PUNCT = re.compile(r'[\s　，。、；：？！「」『』（）《》〈〉【】·．\.\,;:\?!\(\)\[\]<>/\-—–…"\']+', re.U)

def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = ''.join(VAR.get(c, c) for c in s)
    return PUNCT.sub('', s)

src = norm(open(SRC, encoding='utf-8').read())
html = open(PAGE, encoding='utf-8').read()

fails = []

# ---------- 1. 结构闭合 ----------
VOID = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source'}
class Chk(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.bad = [], []
    def handle_starttag(self, t, a):
        if t not in VOID: self.stack.append(t)
    def handle_endtag(self, t):
        if t in VOID: return
        if not self.stack or self.stack[-1] != t:
            self.bad.append((t, self.getpos()))
        else: self.stack.pop()
c = Chk(); c.feed(html)
if c.bad or c.stack: fails.append(f'HTML闭合异常 {c.bad[:3]} 残余{c.stack[:5]}')

# ---------- 2. 文本抽取（跳过 small/lab/src 树） ----------
SKIP = {'small'}
class Tx(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = [[]]
        self.blocks = []      # (class, text)
        self.chips = []       # (yuan, jian)
        self.skip = 0
        self.cur = None       # (class, buf)
        self.inyuan = self.injian = False
        self.yb = self.jb = []
    def handle_starttag(self, t, a):
        attrs = dict(a)
        cls = attrs.get('class', '')
        if t in SKIP: self.skip += 1
        if 'verse' in cls.split() or cls == 'vq':
            self.cur = (cls, [])
        elif self.cur is not None:
            self.cur[1].append(' ')
        if 'xw' in cls.split():
            self.chips.append(['', ''])
        if self.chips and 'yuan' in cls.split(): self.inyuan = True
        if self.chips and 'jian' in cls.split(): self.injian = True
        if t in ('p','div','article','section','h1','h2','h3','li','footer','span','b','button'):
            self.lines.append([])
    def handle_endtag(self, t):
        if t in SKIP and self.skip: self.skip -= 1
        if self.cur is not None and t == 'div':
            self.blocks.append((self.cur[0], ''.join(self.cur[1])))
            self.cur = None
        if self.inyuan and t == 'span': self.inyuan = False
        if self.injian and t == 'span': self.injian = False
        if self.chips and t == 'button':
            pass
        if t in ('p','div','article','section','h1','h2','h3','li','footer','span','b','button'):
            if self.lines: self.lines[-2].extend(self.lines.pop()) if len(self.lines)>1 else None
    def handle_data(self, d):
        if self.skip: return
        if self.cur is not None: self.cur[1].append(d)
        if self.inyuan: self.chips[-1][0] += d
        if self.injian: self.chips[-1][1] += d
        if self.lines: self.lines[-1].append(d)

t = Tx(); t.feed(html)

# 块引文：每个 .verse / .vq 文本须为原文连续段
nq = 0
for cls, buf in t.blocks:
    if not buf.strip(): continue
    nq += 1
    if norm(buf) not in src:
        fails.append(f'块引文({cls})不匹配: {norm(buf)[:40]}')

# 俗字对：原写与校作须都在原文
for y, j in t.chips:
    ny, nj = norm(y), norm(j)
    if not ny or nj not in src or ny not in src:
        fails.append(f'俗字对不成立: {y}→{j}')

# 「」反扫：页面所有「」内容（剥标签后）须见于原文
text_all = ''.join(''.join(l) for l in t.lines)
for q in re.findall(r'「([^」]+)」', text_all):
    nq2 = norm(q)
    if nq2 and nq2 not in src:
        fails.append(f'「」引文不见于原文: {q[:30]}')

# ---------- 3. 排版红线 ----------
raw = html
for ch, name in [('—','长划线—'), ('–','短划线–')]:
    if ch in raw: fails.append(f'禁用{name}')
for i, ln in enumerate(text_all.split('\n')):
    if ln.count('·') > 1:
        fails.append(f'第{i}行·超限')
if re.search(r'href="http|src="http|<link', raw):
    fails.append('存在外部依赖/外链')

# ---------- 4. 结构断言 ----------
tiles = len(re.findall(r'class="tile[ "]', html))
assert_free = tiles == 30
if not assert_free: fails.append(f'词单牌数={tiles} 应30')
outs = len(re.findall(r'class="tile out"', html)); ps = len(re.findall(r'class="tile p"', html))
if (outs, ps) != (2, 12): fails.append(f'重出/伯卷牌数={outs}/{ps} 应2/12')
if nq != 14: fails.append(f'块引文数={nq} 应14(12 verse+2 vq)')
if len(t.chips) != 18: fails.append(f'俗字对数={len(t.chips)} 应18')
for kw in ['殆知阁古代文献简体库', '逐字核验', '历史视之', 'mulu.html']:
    if kw not in html: fails.append(f'页脚缺: {kw}')

print(f'块引文 {nq} 条全过 | 俗字对 {len(t.chips)} 组全过 | 「」反扫全过 | 红线全过' if not fails else '')
for f in fails: print('FAIL:', f)
sys.exit(1 if fails else 0)
