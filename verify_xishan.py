#!/usr/bin/env python3
"""核验 xishan-qinkuang.html 引文与排版规则"""
import re, sys, unicodedata

HTML = '/home/robertsong/workspace/claude/daizhige-daodu/xishan-qinkuang.html'
SRC = '/home/robertsong/workspace/claude/daizhige-simplified/艺藏/音乐/溪山琴况.txt'

VAR = {}

def norm(s):
    s = unicodedata.normalize('NFC', s)
    s = ''.join(VAR.get(c, c) for c in s)
    return ''.join(c for c in s if re.match(r'[㐀-鿿A-Za-z0-9]', c))

html = open(HTML, encoding='utf-8').read()
body = re.sub(r'<script[\s\S]*?</script>', '', html)
src = norm(open(SRC, encoding='utf-8').read())

bad = 0
frags = [(m, 'q') for m in re.findall(r'<q>([\s\S]*?)</q>', html)]
frags += [(m, '「」') for m in re.findall(r'「([^」]+)」', html)]

for q, kind in frags:
    qc = norm(q)
    if not qc:
        bad += 1
        print(f'[EMPTY] <q> 空引文: {q[:40]}')
        continue
    if qc not in src:
        bad += 1
        print(f'[BOOK-FAIL/{kind}] {q[:60]}')
        print(f'   -> norm: {qc[:70]}')
    if qc not in norm(body):
        bad += 1
        print(f'[PAGE-FAIL/{kind}] 页面找不到（疑似 HTML 转义差异）: {q[:60]}')

# 排版红线：长划线、半字线、每行 · 至多 1 个、PUA、空 <a>
for pat, label in [(r'—', '长划线—'), (r'–', '半字线–')]:
    for m in re.finditer(pat, html):
        bad += 1
        print(f'[LAYOUT-FAIL] 发现{label}: …{html[max(0,m.start()-20):m.start()+20]}…')
for i, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        bad += 1
        print(f'[LAYOUT-FAIL] 第{i}行 · 超限: {line.strip()[:60]}')
    if any(0xE000 <= ord(c) <= 0xF8FF for c in line):
        bad += 1
        print(f'[LAYOUT-FAIL] 第{i}行 含私用区字符')

# 律盘：24 枚况字链接，锚点必须存在
gw = re.findall(r'<text class="gw"[^>]*>([^<]*)</text>', html)
if len(gw) != 24:
    bad += 1
    print(f'[PAN-FAIL] 律盘况字数 {len(gw)} != 24')
hrefs = re.findall(r'<a href="#(s-[a-z0-9]+)" aria-label', html)
if len(hrefs) != 24:
    bad += 1
    print(f'[PAN-FAIL] 律盘链接数 {len(hrefs)} != 24')
for h in hrefs:
    if f'id="{h}"' not in html:
        bad += 1
        print(f'[PAN-FAIL] 锚点缺失: {h}')
if norm(''.join(gw)) != norm('和静清远古淡恬逸雅丽亮采洁润圆坚宏细溜健轻重迟速'):
    bad += 1
    print('[PAN-FAIL] 律盘况字顺序与库本首行不一致')

# 页脚三要素与编号
for kw in ['殆知阁', '核验', '时代局限', '之一百八十三']:
    if kw not in html:
        bad += 1
        print(f'[FOOTER-FAIL] 缺 {kw}')

print('---')
print('引文片段数:', len(frags), ' 律盘况字:', len(gw))
print('FAIL:', bad)
sys.exit(1 if bad else 0)
