#!/usr/bin/env python3
# 核验脚本：q/qv 引文逐字比对 + 八十三则则目核对 + 白话反扫六字窗 + 排版规则
import re, sys, unicodedata

HTML = 'dupian-xinshu.html'
LIB  = '/home/robertsong/workspace/claude/daizhige-simplified/儒藏/修身治家/杜骗新书.txt'

def norm(s):
    return ''.join(ch for ch in s if unicodedata.category(ch).startswith(('L','N')))

html = open(HTML, encoding='utf-8').read()
lib  = open(LIB, encoding='utf-8', errors='ignore').read()
libn = norm(lib)

errs, okc = [], 0

# ---- 0. 去掉 script/style，之后的提取与反扫都基于静态 HTML ----
body0 = re.sub(r'<script.*?</script>', '', html, flags=re.S)
body0 = re.sub(r'<style.*?</style>', '', body0, flags=re.S)

# ---- 1. 提取 q / qv 元素（跳过 who 标签）----
def extract(pat):
    out = []
    for m in re.finditer(pat, body0, re.S):
        inner = re.sub(r'<span class="who"[^>]*>.*?</span>', '', m.group(1), flags=re.S)
        inner = re.sub(r'<[^>]+>', '', inner)
        out.append((m.start(), norm(inner)))
    return out

quotes = (extract(r'<div class="q(?: [^"]*)?"[^>]*>(.*?)</div>')
        + extract(r'<span class="qv"[^>]*>(.*?)</span>')
        + extract(r'<div class="qv"[^>]*>(.*?)</div>'))
for pos, q in quotes:
    if not q:
        continue
    if q in libn:
        okc += 1
    else:
        errs.append(f'引文不在库本: {q[:50]}...')

# 则目（JS 字符串里的 list，按｜分隔）
for m in re.finditer(r'list:"([^"]+)"', html):
    for t in m.group(1).split('｜'):
        tn = norm(t)
        if tn and tn not in libn:
            errs.append(f'则目不在库本: {t}')

# ---- 2. 白话反扫：去掉 q/qv、data-t 元素后，逐块 6 字窗 ----
body = re.sub(r'<[^>]*data-t[^>]*>.*?</[^>]*>', '', body0, flags=re.S)  # data-t 豁免
body = re.sub(r'<div class="q[^"]*"[^>]*>.*?</div>', '\n', body, flags=re.S)
body = re.sub(r'<span class="qv"[^>]*>.*?</span>', '\n', body, flags=re.S)
body = re.sub(r'<div class="qv"[^>]*>.*?</div>', '\n', body, flags=re.S)
body = re.sub(r'<[^>]+>', '\n', body)

hits = 0
for block in body.split('\n'):
    b = norm(block)
    for i in range(len(b) - 5):
        if b[i:i+6] in libn:
            hits += 1
            errs.append(f'反扫6字窗撞: …{b[max(0,i-6):i+12]}…')
if hits == 0:
    print('反扫：六字窗零撞')

# ---- 3. 排版规则 ----
if '—' in html or '–' in html:
    errs.append('出现长划线')
vis = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>', '\n', html)
for ln in vis.split('\n'):
    if ln.count('·') > 1:
        errs.append(f'一行多·: {ln.strip()[:40]}')

# ---- 4. 24 类则数合计 ----
counts = [int(x) for x in re.findall(r'n:(\d+),', html)]
print(f'类数 {len(counts)}，则数合计 {sum(counts)}')
if len(counts) != 24 or sum(counts) != 83:
    errs.append(f'类/则数不对: {len(counts)}/{sum(counts)}')

print(f'引文+则目核验通过 {okc} 处')
if errs:
    print('\n'.join(errs[:40]))
    sys.exit(1)
print('ALL PASS')
