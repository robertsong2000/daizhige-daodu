#!/usr/bin/env python3
# 核验 zizheng-xinpian.html + mulu.html：引文双侧逐字、排版红线、mulu 编号连续
import re, sys

PAGE = 'zizheng-xinpian.html'
BOOK = '/home/robertsong/workspace/claude/daizhige-simplified/史藏/志存记录/资政新篇.txt'
MULU = 'mulu.html'

html = open(PAGE, encoding='utf-8').read()
book = open(BOOK, encoding='utf-8').read()
mulu = open(MULU, encoding='utf-8').read()
errs = []

def norm(s):
    return ''.join(re.findall(r'[一-鿿]', s))

# 1. 库本字数断言
ns = len(re.sub(r'\s', '', book))
if ns != 8257:
    errs.append(f'库本去空白字数 {ns} != 8257')

# 2. 引文双侧逐字（仅留汉字归一后子串比对）
b = norm(book)
quotes = re.findall(r'<q>(.*?)</q>', html, re.S)
if len(quotes) < 3:
    errs.append('引文过少')
for i, q in enumerate(quotes, 1):
    qn = norm(q)
    if not qn:
        errs.append(f'引文{i} 归一后为空: {q!r}')
    elif qn not in b:
        errs.append(f'引文{i} 库本无此段: {q!r}')

# 3. 禁长划线
for ch, name in [('—', 'em dash'), ('–', 'en dash')]:
    if ch in html or ch in mulu:
        errs.append(f'{PAGE}/mulu 含{name}')

# 4. 每行 · 最多 1 个（按源码行近似渲染行）
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        errs.append(f'{PAGE}:{i} 一行内多个·')

# 5. 标签配平
for tag in ['div', 'section', 'header', 'footer', 'span', 'q', 'p', 'h2', 'h3', 'svg', 'g', 'a', 'small', 'b', 'em', 'li', 'ol', 'main']:
    o = len(re.findall(rf'<{tag}[\s>]', html))
    c = len(re.findall(rf'</{tag}>', html))
    if o != c:
        errs.append(f'标签 <{tag}> 开{o}闭{c}不配平')

# 6. 零外部依赖 + 零 PUA/ExtB
if re.search(r'\ssrc=|@import|<script|<img|<link[\s>]', html):
    errs.append('存在外部依赖标签')
for ch in html:
    o = ord(ch)
    if 0xE000 <= o <= 0xF8FF or o >= 0x20000:
        errs.append(f'PUA/ExtB 字符 U+{o:X}')
        break

# 7. 页脚三件套
foot = html[html.find('<footer'):]
for need, label in [('殆知阁', '来源'), ('daizhigev20', '来源链接'), ('daizhige-daodu', '导读仓库链接'), ('核验', '核验声明'), ('时代产物', '时代局限提醒')]:
    if need not in foot:
        errs.append(f'页脚缺{label}')

# 8. mulu：收录 + 编号连续 + 计数两处
if 'zizheng-xinpian.html' not in mulu:
    errs.append('mulu 未收录本页')
nums = sorted(int(x) for x in re.findall(r'class="no mono">(\d+)<', mulu))
if nums != list(range(1, len(nums) + 1)):
    errs.append(f'mulu 编号不连续: 1..{len(nums)}')
for need, label in [('二百零二篇导读合订', 'kicker 计数'), ('二百零二篇导读，2026 年 9 月编', 'footer 计数')]:
    if need not in mulu:
        errs.append(f'mulu 缺{label}')

if errs:
    print('FAIL')
    for e in errs:
        print(' -', e)
    sys.exit(1)
print(f'PASS: 库本去空白{ns}字，引文{len(quotes)}条双侧逐字全过，mulu 编号1..{len(nums)}连续，排版红线全过')
