#!/usr/bin/env python3
"""verify_yisi.py — 抱残守缺斋乙巳日记导读页核验
正向: 页面一切引文(.q/q/[data-q] .lt/[data-q] .ttr span, .q 内 <i> 视为本页标签剥除)
      去标点空白归一后必须逐字见于库本。
反向: 其余散文文本节点, 12字窗不得命中库本(未标记引文即失败)。
红线: 长划线、行内多·、扩展区/私用区字符、button 嵌套。
机数: 库本去空白28874、296则、临帖77、购藏42、撰老残5, 页面硬编码须一致。
mulu: 若已收录则联检 href 计数、编号连续、计数文案。
"""
import re, sys, json
from html.parser import HTMLParser

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/抱残守缺斋乙巳日记.txt'
PAGE = '/home/robertsong/workspace/claude/daizhige-daodu/yisi-riji.html'
MULU = '/home/robertsong/workspace/claude/daizhige-daodu/mulu.html'

lib_raw = open(LIB, encoding='utf-8').read()

def norm(s):
    return ''.join(ch for ch in s if ('一' <= ch <= '鿿') or ('㐀' <= ch <= '䶿') or ch.isascii() and ch.isalnum())

NLIB = norm(lib_raw)

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.quotes, self.prose = [], []
        self.stack = []          # (tag, kind) kind: skip|q|i|prose-context
        self.cur = None          # current accumulating quote buffer

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get('class') or '').split()
        kinds = [k for _, k in self.stack]
        if tag in ('script', 'style'):
            self.stack.append((tag, 'skip')); return
        if 'q' in cls or tag == 'q':
            self.cur = [] if self.cur is None else self.cur
            self.stack.append((tag, 'q')); return
        if 'i' in cls or tag == 'i' or 'tth' in cls or 'lh' in cls or 'rh' in cls:
            self.stack.append((tag, 'i')); return
        if a.get('data-q') is not None:
            self.stack.append((tag, 'dq')); return
        if 'lt' in cls or 'ttr' in cls:
            self.stack.append((tag, 'lt')); return
        if any(k in ('dq', 'lt') for k in kinds) and tag == 'span' and 'i' not in kinds:
            self.stack.append((tag, 'lt')); return
        self.stack.append((tag, 'in'))

    def handle_endtag(self, tag):
        for idx in range(len(self.stack) - 1, -1, -1):
            if self.stack[idx][0] == tag:
                top = self.stack[idx:]
                kinds = [k for _, k in top]
                text = ''.join(top_t for top_t in [])
                del self.stack[idx:]
                # 收束 quote
                if 'q' in kinds and self.cur is not None:
                    buf = self.cur; self.cur = None
                    self.quotes.append(''.join(buf))
                elif ('lt' in kinds) and self.cur is not None:
                    buf = self.cur; self.cur = None
                    t = ''.join(buf)
                    if t.strip():
                        self.quotes.append(t)
                return

    def handle_data(self, data):
        kinds = [k for _, k in self.stack]
        if 'skip' in kinds:
            return
        if self.cur is not None:
            if 'i' in kinds:
                return          # .q 内 <i> 是本页标签
            self.cur.append(data)
            return
        if any(k in ('dq', 'lt') for k in kinds):
            if 'lt' in kinds:
                self.quotes.append(data)
            return
        if data.strip():
            self.prose.append(data)

def parse(page):
    p = P()
    p.feed(open(page, encoding='utf-8').read())
    return p

page_raw = open(PAGE, encoding='utf-8').read()
p = parse(PAGE)
fails = []

# ---- 正向引文 ----
seen = set()
qcount = 0
for q in p.quotes:
    n = norm(q)
    if len(n) < 4:
        continue
    qcount += 1
    if n not in NLIB:
        fails.append('引文不在库本: ' + q.strip()[:60])
    seen.add(n)

# ---- 反向 12 字窗 ----
for t in p.prose:
    n = norm(t)
    for i in range(0, max(0, len(n) - 11)):
        w = n[i:i + 12]
        if w in NLIB:
            fails.append('反扫命中(未标记引文): ' + t.strip()[:50] + ' ||窗: ' + w)
            break

# ---- 红线(只扫可见文本; 嵌入数据JSON属库本原样, 不在此列) ----
visible = ''.join(p.prose + p.quotes)
if '—' in visible: fails.append('页面含长划线 —')
if '–' in visible: fails.append('页面含短划线 –')
for ch in set(visible):
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or 0xF900 <= o <= 0xFAFF or o > 0xFFFF:
        fails.append(f'私用/扩展区字符 {ch} U+{o:04X}')
for m in re.finditer(r'<button[^>]*>[^<]*<button', page_raw):
    fails.append('button 嵌套')
for node in p.prose + p.quotes:
    if node.count('·') > 1:
        fails.append('行内多·: ' + node.strip()[:40])

# ---- 机数 ----
n_nonspace = len(re.sub(r'\s', '', lib_raw))
if n_nonspace != 28874:
    fails.append(f'库本去空白 {n_nonspace} != 28874')
if '28,874' not in page_raw: fails.append('页面缺 28,874 字数硬编码')
if '296 则' not in page_raw: fails.append('页面缺 296 则硬编码')
if '二百九十六则' not in page_raw: fails.append('页面缺 二百九十六则')
if '七十七则提到临帖' not in page_raw: fails.append('页面缺 临帖77 硬编码')
seg_ok = len(re.findall(r'^（?(?:元旦|[初一二三四五六七八九十]{1,4}日?)（(?:\d+年)?\d+月\d+日）', lib_raw, re.M))
heads = re.split(r'\n(?=(?:元旦|[初一二三四五六七八九十]{1,4}日?)（(?:\d+年)?\d+月\d+日）)', lib_raw)
n_lin = sum(1 for h in heads if '临《' in h)
if n_lin != 77: fails.append(f'库本临帖则数 {n_lin} != 77')
n_lc = sum(1 for h in heads if '老残游记' in h)
if n_lc != 5: fails.append(f'库本老残则数 {n_lc} != 5')

# ---- 结构 ----
for key in ('文本来源', '库外申报', '时代局限提醒', 'mulu.html', 'daizhigev20'):
    if key not in page_raw:
        fails.append('页面缺结构要素: ' + key)
for kw in ('第二百六十八篇', '第二百六十八'):
    if kw not in page_raw:
        fails.append('页面缺篇号: ' + kw)

# ---- mulu 联检(若已收录) ----
mulu = open(MULU, encoding='utf-8').read()
if 'yisi-riji.html' in mulu:
    if mulu.count('href="yisi-riji.html"') != 1:
        fails.append('mulu href 计数 != 1')
    if mulu.count('yisi-riji.html') != 2:
        fails.append('mulu 总出现 != 2(href+file)')
    nos = [int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu)]
    if sorted(nos) != list(range(1, max(nos) + 1)):
        fails.append('mulu 编号不连续')
    if max(nos) != 268:
        fails.append(f'mulu 最大篇号 {max(nos)} != 268')
    if '二百六十八篇' not in mulu:
        fails.append('mulu 计数文案未更新为二百六十八')
else:
    print('[mulu] 尚未收录, 跳过联检')

print(f'正向引文 {qcount} 处(去重 {len(seen)}), 反扫文本节点 {len(p.prose)} 个')
if fails:
    print('FAIL', len(fails))
    for f in fails[:30]:
        print(' -', f)
    sys.exit(1)
print('PASS')
