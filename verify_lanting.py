#!/usr/bin/env python3
# 核验 lanting-kao.html：引文双侧逐字（去标点+私用区/□归一）、禁长划线、每行中点≤1、
# 「」配对、零外链、机数（字数/名册人数）、结构（JS 挂点、诗签拼回）。
import json, re, sys
from html.parser import HTMLParser

SRC = 'daizhige-simplified/史藏/目录/兰亭考.txt'
PAGE = 'daizhige-daodu/lanting-kao.html'

raw_file = open(SRC, encoding='utf-8').read()
html = open(PAGE, encoding='utf-8').read()

PUNCT = set("，。；：？！「」『』（）《》〈〉【】〔〕·・“”‘’…—－丶:;,.!?()[]{}<>@#$%^&*_+=/|~`　\t \n\r'\"\\、。")

def is_pua(ch):
    return 0xE000 <= ord(ch) <= 0xF8FF

# 私用区归一表：ea20＝玄（房□龄／□冥／王□之），eb3c＝将（云□入昭陵／兰亭□去也）
PUA_MAP = {0xEA20: '玄', 0xEB3C: '将'}

def norm(s):
    out = []
    for ch in s:
        if is_pua(ch):
            ch = PUA_MAP.get(ord(ch), '')
        if ch != '□' and ch not in PUNCT:
            out.append(ch)
    return ''.join(out)

fails = []

# 1 字数机数
n = len(re.sub(r'[\s　]', '', raw_file))
m = re.search(r'去空白<span class="mono">([\d,]+)</span>', html)
if not m or int(m.group(1).replace(',', '')) != n:
    fails.append(f'字数不符: 页{m.group(1) if m else "无"} vs 实测{n}')
if '四万四千九百六十八' not in html:
    fails.append('页脚汉字字数缺失')

# 2 引文：每个 data-k 块与库本、页面双向核对
Q = json.load(open('/tmp/lanting_q.json', encoding='utf-8'))
page_text = norm(re.sub(r'<[^>]+>', '', html))
for k, v in Q.items():
    nv = norm(v)
    if nv not in norm(raw_file):
        fails.append(f'[{k}] 库本失配')
    if nv not in page_text:
        fails.append(f'[{k}] 页面失配')
# 诗签也在 Q 中
if 'shi3' not in Q or 'shi4' not in Q:
    fails.append('Q 缺诗签键')

# 3 诗签 DOM 拼回（只收 b 内文本）
class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cur, self.buf, self.inb = None, [], False
        self.poems = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'div' and 'data-k' in a and a.get('data-k', '').startswith('shi'):
            self.cur = a['data-k']
            self.buf = []
        if tag == 'b' and self.cur:
            self.inb = True
    def handle_endtag(self, tag):
        if tag == 'div' and self.cur:
            self.poems[self.cur] = ''.join(self.buf)
            self.cur = None
        self.inb = False
    def handle_data(self, d):
        if self.cur and self.inb:
            self.buf.append(d)
p = P()
p.feed(html)
for k in ('shi3', 'shi4'):
    got = norm(p.poems.get(k, ''))
    want = norm(Q[k])
    if got != want:
        fails.append(f'诗签[{k}]拼回不等: got{len(got)} want{len(want)}')

# 4 禁长划线
for ch in '—–':
    if ch in html:
        fails.append(f'含长划线{ch!r}')

# 5 每行· ≤ 1
for ln, line in enumerate(html.split('\n'), 1):
    c = line.count('·') + line.count('・')
    if c > 1:
        fails.append(f'第{ln}行中点{c}个')

# 6 「」配对
if html.count('「') != html.count('」'):
    fails.append(f'「」不配对 {html.count("「")}/{html.count("」")}')

# 7 零外链
for mm in re.finditer(r'href="([^"]*)"', html):
    if mm.group(1).startswith('http'):
        fails.append(f'外链 {mm.group(1)}')

# 8 结构挂点
for idv in ('judgebox', 'court', 'xianzhi'):
    if f'id="{idv}"' not in html:
        fails.append(f'缺 id={idv}')

# 9 名册机数
fin = len(re.findall(r'class="chip fin', html))
if fin != 16:
    fails.append(f'罚觥{fin}人不为16')
plain = len(re.findall(r'class="chip"', html))
if plain != 26:
    fails.append(f'成诗{plain}签不为26')
if '四十二人' not in html:
    fails.append('缺四十二人总数')

print('\n'.join(fails) if fails else 'ALL PASS')
sys.exit(1 if fails else 0)
