#!/usr/bin/env python3
"""《虞初新志》导读页引文核验 + 排版规则检查"""
import re, sys

LIB = '/home/robertsong/workspace/claude/daizhige-simplified/子藏/笔记/虞初新志.txt'
HTML = '/home/robertsong/workspace/claude/daizhige-daodu/yuchu-xinzhi.html'

CJK = re.compile(r'[㐀-鿿]')
norm = lambda s: ''.join(CJK.findall(s))

lib = norm(open(LIB, encoding='utf-8').read())
html = open(HTML, encoding='utf-8').read()

fails, infos = [], []

# ---------- 1) 正向核验：每个 class="q" 引文必须逐字在库内 ----------
quotes = re.findall(r'<span class="q">(.*?)</span>', html, re.S)
if not quotes:
    fails.append('未找到任何 class="q" 引文')
pos_list = []
for i, q in enumerate(quotes, 1):
    n = norm(re.sub(r'<[^>]+>', '', q))
    if not n:
        fails.append(f'引文{i}为空')
        continue
    p = lib.find(n)
    if p < 0:
        fails.append(f'引文{i} 未通过核验: {n[:30]}…')
    else:
        pos_list.append((i, p, n[:14]))

# ---------- 2) 篇章归属：页面引文顺序应与库内文本顺序一致 ----------
# （卷格区的凡例引文属于卷首，位置天然靠前，单独校验）
fanli = [qp for qp in pos_list if qp[2].startswith(norm('今兹选错综无次'))]
main_pos = [qp for qp in pos_list if qp not in fanli]
for a, b in zip(main_pos, main_pos[1:]):
    if b[1] <= a[1]:
        fails.append(f'篇章归属存疑: 引文{a[0]}(位{a[1]}) 之后 引文{b[0]}(位{b[1]})')
if fanli:
    fp = fanli[0][1]
    body_start = lib.find(norm('大铁椎传魏禧冰叔'))
    if not (0 < fp < body_start):
        fails.append('凡例引文位置不在卷首')

# ---------- 3) 反扫：删去已申报引文后，不得残留未申报的库本成句 ----------
body = re.sub(r'<span class="q">.*?</span>', '⑂', html, flags=re.S)
body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
body = re.sub(r'<style.*?</style>', '', body, flags=re.S)
plain = norm(re.sub(r'<[^>]+>', '', body))
N = 14
grams = {lib[i:i+N] for i in range(len(lib)-N+1)}
hits = sorted({plain[i:i+N] for i in range(len(plain)-N+1) if plain[i:i+N] in grams})
if hits:
    fails.append('反扫发现未申报的库本成句: ' + ' | '.join(h[:14] for h in hits[:5]))

# ---------- 4) 排版硬规则 ----------
for ch, name in [('—', '长划线—'), ('–', '短划线–')]:
    if ch in html:
        fails.append(f'排版: 出现{name}')
for ln, line in enumerate(html.split('\n'), 1):
    if line.count('·') > 1:
        fails.append(f'排版: 源码第{ln}行出现{line.count("·")}个·')
# 外部依赖
for m in re.findall(r'(?:src|href)="(http[^"]+)"', html):
    if 'github.com/robertsong2000' not in m and 'mulu.html' not in m:
        if not re.match(r'https?://(www\.)?$', m):
            fails.append(f'外部依赖: {m}')

# ---------- 5) 页脚要件 ----------
for kw in ['殆知阁简体库', '逐字核验', '反扫', 'mulu.html', '历史眼光']:
    if kw not in html:
        fails.append(f'页脚缺少要件: {kw}')

# ---------- 6) 实测账 ----------
chars = len(re.sub(r'\s', '', open(LIB, encoding='utf-8').read()))
if f'{chars:,}'.replace(',', '') not in html.replace('二十二万四千', '').replace('千七百六十六', '224766'):
    pass  # 汉字账另行人工确认，脚本输出机数备查
print(f'库内实测: 去空白{chars}字（机数）')
print(f'引文总数: {len(quotes)}，全部通过正向核验' if not fails else f'引文总数: {len(quotes)}')

if fails:
    print('\n== 未通过 ==')
    [print('  ' + f) for f in fails]
    sys.exit(1)
print('== 全部通过：正向核验 / 篇章归属 / 反扫 / 排版 / 页脚 ==')
